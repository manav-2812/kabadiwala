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
    factor = CONDITION_FACTORS.get(cond, 1.00)
    
    # min = base * 0.90 * weight * condition_factor
    # max = base * 1.10 * weight * condition_factor
    min_paise = int(round(base_price_paise_per_kg * 0.90 * weight_kg * factor))
    max_paise = int(round(base_price_paise_per_kg * 1.10 * weight_kg * factor))
    
    return {
        "condition_factor": factor,
        "base_price_paise_per_kg": base_price_paise_per_kg,
        "weight_kg": weight_kg,
        "min_paise": min_paise,
        "max_paise": max_paise,
