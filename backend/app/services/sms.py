"""
Real SMS Gateway Integration Service
Kabadiwala Connect -- SIH 2026 (PS SIH26229)
Supports Fast2SMS (India), 2Factor.in (India), Twilio (Global/India), and MSG91
"""

import re
import secrets
import sys
from typing import Any

import httpx

from app.core.config import settings


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit random OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def clean_phone_number(phone: str) -> str:
    """Sanitize phone number to standard 10-digit Indian format."""
    digits = re.sub(r"\D", "", phone)
    return digits[-10:] if len(digits) >= 10 else digits


def _safe_print(msg: str) -> None:
    """Print to stdout using UTF-8 encoding to avoid Windows CP1252 emoji crashes."""
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except Exception:
        # Ultimate fallback: strip non-ASCII and use regular print
        print(msg.encode("ascii", errors="replace").decode("ascii"))


async def send_sms_otp(phone: str, otp: str) -> dict[str, Any]:
    """
    Send real SMS OTP using configured carrier gateways.
    Fallback to formatted console logging if credentials are unset.
    """
    clean_phone = clean_phone_number(phone)
    formatted_e164 = f"+91{clean_phone}"
    sms_text = (
        f"Your Kabadiwala Connect verification OTP is {otp}. "
        f"Valid for 10 minutes. Do not share with anyone."
    )

    SYNTHETIC_DEMO_NUMBERS = {
        "9876543201", "9876543210", "9876543213",
        "9876543301", "9876543401", "9819810001",
        "9999999999"
    }

    # If it is a synthetic seeded demo test number, keep in Simulator mode to prevent spamming
    if clean_phone in SYNTHETIC_DEMO_NUMBERS:
        border = "=" * 72
        _safe_print(f"\n{border}")
        _safe_print(f"[DEMO TEST ACCOUNT] OTP GENERATED FOR: {formatted_e164}")
        _safe_print(f"   >>> VERIFICATION CODE: {otp} <<<")
        _safe_print("   Note: Seeded demo account uses simulated code for safe testing.")
        _safe_print(f"{border}\n")
        return {
            "delivered": False,
            "provider": "Demo Simulator",
            "status": "logged",
            "phone": formatted_e164,
            "otp": otp,
            "hint": "Synthetic demo number: using simulated code"
        }

    # 1. Fast2SMS (Dedicated Indian Carrier Gateway with instant DLT OTP routing)
    if settings.FAST2SMS_API_KEY:
        try:
            api_key = settings.FAST2SMS_API_KEY.strip()
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {"authorization": api_key}
            payload = {
                "variables_values": otp,
                "route": "otp",
                "numbers": clean_phone
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                data = resp.json()
                if data.get("return") is True:
                    _safe_print(
                        f"\n[SMS GATEWAY] [OK] Real carrier SMS delivered to "
                        f"{formatted_e164} via Fast2SMS (Req ID: {data.get('request_id', 'N/A')})"
                    )
                    return {
                        "delivered": True,
                        "provider": "Fast2SMS",
                        "status": "sent",
                        "phone": formatted_e164
                    }
                else:
                    _safe_print(f"[SMS GATEWAY] [WARN] Fast2SMS response: {data}")
        except Exception as e:
            _safe_print(f"[SMS GATEWAY] [WARN] Fast2SMS dispatch error: {e}")

    # 2. 2Factor.in (Indian OTP gateway with instant free trial)
    if settings.TWOFACTOR_API_KEY:
        try:
            api_key = settings.TWOFACTOR_API_KEY.strip()
            url = f"https://2factor.in/API/V1/{api_key}/SMS/{clean_phone}/{otp}/OTP1"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                data = resp.json()
                if data.get("Status") == "Success":
                    _safe_print(
                        f"\n[SMS GATEWAY] [OK] Real carrier SMS delivered to "
                        f"{formatted_e164} via 2Factor.in "
                        f"(Session ID: {data.get('Details', 'N/A')})"
                    )
                    return {
                        "delivered": True,
                        "provider": "2Factor.in",
                        "status": "sent",
                        "phone": formatted_e164
                    }
                else:
                    _safe_print(f"[SMS GATEWAY] [WARN] 2Factor response: {data}")
        except Exception as e:
            _safe_print(f"[SMS GATEWAY] [WARN] 2Factor dispatch error: {e}")

    # 3. Twilio (International & India)
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
        try:
            sid = settings.TWILIO_ACCOUNT_SID.strip()
            token = settings.TWILIO_AUTH_TOKEN.strip()
            from_num = settings.TWILIO_PHONE_NUMBER.strip()
            url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
            payload = {
                "From": from_num,
                "To": formatted_e164,
                "Body": sms_text
            }
            auth = (sid, token)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, data=payload, auth=auth)
                if resp.status_code in (200, 201):
                    _safe_print(
                        f"\n[SMS GATEWAY] [OK] Real carrier SMS delivered to "
                        f"{formatted_e164} via Twilio"
                    )
                    return {
                        "delivered": True,
                        "provider": "Twilio",
                        "status": "sent",
                        "phone": formatted_e164
                    }
                else:
                    _safe_print(f"[SMS GATEWAY] [WARN] Twilio response ({resp.status_code}): {resp.text}")
        except Exception as e:
            _safe_print(f"[SMS GATEWAY] [WARN] Twilio dispatch error: {e}")

    # 4. MSG91
    if settings.MSG91_AUTH_KEY:
        try:
            url = "https://control.msg91.com/api/v5/otp"
            headers = {
                "authkey": settings.MSG91_AUTH_KEY.strip(),
                "Content-Type": "application/json"
            }
            payload = {
                "template_id": settings.MSG91_TEMPLATE_ID or "",
                "mobile": f"91{clean_phone}",
                "otp": otp
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    _safe_print(
                        f"\n[SMS GATEWAY] [OK] Real carrier SMS delivered to "
                        f"{formatted_e164} via MSG91"
                    )
                    return {
                        "delivered": True,
                        "provider": "MSG91",
                        "status": "sent",
                        "phone": formatted_e164
                    }
        except Exception as e:
            _safe_print(f"[SMS GATEWAY] [WARN] MSG91 dispatch error: {e}")

    # 5. Fallback: Console Logging -- no emoji, pure ASCII-safe
    border = "=" * 72
    _safe_print(f"\n{border}")
    _safe_print(f"[SMS SIMULATOR] OTP GENERATED FOR: {formatted_e164}")
    _safe_print(f"   >>> VERIFICATION CODE: {otp} <<<")
    _safe_print("   Expires in: 10 minutes")
    _safe_print("")
    _safe_print("[TIP] Live SMS OTP is handled by Firebase Phone Auth (10,000 free SMS/mo).")
    _safe_print(f"{border}\n")

    return {
        "delivered": False,
        "provider": "Simulator",
        "status": "logged",
        "phone": formatted_e164,
        "otp": otp,
        "hint": "Carrier SMS is managed via Firebase Phone Auth"
    }
