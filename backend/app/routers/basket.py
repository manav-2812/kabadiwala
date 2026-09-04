from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import User, Collector, Lot, LotItem, LotPhoto, Material, TraceabilityEvent
from app.schemas.all_schemas import BasketResponse, LotItemResponse, BasketItemRequest, MineralChip
from app.services.price_engine import calculate_item_estimate
from app.services.minerals import calculate_recoverable_minerals
from app.services.trace import compute_event_hash, GENESIS_HASH

router = APIRouter(prefix="/basket", tags=["basket"])

async def get_or_create_draft_lot(user: User, db: AsyncSession) -> Lot:
    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    if not col:
        stmt_c = select(Collector)
        res_c = await db.execute(stmt_c)
        col = res_c.scalars().first()

    stmt = (
        select(Lot)
        .where(Lot.collector_id == col.id, Lot.status == "draft")
        .options(
            selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.compositions),
            selectinload(Lot.items).selectinload(LotItem.photos)
        )
    )
    res = await db.execute(stmt)
    lot = res.scalar_one_or_none()
    if not lot:
        # Create fresh draft
        from app.routers.lots import gen_lot_code
        lot = Lot(
            lot_code=gen_lot_code(),
            collector_id=col.id,
            status="draft",
            pickup_lat=col.lat,
            pickup_lng=col.lng,
            pickup_address=col.city
        )
        db.add(lot)
        await db.commit()
        
        # Re-fetch with relations
        res = await db.execute(stmt)
        lot = res.scalar_one_or_none()
        
    return lot

@router.get("", response_model=BasketResponse)
async def get_basket(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    lot = await get_or_create_draft_lot(user, db)
    
    tot_min = 0
    tot_max = 0
    tot_wt = 0
    is_haz = False
    comp_inputs = []
    item_responses = []

    for i in lot.items:
        tot_min += i.est_value_min_paise
        tot_max += i.est_value_max_paise
        tot_wt += i.est_weight_g
        if i.material and i.material.is_hazardous:
            is_haz = True

        if i.material:
            for c in i.material.compositions:
                comp_inputs.append({
                    "element": c.element,
                    "weight_kg": i.est_weight_g / 1000.0,
                    "grams_per_kg": float(c.grams_per_kg)
                })

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
            photo_urls=[p.storage_url for p in i.photos]
        ))

    minerals = calculate_recoverable_minerals(comp_inputs)
    chips = [
        MineralChip(
            element=m["element"],
            name=m["name"],
            grams=m["grams"],
            is_strategic=m["is_strategic"]
        ) for m in minerals
    ]

    return BasketResponse(
        items=item_responses,
        total_items=len(item_responses),
        est_total_min_paise=tot_min,
        est_total_max_paise=tot_max,
        est_total_weight_g=tot_wt,
        recoverable_minerals=chips,
        is_hazardous=is_haz
    )

@router.post("/items")
async def add_basket_item(
    item_data: BasketItemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    lot = await get_or_create_draft_lot(user, db)
    
    stmt_m = select(Material).where(Material.id == item_data.material_id)
    res_m = await db.execute(stmt_m)
    mat = res_m.scalar_one_or_none()
    if not mat:
        raise KabadiwalaAPIException(status_code=404, code="MATERIAL_NOT_FOUND", message_key="lot_not_found")
        
    wt_kg = item_data.est_weight_g / 1000.0
    est = calculate_item_estimate(mat.base_price_paise_per_kg, wt_kg, item_data.condition)

    new_item = LotItem(
        lot_id=lot.id,
        material_id=mat.id,
        est_weight_g=item_data.est_weight_g,
        condition=item_data.condition,
        est_value_min_paise=est["min_paise"],
        est_value_max_paise=est["max_paise"]
    )
    db.add(new_item)
    await db.commit()
    return {"status": "success", "item_id": new_item.id}

@router.delete("/items/{id}")
async def remove_basket_item(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LotItem).where(LotItem.id == id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success", "deleted_id": id}

@router.post("/sell")
async def sell_basket(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    lot = await get_or_create_draft_lot(user, db)
    if not lot.items:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BASKET_EMPTY",
            message_key="basket_empty"
        )
        
    tot_min = sum(i.est_value_min_paise for i in lot.items)
    tot_max = sum(i.est_value_max_paise for i in lot.items)
    tot_wt = sum(i.est_weight_g for i in lot.items)
    is_haz = any(i.material and i.material.is_hazardous for i in lot.items)

    lot.status = "listed"
    lot.est_total_min_paise = tot_min
    lot.est_total_max_paise = tot_max
    lot.est_total_weight_g = tot_wt
    lot.is_hazardous = is_haz

    # Append Genesis and Listed Trace Events
    payload_1 = {"lot_code": lot.lot_code, "action": "lot_created_from_basket", "items_count": len(lot.items)}
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

    payload_2 = {"status": "listed", "est_min": tot_min, "est_max": tot_max}
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
    return {
        "status": "success",
        "lot_id": lot.id,
        "lot_code": lot.lot_code,
        "message": "Basket listed successfully! Quotes will arrive shortly."
    }
