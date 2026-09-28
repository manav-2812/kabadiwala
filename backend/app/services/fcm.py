"""
Firebase Cloud Messaging (FCM) — Web Push Service
Kabadiwala Connect

Free & unlimited for all notification types.

Handles:
  - Price board real-time alerts
  - Pickup reminders & status updates
  - Payout confirmations
  - Admin broadcasts

Setup:
  1. Go to Firebase Console → Project Settings → Service Accounts
  2. Click "Generate new private key" → download JSON file
  3. Add these to backend/.env:
       FIREBASE_SERVICE_ACCOUNT_JSON=/path/to/serviceAccountKey.json
     OR paste the JSON content inline:
       FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}

  4. Frontend: call initFcm() on login, then call registerFcmToken() from authStore
"""
import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache the access token to avoid fetching on every send
_cached_access_token: str | None = None


def _is_fcm_configured() -> bool:
    sa_json = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", None)
    return bool(sa_json)


def _load_service_account() -> dict | None:
    sa_json = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", None)
    if not sa_json:
        return None
    try:
        # Support both file path and inline JSON
        if sa_json.strip().startswith("{"):
            return json.loads(sa_json)
        else:
            with open(sa_json, "r") as f:
                return json.load(f)
    except Exception as exc:
        logger.error("[FCM] Failed to load service account: %s", exc)
        return None


async def _get_oauth_token() -> str | None:
    """Exchange service account credentials for a short-lived OAuth2 token."""
    global _cached_access_token
    if _cached_access_token:
        return _cached_access_token

    sa = _load_service_account()
    if not sa:
        return None

    try:
        import time

        import jwt as pyjwt

        now = int(time.time())
        claim = {
            "iss": sa["client_email"],
            "scope": "https://www.googleapis.com/auth/firebase.messaging",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }
        signed = pyjwt.encode(claim, sa["private_key"], algorithm="RS256")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed,
                },
            )
            data = resp.json()
            token = data.get("access_token")
            if token:
                _cached_access_token = token
                return token
            logger.warning("[FCM] OAuth token exchange failed: %s", data)
            return None
    except Exception as exc:
        logger.error("[FCM] OAuth error: %s", exc)
        return None


async def send_fcm_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: dict | None = None,
    url: str = "/",
) -> dict:
    """
    Send a single FCM push notification to a device token.
    """
    if not _is_fcm_configured():
        logger.info("[FCM] Not configured — skipping push notification.")
        return {"delivered": False, "provider": "FCM", "reason": "not_configured"}

    sa = _load_service_account()
    if not sa:
        return {"delivered": False, "provider": "FCM", "reason": "service_account_error"}

    project_id = sa.get("project_id")
    access_token = await _get_oauth_token()
    if not access_token:
        return {"delivered": False, "provider": "FCM", "reason": "auth_error"}

    message: dict = {
        "message": {
            "token": fcm_token,
            "notification": {"title": title, "body": body},
            "webpush": {
                "notification": {
                    "title": title,
                    "body": body,
                    "icon": "/favicon.svg",
                    "badge": "/favicon.svg",
                },
                "fcm_options": {"link": url},
            },
        }
    }
    if data:
        message["message"]["data"] = {k: str(v) for k, v in data.items()}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=message,
            )
            if resp.status_code == 200:
                logger.info("[FCM] Push sent to token ...%s", fcm_token[-8:])
                return {"delivered": True, "provider": "FCM", "name": resp.json().get("name")}
            elif resp.status_code == 401:
                # Token expired — clear cache and retry once
                global _cached_access_token
                _cached_access_token = None
                return {"delivered": False, "provider": "FCM", "reason": "token_expired"}
            else:
                logger.warning("[FCM] Send failed %d: %s", resp.status_code, resp.text[:200])
                return {"delivered": False, "provider": "FCM", "error": resp.text[:200]}
    except Exception as exc:
        logger.error("[FCM] Exception: %s", exc)
        return {"delivered": False, "provider": "FCM", "error": str(exc)}


async def send_fcm_to_user_tokens(
    fcm_tokens: list[str],
    title: str,
    body: str,
    data: dict | None = None,
    url: str = "/",
) -> list[dict]:
    """Send FCM to multiple device tokens belonging to one user."""
    results = []
    for token in fcm_tokens:
        result = await send_fcm_notification(token, title, body, data, url)
        results.append(result)
    return results
