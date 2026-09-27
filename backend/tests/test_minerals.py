# [SIH-2026-PS-SIH26229] Iteration 115 polish
import pytest
from app.services.minerals import calculate_recoverable_minerals, EFFICIENCIES

def test_critical_minerals_recovery_efficiencies():
    # Base metal efficiency is 0.85
    assert EFFICIENCIES["cu"] == 0.85
    assert EFFICIENCIES["sn"] == 0.85
    # Precious / critical efficiency is 0.70
    assert EFFICIENCIES["au"] == 0.70
    assert EFFICIENCIES["li"] == 0.70
    assert EFFICIENCIES["co"] == 0.70
    assert EFFICIENCIES["nd"] == 0.70

def test_critical_minerals_calculation():
    # 10 kg of PCB: copper 180 g/kg, gold 0.35 g/kg
    items = [
        {"element": "cu", "weight_kg": 10.0, "grams_per_kg": 180.0},
        {"element": "au", "weight_kg": 10.0, "grams_per_kg": 0.35}
    ]
    res = calculate_recoverable_minerals(items)
    
    cu_item = next(x for x in res if x["element"] == "cu")
    au_item = next(x for x in res if x["element"] == "au")
    
    # cu: 10 * 180 * 0.85 = 1530.0 grams
    assert cu_item["grams"] == 1530.0
    assert cu_item["is_strategic"] is True
    
    # au: 10 * 0.35 * 0.70 = 2.45 grams
    assert au_item["grams"] == 2.45
    assert au_item["is_strategic"] is True
