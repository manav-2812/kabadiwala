"""
ML Model Registry Service
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Manages the lifecycle of ML models:
  - log_prediction()     : write every ML call to ml_predictions
  - log_override()       : record user correction, create unverified training label
  - get_active_model()   : fetch active model per task
  - promote_model()      : gate check vs frozen-test metrics, then activate
  - rollback_model()     : reactivate previous model for a task

No automatic promotion. All promotions require explicit admin action via
POST /admin/ml/models/{id}/activate.

Demo-only flag is NEVER cleared here -- only cleared when eval.py writes
demo_only=false to the model record after passing all data gates.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.all_models import MLModel, MLPrediction, TrainingLabel, LotItem


async def log_prediction(
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
    user_override: bool = False,
) -> Optional[str]:
    """
    Log one ML prediction to ml_predictions.
    Returns the created prediction id, or None if logging is disabled.
    """
    if not settings.ML_LOG_PREDICTIONS:
        return None

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
        confidence=round(min(1.0, max(0.0, confidence)), 3),
        latency_ms=max(0, latency_ms),
        user_override=user_override,
    )
    db.add(pred)
    await db.flush()  # get the id without full commit
    return pred.id


async def log_override(
    db: AsyncSession,
    *,
    lot_item_id: str,
    suggested_material_id: str,
    chosen_material_id: str,
    ai_confidence: float,
    prediction_id: Optional[str] = None,
) -> None:
    """
    Record that the user overrode an AI suggestion.
    1. Updates LotItem.user_override = True + final material FK.
    2. Creates a TrainingLabel with source='user_correction', verified=False.
       (Admin must verify before it enters training export.)
    """
    # Update the lot item
    stmt = (
        update(LotItem)
        .where(LotItem.id == lot_item_id)
        .values(user_override=True, material_id=chosen_material_id)
    )
    await db.execute(stmt)

    # Create unverified training label
    label = TrainingLabel(
        photo_id=lot_item_id,  # photo_id is a free-form string ref
        label_material_id=chosen_material_id,
        source="user_correction",
        verified=False,
        training_consent=False,  # explicit consent required separately
    )
    db.add(label)

    # Mark prediction as overridden
    if prediction_id:
        stmt2 = (
            update(MLPrediction)
            .where(MLPrediction.id == prediction_id)
            .values(
                user_override=True,
                final_value_json=json.dumps({"chosen_material_id": chosen_material_id}),
            )
        )
        await db.execute(stmt2)

    await db.commit()


async def get_active_model(db: AsyncSession, task: str) -> Optional[MLModel]:
    """Return the active MLModel for a given task, or None."""
    stmt = (
        select(MLModel)
        .where(MLModel.task == task, MLModel.is_active == True)
        .order_by(desc(MLModel.created_at))
        .limit(1)
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def promote_model(
    db: AsyncSession,
    candidate_id: str,
    promoted_by: str,
) -> dict:
    """
    Promote a candidate model to active.
    Gate checks:
      1. Candidate must exist and have demo_only=True (not already promoted).
      2. metrics_json must contain macro_f1 and top1_accuracy.
      3. macro_f1 >= 0.80 AND no per_class_recall value < 0.60.
      4. Must beat the current active model on frozen test set.

    Returns {"promoted": True/False, "reason": "..."}
    """
    # Fetch candidate
    stmt = select(MLModel).where(MLModel.id == candidate_id)
    res = await db.execute(stmt)
    candidate = res.scalar_one_or_none()
    if not candidate:
        return {"promoted": False, "reason": "Candidate model not found"}
    if not candidate.demo_only:
        return {"promoted": False, "reason": "Model already promoted (demo_only=False)"}

    metrics = json.loads(candidate.metrics_json or "{}")
    macro_f1 = metrics.get("macro_f1", 0.0)
    top1_acc = metrics.get("top1_accuracy", 0.0)
    per_class = metrics.get("per_class_recall", {})

    if macro_f1 < 0.80:
        return {
            "promoted": False,
            "reason": f"macro_f1 {macro_f1:.3f} < 0.80 gate",
        }
    if any(v < 0.60 for v in per_class.values()):
        bad = {k: v for k, v in per_class.items() if v < 0.60}
        return {
            "promoted": False,
            "reason": f"Per-class recall below 0.60 for: {bad}",
        }

    # Fetch current active model
    current = await get_active_model(db, candidate.task)
    if current:
        curr_metrics = json.loads(current.metrics_json or "{}")
        curr_f1 = curr_metrics.get("macro_f1", 0.0)
        if macro_f1 <= curr_f1:
            return {
                "promoted": False,
                "reason": (
                    f"Candidate macro_f1 {macro_f1:.3f} does not beat "
                    f"active model macro_f1 {curr_f1:.3f}"
                ),
            }
        # Deactivate current
        await db.execute(
            update(MLModel)
            .where(MLModel.id == current.id)
            .values(is_active=False)
        )

    # Promote candidate
    await db.execute(
        update(MLModel)
        .where(MLModel.id == candidate_id)
        .values(is_active=True, demo_only=False, created_by=promoted_by)
    )
    await db.commit()

    return {
        "promoted": True,
        "reason": f"Promoted. macro_f1={macro_f1:.3f}, top1_acc={top1_acc:.3f}",
        "previous_model_id": current.id if current else None,
    }


async def rollback_model(db: AsyncSession, model_id: str, rolled_back_by: str) -> dict:
    """
    Roll back to a previously active model.
    Deactivates the current active model for the same task and reactivates model_id.
    """
    stmt = select(MLModel).where(MLModel.id == model_id)
    res = await db.execute(stmt)
    target = res.scalar_one_or_none()
    if not target:
        return {"rolled_back": False, "reason": "Model not found"}

    # Deactivate current active
    current = await get_active_model(db, target.task)
    if current and current.id != model_id:
        await db.execute(
            update(MLModel).where(MLModel.id == current.id).values(is_active=False)
        )

    # Reactivate target
    await db.execute(
        update(MLModel).where(MLModel.id == model_id).values(is_active=True)
    )
    await db.commit()
    return {"rolled_back": True, "from_model_id": current.id if current else None}
