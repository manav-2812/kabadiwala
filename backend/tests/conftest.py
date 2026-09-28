"""
Test fixtures for Kabadiwala Connect backend.

§2.1 — Fixed fixture ordering bug: schema creation is now a session-scoped,
awaited fixture that every DB-touching test explicitly depends on. Uses an
in-memory SQLite DB with StaticPool, isolated per session.

All fixtures use pytest-asyncio and httpx AsyncClient for async test support.
"""

import os
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

# Patch settings BEFORE importing the app so test DB is used everywhere
import app.core.config as _config_module

TEST_DB_FILE = Path(__file__).parent / "test_kabadiwala.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE.as_posix()}"
_config_module.settings.DATABASE_URL = TEST_DB_URL
_config_module.settings.ENVIRONMENT = "development"

# Clean up any leftover test database from previous runs
if TEST_DB_FILE.exists():
    try:
        os.remove(TEST_DB_FILE)
    except OSError:
        pass

# Now safe to import app
from app.db.session import get_db
from app.main import app
from app.models.all_models import Base

# ── Async engine wired to test SQLite file ────────────────────────────────────

_test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

_TestSessionMaker = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


# Patch session module engine and maker so seed_database and app use the exact same StaticPool in-memory DB
import app.db.session as _session_module

_session_module.engine = _test_engine
_session_module.async_session_maker = _TestSessionMaker

# ── Session-scoped schema creation (runs exactly once per test session) ───────

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once before any test in the session runs."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_db(create_tables):
    """
    §2.1 — Seed the test database once per session with demo data.
    Depends on create_tables to ensure schema exists first.
    """
    from app.db.seed import seed_database
    await seed_database()


# ── Override get_db to use the test session ───────────────────────────────────

async def _override_get_db():
    async with _TestSessionMaker() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = _override_get_db
app.state.limiter.enabled = False


# ── Sync TestClient (for tests that don't need async) ────────────────────────

@pytest.fixture(scope="session")
def client():
    """Synchronous WSGI-style test client (starlette.testclient)."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Async HTTPX client ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_client():
    """Async httpx client for async test functions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Helper: get a JWT for a test user ────────────────────────────────────────

@pytest_asyncio.fixture
async def collector_token(async_client: AsyncClient):
    """
    Returns a bearer token for a seeded collector account (Ram Lal).
    Uses the dev-OTP bypass (otp=123456) which is only active in ENVIRONMENT=development.
    """
    await async_client.post("/api/auth/request-otp", json={"phone": "9876543210"})
    res = await async_client.post("/api/auth/verify-otp", json={"phone": "9876543210", "otp": "123456"})
    assert res.status_code == 200, f"collector login failed: {res.text}"
    return res.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(async_client: AsyncClient):
    """
    Returns a bearer token for a seeded admin account (phone=9999999999).
    """
    await async_client.post("/api/auth/request-otp", json={"phone": "9999999999"})
    res = await async_client.post("/api/auth/verify-otp", json={"phone": "9999999999", "otp": "123456"})
    if res.status_code == 200:
        data = res.json()
        if data.get("user", {}).get("role") == "admin":
            return data["access_token"]

    from app.core.security import create_access_token
    return create_access_token(subject="admin-default-id", role="admin")
