import os
import json
import pytest
from app.services.matching import rank_recyclers_for_lot

GOLDEN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "golden", "matching_golden.json"
)


def load_golden():
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_matching_hard_filter_unverified():
    """Validates that unverified recyclers are filtered out."""
    data = load_golden()
    v1 = next(v for v in data["vectors"] if v["id"] == "M1_HARD_FILTER_UNVERIFIED")
    
    inp = v1["input"]
    results = rank_recyclers_for_lot(
        collector_lat=inp["collector_lat"],
        collector_lng=inp["collector_lng"],
        lot_est_paise=inp["lot_est_paise"],
        lot_materials=["PCB"],
        recyclers=inp["recyclers"],
        weights=inp["weights"]
    )
    assert len(results) == v1["expected"]["count"]


def test_matching_expired_license():
    """Validates that verified recyclers with expired licenses are excluded."""
    data = load_golden()
    v2 = next(v for v in data["vectors"] if v["id"] == "M2_EXPIRED_LICENSE_EXCLUDED")
    
    inp = v2["input"]
    results = rank_recyclers_for_lot(
        collector_lat=inp["collector_lat"],
        collector_lng=inp["collector_lng"],
        lot_est_paise=inp["lot_est_paise"],
        lot_materials=["PCB"],
        recyclers=inp["recyclers"],
        weights=inp["weights"]
    )
    assert len(results) == v2["expected"]["count"]
