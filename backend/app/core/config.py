
import os
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from dotenv import load_dotenv
    _backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    _env_file = os.path.join(_backend_dir, ".env")
    if os.path.exists(_env_file):
        load_dotenv(_env_file)
except ImportError:
    pass

_DEFAULT_SECRET = "sih2026-kabadiwala-connect-secret-key-32chars"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "Kabadiwala Connect"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # SQLite fallback when DATABASE_URL is unset
    _default_db_path: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "kabadiwala.db")
    ).replace("\\", "/")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'kabadiwala.db')).replace(chr(92), '/')}"
    )

    # §1.2 — never accept the committed default in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET)

    ALGORITHM: str = "HS256"
    # §1.7 — shorter TTL reduces window for stolen tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 8)))  # 8h default

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # §1.3 — no wildcard; production origins come from env var only
    # Dev origins are explicitly listed; add deployed URL via CORS_ORIGINS_EXTRA env var.
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    # Space-separated additional origins (e.g. deployed Vercel URL) set in production env
    CORS_ORIGINS_EXTRA: str = os.getenv("CORS_ORIGINS_EXTRA", "")

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """Fail loudly on startup if production secrets are unset / left as defaults."""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == _DEFAULT_SECRET:
                raise RuntimeError(
                    "CRITICAL: SECRET_KEY must be overridden in production. "
                    "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            if "*" in self.CORS_ORIGINS:
                raise RuntimeError(
                    "CRITICAL: CORS_ORIGINS must not contain '*' in production."
                )
        return self

    @property
    def all_cors_origins(self) -> List[str]:
        """Merged CORS list, including any extra production origins from env."""
        extra = [o.strip() for o in self.CORS_ORIGINS_EXTRA.split() if o.strip()]
        return list(dict.fromkeys(self.CORS_ORIGINS + extra))  # deduplicate, preserve order

    # Realistic Seed & Safety Mode (Section 8)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    SUPPORT_PHONE: Optional[str] = os.getenv("SUPPORT_PHONE", None)

    # Real SMS Gateway Configurations
    FAST2SMS_API_KEY: Optional[str] = os.getenv("FAST2SMS_API_KEY")
    TWOFACTOR_API_KEY: Optional[str] = os.getenv("TWOFACTOR_API_KEY")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    MSG91_AUTH_KEY: Optional[str] = os.getenv("MSG91_AUTH_KEY")
    MSG91_TEMPLATE_ID: Optional[str] = os.getenv("MSG91_TEMPLATE_ID")

    # Firebase Phone Auth — Web API key used to verify ID tokens server-side
    FIREBASE_WEB_API_KEY: Optional[str] = os.getenv("FIREBASE_WEB_API_KEY")

    # Firebase Cloud Messaging — Service Account JSON (path or inline JSON string)
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    # SMTP / Email OTP Configurations
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SMTP_FROM: Optional[str] = os.getenv("SMTP_FROM", None)
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"

    # ───────────────────────────────────────────────────────────────────────
    # AI / ML Feature Flags (Section 2 of AI Integration Spec)
    # All default to safe/on values; set in .env to override.
    # ---------------------------------------------------------------
    ML_ENABLED: bool = os.getenv("ML_ENABLED", "true").lower() == "true"
    # auto | device | server | off
    ML_CLASSIFY_MODE: str = os.getenv("ML_CLASSIFY_MODE", "auto")
    # Minimum confidence to emit a suggestion (below = "Not sure")
    ML_CLASSIFY_MIN_CONF: float = float(os.getenv("ML_CLASSIFY_MIN_CONF", "0.60"))
    # Real completed rows per material required to enable learned valuation
    ML_MIN_ROWS_PER_MATERIAL: int = int(os.getenv("ML_MIN_ROWS_PER_MATERIAL", "200"))
    # Real rows required to enable Isolation Forest anomaly detector
    ML_MIN_ROWS_ANOMALY: int = int(os.getenv("ML_MIN_ROWS_ANOMALY", "300"))
    # Real calendar days of price data required to show a forecast
    ML_FORECAST_MIN_DAYS: int = int(os.getenv("ML_FORECAST_MIN_DAYS", "30"))
    # Pre-labelling provider for unverified images (none = disabled)
    ML_PRELABEL_PROVIDER: str = os.getenv("ML_PRELABEL_PROVIDER", "none")
    # Whether to log every ML prediction to ml_predictions table
    ML_LOG_PREDICTIONS: bool = os.getenv("ML_LOG_PREDICTIONS", "true").lower() == "true"
    # Path to active ONNX classifier model (relative to backend/)
    ML_CLASSIFY_MODEL_PATH: str = os.getenv("ML_CLASSIFY_MODEL_PATH", "../ml/artifacts/models/classify.onnx")


settings = Settings()
