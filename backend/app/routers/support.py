import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import User, SupportTicket, TicketMessage, FAQ, Lot
from app.schemas.all_schemas import (
    TicketCreate, SupportTicketResponse, MessageCreate,
    TicketMessageResponse, FAQResponse
)
from app.services.support_bot import generate_bot_reply

router = APIRouter(tags=["support"])

@router.get("/support/tickets", response_model=List[SupportTicketResponse])
async def get_my_tickets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.user_id == user.id)
        .options(selectinload(SupportTicket.messages))
        .order_by(desc(SupportTicket.created_at))
    )
    res = await db.execute(stmt)
    tickets = res.scalars().all()

    now = datetime.now(timezone.utc)
    result = []
    for t in tickets:
        msg_list = [
            TicketMessageResponse(
                id=m.id,
                sender_type=m.sender_type,
                sender_name="You" if m.sender_type == "user" else "Support Assistant",
                body=m.body,
                attachment_url=m.attachment_url,
                attachment_type=m.attachment_type,
                duration_s=m.duration_s,
                created_at=m.created_at
            ) for m in t.messages
        ]
        
        breached = (t.status == "open" and t.first_response_due_at < now)
        result.append(SupportTicketResponse(
            id=t.id,
            ticket_no=t.ticket_no,
            category=t.category,
            priority=t.priority,
            status=t.status,
            lot_id=t.lot_id,
            language=t.language,
            first_response_due_at=t.first_response_due_at,
            resolution_due_at=t.resolution_due_at,
            first_responded_at=t.first_responded_at,
            resolved_at=t.resolved_at,
            is_sla_breached=breached,
            messages=msg_list
        ))
    return result

@router.post("/support/tickets", response_model=SupportTicketResponse)
async def create_ticket(
    data: TicketCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    t_no = f"KC-TKT-{random.randint(1000, 9999)}"
    now = datetime.now(timezone.utc)
    
    ticket = SupportTicket(
        ticket_no=t_no,
        user_id=user.id,
        category=data.category,
        priority="high" if data.category in ["dispute", "safety"] else "normal",
        status="open",
        lot_id=data.lot_id,
        transaction_id=data.transaction_id,
        language=data.language or user.language,
        first_response_due_at=now + timedelta(hours=2),
        resolution_due_at=now + timedelta(hours=24),
        source="user"
    )
    db.add(ticket)
    await db.flush()

    # User message
    msg1 = TicketMessage(
        ticket_id=ticket.id,
        sender_user_id=user.id,
        sender_type="user",
        body=data.message,
        attachment_url=data.attachment_url,
        attachment_type=data.attachment_type,
        duration_s=data.duration_s
    )
    db.add(msg1)

    # Fast Auto-Responder reply (within seconds)
    bot_reply_text = generate_bot_reply(data.category, data.message, data.language or user.language)
    msg2 = TicketMessage(
        ticket_id=ticket.id,
        sender_type="bot",
        body=bot_reply_text,
        attachment_type="none"
    )
    db.add(msg2)
    ticket.first_responded_at = now

    await db.commit()
    
    # Reload ticket
    stmt = select(SupportTicket).where(SupportTicket.id == ticket.id).options(selectinload(SupportTicket.messages))
    res = await db.execute(stmt)
    t = res.scalar_one()

    return SupportTicketResponse(
        id=t.id,
        ticket_no=t.ticket_no,
        category=t.category,
        priority=t.priority,
        status=t.status,
        lot_id=t.lot_id,
        language=t.language,
        first_response_due_at=t.first_response_due_at,
        resolution_due_at=t.resolution_due_at,
        first_responded_at=t.first_responded_at,
        messages=[
            TicketMessageResponse(
                id=m.id,
                sender_type=m.sender_type,
                sender_name="You" if m.sender_type == "user" else "JNARDDC Clean Bot",
                body=m.body,
                attachment_url=m.attachment_url,
                attachment_type=m.attachment_type,
                duration_s=m.duration_s,
                created_at=m.created_at
            ) for m in t.messages
        ]
    )

@router.post("/support/tickets/{id}/messages")
async def send_ticket_message(
    id: str,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SupportTicket).where(SupportTicket.id == id)
    res = await db.execute(stmt)
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise KabadiwalaAPIException(status_code=404, code="TICKET_NOT_FOUND", message_key="lot_not_found")
        
    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_user_id=user.id,
        sender_type="agent" if user.role == "admin" else "user",
        body=data.body,
        attachment_url=data.attachment_url,
        attachment_type=data.attachment_type,
        duration_s=data.duration_s
    )
    db.add(msg)
    await db.commit()
    return {"status": "success", "message_id": msg.id}

@router.get("/support/faqs", response_model=List[FAQResponse])
async def get_faqs(lang: str = Query("hi"), db: AsyncSession = Depends(get_db)):
    stmt = select(FAQ).where(FAQ.is_active == True).order_by(FAQ.sort_order)
    res = await db.execute(stmt)
    faqs = res.scalars().all()
    
    output = []
    for f in faqs:
        q = f.question_mr if (lang == "mr" and f.question_mr) else (f.question_hi if lang == "hi" else (f.question_pa if lang == "pa" else f.question_en))
        a = f.answer_mr if (lang == "mr" and f.answer_mr) else (f.answer_hi if lang == "hi" else (f.answer_pa if lang == "pa" else f.answer_en))
        output.append(FAQResponse(
            id=f.id,
            category=f.category,
            question=q,
            answer=a,
            audio_url=f.audio_url
        ))
    return output

@router.get("/admin/support/queue")
async def get_admin_support_queue(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SupportTicket)
        .options(selectinload(SupportTicket.user), selectinload(SupportTicket.messages))
        .order_by(desc(SupportTicket.created_at))
    )
    res = await db.execute(stmt)
    tickets = res.scalars().all()
    now = datetime.now(timezone.utc)
    
    queue = []
    for t in tickets:
        u_name = t.user.name if t.user else "User"
        is_breached = (t.status == "open" and t.first_response_due_at < now)
        queue.append({
            "id": t.id,
            "ticket_no": t.ticket_no,
            "user_name": u_name,
            "category": t.category,
            "priority": t.priority,
            "status": t.status,
            "language": t.language,
            "first_response_due_at": t.first_response_due_at,
            "resolution_due_at": t.resolution_due_at,
            "is_sla_breached": is_breached,
            "messages_count": len(t.messages),
            "created_at": t.created_at
        })
    return queue

@router.patch("/admin/support/tickets/{id}")
async def update_ticket_status(
    id: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SupportTicket).where(SupportTicket.id == id)
    res = await db.execute(stmt)
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise KabadiwalaAPIException(status_code=404, code="TICKET_NOT_FOUND", message_key="lot_not_found")
        
    if "status" in payload:
        ticket.status = payload["status"]
        if payload["status"] in ["resolved", "closed"]:
            ticket.resolved_at = datetime.now(timezone.utc)
    if "priority" in payload:
        ticket.priority = payload["priority"]
        
    await db.commit()
    return {"status": "success", "ticket_id": ticket.id, "ticket_status": ticket.status}
