from typing import Dict, Any, Optional

CONDITION_FACTORS = {
    "working": 1.10,
    "broken": 1.00,
    "burnt": 0.70,
    "unknown": 0.95
}

def calculate_item_estimate(
    base_price_paise_per_kg: int,
    weight_kg: float,
    condition: str = "broken"
) -> Dict[str, Any]:
    cond = condition.lower()
