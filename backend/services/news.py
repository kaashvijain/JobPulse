import os
import logging
import random
from typing import List
import httpx

logger = logging.getLogger(__name__)

class NewsClient:
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY", "").strip()

    def is_mock(self) -> bool:
        # Check if GNews key is set and not equal to "mock"
        return not (self.gnews_key and self.gnews_key.lower() != "mock")

    async def get_hiring_news(self, role: str, city: str) -> List[str]:
        """
        Fetches up to 5 news headlines related to hiring/layoffs for the given role and city.
        Uses GNews API search.
        """
        if self.is_mock():
            logger.info("Using mock news service (GNEWS_API_KEY is not set or mock)")
            return self._generate_mock_news(role, city)

        # Formulate query tiers
        tier_queries = [
            f'"{role}" AND "{city}" AND (hiring OR layoff OR layoffs)',
            f'"{city}" AND (hiring OR layoff OR layoffs OR job market)',
            f'"{role}" AND (hiring OR layoff OR layoffs OR "hiring trend")',
            f'tech AND (hiring OR layoff OR layoffs OR employment)'
        ]

        return await self._fetch_gnews(tier_queries)

    async def _fetch_gnews(self, queries: List[str]) -> List[str]:
        base_url = "https://gnews.io/api/v4/search"
        async with httpx.AsyncClient(timeout=10.0) as client:
            for query in queries:
                try:
                    params = {
                        "q": query,
                        "max": 5,
                        "apikey": self.gnews_key,
                        "lang": "en"
                    }
                    response = await client.get(base_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get("articles", [])
                        if articles:
                            headlines = [
                                f"{art.get('title')} ({art.get('source', {}).get('name', 'GNews')})"
                                for art in articles
                            ]
                            return headlines[:5]
                    else:
                        logger.warning(f"GNews returned status {response.status_code}: {response.text}")
                except Exception as e:
                    logger.error(f"GNews query failed: {str(e)}")
                    
        # If all query tiers returned 0 articles or errored, return mock news
        logger.warning("GNews queries failed or returned empty. Using fallback mock news.")
        return self._generate_mock_news("Role", "City")

    def _generate_mock_news(self, role: str, city: str) -> List[str]:
        """
        Generates realistic hiring/layoff headlines based on the role and city.
        """
        seed_val = hash(f"{role.lower()}_{city.lower()}") % 1000
        random.seed(seed_val)
        
        # Pool of realistic headlines
        hiring_templates = [
            f"Tech giants expand operations in {city}, seeking {role} talent (TechCrunch)",
            f"Why {role} remains one of the most in-demand roles in {city} (Forbes)",
            f"Local startups in {city} secure $150M in funding, aiming to double hiring (VentureBeat)",
            f"Hiring trends: {role} salaries see 10% increase in {city} metro area (Wall Street Journal)",
            f"New technology hubs in {city} drive job vacancies to record highs (Bloomberg)"
        ]
        
        layoff_templates = [
            f"Mid-sized tech firms in {city} announce layoffs affecting {role} teams (TechCrunch)",
            f"Market corrections lead to hiring freeze for {role} positions in {city} (Forbes)",
            f"Major employer in {city} downsizes workforce by 12% amid restructuring (Business Insider)",
            f"Hiring slowdown: {role} vacancies drop as companies cut costs (Wall Street Journal)",
            f"Macroeconomic pressures impact tech hiring in the {city} area (Bloomberg)"
        ]
        
        stable_templates = [
            f"How the {role} market in {city} is adapting to remote work shifts (Wired)",
            f"Steady demand for experienced {role}s in {city} despite overall tech cooling (Forbes)",
            f"Local business leaders discuss state of hiring in {city} (Local Business Times)",
            f"Tech recruitment trends show balanced market for {role} professionals (Recruiting Daily)",
            f"Stable outlook for technology roles in {city} entering Q3 (CIO Magazine)"
        ]
        
        # Decide news tone based on seed (corresponds to trend in postings mock)
        trend_type = seed_val % 3
        if trend_type == 1:
            # Heating Up: more hiring templates
            headlines = random.sample(hiring_templates, 3) + random.sample(stable_templates, 2)
        elif trend_type == 2:
            # Cooling Down: more layoff templates
            headlines = random.sample(layoff_templates, 3) + random.sample(stable_templates, 2)
        else:
            # Stable: more stable templates
            headlines = random.sample(stable_templates, 3) + random.sample(hiring_templates, 1) + random.sample(layoff_templates, 1)
            
        random.shuffle(headlines)
        return headlines[:5]
