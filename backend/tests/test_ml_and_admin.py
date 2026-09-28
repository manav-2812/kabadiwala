"""
test_ml_and_admin.py — ML and admin endpoint tests.

Updated to use admin auth tokens, since all /admin/* routes now require
Depends(require_role("admin")) per §1.1 fix.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ml_classify_confident(async_client: AsyncClient):
    res = await async_client.post("/api/ml/classify", json={"hint_material": "PCB"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # In demo_only mode, top1 confidence is below threshold (not_sure=True)
    # The key fields that must always be present:
    assert "not_sure" in data
    assert "top3" in data
    assert isinstance(data["top3"], list)
    assert len(data["top3"]) == 3
    assert "model" in data
    assert data["model"]["demo_only"] is True  # no real model trained yet
    assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_ml_valuate(async_client: AsyncClient):
    payload = {
        "items": [
            {
                "material_code": "PCB",
                "sub_category": None,
                "weight_g": 5000,
                "condition": "working"
            }
        ],
        "lat": 28.6139,
        "lng": 77.2090
    }
    res = await async_client.post("/api/ml/valuate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["material_code"] == "PCB"
    assert item["min_paise"] <= item["p50_paise"] <= item["max_paise"]
    assert "basis" in item
    assert item["basis"]["layer"] == "rules"  # no ML layer active yet
    assert "total" in data
    assert data["total"]["min_paise"] <= data["total"]["p50_paise"] <= data["total"]["max_paise"]


@pytest.mark.asyncio
async def test_admin_anomalies_requires_auth(async_client: AsyncClient):
    """§1.1: Admin anomalies must require authentication."""
    res = await async_client.get("/api/admin/anomalies")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"


@pytest.mark.asyncio
async def test_admin_anomalies_and_review(async_client: AsyncClient, admin_token: str):
    """Admin can list anomalies and review them."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Get list of anomalies
    res = await async_client.get("/api/admin/anomalies", headers=headers)
    assert res.status_code == 200
    anomalies = res.json()

    if anomalies:
        target = anomalies[0]
        assert "type" in target
        assert "severity" in target
        assert "score" in target

        # Review anomaly
        rev_res = await async_client.post(
            f"/api/admin/anomalies/{target['id']}/review",
            json={"action": "cleared", "notes": "Audited scale calibration records"},
            headers=headers
        )
        assert rev_res.status_code == 200
        assert rev_res.json()["new_status"] == "cleared"


@pytest.mark.asyncio
async def test_admin_matching_weights_requires_auth(async_client: AsyncClient):
    """§1.1: Matching weights must require admin auth."""
    res = await async_client.get("/api/admin/matching-weights")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_matching_weights(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = await async_client.get("/api/admin/matching-weights", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "active_weights" in data or "weights" in data  # either schema variant

    # Update matching weights
    new_weights = {
        "w_distance": 0.20,
        "w_price": 0.50,
        "w_reputation": 0.15,
        "w_hazardous_capability": 0.15,
        "version": "v2.0-test"
    }
    put_res = await async_client.put(
        "/api/admin/matching-weights", json=new_weights, headers=headers
    )
    assert put_res.status_code == 200
    assert put_res.json()["version"] == "v2.0-test"


@pytest.mark.asyncio
async def test_admin_data_health(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = await async_client.get("/api/admin/data-health", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "dataset_summary" in data
    assert "models" in data
    assert "anomalies" in data


@pytest.mark.asyncio
async def test_admin_export_anonymized_csv(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = await async_client.get("/api/admin/export-anonymized-csv", headers=headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    assert "lot_code" in content
    assert "coarse_lat" in content
    assert "collector_phone_hash" in content
