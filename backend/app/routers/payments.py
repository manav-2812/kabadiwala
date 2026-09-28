import hashlib
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.i18n import KabadiwalaAPIException
from app.core.lot_state import LotStatus
from app.db.session import get_db
from app.models.all_models import (
    Document,
    Lot,
    Payment,
    TraceabilityEvent,
    Transaction,
    User,
)
from app.routers.auth import get_current_user
from app.schemas.all_schemas import PaymentInitiateRequest, PaymentResponse
from app.services.payments import process_simulated_payment
from app.services.trace import GENESIS_HASH, compute_event_hash
from app.ws.manager import ws_manager

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    data: PaymentInitiateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Transaction)
        .where(Transaction.id == data.transaction_id)
        .options(
            selectinload(Transaction.lot).selectinload(Lot.trace_events),
            selectinload(Transaction.collector)
        )
    )
    res = await db.execute(stmt)
    tx = res.scalar_one_or_none()
    if not tx:
        raise KabadiwalaAPIException(status_code=404, code="TRANSACTION_NOT_FOUND", message_key="transaction_not_found")

    lot = tx.lot
    payout_amt = tx.final_amount_paise or tx.agreed_amount_paise

    # Simulated processing
    sim_res = process_simulated_payment(amount_paise=payout_amt, method=data.method)

    payment = Payment(
        transaction_id=tx.id,
        payee_collector_id=tx.collector_id,
        amount_paise=payout_amt,
        method=data.method,
        upi_ref=sim_res["upi_ref"],
        status=sim_res["status"],
        paid_at=sim_res["paid_at"],
        failure_reason=sim_res["failure_reason"],
        platform_fee_paise=0
    )
    db.add(payment)

    if sim_res["status"] == "success":
        lot.status = LotStatus.COMPLETED.value
        tx.status = "completed"

        # Credit collector wallet atomically
        col = tx.collector
        if col:
            col.wallet_balance_paise += payout_amt
            col.total_earned_paise += payout_amt
            col.lots_completed += 1

        # Register formal receipt document
        doc = Document(
            type="receipt",
            number=tx.receipt_no or f"KC-RCT-{datetime.now(timezone.utc).year}-{lot.lot_code}",
            lot_id=lot.id,
            transaction_id=tx.id,
            user_id=col.user_id if col else None,
            storage_url=f"/api/documents/{tx.receipt_no}/pdf",
            sha256=hashlib.sha256((tx.receipt_no or "").encode()).hexdigest()
        )
        db.add(doc)

        # Append Trace Events: payment_made and processed
        events = sorted(lot.trace_events, key=lambda e: e.seq)
        last_h = events[-1].event_hash if events else GENESIS_HASH
        next_seq = (events[-1].seq + 1) if events else 1

        p1 = {"event": "payment_made", "amount_paise": payout_amt, "upi_ref": sim_res["upi_ref"]}
        h1 = compute_event_hash(last_h, next_seq, "payment_made", p1, datetime.now(timezone.utc))
        ev1 = TraceabilityEvent(
            lot_id=lot.id,
            seq=next_seq,
            event_type="payment_made",
            actor_user_id=user.id,
            actor_role=user.role,
            payload_json=json.dumps(p1),
            prev_hash=last_h,
            event_hash=h1
        )
        db.add(ev1)

        p2 = {"event": "processed", "formal_channel_verified": True}
        h2 = compute_event_hash(h1, next_seq + 1, "processed", p2, datetime.now(timezone.utc))
        ev2 = TraceabilityEvent(
            lot_id=lot.id,
            seq=next_seq + 1,
            event_type="processed",
            actor_user_id=user.id,
            actor_role=user.role,
            payload_json=json.dumps(p2),
            prev_hash=h1,
            event_hash=h2
        )
        db.add(ev2)
    else:
        lot.status = LotStatus.PAYMENT_FAILED.value
        tx.status = "payment_failed"

    await db.commit()

    await ws_manager.broadcast({
        "type": "payment_updated",
        "transaction_id": tx.id,
        "status": payment.status,
        "amount_paise": payout_amt
    }, channel="global")

    return PaymentResponse(
        id=payment.id,
        transaction_id=tx.id,
        amount_paise=payout_amt,
        method=payment.method,
        upi_ref=payment.upi_ref,
        status=payment.status,
        paid_at=payment.paid_at,
        failure_reason=payment.failure_reason,
        platform_fee_paise=0
    )

@router.post("/{id}/confirm-cash")
async def confirm_cash_payment(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Payment).where(Payment.id == id).options(
        selectinload(Payment.transaction).selectinload(Transaction.lot).selectinload(Lot.trace_events),
        selectinload(Payment.transaction).selectinload(Transaction.collector)
    )
    res = await db.execute(stmt)
    payment = res.scalar_one_or_none()
    if not payment:
        raise KabadiwalaAPIException(status_code=404, code="PAYMENT_NOT_FOUND", message_key="transaction_not_found")

    tx = payment.transaction
    lot = tx.lot

    payment.method = "cash"
    payment.status = "success"
    payment.upi_ref = f"CASH-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    payment.paid_at = datetime.now(timezone.utc)

    lot.status = LotStatus.COMPLETED.value
    tx.status = "completed"

    col = tx.collector
    if col:
        col.total_earned_paise += payment.amount_paise
        col.lots_completed += 1

    # Append Trace
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    p1 = {"event": "payment_made", "method": "cash", "amount_paise": payment.amount_paise}
    h1 = compute_event_hash(last_h, next_seq, "payment_made", p1, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="payment_made",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(p1),
        prev_hash=last_h,
        event_hash=h1
    )
    db.add(ev)

    await db.commit()
    return {"status": "success", "message": "Dual cash payment confirmed and recorded in audit trail."}
