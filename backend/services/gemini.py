import os
import json
import logging
from typing import List, Dict, Any
from backend.models import GeminiReasoningResponse

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        # The new Google GenAI SDK uses GEMINI_API_KEY or GEMINI_API_KEY
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            # Fallback check for standard GOOGLE_API_KEY
            self.api_key = os.getenv("GOOGLE_API_KEY", "").strip()
            
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    def is_mock(self) -> bool:
        return not self.api_key or self.api_key.lower() == "mock"

    async def analyze_market(
        self, role: str, city: str, weekly_counts: List[int], momentum_score: float, news_headlines: List[str]
    ) -> Dict[str, Any]:
        """
        Calls Gemini to perform reasoning on the posting trend and headlines.
        Returns a dictionary with 'market_trend' and 'llm_explanation'.
        """
        # Determine the initial trend from the score
        if momentum_score > 0.15:
            initial_trend = "heating up"
        elif momentum_score < -0.15:
            initial_trend = "cooling down"
        else:
            initial_trend = "stable"

        if self.is_mock():
            logger.info("Using mock Gemini service (GEMINI_API_KEY or GOOGLE_API_KEY is not set or mock)")
            return self._generate_mock_reasoning(role, city, weekly_counts, momentum_score, news_headlines, initial_trend)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            # Build the prompt
            prompt = f"""
Analyze the job market for:
- Role: {role}
- City: {city}
- Weekly posting counts (chronological, oldest to newest): {weekly_counts}
- Calculated momentum score: {momentum_score:.4f} (interpreted as '{initial_trend}')
- Top news headlines:
{chr(10).join([f"  * {headline}" for headline in news_headlines])}

Please assess if the market is 'heating up', 'stable', or 'cooling down'. Note that you can override the initial mathematical momentum interpretation of '{initial_trend}' if the news context strongly suggests otherwise (e.g., massive layoffs in the news might override a slightly positive posting score, or high hiring activity might override a slightly flat posting trend).

You MUST return a JSON object with:
1. "market_trend": one of the strings: "heating up", "stable", or "cooling down"
2. "llm_explanation": a concise 2-4 sentence explanation referencing both the weekly posting trends (numbers) and the news headlines.

DO NOT return any markdown formatting, backticks, or text commentary outside the JSON object.
"""

            # Call Gemini
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiReasoningResponse,
                    system_instruction=(
                        "You are a professional labor market and recruitment trends analyst. "
                        "You evaluate quantitative posting trends and qualitative news context to decide "
                        "if a job market is heating up, stable, or cooling down."
                    ),
                    temperature=0.2,
                ),
            )

            # Parse the JSON response
            text = response.text.strip()
            # Clean possible markdown wrap (defensive coding)
            if text.startswith("```json"):
                text = text.replace("```json", "", 1)
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)
            return {
                "market_trend": result.get("market_trend", initial_trend),
                "llm_explanation": result.get("llm_explanation", "No explanation could be generated.")
            }

        except Exception as e:
            logger.error(f"Gemini API execution failed: {str(e)}")
            # Return initial trend and default explanation on error
            return {
                "market_trend": initial_trend,
                "llm_explanation": f"Note: AI analysis fell back due to API connection issue. The market is mathematically evaluated as {initial_trend} based on a posting momentum score of {momentum_score:.2f}."
            }

    def _generate_mock_reasoning(
        self, role: str, city: str, weekly_counts: List[int], momentum_score: float, news_headlines: List[str], initial_trend: str
    ) -> Dict[str, Any]:
        """
        Generates realistic reasoning matching the trend.
        """
        first = weekly_counts[0] if weekly_counts else 0
        last = weekly_counts[-1] if weekly_counts else 0
        pct = abs(momentum_score) * 100

        if initial_trend == "heating up":
            explanation = (
                f"The job market for {role} in {city} is heating up. "
                f"Weekly job listings rose from {first} to {last} ({pct:.1f}% increase) over the last five weeks. "
                f"This growth is supported by positive news reports, such as local operations expansions and new venture funding rounds."
            )
        elif initial_trend == "cooling down":
            explanation = (
                f"The job market for {role} in {city} is cooling down, reflecting a {pct:.1f}% decline "
                f"in weekly vacancy counts from {first} down to {last}. "
                f"News articles reporting organizational restructuring and workforce resizing suggest that employers are tightening budgets."
            )
        else:
            explanation = (
                f"The job market for {role} in {city} appears stable. "
                f"Vacancy counts hovered around {first} postings weekly with minor fluctuations (momentum of {momentum_score:.1f}%). "
                f"News headlines paint a balanced picture of typical organizational changes without significant market displacement."
            )

        return {
            "market_trend": initial_trend,
            "llm_explanation": explanation
        }
