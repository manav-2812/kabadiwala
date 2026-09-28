import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import KabadiwalaAPIException
from app.db.session import get_db
from app.models.all_models import (
    Collector,
    Lot,
    Quote,
    Recycler,
    TraceabilityEvent,
    User,
)
from app.routers.auth import get_current_user
from app.schemas.all_schemas import TraceEventResponse, TraceVerifyResponse
from app.services.trace import verify_event_chain

router = APIRouter(tags=["trace"])

@router.get("/lots/{lot_id}/trace", response_model=list[TraceEventResponse])
async def get_lot_trace(
    lot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_l = select(Lot).where(Lot.id == lot_id)
    res_l = await db.execute(stmt_l)
    lot = res_l.scalar_one_or_none()
    if not lot:
        raise KabadiwalaAPIException(status_code=404, code="LOT_NOT_FOUND", message_key="lot_not_found")

    if user.role != "admin":
        allowed = False
        if user.role == "collector":
            col_res = await db.execute(select(Collector).where(Collector.user_id == user.id))
            col = col_res.scalar_one_or_none()
            if col and lot.collector_id == col.id:
                allowed = True
        elif user.role == "recycler":
            rec_res = await db.execute(select(Recycler).where(Recycler.user_id == user.id))
            rec = rec_res.scalar_one_or_none()
            if rec:
                q_res = await db.execute(select(Quote).where(Quote.lot_id == lot.id, Quote.recycler_id == rec.id))
                if q_res.scalar_one_or_none():
                    allowed = True
        elif user.role == "aggregator":
            allowed = True
        if not allowed:
            raise KabadiwalaAPIException(status_code=404, code="LOT_NOT_FOUND", message_key="lot_not_found")

    stmt = (
        select(TraceabilityEvent)
        .where(TraceabilityEvent.lot_id == lot_id)
        .order_by(TraceabilityEvent.seq.asc())
    )
    res = await db.execute(stmt)
    events = res.scalars().all()

    output = []
    for e in events:
        try:
            p = json.loads(e.payload_json) if isinstance(e.payload_json, str) else e.payload_json
        except Exception:
            p = {}

        output.append(TraceEventResponse(
            id=e.id,
            lot_id=e.lot_id,
            seq=e.seq,
            event_type=e.event_type,
            actor_user_id=e.actor_user_id,
            actor_role=e.actor_role,
            payload=p,
            geo_lat=float(e.geo_lat) if e.geo_lat is not None else None,
            geo_lng=float(e.geo_lng) if e.geo_lng is not None else None,
            occurred_at=e.occurred_at,
            prev_hash=e.prev_hash,
            event_hash=e.event_hash
        ))
    return output

@router.get("/lots/{lot_id}/trace/verify", response_model=TraceVerifyResponse)
async def verify_lot_trace(
    lot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_l = select(Lot).where(Lot.id == lot_id)
    res_l = await db.execute(stmt_l)
    lot = res_l.scalar_one_or_none()
    if not lot:
        raise KabadiwalaAPIException(status_code=404, code="LOT_NOT_FOUND", message_key="lot_not_found")

    if user.role != "admin":
        allowed = False
        if user.role == "collector":
            col_res = await db.execute(select(Collector).where(Collector.user_id == user.id))
            col = col_res.scalar_one_or_none()
            if col and lot.collector_id == col.id:
                allowed = True
        elif user.role == "recycler":
            rec_res = await db.execute(select(Recycler).where(Recycler.user_id == user.id))
            rec = rec_res.scalar_one_or_none()
            if rec:
                q_res = await db.execute(select(Quote).where(Quote.lot_id == lot.id, Quote.recycler_id == rec.id))
                if q_res.scalar_one_or_none():
                    allowed = True
        elif user.role == "aggregator":
            allowed = True
        if not allowed:
            raise KabadiwalaAPIException(status_code=404, code="LOT_NOT_FOUND", message_key="lot_not_found")

    stmt = (
        select(TraceabilityEvent)
        .where(TraceabilityEvent.lot_id == lot_id)
        .order_by(TraceabilityEvent.seq.asc())
    )
    res = await db.execute(stmt)
    events = list(res.scalars().all())

    result = verify_event_chain(events)
    return TraceVerifyResponse(
        lot_id=lot_id,
        valid=result["valid"],
        total_events=result["total_events"],
        broken_at_seq=result["broken_at_seq"],
        last_hash=result["last_hash"]
    )
