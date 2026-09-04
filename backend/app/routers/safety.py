from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User, Collector, Material, SafetyAcknowledgement, Lot

router = APIRouter(prefix="/safety", tags=["safety"])

@router.get("/{material_code}")
async def get_safety_card(material_code: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Material).where(Material.code == material_code.upper())
    res = await db.execute(stmt)
    mat = res.scalar_one_or_none()
    if not mat:
        return {
            "code": material_code,
            "hazard_level": "low",
            "is_hazardous": False,
            "hazard_note": "Handle with standard protective gloves and footwear.",
            "safety_tip": "Do not break or burn. Store in dry shade.",
            "bonus_inr": 0.0
        }

    bonus = 50.0 if mat.is_hazardous else 0.0  # Hazardous safe-handling bonus
    return {
        "id": mat.id,
        "code": mat.code,
        "name_en": mat.name_en,
        "name_hi": mat.name_hi,
        "name_pa": mat.name_pa,
        "is_hazardous": mat.is_hazardous,
        "hazard_level": mat.hazard_level,
        "hazard_note_en": mat.hazard_note_en,
        "hazard_note_hi": mat.hazard_note_hi,
        "hazard_note_pa": mat.hazard_note_pa,
        "safety_tip_en": mat.safety_tip_en,
        "safety_tip_hi": mat.safety_tip_hi,
        "safety_tip_pa": mat.safety_tip_pa,
        "safe_handling_bonus_inr": bonus
    }

@router.post("/acknowledge")
async def acknowledge_safety(
    payload: Dict[str, str],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    lot_id = payload.get("lot_id")
    material_id = payload.get("material_id")

    stmt_c = select(Collector).where(Collector.user_id == user.id)
    res_c = await db.execute(stmt_c)
    col = res_c.scalar_one_or_none()
    col_id = col.id if col else user.id

    ack = SafetyAcknowledgement(
        lot_id=lot_id or "general",
        collector_id=col_id,
        material_id=material_id or "general",
        acknowledged_at=datetime.now(timezone.utc)
    )
    db.add(ack)

    if lot_id:
        stmt_l = select(Lot).where(Lot.id == lot_id)
        res_l = await db.execute(stmt_l)
        lot = res_l.scalar_one_or_none()
        if lot:
            lot.safety_acknowledged_at = datetime.now(timezone.utc)

    await db.commit()
    return {"status": "success", "message": "Safety protocols acknowledged. Safe handling bonus applied."}
