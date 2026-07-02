from typing import List

def calculate_momentum_score(weekly_counts: List[int]) -> float:
    """
    Calculate momentum score based on weekly job posting counts.
    Formula: score = (latest_week - first_week) / first_week
    
    weekly_counts is in chronological order (oldest first, newest last):
      weekly_counts = [C_oldest, C_4, C_3, C_2, C_latest]
    """
    if not weekly_counts or len(weekly_counts) < 2:
        return 0.0
    
    first_week = weekly_counts[0]
    latest_week = weekly_counts[-1]
    
    if first_week == 0:
        if latest_week > 0:
            return 1.0  # Infinite relative increase, return 100% growth indicator
        return 0.0
        
    return (latest_week - first_week) / first_week

def interpret_market_trend(score: float) -> str:
    """
    Map momentum score to initial trend categorizations.
      - score > 0.15: heating up
      - score between -0.15 and 0.15: stable
      - score < -0.15: cooling down
    """
    if score > 0.15:
        return "heating up"
    elif score < -0.15:
        return "cooling down"
    else:
        return "stable"
