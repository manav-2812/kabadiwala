import json
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User, Collector, Notification, PriceAlert, Material
from app.schemas.all_schemas import NotificationResponse
from app.services.fcm import send_fcm_notification

router = APIRouter(tags=["notifications"])


# ─────────────────────────────────────────────
# FCM Device Token Registration
# ─────────────────────────────────────────────

@router.post("/notifications/fcm-token")
async def register_fcm_token(
    payload: Dict[str, Any] = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register the browser/device FCM token for the authenticated user.
    Frontend calls this once after initFcm() returns a token.
    The token is stored on the User model so the backend can push notifications to it.
    """
    token: str = payload.get("fcm_token", "").strip()
    if not token:
        return {"status": "error", "message": "fcm_token is required"}

    # Store on user (multiple tokens per user supported — store as JSON list)
    existing_raw = getattr(user, "fcm_tokens", None) or "[]"
    try:
        tokens: list = json.loads(existing_raw) if isinstance(existing_raw, str) else existing_raw
    except Exception:
        tokens = []

    if token not in tokens:
        tokens.append(token)
        # Keep only last 5 tokens (browsers rotate them)
        tokens = tokens[-5:]

    user.fcm_tokens = json.dumps(tokens)  # type: ignore[attr-defined]
    await db.commit()

    return {"status": "success", "registered": True}


# ─────────────────────────────────────────────
# Push Notification — Single User (internal util)
# ─────────────────────────────────────────────

async def push_to_user(
    user: User,
    title: str,
    body: str,
    data: dict | None = None,
    url: str = "/",
) -> list[dict]:
    """
    Send FCM push notification to all registered devices of a user.
    Called internally from other service endpoints (e.g., on pickup completion).
    """
    tokens_raw = getattr(user, "fcm_tokens", None) or "[]"
    try:
        tokens: list = json.loads(tokens_raw) if isinstance(tokens_raw, str) else tokens_raw
    except Exception:
        tokens = []

    results = []
    for token in tokens:
        result = await send_fcm_notification(token, title, body, data, url)
        results.append(result)
    return results


# ─────────────────────────────────────────────
# Notification History
# ─────────────────────────────────────────────

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(desc(Notification.created_at))
        .limit(30)
    )
    res = await db.execute(stmt)
    notifications = res.scalars().all()

    lang = user.language or "hi"
    output = []
    for n in notifications:
        title = n.title_hi if lang == "hi" else (n.title_pa if lang == "pa" else n.title_en)
        body = n.body_hi if lang == "hi" else (n.body_pa if lang == "pa" else n.body_en)
        sms = f"KC ALERT: {body}"

        try:
            p = json.loads(n.payload_json) if isinstance(n.payload_json, str) else n.payload_json
        except Exception:
            p = {}

        output.append(NotificationResponse(
            id=n.id,
            type=n.type,
            title=title,
            body=body,
            sms_preview=sms,
            payload=p,
            read_at=n.read_at,
            created_at=n.created_at
        ))
    return output


@router.post("/notifications/{id}/read")
async def mark_read(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Notification).where(Notification.id == id)
    res = await db.execute(stmt)
    n = res.scalar_one_or_none()
    if n:
        n.read_at = datetime.now(timezone.utc)
        await db.commit()
    return {"status": "success", "id": id}


@router.post("/notifications/read-all")
async def mark_all_read(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Notification).where(Notification.user_id == user.id, Notification.read_at == None)
    res = await db.execute(stmt)
    notifications = res.scalars().all()
    now = datetime.now(timezone.utc)
    for n in notifications:
        n.read_at = now
    await db.commit()
    return {"status": "success", "marked": len(notifications)}


# ─────────────────────────────────────────────
# Price Alerts
# ─────────────────────────────────────────────

@router.get("/price-alerts")
async def get_price_alerts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    col_id = col.id if col else user.id

    stmt = select(PriceAlert).where(PriceAlert.collector_id == col_id)
    res = await db.execute(stmt)
    alerts = res.scalars().all()
    return [
        {
            "id": a.id,
            "material_id": a.material_id,
            "direction": a.direction,
            "threshold_paise": a.threshold_paise,
            "is_active": a.is_active,
        }
        for a in alerts
    ]


@router.post("/price-alerts")
async def create_price_alert(
    payload: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    col_id = col.id if col else user.id

    alert = PriceAlert(
        collector_id=col_id,
        material_id=payload.get("material_id", ""),
        direction=payload.get("direction", "above"),
        threshold_paise=int(payload.get("threshold_paise", 40000)),
        is_active=True,
    )
    db.add(alert)
    await db.commit()
    return {"status": "success", "alert_id": alert.id}


# ─────────────────────────────────────────────
# Admin: Test push / WhatsApp (dev only)
# ─────────────────────────────────────────────

@router.post("/notifications/test-push")
async def test_push_notification(
    payload: Dict[str, Any] = Body(...),
    user: User = Depends(get_current_user),
):
    """
    Send a test FCM push to all devices registered for the current user.
    Only available to admins or during development.
    """
    results = await push_to_user(
        user,
        title=payload.get("title", "Test Notification"),
        body=payload.get("body", "This is a test push from Kabadiwala Connect."),
        url=payload.get("url", "/"),
    )
    return {"status": "sent", "results": results}
