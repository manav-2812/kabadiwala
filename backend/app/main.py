from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Vernacular, low-literacy, offline-tolerant e-waste marketplace connecting informal collectors with authorized recyclers.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
