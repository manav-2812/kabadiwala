"""
Recyclers Router
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

GET /recyclers/nearby -- ranked list with 6-weight score, reason codes,
                         distance_km, weights_version, impression logged.
"""
from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.all_models import Lot, MatchingWeight, MLPrediction, Recycler
from app.services.matching import DEFAULT_WEIGHTS, rank_recyclers_for_lot

router = APIRouter(prefix="/recyclers", tags=["recyclers"])


async def _load_active_weights(db: AsyncSession):
    """Load the active MatchingWeight row from DB, or fall back to defaults."""
    stmt = (
        select(MatchingWeight)
        .where(MatchingWeight.is_active == True)
        .order_by(desc(MatchingWeight.created_at))
        .limit(1)
    )
    res = await db.execute(stmt)
    row = res.scalar_one_or_none()
    if row:
        try:
            w = json.loads(row.weights_json)
            return w, row.version
        except Exception:
            pass
    return DEFAULT_WEIGHTS, "default"


@router.get("/nearby")
async def get_nearby_recyclers(
    lat: float = Query(28.6139),
    lng: float = Query(77.2090),
    lot_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns recyclers ranked by 6-factor explainable score.
    Hard filters: authorization_status=verified AND license_valid_to >= now.
    Impressions logged to ml_predictions for future ranker training.
    """
    lot_est = 250000  # default 2,500 rupees
    lot_materials = []
    if lot_id:
        stmt_lot = select(Lot).where(Lot.id == lot_id)
        res_lot = await db.execute(stmt_lot)
        lot = res_lot.scalar_one_or_none()
        if lot:
            lot_est = lot.est_total_max_paise or 250000

    # Load weights from DB (admin-editable, versioned)
    weights, weights_version = await _load_active_weights(db)

    stmt_r = select(Recycler)
    res_r = await db.execute(stmt_r)
    recyclers = list(res_r.scalars().all())

    ranked = rank_recyclers_for_lot(
        collector_lat=lat,
        collector_lng=lng,
        lot_est_paise=lot_est,
        lot_materials=lot_materials,
        recyclers=recyclers,
        weights=weights,
        weights_version=weights_version,
    )

    # Log impression to ml_predictions (for future learning-to-rank)
    if settings.ML_LOG_PREDICTIONS and ranked:
        impression_data = [
            {"id": r["id"], "score": r["ranking_score"], "reasons": r["reasons"]}
            for r in ranked[:5]
        ]
        input_hash = hashlib.sha256(
            json.dumps({"lat": lat, "lng": lng, "lot_id": lot_id}).encode()
        ).hexdigest()
        pred = MLPrediction(
            model_id=None,
            task="matching",
            path="rules",
            entity_type="lot",
            entity_id=lot_id or "none",
            input_hash=input_hash,
            output_json=json.dumps(impression_data),
            confidence=0.0,
            latency_ms=0,
        )
        db.add(pred)
        await db.commit()

    # Flatten to response-friendly dicts (include reasons + weights_version)
    return [
        {
            "id": r["id"],
            "company_name": r["company_name"],
            "contact_person": r["contact_person"],
            "address": r["address"],
            "city": r["city"],
            "lat": r["lat"],
            "lng": r["lng"],
            "distance_km": r["distance_km"],
            "cpcb_license_no": r["cpcb_license_no"],
            "spcb_authorization_no": r["spcb_authorization_no"],
            "license_valid_to": r.get("license_valid_to"),
            "authorization_status": r["authorization_status"],
            "rating_avg": r["rating_avg"],
            "reliability_score": r["reliability_score"],
            "pickup_available": r["pickup_available"],
            "estimated_payout_paise": r["estimated_payout_paise"],
            "ranking_score": r["ranking_score"],
            "reasons": r["reasons"],
            "weights_version": r["weights_version"],
        }
        for r in ranked
    ]
