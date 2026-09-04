import json
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import Lot, TraceabilityEvent
from app.schemas.all_schemas import TraceEventResponse, TraceVerifyResponse
from app.services.trace import verify_event_chain

router = APIRouter(tags=["trace"])

@router.get("/lots/{lot_id}/trace", response_model=List[TraceEventResponse])
async def get_lot_trace(
    lot_id: str,
    db: AsyncSession = Depends(get_db)
):
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
    db: AsyncSession = Depends(get_db)
):
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
