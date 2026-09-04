import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.all_models import Lot, TraceabilityEvent, Transaction
from app.db.seed import seed_database
from app.services.trace import compute_event_hash, GENESIS_HASH
from app.ws.manager import ws_manager

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/reset")
async def demo_reset():
    await seed_database()
    return {"status": "success", "message": "Database reset and seeded with full demo scenario."}

@router.post("/tamper")
async def demo_tamper(payload: Optional[Dict[str, str]] = None, db: AsyncSession = Depends(get_db)):
    lot_code = payload.get("lot_code", "KC-LOT-0001") if payload else "KC-LOT-0001"
    stmt = select(Lot).where(Lot.lot_code == lot_code)
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        stmt = select(Lot).where(Lot.status == "completed")
        res = await db.execute(stmt)
        lot = res.scalars().first()

    stmt_ev = select(TraceabilityEvent).where(TraceabilityEvent.lot_id == lot.id).order_by(TraceabilityEvent.seq.asc())
    res_ev = await db.execute(stmt_ev)
    events = res_ev.scalars().all()
    
    if len(events) >= 2:
        target_ev = events[1]
        target_ev.event_hash = "deadbeef" + target_ev.event_hash[8:]
        await db.commit()
        
    return {
        "status": "tampered",
        "lot_code": lot.lot_code,
        "tampered_seq": 2,
        "message": f"Tampering simulated on seq 2 of {lot.lot_code}. Audit chain should now fail verification."
    }

@router.post("/repair")
async def demo_repair(payload: Optional[Dict[str, str]] = None, db: AsyncSession = Depends(get_db)):
    lot_code = payload.get("lot_code", "KC-LOT-0001") if payload else "KC-LOT-0001"
    stmt = select(Lot).where(Lot.lot_code == lot_code)
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        stmt = select(Lot).where(Lot.status == "completed")
        res = await db.execute(stmt)
        lot = res.scalars().first()

    stmt_ev = select(TraceabilityEvent).where(TraceabilityEvent.lot_id == lot.id).order_by(TraceabilityEvent.seq.asc())
    res_ev = await db.execute(stmt_ev)
    events = res_ev.scalars().all()

    prev_h = GENESIS_HASH
    for ev in events:
        try:
            p = json.loads(ev.payload_json) if isinstance(ev.payload_json, str) else ev.payload_json
        except Exception:
            p = {}
        new_h = compute_event_hash(prev_h, ev.seq, ev.event_type, p, ev.occurred_at)
        ev.prev_hash = prev_h
        ev.event_hash = new_h
        prev_h = new_h

    await db.commit()
    return {
        "status": "repaired",
        "lot_code": lot.lot_code,
        "message": f"Cryptographic integrity repaired for {lot.lot_code}."
    }

@router.post("/simulate-agent-route/{transaction_id}")
async def simulate_agent_route(transaction_id: str):
    await ws_manager.broadcast({
        "type": "route_simulated",
        "transaction_id": transaction_id,
        "message": "Live pickup agent route simulation active."
    }, channel="global")
    return {"status": "active", "transaction_id": transaction_id}

@router.post("/simulate-payment-failure")
async def simulate_payment_failure():
    return {"status": "configured", "message": "Next payment transaction will simulate bank gateway timeout."}
