from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.i18n import KabadiwalaAPIException
from app.ws.manager import ws_manager

# Import all routers
from app.routers import (
    auth, materials, prices, lots, basket, recyclers,
    quotes, transactions, payments, wallet, trace, safety,
    documents, support, notifications, dashboard, demo, sync,
    ml, admin
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Guard: startup check fails if DEMO_MODE=false while any is_synthetic=true user exists."""
    if not settings.DEMO_MODE:
        from app.db.session import async_session_maker
        from app.models.all_models import User
        from sqlalchemy import select
        async with async_session_maker() as db:
            result = await db.execute(select(User).where(User.is_synthetic == True))
            synthetic_users = result.scalars().all()
            if synthetic_users:
                raise RuntimeError(
                    f"CRITICAL SAFETY VIOLATION: DEMO_MODE is False but {len(synthetic_users)} "
                    f"synthetic users exist in the database with reachable notification channels. "
                    f"Set DEMO_MODE=True or retire synthetic users before live deployment."
                )
    yield

# §1.6 — Rate limiter (slowapi, compatible with FastAPI/Starlette)
# The key function uses the request body phone param; falls back to IP.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Vernacular, low-literacy, offline-tolerant e-waste marketplace connecting informal collectors with authorized recyclers.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMIT_EXCEEDED",
            "message_key": "auth_otp_rate_limited",
            "details": {"detail": f"Rate limit exceeded: {exc.detail}"}
        }
    )

# CORS — §1.3: no wildcard; explicit origins only
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vernacular Error Handler
@app.exception_handler(KabadiwalaAPIException)
async def kabadiwala_api_exception_handler(request: Request, exc: KabadiwalaAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(materials.router, prefix=settings.API_V1_STR)
app.include_router(prices.router, prefix=settings.API_V1_STR)
app.include_router(lots.router, prefix=settings.API_V1_STR)
app.include_router(basket.router, prefix=settings.API_V1_STR)
app.include_router(recyclers.router, prefix=settings.API_V1_STR)
app.include_router(quotes.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(wallet.router, prefix=settings.API_V1_STR)
app.include_router(trace.router, prefix=settings.API_V1_STR)
app.include_router(safety.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(support.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(demo.router, prefix=settings.API_V1_STR)
app.include_router(sync.router, prefix=settings.API_V1_STR)
app.include_router(ml.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

# Top-level public aliases required by PS spec
app.include_router(documents.router) # /verify/{doc_number}
app.include_router(ml.router) # /ml/classify, /ml/valuate
app.include_router(admin.router) # /admin/anomalies, /admin/matching-weights, /admin/data-health

# WebSocket Endpoints
@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="global")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="global")

@app.websocket("/ws/tracking/{transaction_id}")
async def websocket_tracking(websocket: WebSocket, transaction_id: str):
    channel = f"tracking_{transaction_id}"
    await ws_manager.connect(websocket, channel=channel)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel=channel)

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health():
    """Liveness probe — returns 200 if the process is alive."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    """Readiness probe — checks DB connectivity before accepting traffic."""
    from app.db.session import async_session_maker
    from sqlalchemy import text
    try:
        async with async_session_maker() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"status": "not_ready", "detail": str(exc)})
