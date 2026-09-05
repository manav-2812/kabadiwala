from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import User, Collector, Payment, Transaction, Lot, Document, Quote, Recycler
from app.services.price_engine import get_formal_premium_paise

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("")
async def get_wallet_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Collector).where(Collector.user_id == user.id)
    res = await db.execute(stmt)
    col = res.scalar_one_or_none()
    if not col:
        stmt = select(Collector)
        res = await db.execute(stmt)
        col = res.scalars().first()

    formal_premium = get_formal_premium_paise(col.total_earned_paise)

    # Calculate pending dues
    stmt_dues = select(Transaction).where(
        Transaction.collector_id == col.id,
        Transaction.due_status == "pending",
        Transaction.balance_paise > 0
    )
    res_dues = await db.execute(stmt_dues)
    pending_txs = res_dues.scalars().all()
    pending_dues_paise = sum(tx.balance_paise for tx in pending_txs)
    pending_dues_count = len(pending_txs)

    return {
        "wallet_balance_paise": col.wallet_balance_paise,
        "total_earned_paise": col.total_earned_paise,
        "cash_in_hand_paise": col.total_earned_paise,
        "pending_dues_paise": pending_dues_paise,
        "pending_dues_inr": round(pending_dues_paise / 100.0, 2),
        "pending_dues_count": pending_dues_count,
        "lots_completed": col.lots_completed,
        "trust_score": col.trust_score,
        "formal_premium_paise": formal_premium,
        "formal_premium_inr": round(formal_premium / 100.0, 2),
        "upi_id": col.upi_id or f"{user.phone}@upi"
    }

@router.get("/dues")
async def get_wallet_dues(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    if not col:
        stmt_c = select(Collector)
        res_c = await db.execute(stmt_c)
        col = res_c.scalars().first()

    stmt = (
        select(Transaction)
        .where(
            Transaction.collector_id == col.id,
            Transaction.due_status == "pending",
            Transaction.balance_paise > 0
        )
        .options(
            selectinload(Transaction.lot),
            selectinload(Transaction.quote).selectinload(Quote.recycler)
        )
        .order_by(desc(Transaction.balance_due_at))
    )
    res = await db.execute(stmt)
    txs = res.scalars().all()

    dues = []
    for tx in txs:
        buyer_name = tx.quote.recycler.company_name if tx.quote and tx.quote.recycler else "Authorized Buyer"
        buyer_phone = "9811122201"
        dues.append({
            "transaction_id": tx.id,
            "lot_id": tx.lot_id,
            "lot_code": tx.lot.lot_code if tx.lot else "N/A",
            "buyer_name": buyer_name,
            "buyer_phone": buyer_phone,
            "balance_paise": tx.balance_paise,
            "balance_inr": round(tx.balance_paise / 100.0, 2),
            "due_date": tx.balance_due_at.isoformat() if tx.balance_due_at else None,
            "advance_paise": tx.advance_paise,
            "total_paise": tx.final_amount_paise or tx.agreed_amount_paise,
            "due_status": tx.due_status
        })
    return dues

@router.get("/history")
async def get_wallet_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    if not col:
        stmt_c = select(Collector)
        res_c = await db.execute(stmt_c)
        col = res_c.scalars().first()

    stmt = (
        select(Payment)
        .where(Payment.payee_collector_id == col.id)
        .options(selectinload(Payment.transaction).selectinload(Transaction.lot))
        .order_by(desc(Payment.paid_at))
        .limit(20)
    )
    res = await db.execute(stmt)
    payments = res.scalars().all()

    history = []
    for p in payments:
        tx = p.transaction
        lot = tx.lot if tx else None
        history.append({
            "id": p.id,
            "amount_paise": p.amount_paise,
            "amount_inr": round(p.amount_paise / 100.0, 2),
            "method": p.method,
            "upi_ref": p.upi_ref,
            "status": p.status,
            "paid_at": p.paid_at,
            "lot_code": lot.lot_code if lot else "N/A",
            "receipt_no": tx.receipt_no if tx else None
        })
    return history

@router.post("/withdraw")
async def withdraw_balance(
    payload: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Collector).where(Collector.user_id == user.id)
    res = await db.execute(stmt)
    col = res.scalar_one_or_none()
    if not col:
        stmt = select(Collector)
        res = await db.execute(stmt)
        col = res.scalars().first()

    amt_paise = int(payload.get("amount_paise", 0))
    if amt_paise < 5000: # Minimum ₹50
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="MIN_WITHDRAWAL",
            message_key="payment_failed",
            details={"min_inr": 50}
        )
        
    if amt_paise > col.wallet_balance_paise:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INSUFFICIENT_FUNDS",
            message_key="payment_failed"
        )
        
    col.wallet_balance_paise -= amt_paise
    await db.commit()

    return {
        "status": "success",
        "withdrawn_paise": amt_paise,
        "remaining_balance_paise": col.wallet_balance_paise,
        "upi_id": col.upi_id or f"{user.phone}@upi",
        "reference": f"KCWTH{datetime.now(timezone.utc).strftime('%d%H%M%S')}"
    }
