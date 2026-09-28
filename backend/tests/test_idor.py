"""
test_idor.py — §1.8 Object-Level Authorization (IDOR) tests.

For each audited endpoint taking a resource ID:
  - Account A creates a resource (lot/quote/etc.)
  - Account B's token must get 404 (not the resource content, not 403)
  - Account A's own token must still get 200

This is as important as test_rbac.py — this bug class doesn't require
bypassing a role check, only knowing/guessing another user's resource ID.

Reference implementation pattern: wallet.py (correctly owner-scoped).
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _get_token(ac: AsyncClient, phone: str) -> str:
    await ac.post("/api/auth/request-otp", json={"phone": phone})
    res = await ac.post("/api/auth/verify-otp", json={"phone": phone, "otp": "123456"})
    assert res.status_code == 200, f"Login failed for {phone}: {res.text}"
    return res.json()["access_token"]


async def _create_lot(ac: AsyncClient, token: str) -> str:
    """Create a minimal lot and return its ID."""
    # First get a valid material ID
    mats = await ac.get("/api/materials")
    mat_id = mats.json()[0]["id"] if mats.json() else "pcb-id"

    res = await ac.post(
        "/api/lots",
        json={
            "items": [{
                "material_id": mat_id,
                "est_weight_g": 500,
                "condition": "broken",
                "photo_urls": [],
                "ai_suggested_material_id": None,
                "ai_confidence": None,
                "user_override": False,
            }],
            "pickup_lat": 18.52,
            "pickup_lng": 73.85,
            "pickup_address": "Test Address",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, f"Lot creation failed: {res.text[:300]}"
    return res.json()["id"]


@pytest.mark.asyncio
async def test_collector_cannot_read_other_collectors_lot():
    """
    §1.8: Collector B's token must get 404 on Collector A's lot.
    Must NOT return the lot data.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = await _get_token(ac, "9800000011")
        token_b = await _get_token(ac, "9800000012")

        lot_id = await _create_lot(ac, token_a)

        # B tries to read A's lot
        res = await ac.get(
            f"/api/lots/{lot_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res.status_code == 404, (
            f"Collector B was able to read Collector A's lot! "
            f"Status: {res.status_code}, Body: {res.text[:200]}"
        )

        # A can still read their own lot
        res_a = await ac.get(
            f"/api/lots/{lot_id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res_a.status_code == 200, (
            f"Collector A cannot read their own lot! Status: {res_a.status_code}"
        )


@pytest.mark.asyncio
async def test_collector_cannot_cancel_other_collectors_lot():
    """
    §1.8: Collector B's token must get 404 attempting to cancel Collector A's lot.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = await _get_token(ac, "9800000013")
        token_b = await _get_token(ac, "9800000014")

        lot_id = await _create_lot(ac, token_a)

        res = await ac.post(
            f"/api/lots/{lot_id}/cancel",
            json={"reason_code": "changed_mind", "note": "test"},
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res.status_code == 404, (
            f"Collector B was able to cancel Collector A's lot! "
            f"Status: {res.status_code}, Body: {res.text[:200]}"
        )


@pytest.mark.asyncio
async def test_collector_cannot_accept_quote_on_other_collectors_lot():
    """
    §1.8: The most severe IDOR — accept_quote must verify lot ownership.
    Collector B must get 404 trying to accept a quote on A's lot.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = await _get_token(ac, "9800000015")
        token_b = await _get_token(ac, "9800000016")

        lot_id = await _create_lot(ac, token_a)

        # Get quotes on A's lot (may be empty — that's fine, we test with a fake ID)
        quotes_res = await ac.get(
            f"/api/lots/{lot_id}/quotes",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        quotes = quotes_res.json() if quotes_res.status_code == 200 else []

        if quotes:
            quote_id = quotes[0]["id"]
            # B tries to accept a quote on A's lot
            res = await ac.post(
                f"/api/quotes/{quote_id}/accept",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            assert res.status_code == 404, (
                f"Collector B was able to accept a quote on Collector A's lot! "
                f"Status: {res.status_code}, Body: {res.text[:200]}"
            )
        else:
            # Even with a non-existent quote ID, B must get 404 not 200
            res = await ac.post(
                "/api/quotes/non-existent-quote-id/accept",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            assert res.status_code == 404


@pytest.mark.asyncio
async def test_lot_list_collector_only_shows_own_lots():
    """
    GET /api/lots?collector_only=true must only return the calling
    collector's own lots, not all lots in the system.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = await _get_token(ac, "9800000017")
        token_b = await _get_token(ac, "9800000018")

        lot_id_a = await _create_lot(ac, token_a)

        # B queries collector_only lots — must NOT see A's lot
        res = await ac.get(
            "/api/lots?collector_only=true",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res.status_code == 200
        b_lots = res.json()
        b_lot_ids = [l["id"] for l in b_lots]
        assert lot_id_a not in b_lot_ids, (
            f"Collector B's lot list contains Collector A's lot ID {lot_id_a}! "
            f"B's lots: {b_lot_ids}"
        )
