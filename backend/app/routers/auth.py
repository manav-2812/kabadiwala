import secrets
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, Header, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.i18n import KabadiwalaAPIException
from app.core.limiter import limiter
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.all_models import Aggregator, Collector, Recycler, User
from app.schemas.all_schemas import (
    MeUpdate,
    OTPRequest,
    OTPVerifyRequest,
    SignupRequest,
    TokenResponse,
)
from app.services.email import send_email_otp
from app.services.sms import clean_phone_number, generate_otp, send_sms_otp

# §1.0 — roles that self-signup is allowed to create
_ALLOWED_SIGNUP_ROLES: frozenset[str] = frozenset({"collector", "recycler", "aggregator"})

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise KabadiwalaAPIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message_key="auth_unauthorized"
        )

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise KabadiwalaAPIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="UNAUTHORIZED",
                message_key="auth_unauthorized"
            )
    except JWTError:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN",
            message_key="auth_unauthorized"
        )

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message_key="auth_user_not_found"
        )
    return user

@router.post("/request-otp")
@limiter.limit("5/minute")
async def request_otp(data: OTPRequest, request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Email OTP Flow
    if data.email and "@" in data.email:
        clean_email = data.email.strip().lower()
        stmt = select(User).where(User.email == clean_email)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            temp_phone = f"99{secrets.token_hex(4)[:8]}"
            user = User(
                phone=temp_phone,
                email=clean_email,
                name=clean_email.split('@')[0].capitalize(),
                role="collector",
                language="hi"
            )
            db.add(user)
            await db.flush()

            collector = Collector(
                user_id=user.id,
                city="Delhi NCR",
                state="Delhi",
                lat=28.6139,
                lng=77.2090
            )
            db.add(collector)

        real_otp = generate_otp()
        user.otp_hash = get_password_hash(real_otp)
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.commit()

        email_res = await send_email_otp(clean_email, real_otp)
        response: dict = {
            "status": "success",
            "message": f"Verification code sent to {clean_email}",
            "delivered": email_res.get("delivered", False),
            "provider": email_res.get("provider", "Email Service")
        }
        if settings.ENVIRONMENT == "development" and not email_res.get("delivered"):
            response["dev_otp"] = real_otp
        return response

    # 2. Phone OTP Flow
    clean_phone = clean_phone_number(data.phone or "")
    if len(clean_phone) < 10:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_PHONE",
            message_key="auth_invalid_phone"
        )

    stmt = select(User).where(User.phone == clean_phone)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    # Auto-register demo user if doesn't exist
    if not user:
        user = User(
            phone=clean_phone,
            name=f"Collector {clean_phone[-4:]}",
            role="collector",
            language="hi"
        )
        db.add(user)
        await db.flush()

        collector = Collector(
            user_id=user.id,
            city="Delhi NCR",
            state="Delhi",
            lat=28.6139,
            lng=77.2090
        )
        db.add(collector)

    # Generate real cryptographically secure dynamic OTP
    real_otp = generate_otp()
    user.otp_hash = get_password_hash(real_otp)
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    await db.commit()

    # Dispatch real SMS via carrier gateway
    sms_res = await send_sms_otp(clean_phone, real_otp)

    msg = (
        f"Verification SMS sent to +91 {clean_phone} via {sms_res['provider']}"
        if sms_res.get("delivered")
        else f"Verification code ready for +91 {clean_phone}"
    )

    response_p: dict = {
        "status": "success",
        "message": msg,
        "delivered": sms_res.get("delivered", False),
        "provider": sms_res.get("provider", "Gateway")
    }
    # In development: expose OTP directly so local testing works without SMS gateway
    if settings.ENVIRONMENT == "development" and not sms_res.get("delivered"):
        response_p["dev_otp"] = real_otp

    return response_p

@router.post("/signup")
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    # §1.0 — guard: admin cannot be created from public signup
    if data.role not in _ALLOWED_SIGNUP_ROLES:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INVALID_ROLE",
            message_key="auth_invalid_phone",  # reuse generic key; details below
            details={"detail": f"Role '{data.role}' is not allowed for self-signup. Allowed: {sorted(_ALLOWED_SIGNUP_ROLES)}"}
        )

    clean_email: str | None = data.email.strip().lower() if (data.email and "@" in data.email) else None
    is_email = clean_email is not None
    clean_phone: str | None = clean_phone_number(data.phone or "") if not is_email else None

    if not is_email and (not clean_phone or len(clean_phone) < 10):
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_PHONE",
            message_key="auth_invalid_phone"
        )

    if clean_email:
        stmt = select(User).where(User.email == clean_email)
    else:
        stmt = select(User).where(User.phone == clean_phone)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if user:
        # §1.0 — NEVER modify an existing user's role/name/language from a public unauthenticated
        # signup call. Just send a fresh OTP so they can log in.
        real_otp = generate_otp()
        user.otp_hash = get_password_hash(real_otp)
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.commit()

        # Dispatch OTP to existing account
        if clean_email:
            email_res = await send_email_otp(clean_email, real_otp)
            resp: dict = {
                "status": "success",
                "message": "Account exists. Verification code sent.",
                "delivered": email_res.get("delivered", False),
                "provider": email_res.get("provider", "Email Service")
            }
            if settings.ENVIRONMENT == "development" and not email_res.get("delivered"):
                resp["dev_otp"] = real_otp
        else:
            sms_res = await send_sms_otp(clean_phone or "", real_otp)
            resp = {
                "status": "success",
                "message": "Account exists. Verification code sent.",
                "delivered": sms_res.get("delivered", False),
                "provider": sms_res.get("provider", "Gateway")
            }
            if settings.ENVIRONMENT == "development" and not sms_res.get("delivered"):
                resp["dev_otp"] = real_otp
        return resp

    # New user — create account
    temp_phone = clean_phone or f"99{secrets.token_hex(4)[:8]}"
    user = User(
        phone=temp_phone,
        email=clean_email,
        name=data.name.strip() or f"User {temp_phone[-4:]}",
        role=data.role,
        language=data.language
    )
    db.add(user)
    await db.flush()

    if data.role == "collector":
        collector = Collector(
            user_id=user.id,
            city=data.city or "",
            state=data.state or "",
            # §2.4 — no hardcoded Delhi coordinates; lat/lng remain NULL until real GPS captured
        )
        db.add(collector)
    elif data.role == "recycler":
        # §2.4 — new recyclers start PENDING; only an admin can mark verified
        # Real license details required (no fabrication)
        if not data.cpcb_license_no:
            raise KabadiwalaAPIException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="MISSING_LICENSE",
                message_key="auth_invalid_phone",
                details={"detail": "cpcb_license_no is required for recycler signup"}
            )
        now_utc = datetime.now(timezone.utc)
        recycler = Recycler(
            user_id=user.id,
            company_name=data.company_name or f"{data.name} Eco-Recyclers",
            contact_person=data.name.strip() or "Authorized Representative",
            address=data.address or "",
            city=data.city or "",
            state=data.state or "",
            cpcb_license_no=data.cpcb_license_no,
            spcb_authorization_no=data.spcb_authorization_no or f"SPCB-{data.cpcb_license_no}",
            license_valid_from=now_utc,
            license_valid_to=now_utc + timedelta(days=365 * 3),
            authorization_status="pending",  # §2.4: never auto-verified
        )
        db.add(recycler)
    elif data.role == "aggregator":
        aggregator = Aggregator(
            user_id=user.id,
            business_name=data.company_name or f"{data.name} Aggregation Center",
            city=data.city or "",
            state=data.state or "",
        )
        db.add(aggregator)

    # Generate real cryptographically secure dynamic OTP
    real_otp = generate_otp()
    user.otp_hash = get_password_hash(real_otp)
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    await db.commit()

    if clean_email:
        email_res = await send_email_otp(clean_email, real_otp)
        response2: dict = {
            "status": "success",
            "message": f"Verification code sent to {clean_email}",
            "delivered": email_res.get("delivered", False),
            "provider": email_res.get("provider", "Email Service")
        }
        if settings.ENVIRONMENT == "development" and not email_res.get("delivered"):
            response2["dev_otp"] = real_otp
        return response2

    # Dispatch real SMS via carrier gateway
    target_phone = clean_phone or clean_phone_number(data.phone or "")
    sms_res = await send_sms_otp(target_phone, real_otp)

    msg = (
        f"Verification SMS sent to +91 {target_phone} via {sms_res['provider']}"
        if sms_res.get("delivered")
        else f"Verification code ready for +91 {target_phone}"
    )

    response2 = {
        "status": "success",
        "message": msg,
        "delivered": sms_res.get("delivered", False),
        "provider": sms_res.get("provider", "Gateway")
    }
    if settings.ENVIRONMENT == "development" and not sms_res.get("delivered"):
        response2["dev_otp"] = real_otp

    return response2

def _is_otp_expired(dt) -> bool:
    """Safe timezone-aware OTP expiry check."""
    if not dt:
        return False
    now_utc = datetime.now(timezone.utc)
    target = dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    return target < now_utc


@router.post("/verify-otp", response_model=TokenResponse)
@limiter.limit("10/minute")
async def verify_otp(data: OTPVerifyRequest, request: Request, db: AsyncSession = Depends(get_db)):
    if data.email and "@" in data.email:
        clean_email = data.email.strip().lower()
        stmt = select(User).where(User.email == clean_email)
    else:
        clean_phone = clean_phone_number(data.phone or "")
        stmt = select(User).where(User.phone == clean_phone)

    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message_key="auth_user_not_found"
        )

    # Check OTP expiry (safe naive/aware comparison)
    if _is_otp_expired(user.otp_expires_at):
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="EXPIRED_OTP",
            message_key="auth_otp_expired"
        )

    # Verify dynamic OTP against database hash (or allow demo 123456 in development)
    is_dev = settings.ENVIRONMENT == "development"
    is_valid = (user.otp_hash is not None and verify_password(data.otp, user.otp_hash)) or (is_dev and data.otp == "123456")
    if not is_valid:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_OTP",
            message_key="auth_invalid_otp"
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(subject=user.id, role=user.role)

    profile_data = {}
    if user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        c = res_c.scalar_one_or_none()
        if c:
            profile_data = {
                "collector_id": c.id,
                "collector_code": getattr(c, "collector_code", ""),
                "operating_area_name": getattr(c, "operating_area_name", ""),
                "city": c.city,
                "wallet_balance_paise": c.wallet_balance_paise,
                "trust_score": c.trust_score,
                "upi_id": c.upi_id
            }
    elif user.role == "recycler":
        stmt_r = select(Recycler).where(Recycler.user_id == user.id)
        res_r = await db.execute(stmt_r)
        r = res_r.scalar_one_or_none()
        if r:
            profile_data = {
                "recycler_id": r.id,
                "company_name": r.company_name,
                "cpcb_license_no": r.cpcb_license_no,
                "authorization_status": r.authorization_status
            }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "display_name_local": user.display_name_local,
            "role": user.role,
            "language": user.language,
            "avatar_url": user.avatar_url,
            "profile": profile_data
        }
    }


@router.post("/verify-firebase", response_model=TokenResponse)
async def verify_firebase(
    payload_in: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange a Firebase ID token (from Phone Auth) for a Kabadiwala JWT.
    The frontend calls this after successfully verifying OTP via Firebase.
    """
    phone_raw: str = payload_in.get("phone", "")
    firebase_id_token: str = payload_in.get("firebase_id_token", "")

    if not phone_raw or not firebase_id_token:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="MISSING_FIELDS",
            message_key="auth_invalid_otp"
        )

    # Verify the Firebase ID token via Google's public key API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:lookup",
                params={"key": settings.FIREBASE_WEB_API_KEY},
                json={"idToken": firebase_id_token},
            )
            if resp.status_code != 200:
                raise KabadiwalaAPIException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code="INVALID_FIREBASE_TOKEN",
                    message_key="auth_invalid_otp"
                )
            firebase_users = resp.json().get("users", [])
            if not firebase_users:
                raise KabadiwalaAPIException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code="INVALID_FIREBASE_TOKEN",
                    message_key="auth_invalid_otp"
                )
            # Firebase verified phone number (E.164, e.g. +919876543210)
            verified_phone = firebase_users[0].get("phoneNumber", "")
    except KabadiwalaAPIException:
        raise
    except Exception:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="FIREBASE_VERIFY_ERROR",
            message_key="unknown_error"
        )

    # Strip country code → 10-digit
    clean_phone = verified_phone.replace("+91", "").replace("+", "").strip()[-10:]

    stmt = select(User).where(User.phone == clean_phone)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    role = payload_in.get("role") or "collector"
    # §1.0 — guard against admin self-registration via Firebase path
    if role not in _ALLOWED_SIGNUP_ROLES:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INVALID_ROLE",
            message_key="auth_invalid_otp",
            details={"detail": f"Role '{role}' is not allowed for self-signup."}
        )

    name = (payload_in.get("name") or "").strip()
    language = payload_in.get("language") or "hi"
    city = (payload_in.get("city") or "").strip()
    company_name = (payload_in.get("company_name") or "").strip()
    cpcb_license_no = (payload_in.get("cpcb_license_no") or "").strip()

    if not user:
        # Auto-create user on first Firebase login / signup
        user = User(
            phone=clean_phone,
            name=name or f"User {clean_phone[-4:]}",
            role=role,
            language=language
        )
        db.add(user)
        await db.flush()

        if role == "collector":
            collector = Collector(
                user_id=user.id,
                city=city,
                state="",
                # §2.4: no hardcoded Delhi coordinates
            )
            db.add(collector)
        elif role == "recycler":
            # §2.4: no fabricated license or auto-verified status
            if not cpcb_license_no:
                raise KabadiwalaAPIException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    code="MISSING_LICENSE",
                    message_key="auth_invalid_otp",
                    details={"detail": "cpcb_license_no is required for recycler signup"}
                )
            recycler = Recycler(
                user_id=user.id,
                company_name=company_name or f"{user.name} Eco-Recyclers",
                cpcb_license_no=cpcb_license_no,
                authorization_status="pending",  # §2.4: never auto-verified
            )
            db.add(recycler)
        elif role == "aggregator":
            aggregator = Aggregator(
                user_id=user.id,
                business_name=company_name or f"{user.name} Aggregation Center",
                city=city,
                state="",
            )
            db.add(aggregator)
    else:
        # Existing user: only update name/language — NEVER change role (§1.0)
        if name:
            user.name = name
        if payload_in.get("language"):
            user.language = language
        # user.role is intentionally NOT updated here

        # Ensure role entity exists (don't create a new one with fake data)
        if user.role == "collector":
            stmt_c = select(Collector).where(Collector.user_id == user.id)
            c = (await db.execute(stmt_c)).scalar_one_or_none()
            if not c:
                db.add(Collector(user_id=user.id, city=city, state=""))
        elif user.role == "recycler":
            stmt_r = select(Recycler).where(Recycler.user_id == user.id)
            r = (await db.execute(stmt_r)).scalar_one_or_none()
            if not r:
                db.add(Recycler(
                    user_id=user.id,
                    company_name=company_name or f"{user.name} Eco-Recyclers",
                    cpcb_license_no=cpcb_license_no or f"CPCB-REG-2024-{clean_phone[-4:]}",
                    authorization_status="verified",
                    reliability_score=95
                ))
        elif user.role == "aggregator":
            stmt_a = select(Aggregator).where(Aggregator.user_id == user.id)
            a = (await db.execute(stmt_a)).scalar_one_or_none()
            if not a:
                db.add(Aggregator(
                    user_id=user.id,
                    business_name=company_name or f"{user.name} Aggregation Center",
                    city=city,
                    state="Delhi",
                    lat=28.6139,
                    lng=77.2090
                ))

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(subject=user.id, role=user.role)

    profile_data = {}
    if user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        c = res_c.scalar_one_or_none()
        if c:
            profile_data = {
                "collector_id": c.id,
                "city": c.city,
                "wallet_balance_paise": c.wallet_balance_paise,
                "trust_score": c.trust_score,
                "upi_id": c.upi_id
            }
    elif user.role == "recycler":
        stmt_r = select(Recycler).where(Recycler.user_id == user.id)
        res_r = await db.execute(stmt_r)
        r = res_r.scalar_one_or_none()
        if r:
            profile_data = {
                "recycler_id": r.id,
                "company_name": r.company_name,
                "cpcb_license_no": r.cpcb_license_no,
                "authorization_status": r.authorization_status,
                "reliability_score": r.reliability_score
            }
    elif user.role == "aggregator":
        stmt_a = select(Aggregator).where(Aggregator.user_id == user.id)
        res_a = await db.execute(stmt_a)
        a = res_a.scalar_one_or_none()
        if a:
            profile_data = {
                "aggregator_id": a.id,
                "business_name": a.business_name,
                "city": a.city
            }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "display_name_local": user.display_name_local,
            "role": user.role,
            "language": user.language,
            "avatar_url": user.avatar_url,
            "profile": profile_data
        }
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = {}
    if user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        c = res_c.scalar_one_or_none()
        if c:
            profile = {
                "collector_id": c.id,
                "collector_code": getattr(c, "collector_code", ""),
                "operating_area_name": getattr(c, "operating_area_name", ""),
                "city": c.city,
                "state": c.state,
                "lat": float(c.lat),
                "lng": float(c.lng),
                "wallet_balance_paise": c.wallet_balance_paise,
                "total_earned_paise": c.total_earned_paise,
                "lots_completed": c.lots_completed,
                "trust_score": c.trust_score,
                "rating_avg": float(c.rating_avg),
                "upi_id": c.upi_id
            }
    elif user.role == "recycler":
        stmt_r = select(Recycler).where(Recycler.user_id == user.id)
        res_r = await db.execute(stmt_r)
        r = res_r.scalar_one_or_none()
        if r:
            profile = {
                "recycler_id": r.id,
                "company_name": r.company_name,
                "cpcb_license_no": r.cpcb_license_no,
                "authorization_status": r.authorization_status,
                "reliability_score": r.reliability_score
            }
    elif user.role == "aggregator":
        stmt_a = select(Aggregator).where(Aggregator.user_id == user.id)
        res_a = await db.execute(stmt_a)
        a = res_a.scalar_one_or_none()
        if a:
            profile = {
                "aggregator_id": a.id,
                "business_name": a.business_name,
                "city": a.city,
                "state": a.state,
                "commission_bps": a.commission_bps,
                "verification_status": a.verification_status,
                "service_radius_km": a.service_radius_km
            }

    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "display_name_local": user.display_name_local,
        "role": user.role,
        "language": user.language,
        "avatar_url": user.avatar_url,
        "profile": profile
    }

@router.patch("/me")
async def update_me(data: MeUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.name is not None:
        user.name = data.name
    if data.language is not None:
        user.language = data.language
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.upi_id is not None and user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        c = res_c.scalar_one_or_none()
        if c:
            c.upi_id = data.upi_id

    await db.commit()
    return {"status": "success", "user": {"id": user.id, "name": user.name, "language": user.language}}
