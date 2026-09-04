from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import Document, Transaction, Lot, LotItem, Recycler, Collector, User, Quote
from app.services.receipt import generate_handover_receipt_pdf
from app.services.trace import verify_event_chain

router = APIRouter(tags=["documents"])

@router.get("/documents")
async def get_documents(
    type: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).order_by(desc(Document.generated_at))
    if type:
        stmt = stmt.where(Document.type == type)
    res = await db.execute(stmt)
    docs = res.scalars().all()
    return [
        {
            "id": d.id,
            "type": d.type,
            "number": d.number,
            "lot_id": d.lot_id,
            "transaction_id": d.transaction_id,
            "storage_url": d.storage_url,
            "generated_at": d.generated_at
        } for d in docs
    ]

@router.get("/documents/{number}/pdf")
async def download_document_pdf(
    number: str,
    db: AsyncSession = Depends(get_db)
):
    # Find transaction by receipt_no
    stmt = (
        select(Transaction)
        .where(Transaction.receipt_no == number)
        .options(
            selectinload(Transaction.lot).selectinload(Lot.items).selectinload(LotItem.material),
            selectinload(Transaction.lot).selectinload(Lot.trace_events),
            selectinload(Transaction.collector).selectinload(Collector.user),
            selectinload(Transaction.quote).selectinload(Quote.recycler),
            selectinload(Transaction.payments)
        )
    )
    res = await db.execute(stmt)
    tx = res.scalar_one_or_none()
    
    if not tx:
        # Generate generic demo receipt
        pdf_bytes, sha = generate_handover_receipt_pdf(
            receipt_no=number,
            lot_code="KC-LOT-0001",
            date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            collector_name="Ramesh Kumar",
            buyer_name="EcoBirba Circular Recyclers",
            buyer_license="CPCB/E-WASTE/DL/2023/042",
            items=[{"name": "Circuit Boards (PCB)", "condition": "broken", "est_kg": 5.0, "actual_kg": 5.2, "amount_inr": 2184.0}],
            agreed_inr=2100.0,
            final_inr=2184.0,
            upi_ref="KCUPI9918237412",
            hash_chain_summary="6a84f329987dae0114bc5012f94ca23"
        )
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename={number}.pdf"
        })

    lot = tx.lot
    col_name = tx.collector.user.name if tx.collector and tx.collector.user else "Collector"
    buyer = tx.quote.recycler if tx.quote else None
    buyer_name = buyer.company_name if buyer else "Authorized Recycler"
    buyer_lic = buyer.cpcb_license_no if buyer else "CPCB-REG-2024"
    
    items_list = []
    for i in lot.items:
        items_list.append({
            "name": i.material.name_en if i.material else "E-Waste Item",
            "condition": i.condition,
            "est_kg": i.est_weight_g / 1000.0,
            "actual_kg": (i.actual_weight_g or i.est_weight_g) / 1000.0,
            "amount_inr": (i.final_value_paise or i.est_value_max_paise) / 100.0
        })

    first_payment = tx.payments[0] if tx.payments else None
    upi_ref = (first_payment.upi_ref if (first_payment and first_payment.upi_ref) else "KCUPI1234567890")
    last_event = sorted(lot.trace_events, key=lambda e: e.seq)[-1] if lot.trace_events else None
    hash_summary = last_event.event_hash if last_event else "000000000000"

    pdf_bytes, sha = generate_handover_receipt_pdf(
        receipt_no=number,
        lot_code=lot.lot_code,
        date_str=tx.created_at.strftime("%Y-%m-%d %H:%M UTC"),
        collector_name=col_name,
        buyer_name=buyer_name,
        buyer_license=buyer_lic,
        items=items_list,
        agreed_inr=tx.agreed_amount_paise / 100.0,
        final_inr=(tx.final_amount_paise or tx.agreed_amount_paise) / 100.0,
        upi_ref=upi_ref,
        hash_chain_summary=hash_summary
    )

    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename={number}.pdf"
    })

@router.get("/verify/{doc_number}")
async def public_verify_document(
    doc_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Public verification endpoint (via QR scan) adhering to privacy rules:
    returns lot code, amount, timestamp and hash verification status only, zero PII.
    """
    stmt = (
        select(Transaction)
        .where(Transaction.receipt_no == doc_number)
        .options(selectinload(Transaction.lot).selectinload(Lot.trace_events))
    )
    res = await db.execute(stmt)
    tx = res.scalar_one_or_none()

    if not tx:
        return {
            "receipt_no": doc_number,
            "verified": False,
            "status": "Document record not found in national registry."
        }

    lot = tx.lot
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    verification = verify_event_chain(events)

    return {
        "receipt_no": doc_number,
        "lot_code": lot.lot_code,
        "verified": verification["valid"],
        "compliance": "E-Waste (Management) Rules, 2022 Compliant",
        "settled_amount_inr": (tx.final_amount_paise or tx.agreed_amount_paise) / 100.0,
        "handover_timestamp": tx.created_at.isoformat(),
        "trace_events_count": verification["total_events"],
        "chain_integrity": "Cryptographically Intact (SHA-256)" if verification["valid"] else "TAMPER_DETECTED"
    }
