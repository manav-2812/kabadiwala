import warnings

warnings.filterwarnings("ignore", message=r".*starlette\.testclient.*")
warnings.filterwarnings("ignore", message=r".*httpx2.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r".*starlette.*")

from starlette.testclient import TestClient

from app.main import app


def test_get_materials(client: TestClient):
    response = client.get("/api/materials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    assert any(m["code"] == "PCB" for m in data)
    assert any(m["code"] == "BATTERY_LI" for m in data)

def test_get_price_summary(client: TestClient):
    response = client.get("/api/prices/summary")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    pcb = next(m for m in data if m["material_code"] == "PCB")
    assert len(pcb["sparkline"]) > 0
    assert "trend_reason_en" in pcb

def test_instant_estimate_endpoint(client: TestClient):
    payload = [
        {"material_code": "PCB", "weight_kg": 5.0, "condition": "broken"},
        {"material_code": "BATTERY_LI", "weight_kg": 2.0, "condition": "working"}
    ]
    response = client.post("/api/lots/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_weight_kg"] == 7.0
    assert data["total_min_inr"] > 0
    assert data["total_max_inr"] >= data["total_min_inr"]
    assert len(data["recoverable_minerals"]) > 0
    assert data["is_hazardous"] is True

def test_auth_request_and_verify_otp(client: TestClient):
    req_res = client.post("/api/auth/request-otp", json={"phone": "9876543201"})
    assert req_res.status_code == 200

    verify_res = client.post("/api/auth/verify-otp", json={"phone": "9876543201", "otp": "123456"})
    assert verify_res.status_code == 200
    token_data = verify_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["role"] == "collector"

def test_request_otp_rate_limiting(client: TestClient):
    app.state.limiter.enabled = True
    try:
        # Rapid requests from the same client trigger rate limiting
        responses = [client.post("/api/auth/request-otp", json={"phone": "9876543299"}) for _ in range(8)]
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, f"Expected 429 in rate limit responses, got: {status_codes}"
    finally:
        app.state.limiter.enabled = False

def test_admin_kpis_endpoint(client: TestClient):
    response = client.get("/api/dashboard/admin/kpis")
    assert response.status_code == 200
    kpis = response.json()
    assert kpis["formalised_tonnes"] >= 0
    assert kpis["active_collectors"] > 0
    assert kpis["critical_minerals_recovered_kg"] >= 0

def test_public_verify_endpoint(client: TestClient):
    # Test valid receipt
    response = client.get("/verify/KC-RCT-2026-00001")
    assert response.status_code == 200
    data = response.json()
    assert "verified" in data
    assert "compliance" in data
