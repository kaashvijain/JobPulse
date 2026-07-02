import os
import asyncio
import logging
import random
from typing import List
import httpx

logger = logging.getLogger(__name__)

class USAJobsClient:
    def __init__(self):
        self.email = os.getenv("USAJOBS_EMAIL", "").strip()
        self.api_key = os.getenv("USAJOBS_KEY", "").strip()
        self.base_url = "https://data.usajobs.gov/api/search"

    def is_mock(self) -> bool:
        return not self.email or not self.api_key or self.email.lower() == "mock" or self.api_key.lower() == "mock"

    async def get_weekly_posting_counts(self, role: str, city: str) -> List[int]:
        """
        Retrieves job posting counts for the last 5 weeks.
        Returns a list of 5 counts in chronological order (oldest week first, latest week last).
        """
        if self.is_mock():
            logger.info("Using mock job postings service (USAJOBS_EMAIL or USAJOBS_KEY is not set or mock)")
            # Generate deterministic mock counts based on role/city hash to look realistic
            seed_val = hash(f"{role.lower()}_{city.lower()}") % 1000
            random.seed(seed_val)
            
            # Decide on a trend: 0 = stable, 1 = heating up, 2 = cooling down
            trend_type = seed_val % 3
            base_count = 100 + (seed_val % 300)
            
            mock_counts = []
            current = base_count
            for i in range(5):
                if trend_type == 1:
                    # Heating up: oldest (first index) is smaller, newest (last index) is larger
                    change = random.randint(5, 25)
                elif trend_type == 2:
                    # Cooling down: oldest is larger, newest is smaller
                    change = random.randint(-25, -5)
                else:
                    # Stable: slight fluctuation
                    change = random.randint(-10, 10)
                current = max(10, current + change)
                mock_counts.append(current)
                
            # mock_counts is chronological: [W5, W4, W3, W2, W1]
            return mock_counts

        # Query the 5 periods concurrently: max_days_old = [7, 14, 21, 28, 35]
        days_limits = [7, 14, 21, 28, 35]
        tasks = [self._fetch_count_for_days(role, city, limit) for limit in days_limits]
        
        try:
            # Run all requests concurrently
            cumulative_counts = await asyncio.gather(*tasks)
            
            # cumulative_counts maps to [C_7, C_14, C_21, C_28, C_35]
            c_7, c_14, c_21, c_28, c_35 = cumulative_counts
            
            # Calculate incremental weekly counts
            w1 = c_7
            w2 = max(0, c_14 - c_7)
            w3 = max(0, c_21 - c_14)
            w4 = max(0, c_28 - c_21)
            w5 = max(0, c_35 - c_28)
            
            # Return in chronological order: [W5, W4, W3, W2, W1]
            # (oldest week to newest week)
            return [w5, w4, w3, w2, w1]
            
        except httpx.HTTPStatusError as e:
            logger.error(f"USAJobs API returned error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch job postings from USAJobs: {str(e)}")
            raise

    async def _fetch_count_for_days(self, role: str, city: str, max_days_old: int) -> int:
        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.email,
            "Authorization-Key": self.api_key
        }
        params = {
            "Keyword": role,
            "LocationName": city,
            "DatePosted": max_days_old,
            "ResultsPerPage": 1
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            search_result = data.get("SearchResult", {})
            return search_result.get("SearchResultCountAll", 0)
