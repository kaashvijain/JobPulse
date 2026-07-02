from datetime import datetime, timezone
import logging
import asyncio
import httpx
from fastapi import APIRouter, Query, HTTPException, status
from backend.models import JobPulseResponse, PostingsData
from backend.services.cache import InMemoryTTLCache
from backend.services.scoring import calculate_momentum_score
from backend.services.postings import USAJobsClient
from backend.services.news import NewsClient
from backend.services.gemini import GeminiClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# Instantiate services
cache = InMemoryTTLCache(default_ttl_seconds=600)  # 10 minutes cache
usajobs_client = USAJobsClient()
news_client = NewsClient()
gemini_client = GeminiClient()

@router.get(
    "/job-pulse",
    response_model=JobPulseResponse,
    summary="Get job market status and trends",
    description="Calculate job posting counts and news sentiment to determine if a market is heating up, stable, or cooling down."
)
async def get_job_pulse(
    role: str = Query(..., description="Job role or title to analyze (e.g., 'Software Engineer')", min_length=1),
    city: str = Query(..., description="City or location to analyze (e.g., 'San Francisco')", min_length=1)
):
    # Normalize input
    clean_role = role.strip()
    clean_city = city.strip()
    
    # 1. Check cache first
    try:
        cached_result = await cache.get(clean_role, clean_city)
        if cached_result is not None:
            logger.info(f"Cache HIT for role='{clean_role}', city='{clean_city}'")
            return cached_result
    except Exception as e:
        logger.error(f"Error checking cache: {str(e)}")
        
    logger.info(f"Cache MISS for role='{clean_role}', city='{clean_city}'. Fetching live data...")

    # 2. Fetch job postings and news concurrently
    try:
        weekly_counts, news_headlines = await asyncio.gather(
            usajobs_client.get_weekly_posting_counts(clean_role, clean_city),
            news_client.get_hiring_news(clean_role, clean_city),
            return_exceptions=False
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTPStatusError fetching external data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External service dependency error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Error fetching external data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve data from job and news providers: {str(e)}"
        )

    # 3. Calculate momentum score
    try:
        score = calculate_momentum_score(weekly_counts)
    except Exception as e:
        logger.error(f"Error calculating momentum score: {str(e)}")
        score = 0.0

    # 4. Request Gemini Reasoning
    try:
        gemini_result = await gemini_client.analyze_market(
            role=clean_role,
            city=clean_city,
            weekly_counts=weekly_counts,
            momentum_score=score,
            news_headlines=news_headlines
        )
    except Exception as e:
        logger.error(f"Error requesting Gemini reasoning: {str(e)}")
        # Handled in Gemini client fallback, but as an extra safeguard:
        gemini_result = {
            "market_trend": "stable",
            "llm_explanation": "A structural assessment could not be generated. Defaulting to stable analysis."
        }

    # 5. Assemble response object
    as_of_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    response_data = JobPulseResponse(
        role=clean_role,
        city=clean_city,
        as_of=as_of_timestamp,
        postings=PostingsData(
            weekly_counts=weekly_counts,
            score=score
        ),
        news=news_headlines,
        market_trend=gemini_result.get("market_trend", "stable"),
        llm_explanation=gemini_result.get("llm_explanation", "")
    )

    # 6. Save in cache
    try:
        await cache.set(clean_role, clean_city, response_data)
    except Exception as e:
        logger.error(f"Failed to save response to cache: {str(e)}")

    return response_data
