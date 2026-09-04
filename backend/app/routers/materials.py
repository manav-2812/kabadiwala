from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.all_models import Material, MaterialComposition
from app.schemas.all_schemas import MaterialResponse, MaterialCompositionResponse

router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("", response_model=List[MaterialResponse])
async def get_materials(db: AsyncSession = Depends(get_db)):
    stmt = select(Material).options(selectinload(Material.compositions))
    res = await db.execute(stmt)
    materials = res.scalars().all()
    
    result = []
    for m in materials:
        result.append(MaterialResponse(
            id=m.id,
            code=m.code,
            name_en=m.name_en,
            name_hi=m.name_hi,
            name_mr=m.name_mr or m.name_hi or m.name_en,
            name_pa=m.name_pa,
            icon_key=m.icon_key,
            base_price_paise_per_kg=m.base_price_paise_per_kg,
            price_floor_paise=m.price_floor_paise,
            price_ceiling_paise=m.price_ceiling_paise,
            is_hazardous=m.is_hazardous,
            hazard_level=m.hazard_level,
            hazard_note_en=m.hazard_note_en,
            hazard_note_hi=m.hazard_note_hi,
            hazard_note_mr=m.hazard_note_mr,
            hazard_note_pa=m.hazard_note_pa,
            safety_tip_en=m.safety_tip_en,
            safety_tip_hi=m.safety_tip_hi,
            safety_tip_mr=m.safety_tip_mr,
            safety_tip_pa=m.safety_tip_pa,
            strategic_flag=m.strategic_flag,
            compositions=[
                MaterialCompositionResponse(
                    element=c.element,
                    grams_per_kg=float(c.grams_per_kg),
                    source_note=c.source_note
                ) for c in m.compositions
            ]
        ))
    return result

@router.get("/{id}/composition", response_model=List[MaterialCompositionResponse])
async def get_composition(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(MaterialComposition).where(MaterialComposition.material_id == id)
    res = await db.execute(stmt)
    comps = res.scalars().all()
    return [
        MaterialCompositionResponse(
            element=c.element,
            grams_per_kg=float(c.grams_per_kg),
            source_note=c.source_note
        ) for c in comps
    ]
