from pydantic import BaseModel, Field
from typing import List

class PostingsData(BaseModel):
    weekly_counts: List[int] = Field(
        ..., 
        description="Weekly posting counts in chronological order (oldest to newest, e.g. Week 5, Week 4, Week 3, Week 2, Week 1)"
    )
    score: float = Field(..., description="Calculated momentum score")

class JobPulseResponse(BaseModel):
    role: str = Field(..., description="Job role analyzed")
    city: str = Field(..., description="City analyzed")
    as_of: str = Field(..., description="ISO 8601 formatted timestamp of the analysis")
    postings: PostingsData = Field(..., description="Job posting statistics")
    news: List[str] = Field(..., description="Top 5 hiring/layoff news headlines")
    market_trend: str = Field(..., description="Final market trend: heating up, stable, or cooling down")
    llm_explanation: str = Field(..., description="AI explanation referencing trend and news")

class GeminiReasoningResponse(BaseModel):
    market_trend: str = Field(..., description="heating up | stable | cooling down")
    llm_explanation: str = Field(..., description="2-4 sentence explanation referencing both trend and news")
