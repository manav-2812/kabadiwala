"""
test_matching_golden.py — Matching service tests.

§2.4: Confirms that the matching engine excludes recyclers with:
  - authorization_status != "verified"
  - expired license (license_valid_to < now)

Uses the Malwa Materials Recovery persona as the expired-license test fixture,
and the existing ml/golden/matching_golden.json as a regression golden file.
"""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from app.services.matching import rank_recyclers_for_lot


def _make_recycler(**overrides):
    """Minimal recycler dict for matching tests."""
    base = {
        "id": "rec-test-1",
        "company_name": "Test Recycler",
        "authorization_status": "verified",
        "license_valid_to": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        "lat": 18.52,
        "lng": 73.85,
        "accepted_material_codes": ["PCB", "BATTERY_LI"],
        "pickup_available": True,
        "rating_avg": 4.5,
        "reliability_score": 80,
        "rates": {"PCB": 45000},
        "response_rate": 0.9,
    }
    base.update(overrides)
    return base


LOT_LAT = 18.52
LOT_LNG = 73.85
LOT_EST_PAISE = 500_000  # ₹5,000
LOT_MATERIALS = ["PCB"]


def test_matching_excludes_pending_recycler():
    """§2.4: A recycler with authorization_status='pending' must never be returned."""
    pending = _make_recycler(id="rec-pending", authorization_status="pending")
    verified = _make_recycler(id="rec-verified")

    results = rank_recyclers_for_lot(
        LOT_LAT, LOT_LNG, LOT_EST_PAISE, LOT_MATERIALS, [pending, verified]
    )
    result_ids = [r["id"] for r in results]

    assert "rec-pending" not in result_ids, (
        "Pending recycler appeared in matching results — §2.4 fix not applied!"
    )
    assert "rec-verified" in result_ids


def test_matching_excludes_expired_license():
    """
    §2.4: A verified recycler with license_valid_to in the past (expired)
    must be excluded from matching results.

    This test uses the Malwa Materials Recovery persona pattern.
    """
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    expired = _make_recycler(
        id="malwa-materials-recovery",
        company_name="Malwa Materials Recovery",
        authorization_status="verified",
        license_valid_to=yesterday,  # ← expired yesterday
    )
    valid = _make_recycler(id="rec-valid-license")

    results = rank_recyclers_for_lot(
        LOT_LAT, LOT_LNG, LOT_EST_PAISE, LOT_MATERIALS, [expired, valid]
    )
    result_ids = [r["id"] for r in results]

    assert "malwa-materials-recovery" not in result_ids, (
        "Malwa Materials Recovery (expired license) appeared in matching results! "
        "The §2.4 license expiry filter is not working."
    )
    assert "rec-valid-license" in result_ids


def test_matching_includes_valid_verified_recycler():
    """Sanity: a verified, non-expired recycler with matching materials is included."""
    recycler = _make_recycler()

    results = rank_recyclers_for_lot(
        LOT_LAT, LOT_LNG, LOT_EST_PAISE, LOT_MATERIALS, [recycler]
    )
    assert len(results) == 1
    assert results[0]["id"] == "rec-test-1"


def test_matching_golden_file():
    """
    Regression golden-file test — verifies that the matching algorithm output
    hasn't silently changed for the canonical lot+recycler fixture.

    Golden file format: {description, tolerance, vectors: [{id, input, expected}]}
    Input: {collector_lat, collector_lng, lot_est_paise, weights?, recyclers}
    Expected: {count, first_rank_id?}
    """
    golden_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "ml", "golden", "matching_golden.json"
    )
    golden_path = os.path.normpath(golden_path)

    if not os.path.exists(golden_path):
        pytest.skip(f"Golden file not found at {golden_path}")

    with open(golden_path, "r", encoding="utf-8") as f:
        golden = json.load(f)

    vectors = golden.get("vectors", [])
    if not vectors:
        pytest.skip("Golden file has no vectors")

    failures = []
    for vec in vectors:
        vec_id = vec.get("id", "unknown")
        inp = vec["input"]
        expected = vec["expected"]

        results = rank_recyclers_for_lot(
            collector_lat=float(inp.get("collector_lat", LOT_LAT)),
            collector_lng=float(inp.get("collector_lng", LOT_LNG)),
            lot_est_paise=int(inp.get("lot_est_paise", LOT_EST_PAISE)),
            lot_materials=inp.get("lot_materials", LOT_MATERIALS),
            recyclers=inp.get("recyclers", []),
            weights=inp.get("weights"),
        )

        exp_count = expected.get("count")
        if exp_count is not None and len(results) != exp_count:
            failures.append(
                f"Vector '{vec_id}': expected count={exp_count}, got {len(results)}"
            )

        exp_first = expected.get("first_rank_id")
        if exp_first and results and results[0].get("id") != exp_first:
            failures.append(
                f"Vector '{vec_id}': expected first_rank_id='{exp_first}', "
                f"got '{results[0].get('id')}'"
            )

    assert not failures, "Matching golden-file regressions:\n" + "\n".join(failures)

