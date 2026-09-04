import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.core.i18n import KabadiwalaAPIException
from app.core.lot_state import validate_transition, LotStatus
from app.models.all_models import (
    User, Lot, Quote, Transaction, Recycler, TraceabilityEvent, PickupAgent
)
from app.schemas.all_schemas import QuoteCreate, QuoteResponse
from app.services.trace import compute_event_hash, GENESIS_HASH
from app.ws.manager import ws_manager

router = APIRouter(tags=["quotes"])

@router.post("/lots/{lot_id}/quotes", response_model=QuoteResponse)
async def submit_quote(
    lot_id: str,
    data: QuoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lot).where(Lot.id == lot_id).options(selectinload(Lot.trace_events))
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        raise KabadiwalaAPIException(status_code=404, code="LOT_NOT_FOUND", message_key="lot_not_found")
        
    stmt_r = select(Recycler).where(Recycler.user_id == user.id)
    res_r = await db.execute(stmt_r)
    rec = res_r.scalar_one_or_none()
    if not rec:
        stmt_r = select(Recycler)
        res_r = await db.execute(stmt_r)
        rec = res_r.scalars().first()

    quote = Quote(
        lot_id=lot.id,
        recycler_id=rec.id,
        price_paise_total=data.price_paise_total,
        pickup_mode=data.pickup_mode,
        pickup_eta_at=datetime.now(timezone.utc) + timedelta(hours=data.pickup_eta_hours),
        valid_until=datetime.now(timezone.utc) + timedelta(days=2),
        status="sent",
        note=data.note
    )
    db.add(quote)
    
    if lot.status == "listed":
        lot.status = "quoted"

    # Append Trace Event
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"quote_id": quote.id, "recycler": rec.company_name, "amount_paise": data.price_paise_total}
    ev_h = compute_event_hash(last_h, next_seq, "quote_received", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="quote_received",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()

    # WebSocket Broadcast
    await ws_manager.broadcast({
        "type": "quote_received",
        "lot_id": lot.id,
        "amount_paise": data.price_paise_total,
        "recycler_name": rec.company_name
    }, channel="global")

    return QuoteResponse(
        id=quote.id,
        lot_id=lot.id,
        recycler_id=rec.id,
        recycler_name=rec.company_name,
        recycler_cpcb_license=rec.cpcb_license_no,
        recycler_rating=float(rec.rating_avg),
        price_paise_total=quote.price_paise_total,
        pickup_mode=quote.pickup_mode,
        pickup_eta_at=quote.pickup_eta_at,
        valid_until=quote.valid_until,
        status=quote.status,
        note=quote.note
    )

@router.get("/lots/{lot_id}/quotes", response_model=List[QuoteResponse])
async def get_lot_quotes(
    lot_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Quote)
        .where(Quote.lot_id == lot_id)
        .options(selectinload(Quote.recycler))
        .order_by(Quote.price_paise_total.desc())
    )
    res = await db.execute(stmt)
    quotes = res.scalars().all()
    if not quotes:
        return []

    max_p = max(q.price_paise_total for q in quotes)
    
    result = []
    for idx, q in enumerate(quotes):
        rec = q.recycler
        result.append(QuoteResponse(
            id=q.id,
            lot_id=q.lot_id,
            recycler_id=q.recycler_id,
            recycler_name=rec.company_name if rec else "Recycler",
            recycler_cpcb_license=rec.cpcb_license_no if rec else "CPCB-REG",
            recycler_rating=float(rec.rating_avg) if rec else 4.8,
            price_paise_total=q.price_paise_total,
            pickup_mode=q.pickup_mode,
            pickup_eta_at=q.pickup_eta_at,
            valid_until=q.valid_until,
            status=q.status,
            note=q.note,
            is_best_price=(q.price_paise_total == max_p),
            is_nearest=(idx == 0)
        ))
    return result

@router.post("/quotes/{id}/accept")
async def accept_quote(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Quote).where(Quote.id == id).options(selectinload(Quote.lot).selectinload(Lot.trace_events), selectinload(Quote.recycler))
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise KabadiwalaAPIException(status_code=404, code="QUOTE_NOT_FOUND", message_key="quote_not_found")
        
    lot = quote.lot
    validate_transition(lot.status, LotStatus.ACCEPTED)
    
    quote.status = "accepted"
    lot.status = LotStatus.ACCEPTED.value

    # Assign an active agent from this recycler
    stmt_ag = select(PickupAgent).where(PickupAgent.recycler_id == quote.recycler_id)
    res_ag = await db.execute(stmt_ag)
    agent = res_ag.scalars().first()
    if not agent:
        stmt_ag = select(PickupAgent)
        res_ag = await db.execute(stmt_ag)
        agent = res_ag.scalars().first()

    # Create transaction
    rct_no = f"KC-RCT-{datetime.now(timezone.utc).year}-{random.randint(10000, 99999)}"
    tx = Transaction(
        lot_id=lot.id,
        quote_id=quote.id,
        collector_id=lot.collector_id,
        buyer_type="recycler",
        buyer_id=quote.recycler_id,
        agreed_amount_paise=quote.price_paise_total,
        handover_qr_token=f"QR-AUTH-{lot.lot_code}",
        status="scheduled",
        receipt_no=rct_no,
        agent_id=agent.id if agent else None
    )
    db.add(tx)

    # Append Trace Event
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"quote_id": quote.id, "amount_paise": quote.price_paise_total, "receipt_no": rct_no}
    ev_h = compute_event_hash(last_h, next_seq, "quote_accepted", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="quote_accepted",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()

    await ws_manager.broadcast({
        "type": "quote_accepted",
        "lot_id": lot.id,
        "transaction_id": tx.id
    }, channel="global")

    return {
        "status": "success",
        "lot_id": lot.id,
        "transaction_id": tx.id,
        "message": "Quote accepted! Pickup agent has been scheduled."
    }
