# [SIH-2026-PS-SIH26229] Iteration 50 polish
import pytest
from app.services.price_engine import calculate_item_estimate, get_formal_premium_paise, CONDITION_FACTORS

def test_price_engine_working_condition():
    # Base price: 40000 paise (₹400), 2 kg, working condition (1.10x)
    # min = 40000 * 0.90 * 2 * 1.10 = 79200
    # max = 40000 * 1.10 * 2 * 1.10 = 96800
    res = calculate_item_estimate(base_price_paise_per_kg=40000, weight_kg=2.0, condition="working")
    assert res["min_paise"] == 79200
    assert res["max_paise"] == 96800
    assert res["min_inr"] == 792.00
    assert res["max_inr"] == 968.00
    assert res["condition_factor"] == 1.10

def test_price_engine_burnt_condition():
    # Burnt factor is 0.70
    res = calculate_item_estimate(base_price_paise_per_kg=50000, weight_kg=1.0, condition="burnt")
    assert res["condition_factor"] == 0.70
    assert res["min_paise"] == round(50000 * 0.90 * 1.0 * 0.70)
    assert res["max_paise"] == round(50000 * 1.10 * 1.0 * 0.70)

def test_price_engine_broken_default():
    # Broken factor is 1.00
    res = calculate_item_estimate(base_price_paise_per_kg=20000, weight_kg=5.0, condition="broken")
    assert res["condition_factor"] == 1.00
    assert res["min_paise"] == 90000
    assert res["max_paise"] == 110000

def test_formal_premium_calculation():
    # Informal is 80% of formal base. Premium = 20%
    base = 100000 # ₹1,000
    premium = get_formal_premium_paise(base)
    assert premium == 20000 # ₹200 extra formal benefit
