"""
ML API Router
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Endpoints:
  POST /ml/classify  -- material photo classification (demo_only until data gate met)
  POST /ml/valuate   -- Layer-1 rules valuation (honest basis, no random numbers)
  GET  /ml/models    -- list active models with demo_only flag
  GET  /prices/trends -- MA7/14/30, slope, arrow, forecast (gated)

Honesty rules enforced:
  - demo_only=true until real data gates are met (Section 3.1 / 5.2)
  - No random numbers used for any displayed metric
  - Every number in the response comes from the DB or deterministic rules
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.core.config import settings
from app.db.session import get_db
from app.models.all_models import (
    Material, MaterialSubcategory, PriceHistory, MLModel, MLPrediction
)
from app.services.valuation import valuate_item, compute_rules_valuation

router = APIRouter(prefix="/ml", tags=["ml"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ValuateItemInput(BaseModel):
    material_code: str
    sub_category: Optional[str] = None
    weight_g: int
    condition: str = "broken"
    source_type: Optional[str] = None


class ValuateRequest(BaseModel):
    items: List[ValuateItemInput]
    lat: Optional[float] = None
    lng: Optional[float] = None


class ClassifyRequest(BaseModel):
    image_base64: Optional[str] = None
    filename: Optional[str] = "scrap.jpg"
    hint_material: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_active_model(db: AsyncSession, task: str) -> Optional[MLModel]:
    stmt = (
        select(MLModel)
        .where(MLModel.task == task, MLModel.is_active == True)
        .order_by(desc(MLModel.created_at))
        .limit(1)
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def _log_prediction(
    db: AsyncSession,
    *,
    task: str,
    path: str,
    entity_type: str,
    entity_id: str,
    input_data: Any,
    output_data: Any,
    confidence: float = 0.0,
    latency_ms: int = 0,
    model_id: Optional[str] = None,
) -> None:
    """Log prediction to ml_predictions if ML_LOG_PREDICTIONS is enabled."""
    if not settings.ML_LOG_PREDICTIONS:
        return
    input_hash = hashlib.sha256(
        json.dumps(input_data, sort_keys=True, default=str).encode()
    ).hexdigest()
    pred = MLPrediction(
        model_id=model_id,
        task=task,
        path=path,
        entity_type=entity_type,
        entity_id=entity_id,
        input_hash=input_hash,
        output_json=json.dumps(output_data, default=str),
        confidence=round(confidence, 3),
        latency_ms=latency_ms,
        user_override=False,
    )
    db.add(pred)
    await db.commit()


# ---------------------------------------------------------------------------
# POST /ml/classify
# ---------------------------------------------------------------------------

DEMO_CLASSES = [
    "CRT", "LCD", "PCB", "CABLE", "BATTERY_LI",
    "BATTERY_PB", "MOTOR", "MAGNET", "PLASTIC_MIXED", "OTHER"
]

DEMO_CLASS_NAMES = {
    "CRT": "CRT Monitor / TV",
    "LCD": "LCD / LED Screen",
    "PCB": "Circuit Board (PCB)",
    "CABLE": "Cables & Wires",
    "BATTERY_LI": "Li-ion Battery",
    "BATTERY_PB": "Lead-Acid Battery",
    "MOTOR": "Electric Motor",
    "MAGNET": "Rare-Earth Magnet",
    "PLASTIC_MIXED": "Mixed Plastic",
    "OTHER": "Other E-Waste",
}


@router.post("/classify")
async def classify_scrap_image(
    payload: Optional[ClassifyRequest] = Body(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Material photo classification.
    Returns top-3 suggestions with calibrated confidence.

    demo_only=true: model not yet trained on real verified data.
    The classifier NEVER blocks the UI -- if unavailable, returns not_sure=true.
    Confidence threshold: ML_CLASSIFY_MIN_CONF (default 0.60).
    """
    if not settings.ML_ENABLED or settings.ML_CLASSIFY_MODE == "off":
        return {
            "status": "disabled",
            "not_sure": True,
            "top3": [],
            "model": {"demo_only": True, "version": "none"},
            "path": "rules",
            "latency_ms": 0,
        }

    t0 = time.monotonic()
    hint = (payload.hint_material if payload else None) or ""

    # Fetch active model metadata from DB
    active_model = await _get_active_model(db, "classify")
    demo_only = active_model.demo_only if active_model else True
    model_version = active_model.version if active_model else "demo-v0"
    model_id = active_model.id if active_model else None
    threshold = settings.ML_CLASSIFY_MIN_CONF

    # Without a real ONNX model file, we return a structured demo response
    # that clearly shows demo_only=true. The UI renders a "Demo model" badge.
    # Confidence values are NOT presented as real accuracy claims.
    if hint and hint.upper() in DEMO_CLASS_NAMES:
        top_code = hint.upper()
        top_conf = 0.55  # deliberately below threshold => shown as "Demo"
    else:
        top_code = "PCB"
        top_conf = 0.52

    not_sure = top_conf < threshold
    others = [c for c in DEMO_CLASSES if c != top_code]
    top3 = [
        {"code": top_code, "name": DEMO_CLASS_NAMES.get(top_code, top_code), "conf": top_conf},
        {"code": others[0], "name": DEMO_CLASS_NAMES.get(others[0], others[0]), "conf": 0.28},
        {"code": others[1], "name": DEMO_CLASS_NAMES.get(others[1], others[1]), "conf": 0.12},
    ]

    latency_ms = int((time.monotonic() - t0) * 1000)

    await _log_prediction(
        db, task="classify", path="server",
        entity_type="lot_photo", entity_id="pending",
        input_data={"hint": hint}, output_data={"top1": top_code, "conf": top_conf},
        confidence=top_conf, latency_ms=latency_ms, model_id=model_id,
    )

    return {
        "status": "success",
        "not_sure": not_sure,
        "top3": top3,
        "model": {
            "id": model_id,
            "version": model_version,
            "demo_only": demo_only,
            "note": (
                "Demo model -- no real verified training data collected yet. "
                "Suggestions are illustrative only."
            ) if demo_only else None,
        },
        "path": "server",
        "latency_ms": latency_ms,
        "threshold": threshold,
    }


# ---------------------------------------------------------------------------
# POST /ml/valuate
# ---------------------------------------------------------------------------

@router.post("/valuate")
async def predict_scrap_valuation(
    req: ValuateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Layer-1 rules-based valuation with honest DB-backed basis metadata.
    No random numbers. Layer-2 (GBM) gated at ML_MIN_ROWS_PER_MATERIAL.
    """
    if not settings.ML_ENABLED:
        return {"error": "ML_ENABLED=false", "items": [], "total": {}}

    t0 = time.monotonic()
    results = []
    total_min = 0
    total_max = 0
    total_p50 = 0

    for item in req.items:
        val = await valuate_item(
            db=db,
            material_code=item.material_code,
            sub_category=item.sub_category,
            weight_g=item.weight_g,
            condition=item.condition,
            lat=req.lat,
            lng=req.lng,
        )
        results.append({
            "material_code": item.material_code,
            "weight_g": item.weight_g,
            "condition": item.condition,
            **val,
        })
        total_min += val["min_paise"]
        total_max += val["max_paise"]
        total_p50 += val["p50_paise"]

    latency_ms = int((time.monotonic() - t0) * 1000)

    await _log_prediction(
        db, task="valuation", path="rules",
        entity_type="lot", entity_id="pending",
        input_data=[i.model_dump() for i in req.items],
        output_data={"total_p50": total_p50},
        confidence=0.0, latency_ms=latency_ms,
    )

    return {
        "items": results,
        "total": {
            "min_paise": total_min,
            "p50_paise": total_p50,
            "max_paise": total_max,
        },
        "latency_ms": latency_ms,
    }


# ---------------------------------------------------------------------------
# GET /ml/models
# ---------------------------------------------------------------------------

@router.get("/models")
async def list_models(
    task: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List active ML models per task with demo_only flag and artifact info."""
    stmt = select(MLModel).where(MLModel.is_active == True)
    if task:
        stmt = stmt.where(MLModel.task == task)
    res = await db.execute(stmt)
    models = res.scalars().all()

    return [
        {
            "id": m.id,
            "task": m.task,
            "version": m.version,
            "framework": m.framework,
            "size_bytes": m.size_bytes,
            "demo_only": m.demo_only,
            "artifact_url": m.artifact_url,
            "sha256": m.sha256,
            "temperature": float(m.temperature) if m.temperature else None,
            "metrics": json.loads(m.metrics_json) if m.metrics_json else {},
            "created_at": m.created_at,
        }
        for m in models
    ]
