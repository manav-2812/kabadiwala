"""
test_rbac.py — §1.1 RBAC enforcement tests.

Every admin endpoint must:
  - Return 401 for unauthenticated requests (no token)
  - Return 403 for requests with a collector-role token
  - Return 200/2xx for requests with a valid admin-role token

This is the single most important test file: it directly tests the worst
security bug found in the audit.
"""

import pytest
from httpx import AsyncClient

# Admin endpoints to check — (method, path, optional_body)
ADMIN_ENDPOINTS = [
    ("GET",  "/api/admin/anomalies", None),
    ("GET",  "/api/admin/matching-weights", None),
    ("GET",  "/api/admin/data-health", None),
    ("GET",  "/api/admin/export-anonymized-csv", None),
    ("GET",  "/api/admin/ml/overview", None),
    ("GET",  "/api/admin/ml/predictions", None),
    ("GET",  "/api/admin/ml/drift", None),
    ("GET",  "/api/admin/labels", None),
    ("GET",  "/api/admin/collectors", None),
    ("POST", "/api/admin/ml/retrain", {"task": "classify"}),
    ("POST", "/api/admin/matching-weights", {
        "payout": 0.30, "proximity": 0.20, "rate": 0.20,
        "pickup": 0.10, "reliability": 0.10, "response": 0.10
    }),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", ADMIN_ENDPOINTS)
async def test_admin_endpoint_requires_auth(
    async_client: AsyncClient,
    method: str,
    path: str,
    body,
):
    """Unauthenticated request (no token) → 401."""
    if method == "GET":
        res = await async_client.get(path)
    else:
        res = await async_client.post(path, json=body or {})
    assert res.status_code == 401, (
        f"{method} {path} returned {res.status_code} without auth token — "
        f"expected 401. Response: {res.text[:200]}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", ADMIN_ENDPOINTS)
async def test_admin_endpoint_rejects_collector(
    async_client: AsyncClient,
    collector_token: str,
    method: str,
    path: str,
    body,
):
    """Collector-role token → 403 on all admin endpoints."""
    headers = {"Authorization": f"Bearer {collector_token}"}
    if method == "GET":
        res = await async_client.get(path, headers=headers)
    else:
        res = await async_client.post(path, json=body or {}, headers=headers)
    assert res.status_code == 403, (
        f"{method} {path} returned {res.status_code} with collector token — "
        f"expected 403. Response: {res.text[:200]}"
    )


@pytest.mark.asyncio
async def test_admin_anomalies_accessible_to_admin(
    async_client: AsyncClient,
    admin_token: str,
):
    """Admin token → GET /api/admin/anomalies returns 200."""
    res = await async_client.get(
        "/api/admin/anomalies",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, f"Admin anomalies failed: {res.text[:200]}"


@pytest.mark.asyncio
async def test_admin_data_health_accessible_to_admin(
    async_client: AsyncClient,
    admin_token: str,
):
    """Admin token → GET /api/admin/data-health returns 200."""
    res = await async_client.get(
        "/api/admin/data-health",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, f"Data health failed: {res.text[:200]}"


@pytest.mark.asyncio
async def test_signup_with_admin_role_rejected():
    """POST /auth/signup with role=admin → 422 (not allowed for self-signup)."""
    from httpx import ASGITransport, AsyncClient

    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/auth/signup", json={
            "phone": "9999000001",
            "name": "Hacker",
            "role": "admin",
            "language": "en"
        })
    assert res.status_code in (422, 403), (
        f"Signup with role=admin returned {res.status_code} — expected 422/403. "
        f"Response: {res.text[:200]}"
    )


@pytest.mark.asyncio
async def test_signup_existing_user_does_not_change_role(async_client: AsyncClient):
    """
    §1.0: Signing up with an existing phone and a different role
    must NOT change the existing user's role.
    """
    phone = "9876500099"
    # Initial signup as collector
    await async_client.post("/api/auth/request-otp", json={"phone": phone})
    # Second signup attempt as recycler — must not change role
    res = await async_client.post("/api/auth/signup", json={
        "phone": phone,
        "name": "Attacker",
        "role": "recycler",
        "language": "en",
        "cpcb_license_no": "FAKE-LICENSE-001"
    })
    # Should succeed (sends OTP) but must not modify the existing account's role
    assert res.status_code == 200

    # Login and check the role is still collector
    await async_client.post("/api/auth/request-otp", json={"phone": phone})
    login = await async_client.post("/api/auth/verify-otp", json={"phone": phone, "otp": "123456"})
    if login.status_code == 200:
        role = login.json().get("user", {}).get("role")
        # The role must be the original one (collector), not what the attacker tried to set
        assert role != "recycler", (
            "Signup was able to change existing user's role to 'recycler'! "
            "This is a critical §1.0 vulnerability."
        )
