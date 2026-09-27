# [SIH-2026-PS-SIH26229] Iteration 118 polish
import os
import json
import pytest
from app.services.valuation import compute_rules_valuation

GOLDEN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "golden", "valuation_golden.json"
)


def load_golden():
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_golden_vectors_parity():
    """Validates that Layer 1 Python valuation rules match all golden test vectors."""
    data = load_golden()
    tol = data.get("tolerance_paise", 1)

    for vec in data["vectors"]:
        v_id = vec["id"]
        inp = vec["input"]
        exp = vec["expected"]

        res = compute_rules_valuation(
            base_paise_per_kg=inp["base_price_paise_per_kg"],
            weight_g=inp["weight_g"],
            condition=inp["condition"]
        )

        assert abs(res["min_paise"] - exp["min_paise"]) <= tol, (
            f"[{v_id}] min_paise mismatch: got {res['min_paise']}, expected {exp['min_paise']}"
        )
        assert abs(res["p50_paise"] - exp["p50_paise"]) <= tol, (
            f"[{v_id}] p50_paise mismatch: got {res['p50_paise']}, expected {exp['p50_paise']}"
        )
        assert abs(res["max_paise"] - exp["max_paise"]) <= tol, (
            f"[{v_id}] max_paise mismatch: got {res['max_paise']}, expected {exp['max_paise']}"
        )
        assert res["condition_factor"] == pytest.approx(exp["condition_factor"], abs=0.01)
        assert res["layer"] == "rules"
