"""
Real Email OTP Service
Kabadiwala Connect — SIH 2026 (PS SIH26229)
Ministry of Mines / JNARDDC — Clean & Green Technology

Dispatches real HTML email verification codes via SMTP (Gmail, Outlook, custom SMTP, Brevo, SendGrid).
Falls back to formatted console logging if credentials are unset.
"""

import asyncio
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.core.config import settings


def _safe_print(msg: str) -> None:
    """Print to stdout using UTF-8 encoding."""
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except Exception:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def _send_smtp_sync(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """Synchronous SMTP worker called in threadpool."""
    host = settings.SMTP_HOST or "smtp.gmail.com"
    port = settings.SMTP_PORT or 587
    user = settings.SMTP_USER
    password = settings.SMTP_PASSWORD
    from_addr = settings.SMTP_FROM or user or "noreply@kabadiwala-connect.gov.in"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Kabadiwala Connect <{from_addr}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if settings.SMTP_TLS:
        server = smtplib.SMTP(host, port, timeout=12)
        server.ehlo()
        server.starttls()
        server.ehlo()
    else:
        server = smtplib.SMTP_SSL(host, port, timeout=12)
        server.ehlo()

    if user and password:
        server.login(user, password)

    server.sendmail(from_addr, [to_email], msg.as_string())
    server.quit()
    return True


async def send_email_otp(to_email: str, otp: str) -> dict[str, Any]:
    """
    Send an OTP authentication code to user's email address.
    If SMTP credentials are configured, sends real email via SMTP.
    Otherwise logs in console for instant local development testing.
    """
    clean_email = to_email.strip().lower()

    subject = f"Your Kabadiwala Connect Verification Code: {otp}"

    text_body = (
        f"Namaste,\n\n"
        f"Your Kabadiwala Connect verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Ministry of Mines & JNARDDC — Clean & Green Technology (SIH 2026)"
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F8FAF9; margin: 0; padding: 30px;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #E3E0D5; padding: 32px; box-shadow: 0 4px 20px rgba(11, 61, 46, 0.05);">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
      <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #0B3D2E, #14634A); color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; line-height: 44px; text-align: center;">KC</div>
      <div>
        <h2 style="margin: 0; font-size: 18px; color: #0B3D2E; font-weight: 900;">Kabadiwala Connect</h2>
        <p style="margin: 0; font-size: 11px; color: #5B6B62; font-weight: 600;">Ministry of Mines &amp; JNARDDC • E-Waste Portal</p>
      </div>
    </div>

    <h3 style="color: #14201A; font-size: 20px; font-weight: 800; margin: 0 0 12px 0;">Sign In Verification Code</h3>
    <p style="color: #5B6B62; font-size: 13px; line-height: 1.6; margin: 0 0 24px 0;">
      Use the 6-digit verification code below to authenticate into the Kabadiwala Connect portal.
    </p>

    <div style="background: #E4F4EA; border: 1.5px solid #2E9E5B; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 24px;">
      <span style="font-size: 11px; font-weight: 800; color: #14634A; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 6px;">Your One-Time Password (OTP)</span>
      <div style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 900; letter-spacing: 8px; color: #0B3D2E;">{otp}</div>
    </div>

    <p style="color: #5B6B62; font-size: 12px; line-height: 1.5; margin: 0 0 20px 0;">
      ⏱️ This verification code is valid for <strong>10 minutes</strong>. Do not share this code with anyone.
    </p>

    <div style="border-top: 1px solid #E3E0D5; padding-top: 18px; color: #8F9E96; font-size: 11px; text-align: center;">
      Smart India Hackathon 2026 • Problem Statement SIH26229<br>
      Autonomous Circular Economy Marketplace
    </div>
  </div>
</body>
</html>"""

    # If SMTP is configured, attempt real email delivery
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            await asyncio.to_thread(_send_smtp_sync, clean_email, subject, html_body, text_body)
            _safe_print(f"\n[EMAIL SERVICE] [OK] Real OTP email delivered to {clean_email} via SMTP ({settings.SMTP_HOST})")
            return {
                "delivered": True,
                "provider": "SMTP Email",
                "status": "sent",
                "email": clean_email
            }
        except Exception as e:
            _safe_print(f"[EMAIL SERVICE] [WARN] SMTP dispatch failed: {e}")

    # Fallback: Console Logging
    border = "=" * 72
    _safe_print(f"\n{border}")
    _safe_print(f"[EMAIL SERVICE] OTP CODE GENERATED FOR: {clean_email}")
    _safe_print(f"   >>> VERIFICATION CODE: {otp} <<<")
    _safe_print(f"   Subject: {subject}")
    _safe_print("   Note: Add SMTP_USER and SMTP_PASSWORD in backend/.env for live delivery.")
    _safe_print(f"{border}\n")

    return {
        "delivered": False,
        "provider": "Email Simulator",
        "status": "logged",
        "email": clean_email,
        "otp": otp
    }
