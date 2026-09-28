import hashlib
import json
import secrets
import string
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.i18n import KabadiwalaAPIException
from app.core.lot_state import LotStatus, validate_transition
from app.db.session import get_db
from app.models.all_models import (
    Cancellation,
    Collector,
    Lot,
    LotItem,
    LotPhoto,
    Material,
    Quote,
    TraceabilityEvent,
    User,
)
from app.routers.auth import get_current_user
from app.schemas.all_schemas import (
    EstimateItemRequest,
    EstimateItemResponse,
    LotCreate,
    LotEstimateResponse,
    LotItemResponse,
    LotResponse,
    MineralChip,
)
from app.services.minerals import calculate_recoverable_minerals
from app.services.price_engine import calculate_item_estimate
from app.services.trace import GENESIS_HASH, compute_event_hash

router = APIRouter(prefix="/lots", tags=["lots"])

def gen_lot_code() -> str:
    # §1.5 — use secrets.choice, not random.choices (Mersenne Twister)
    chars = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"KC-LOT-{chars}"

@router.post("/estimate", response_model=LotEstimateResponse)
async def estimate_lot(items: list[EstimateItemRequest], db: AsyncSession = Depends(get_db)):
    stmt = select(Material).options(selectinload(Material.compositions))
    res = await db.execute(stmt)
    mat_map = {m.code: m for m in res.scalars().all()}

    comp_inputs = []
    item_responses = []
    tot_min_p = 0
    tot_max_p = 0
    tot_wt = 0.0
    is_haz = False

    for item in items:
        mat = mat_map.get(item.material_code)
        if not mat:
            continue
        if mat.is_hazardous:
            is_haz = True

        est = calculate_item_estimate(
            base_price_paise_per_kg=mat.base_price_paise_per_kg,
            weight_kg=item.weight_kg,
            condition=item.condition
        )
        tot_min_p += est["min_paise"]
        tot_max_p += est["max_paise"]
        tot_wt += item.weight_kg

        item_responses.append(EstimateItemResponse(
            material_code=item.material_code,
            weight_kg=item.weight_kg,
            min_paise=est["min_paise"],
            max_paise=est["max_paise"],
            min_inr=est["min_inr"],
            max_inr=est["max_inr"],
            condition_factor=est["condition_factor"],
            base_price_paise_per_kg=mat.base_price_paise_per_kg
        ))

        for c in mat.compositions:
            comp_inputs.append({
                "element": c.element,
                "weight_kg": item.weight_kg,
                "grams_per_kg": float(c.grams_per_kg)
            })

    minerals = calculate_recoverable_minerals(comp_inputs)
    mineral_chips = [
        MineralChip(
            element=m["element"],
            name=m["name"],
            grams=m["grams"],
            is_strategic=m["is_strategic"]
        ) for m in minerals
    ]

    return LotEstimateResponse(
        items=item_responses,
        total_min_paise=tot_min_p,
        total_max_paise=tot_max_p,
        total_min_inr=round(tot_min_p / 100.0, 2),
        total_max_inr=round(tot_max_p / 100.0, 2),
        total_weight_kg=round(tot_wt, 2),
        recoverable_minerals=mineral_chips,
        is_hazardous=is_haz,
        explanation="Calculated using verified national scrap index, condition rating, and estimated recovery yields."
    )

@router.post("", response_model=LotResponse)
async def create_lot(
    data: LotCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve collector profile
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()

    if not col:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="COLLECTOR_NOT_FOUND",
            message_key="auth_user_not_found",
            details={"detail": "No collector profile found for user"}
        )

    # Idempotency check on client_uuid
    if data.client_uuid:
        stmt_exist = select(Lot).where(Lot.client_uuid == data.client_uuid)
        res_exist = await db.execute(stmt_exist)
        existing = res_exist.scalar_one_or_none()
        if existing:
            return await get_lot_detail(existing.id, user, db)

    lot_code = gen_lot_code()
    lot = Lot(
        lot_code=lot_code,
        collector_id=col.id,
        status="listed",
        pickup_lat=data.pickup_lat or col.lat,
        pickup_lng=data.pickup_lng or col.lng,
        pickup_address=data.pickup_address or col.city,
        client_uuid=data.client_uuid,
        offline_created=data.offline_created,
        safety_acknowledged_at=datetime.now(timezone.utc)
    )
    db.add(lot)
    await db.flush()

    total_min = 0
    total_max = 0
    total_wt = 0
    is_haz = False

    stmt_m = select(Material)
    res_m = await db.execute(stmt_m)
    mat_map = {m.id: m for m in res_m.scalars().all()}

    for item_data in data.items:
        mat = mat_map.get(item_data.material_id)
        if not mat:
            continue
        if mat.is_hazardous:
            is_haz = True

        wt_kg = item_data.est_weight_g / 1000.0
        est = calculate_item_estimate(mat.base_price_paise_per_kg, wt_kg, item_data.condition)

        total_min += est["min_paise"]
        total_max += est["max_paise"]
        total_wt += item_data.est_weight_g

        lot_item = LotItem(
            lot_id=lot.id,
            material_id=mat.id,
            est_weight_g=item_data.est_weight_g,
            condition=item_data.condition,
            est_value_min_paise=est["min_paise"],
            est_value_max_paise=est["max_paise"],
            ai_suggested_material_id=item_data.ai_suggested_material_id,
            ai_confidence=item_data.ai_confidence,
            user_override=item_data.user_override
        )
        db.add(lot_item)
        await db.flush()

        for url in item_data.photo_urls:
            photo = LotPhoto(
                lot_item_id=lot_item.id,
                storage_url=url,
                thumb_url=url,
                sha256=hashlib.sha256(url.encode()).hexdigest()
            )
            db.add(photo)

    lot.est_total_min_paise = total_min
    lot.est_total_max_paise = total_max
    lot.est_total_weight_g = total_wt
    lot.is_hazardous = is_haz

    # Append Genesis and Listed Traceability Events
    payload_1 = {"lot_code": lot_code, "action": "lot_created", "items_count": len(data.items)}
    h1 = compute_event_hash(GENESIS_HASH, 1, "lot_created", payload_1, datetime.now(timezone.utc))
    ev1 = TraceabilityEvent(
        lot_id=lot.id,
        seq=1,
        event_type="lot_created",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload_1),
        geo_lat=lot.pickup_lat,
        geo_lng=lot.pickup_lng,
        prev_hash=GENESIS_HASH,
        event_hash=h1
    )
    db.add(ev1)

    payload_2 = {"status": "listed", "est_min": total_min, "est_max": total_max}
    h2 = compute_event_hash(h1, 2, "listed", payload_2, datetime.now(timezone.utc))
    ev2 = TraceabilityEvent(
        lot_id=lot.id,
        seq=2,
        event_type="listed",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(payload_2),
        geo_lat=lot.pickup_lat,
        geo_lng=lot.pickup_lng,
        prev_hash=h1,
        event_hash=h2
    )
    db.add(ev2)

    await db.commit()
    return await get_lot_detail(lot.id, user, db)

@router.get("", response_model=list[LotResponse])
async def get_lots(
    status: str | None = None,
    collector_only: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lot)
        .options(
            selectinload(Lot.items).selectinload(LotItem.material),
            selectinload(Lot.items).selectinload(LotItem.photos),
            selectinload(Lot.quotes),
            selectinload(Lot.collector).selectinload(Collector.user)
        )
        .order_by(desc(Lot.created_at))
    )
    if collector_only and user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        col = res_c.scalar_one_or_none()
        if col:
            stmt = stmt.where(Lot.collector_id == col.id)
    elif status:
        stmt = stmt.where(Lot.status == status)

    res = await db.execute(stmt)
    lots = res.scalars().all()

    output = []
    for l in lots:
        c_name = l.collector.user.name if l.collector and l.collector.user else "Collector"
        item_responses = []
        for i in l.items:
            item_responses.append(LotItemResponse(
                id=i.id,
                material_id=i.material_id,
                material_code=i.material.code if i.material else None,
                material_name=i.material.name_en if i.material else None,
                est_weight_g=i.est_weight_g,
                actual_weight_g=i.actual_weight_g,
                condition=i.condition,
                est_value_min_paise=i.est_value_min_paise,
                est_value_max_paise=i.est_value_max_paise,
                final_value_paise=i.final_value_paise,
                photo_urls=[p.storage_url for p in i.photos]
            ))

        output.append(LotResponse(
            id=l.id,
            lot_code=l.lot_code,
            collector_id=l.collector_id,
            collector_name=c_name,
            status=l.status,
            est_total_min_paise=l.est_total_min_paise,
            est_total_max_paise=l.est_total_max_paise,
            est_total_weight_g=l.est_total_weight_g,
            actual_total_weight_g=l.actual_total_weight_g,
            final_amount_paise=l.final_amount_paise,
            pickup_lat=float(l.pickup_lat),
            pickup_lng=float(l.pickup_lng),
            pickup_address=l.pickup_address,
            is_hazardous=l.is_hazardous,
            created_at=l.created_at,
            items=item_responses,
            quote_count=len(l.quotes)
        ))
    return output

@router.get("/{id}", response_model=LotResponse)
async def get_lot_detail(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lot)
        .where(Lot.id == id)
        .options(
            selectinload(Lot.items).selectinload(LotItem.material),
            selectinload(Lot.items).selectinload(LotItem.photos),
            selectinload(Lot.quotes).selectinload(Quote.recycler),
            selectinload(Lot.transaction),
            selectinload(Lot.collector).selectinload(Collector.user)
        )
    )
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="LOT_NOT_FOUND",
            message_key="lot_not_found"
        )

    # §1.8 IDOR: collectors can only see their own lots.
    # Admins and recyclers may see all lots (for quoting / admin views).
    if user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        caller_col = res_c.scalar_one_or_none()
        if not caller_col or lot.collector_id != caller_col.id:
            # Return 404, not 403, to avoid confirming the lot exists
            raise KabadiwalaAPIException(
                status_code=status.HTTP_404_NOT_FOUND,
                code="LOT_NOT_FOUND",
                message_key="lot_not_found"
            )

    c_name = lot.collector.user.name if lot.collector and lot.collector.user else "Collector"
    item_responses = []
    for i in lot.items:
        item_responses.append(LotItemResponse(
            id=i.id,
            material_id=i.material_id,
            material_code=i.material.code if i.material else None,
            material_name=i.material.name_en if i.material else None,
            est_weight_g=i.est_weight_g,
            actual_weight_g=i.actual_weight_g,
            condition=i.condition,
            est_value_min_paise=i.est_value_min_paise,
            est_value_max_paise=i.est_value_max_paise,
            final_value_paise=i.final_value_paise,
            photo_urls=[p.storage_url for p in i.photos]
        ))

    active_q = None
    if lot.quotes:
        best_q = max(lot.quotes, key=lambda q: q.price_paise_total)
        active_q = {
            "id": best_q.id,
            "recycler_name": best_q.recycler.company_name if best_q.recycler else "Recycler",
            "price_paise_total": best_q.price_paise_total,
            "status": best_q.status
        }

    tx_data = None
    if lot.transaction:
        tx_data = {
            "id": lot.transaction.id,
            "receipt_no": lot.transaction.receipt_no,
            "status": lot.transaction.status,
            "agreed_amount_paise": lot.transaction.agreed_amount_paise,
            "final_amount_paise": lot.transaction.final_amount_paise,
            "weight_variance_pct": float(lot.transaction.weight_variance_pct) if lot.transaction.weight_variance_pct is not None else None
        }

    return LotResponse(
        id=lot.id,
        lot_code=lot.lot_code,
        collector_id=lot.collector_id,
        collector_name=c_name,
        status=lot.status,
        est_total_min_paise=lot.est_total_min_paise,
        est_total_max_paise=lot.est_total_max_paise,
        est_total_weight_g=lot.est_total_weight_g,
        actual_total_weight_g=lot.actual_total_weight_g,
        final_amount_paise=lot.final_amount_paise,
        pickup_lat=float(lot.pickup_lat),
        pickup_lng=float(lot.pickup_lng),
        pickup_address=lot.pickup_address,
        is_hazardous=lot.is_hazardous,
        created_at=lot.created_at,
        items=item_responses,
        quote_count=len(lot.quotes),
        active_quote=active_q,
        transaction=tx_data
    )

@router.post("/{id}/cancel")
async def cancel_lot(
    id: str,
    payload: dict[str, str],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lot).where(Lot.id == id).options(selectinload(Lot.trace_events))
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="LOT_NOT_FOUND",
            message_key="lot_not_found"
        )

    # §1.8 IDOR: only the owning collector (or an admin) can cancel a lot
    if user.role == "collector":
        stmt_c = select(Collector).where(Collector.user_id == user.id)
        res_c = await db.execute(stmt_c)
        caller_col = res_c.scalar_one_or_none()
        if not caller_col or lot.collector_id != caller_col.id:
            raise KabadiwalaAPIException(
                status_code=status.HTTP_404_NOT_FOUND,
                code="LOT_NOT_FOUND",
                message_key="lot_not_found"
            )

    validate_transition(lot.status, LotStatus.CANCELLED)
    lot.status = LotStatus.CANCELLED.value

    cancel_record = Cancellation(
        lot_id=lot.id,
        by_user_id=user.id,
        by_role=user.role,
        reason_code=payload.get("reason_code", "other"),
        note=payload.get("note", "")
    )
    db.add(cancel_record)

    # Append Trace Event
    events = sorted(lot.trace_events, key=lambda e: e.seq)
    last_h = events[-1].event_hash if events else GENESIS_HASH
    next_seq = (events[-1].seq + 1) if events else 1

    p_load = {"action": "cancelled", "reason": payload.get("reason_code", "other")}
    c_hash = compute_event_hash(last_h, next_seq, "cancelled", p_load, datetime.now(timezone.utc))
    ev = TraceabilityEvent(
        lot_id=lot.id,
        seq=next_seq,
        event_type="cancelled",
        actor_user_id=user.id,
        actor_role=user.role,
        payload_json=json.dumps(p_load),
        prev_hash=last_h,
        event_hash=c_hash
    )
    db.add(ev)

    await db.commit()
    return {"status": "success", "lot_id": lot.id, "new_status": lot.status}
