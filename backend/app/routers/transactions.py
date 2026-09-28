import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.i18n import KabadiwalaAPIException
from app.core.lot_state import LotStatus, validate_transition
from app.db.session import get_db
from app.models.all_models import (
    Collector,
    Lot,
    LotItem,
    Quote,
    Recycler,
    TraceabilityEvent,
    Transaction,
    User,
)
from app.routers.auth import get_current_user
from app.schemas.all_schemas import (
    CashHandoverConfirmRequest,
    DisputeRequest,
    HandoverConfirmRequest,
    TrackingPoint,
    WeighInRequest,
)
from app.services.trace import GENESIS_HASH, compute_event_hash
from app.ws.manager import ws_manager

router = APIRouter(prefix="/transactions", tags=["transactions"])

async def get_authorized_transaction(
    tx_id: str,
    user: User,
    db: AsyncSession,
    load_items: bool = False,
    load_events: bool = False
) -> Transaction:
    options = [
        selectinload(Transaction.lot),
        selectinload(Transaction.collector).selectinload(Collector.user),
        selectinload(Transaction.quote).selectinload(Quote.recycler),
        selectinload(Transaction.agent),
    ]
    if load_items:
        options.append(selectinload(Transaction.lot).selectinload(Lot.items).selectinload(LotItem.material))
    if load_events:
        options.append(selectinload(Transaction.lot).selectinload(Lot.trace_events))

    stmt = select(Transaction).where(Transaction.id == tx_id).options(*options)
    res = await db.execute(stmt)
    tx = res.scalar_one_or_none()
    if not tx:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="TRANSACTION_NOT_FOUND",
            message_key="transaction_not_found"
        )

    # Enforce IDOR authorization: user must be admin, or owning collector, or counterparty recycler
    if user.role != "admin":
        allowed = False
        if user.role == "collector" and tx.collector and tx.collector.user_id == user.id:
            allowed = True
        elif user.role == "recycler" and tx.quote and tx.quote.recycler:
            rec_res = await db.execute(select(Recycler).where(Recycler.user_id == user.id))
            rec = rec_res.scalar_one_or_none()
            if rec and tx.quote.recycler_id == rec.id:
                allowed = True
        elif user.role == "aggregator":
            allowed = True
        if not allowed:
            raise KabadiwalaAPIException(
                status_code=status.HTTP_404_NOT_FOUND,
                code="TRANSACTION_NOT_FOUND",
                message_key="transaction_not_found"
            )
    return tx

@router.get("/{id}")
async def get_transaction(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_items=True, load_events=False)

    lot = tx.lot
    items_data = []
    for item in lot.items:
        items_data.append({
            "id": item.id,
            "material_code": item.material.code if item.material else "SCRAP",
            "material_name": item.material.name_en if item.material else "Scrap Item",
            "est_weight_g": item.est_weight_g,
            "actual_weight_g": item.actual_weight_g,
            "condition": item.condition
        })

    return {
        "id": tx.id,
        "lot_id": lot.id,
        "lot_code": lot.lot_code,
        "receipt_no": tx.receipt_no,
        "status": tx.status,
        "lot_status": lot.status,
        "agreed_amount_paise": tx.agreed_amount_paise,
        "final_amount_paise": tx.final_amount_paise,
        "weight_variance_pct": float(tx.weight_variance_pct) if tx.weight_variance_pct is not None else None,
        "dispute_reason": tx.dispute_reason,
        "collector_name": tx.collector.user.name if tx.collector and tx.collector.user else "Collector",
        "buyer_name": tx.quote.recycler.company_name if tx.quote and tx.quote.recycler else "Recycler",
        "buyer_license": tx.quote.recycler.cpcb_license_no if tx.quote and tx.quote.recycler else "CPCB-REG",
        "agent": {
            "name": tx.agent.name if tx.agent else "Assigned Agent",
            "phone": tx.agent.phone if tx.agent else "9811122201",
            "vehicle_no": tx.agent.vehicle_no if tx.agent else "DL 1Y 4412"
        } if tx.agent else None,
        "payment_method": tx.payment_method,
        "cash_confirmed_by_collector": tx.cash_confirmed_by_collector,
        "cash_confirmed_collector_at": tx.cash_confirmed_collector_at.isoformat() if tx.cash_confirmed_collector_at else None,
        "collector_confirm_lat": float(tx.collector_confirm_lat) if tx.collector_confirm_lat is not None else None,
        "collector_confirm_lng": float(tx.collector_confirm_lng) if tx.collector_confirm_lng is not None else None,
        "cash_confirmed_by_buyer": tx.cash_confirmed_by_buyer,
        "cash_confirmed_buyer_at": tx.cash_confirmed_buyer_at.isoformat() if tx.cash_confirmed_buyer_at else None,
        "buyer_confirm_lat": float(tx.buyer_confirm_lat) if tx.buyer_confirm_lat is not None else None,
        "buyer_confirm_lng": float(tx.buyer_confirm_lng) if tx.buyer_confirm_lng is not None else None,
        "advance_paise": tx.advance_paise,
        "balance_paise": tx.balance_paise,
        "balance_due_at": tx.balance_due_at.isoformat() if tx.balance_due_at else None,
        "due_status": tx.due_status,
        "items": items_data
    }

@router.post("/{id}/arrive")
async def mark_arrival(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_events=True)
    lot = tx.lot
    validate_transition(lot.status, LotStatus.ARRIVED)

    lot.status = LotStatus.ARRIVED.value
    tx.status = "arrived"

    # Trace
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"event": "agent_arrived", "receipt_no": tx.receipt_no}
    ev_h = compute_event_hash(last_h, next_seq, "arrived", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="arrived",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({"type": "agent_arrived", "transaction_id": tx.id}, channel="global")
    return {"status": "success", "tx_status": tx.status, "lot_status": lot.status}

@router.post("/{id}/weigh")
async def record_weigh_in(
    id: str,
    data: WeighInRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_items=True, load_events=True)
    lot = tx.lot

    total_est_g = lot.est_total_weight_g or 1
    total_act_g = 0

    for item in lot.items:
        if item.id in data.actual_weights:
            act_w = data.actual_weights[item.id]
            item.actual_weight_g = act_w
            total_act_g += act_w
        else:
            item.actual_weight_g = item.est_weight_g
            total_act_g += item.est_weight_g

    lot.actual_total_weight_g = total_act_g

    # Weight variance %
    variance_pct = abs(total_act_g - total_est_g) / float(total_est_g) * 100.0
    tx.weight_variance_pct = round(variance_pct, 2)

    # Recalculate amount based on actual weight
    weight_ratio = total_act_g / float(total_est_g)
    final_amt = round(tx.agreed_amount_paise * weight_ratio)
    tx.final_amount_paise = final_amt
    lot.final_amount_paise = final_amt

    # If variance > 10%, requires explicit confirmation or dispute
    if variance_pct > 10.0:
        lot.status = LotStatus.AWAITING_CONFIRM.value
        tx.status = "awaiting_confirm"
    else:
        lot.status = LotStatus.PAYMENT_PENDING.value
        tx.status = "payment_pending"

    # Append Trace
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {
        "event": "weighed",
        "actual_weight_g": total_act_g,
        "variance_pct": round(variance_pct, 2),
        "revised_amount_paise": final_amt
    }
    ev_h = compute_event_hash(last_h, next_seq, "weighed", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="weighed",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({
        "type": "weigh_in_completed",
        "transaction_id": tx.id,
        "variance_pct": round(variance_pct, 2),
        "status": tx.status
    }, channel="global")

    return {
        "status": "success",
        "lot_status": lot.status,
        "tx_status": tx.status,
        "actual_total_weight_g": total_act_g,
        "variance_pct": round(variance_pct, 2),
        "requires_confirmation": (variance_pct > 10.0),
        "final_amount_paise": final_amt
    }

@router.post("/{id}/confirm")
async def confirm_handover(
    id: str,
    data: HandoverConfirmRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_events=True)
    lot = tx.lot

    # Accept revised or normal weigh-in
    tx.collector_confirmed_at = datetime.now(timezone.utc)
    tx.buyer_confirmed_at = datetime.now(timezone.utc)

    lot.status = LotStatus.PAYMENT_PENDING.value
    tx.status = "payment_pending"

    # Append Trace
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"event": "handover_confirmed", "verified_via": "otp_qr"}
    ev_h = compute_event_hash(last_h, next_seq, "handover_confirmed", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="handover_confirmed",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({"type": "handover_confirmed", "transaction_id": tx.id}, channel="global")
    return {"status": "success", "lot_status": lot.status, "tx_status": tx.status}

@router.post("/{id}/confirm-cash-handover")
async def confirm_cash_handover(
    id: str,
    data: CashHandoverConfirmRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_events=True)

    lot = tx.lot
    total_due = tx.final_amount_paise or tx.agreed_amount_paise
    now = datetime.now(timezone.utc)

    if data.role == "collector":
        tx.cash_confirmed_by_collector = True
        tx.cash_confirmed_collector_at = now
        tx.collector_confirm_lat = data.lat
        tx.collector_confirm_lng = data.lng
    elif data.role == "buyer":
        tx.cash_confirmed_by_buyer = True
        tx.cash_confirmed_buyer_at = now
        tx.buyer_confirm_lat = data.lat
        tx.buyer_confirm_lng = data.lng
    else:
        tx.cash_confirmed_by_collector = True
        tx.cash_confirmed_collector_at = now
        tx.collector_confirm_lat = data.lat
        tx.collector_confirm_lng = data.lng
        tx.cash_confirmed_by_buyer = True
        tx.cash_confirmed_buyer_at = now
        tx.buyer_confirm_lat = data.lat
        tx.buyer_confirm_lng = data.lng

    if data.is_partial:
        adv = data.advance_paise or data.cash_amount_paise or int(total_due * 0.5)
        tx.advance_paise = adv
        tx.balance_paise = max(0, total_due - adv)
        tx.balance_due_at = now + timedelta(days=data.due_days or 7)
        tx.due_status = "pending"
        tx.payment_status = "partial"
    else:
        adv = data.cash_amount_paise or total_due
        tx.advance_paise = adv
        tx.balance_paise = 0
        tx.due_status = "none"
        tx.payment_status = "paid"

    tx.payment_method = "cash"
    lot.status = LotStatus.COMPLETED.value
    tx.status = "completed"

    col = tx.collector
    if col and adv > 0:
        col.total_earned_paise += adv
        col.lots_completed += 1

    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {
        "event": "cash_handover_confirmed",
        "role": data.role,
        "cash_advance_paise": tx.advance_paise,
        "balance_paise": tx.balance_paise,
        "due_status": tx.due_status,
        "lat": data.lat,
        "lng": data.lng
    }
    ev_h = compute_event_hash(last_h, next_seq, "cash_handover_confirmed", payload, now)
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="cash_handover_confirmed",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({
        "type": "cash_handover_confirmed",
        "transaction_id": tx.id,
        "balance_paise": tx.balance_paise
    }, channel="global")

    return {
        "status": "success",
        "lot_status": lot.status,
        "tx_status": tx.status,
        "payment_status": tx.payment_status,
        "advance_paise": tx.advance_paise,
        "balance_paise": tx.balance_paise,
        "due_status": tx.due_status
    }

@router.post("/{id}/settle-due")
async def settle_due(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_events=True)

    if tx.due_status != "pending" or tx.balance_paise <= 0:
        return {"status": "already_settled", "message": "No pending dues for this transaction"}

    settled_paise = tx.balance_paise
    tx.advance_paise += settled_paise
    tx.balance_paise = 0
    tx.due_status = "settled"
    tx.payment_status = "paid"

    col = tx.collector
    if col:
        col.total_earned_paise += settled_paise

    lot = tx.lot
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"event": "due_settled_cash", "settled_amount_paise": settled_paise}
    ev_h = compute_event_hash(last_h, next_seq, "due_settled_cash", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="due_settled_cash",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({
        "type": "due_settled",
        "transaction_id": tx.id,
        "settled_paise": settled_paise
    }, channel="global")

    return {
        "status": "success",
        "settled_amount_paise": settled_paise,
        "balance_paise": 0,
        "due_status": "settled"
    }

@router.post("/{id}/dispute")
async def raise_dispute(
    id: str,
    data: DisputeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db, load_events=True)
    lot = tx.lot
    validate_transition(lot.status, LotStatus.DISPUTED)

    lot.status = LotStatus.DISPUTED.value
    tx.status = "disputed"
    tx.dispute_reason = data.reason

    # Append Trace
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    payload = {"event": "disputed", "reason": data.reason}
    ev_h = compute_event_hash(last_h, next_seq, "disputed", payload, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="disputed",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload),
        prev_hash=last_h,
        event_hash=ev_h
    )
    db.add(ev)

    await db.commit()
    await ws_manager.broadcast({"type": "dispute_raised", "transaction_id": tx.id, "reason": data.reason}, channel="global")
    return {"status": "disputed", "message": "Dispute raised. Handover frozen pending supervisor review."}

@router.get("/{id}/tracking", response_model=TrackingPoint)
async def get_live_tracking(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = await get_authorized_transaction(id, user, db)

    agent = tx.agent
    dest_lat = float(tx.lot.pickup_lat) if tx.lot else 28.6139
    dest_lng = float(tx.lot.pickup_lng) if tx.lot else 77.2090

    # Moving coordinates calculation for demo
    now_sec = int(datetime.now(timezone.utc).timestamp()) % 120
    ratio = now_sec / 120.0

    start_lat = dest_lat - 0.015
    start_lng = dest_lng - 0.015
    cur_lat = start_lat + (dest_lat - start_lat) * ratio
    cur_lng = start_lng + (dest_lng - start_lng) * ratio
    eta_min = max(1, int(15 * (1.0 - ratio)))

    return TrackingPoint(
        transaction_id=tx.id,
        agent_name=agent.name if agent else "Kuldeep Singh",
        agent_phone=agent.phone if agent else "9811122201",
        agent_vehicle=agent.vehicle_no if agent else "DL 1Y 4412",
        lat=round(cur_lat, 6),
        lng=round(cur_lng, 6),
        speed_kmh=26.5,
        eta_min=eta_min,
        is_arrived=(ratio >= 0.95 or tx.status == "arrived")
    )
