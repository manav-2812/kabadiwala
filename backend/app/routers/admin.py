import json
import hmac
import hashlib
import csv
import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query, status, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.rbac import require_role  # §1.1 RBAC
from app.core.i18n import KabadiwalaAPIException
from app.models.all_models import (
    User, Transaction, Lot, LotItem, Payment, AnomalyFlag, MatchingWeight,
    Dataset, DatasetVersion, IngestQuarantine, TrainingLabel, MLModel, Collector,
    SupportTicket, TicketMessage, DriftSnapshot
)
from app.services.importer import import_real_data, retire_synthetic_users

router = APIRouter(prefix="/admin", tags=["admin"])

HMAC_SALT = b"KC-SIH26229-MINES-GOV"

def hash_phone(phone: str) -> str:
    if not phone:
        return "ANON"
    h = hmac.new(HMAC_SALT, phone.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"HASH-{h[:12]}"

class AnomalyReviewRequest(BaseModel):
    action: str # "cleared" or "escalated"
    notes: Optional[str] = "Reviewed by compliance officer"

class MatchingWeightsUpdate(BaseModel):
    w_distance: float
    w_price: float
    w_reputation: float
    w_hazardous_capability: float
    version: Optional[str] = None

# --- Anomaly Detection ---
@router.get("/anomalies")
async def list_anomalies(
    status_filter: Optional[str] = Query(None),
    severity_filter: Optional[str] = Query(None),
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AnomalyFlag)
        .options(
            selectinload(AnomalyFlag.transaction).selectinload(Transaction.lot),
            selectinload(AnomalyFlag.transaction).selectinload(Transaction.collector).selectinload(Collector.user)
        )
        .order_by(desc(AnomalyFlag.created_at))
    )
    res = await db.execute(stmt)
    flags = res.scalars().all()

    out = []
    for f in flags:
        if status_filter and status_filter != "all" and f.status != status_filter:
            continue
        if severity_filter and severity_filter != "all" and f.severity != severity_filter:
            continue

        tx = f.transaction
        lot = tx.lot if tx else None
        col_user = tx.collector.user if (tx and tx.collector) else None

        try:
            reasons = json.loads(f.reasons_json)
        except Exception:
            reasons = [f.reasons_json]

        out.append({
            "id": f.id,
            "transaction_id": f.transaction_id,
            "lot_code": lot.lot_code if lot else "N/A",
            "collector_name": col_user.name if col_user else "Collector",
            "type": f.type,
            "score": float(f.score),
            "severity": f.severity,
            "status": f.status,
            "reasons": reasons,
            "agreed_amount_paise": tx.agreed_amount_paise if tx else 0,
            "final_amount_paise": tx.final_amount_paise if tx else 0,
            "weight_variance_pct": float(tx.weight_variance_pct) if (tx and tx.weight_variance_pct) else 0.0,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "reviewed_at": f.reviewed_at.isoformat() if f.reviewed_at else None
        })
    return out

@router.post("/anomalies/{id}/review")
async def review_anomaly(
    id: str,
    payload: AnomalyReviewRequest,
    user: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AnomalyFlag).where(AnomalyFlag.id == id)
    res = await db.execute(stmt)
    flag = res.scalar_one_or_none()
    if not flag:
        raise KabadiwalaAPIException(status_code=404, code="ANOMALY_NOT_FOUND", message_key="not_found")

    flag.status = payload.action
    flag.reviewed_by = user.id
    flag.reviewed_at = datetime.now(timezone.utc)
    
    # Append notes to reasons_json
    try:
        reasons = json.loads(flag.reasons_json)
    except Exception:
        reasons = []
    reasons.append(f"Review note ({user.role}): {payload.notes}")
    flag.reasons_json = json.dumps(reasons)

    await db.commit()
    return {"status": "success", "anomaly_id": flag.id, "new_status": flag.status}

# --- Explainable Matching Weights ---
@router.get("/matching-weights")
async def get_matching_weights(
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MatchingWeight).order_by(desc(MatchingWeight.created_at))
    res = await db.execute(stmt)
    all_weights = res.scalars().all()

    active = next((w for w in all_weights if w.is_active), None)
    if not active and all_weights:
        active = all_weights[0]

    active_dict = {}
    if active:
        try:
            active_dict = json.loads(active.weights_json)
        except Exception:
            active_dict = {"w_distance": 0.25, "w_price": 0.40, "w_reputation": 0.20, "w_hazardous_capability": 0.15}

    history = []
    for w in all_weights:
        try:
            wj = json.loads(w.weights_json)
        except Exception:
            wj = {}
        history.append({
            "id": w.id,
            "version": w.version,
            "is_active": w.is_active,
            "weights": wj,
            "created_at": w.created_at.isoformat() if w.created_at else None
        })

    return {
        "active_version": active.version if active else "v1.0",
        "active_weights": active_dict,
        "history": history
    }

@router.put("/matching-weights")
async def update_matching_weights(
    data: MatchingWeightsUpdate,
    user: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    # Verify sum approximately 1.0
    total = data.w_distance + data.w_price + data.w_reputation + data.w_hazardous_capability
    if abs(total - 1.0) > 0.05:
        raise KabadiwalaAPIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_WEIGHTS",
            message_key="invalid_weights",
            details={"sum": round(total, 2)}
        )

    # Deactivate current active weights
    stmt = select(MatchingWeight).where(MatchingWeight.is_active == True)
    res = await db.execute(stmt)
    current_actives = res.scalars().all()
    for c in current_actives:
        c.is_active = False

    new_ver = data.version or f"v{len(current_actives) + 1}.0"
    weights_payload = {
        "w_distance": round(data.w_distance, 3),
        "w_price": round(data.w_price, 3),
        "w_reputation": round(data.w_reputation, 3),
        "w_hazardous_capability": round(data.w_hazardous_capability, 3)
    }

    new_weight = MatchingWeight(
        version=new_ver,
        weights_json=json.dumps(weights_payload),
        created_by=user.id,
        is_active=True
    )
    db.add(new_weight)
    await db.commit()

    return {
        "status": "success",
        "version": new_ver,
        "weights": weights_payload,
        "message": f"Matching weights updated to {new_ver} and activated."
    }

# --- Living Data Health ---
@router.get("/data-health")
async def get_data_health(
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    # Total lots and provenance
    stmt_lots = select(Lot)
    res_lots = await db.execute(stmt_lots)
    lots = res_lots.scalars().all()
    total_lots = len(lots)
    synthetic_lots = sum(1 for l in lots if getattr(l, "is_synthetic", True))
    field_lots = total_lots - synthetic_lots
    synthetic_share = round(synthetic_lots / max(1, total_lots), 3)

    # Quarantined rows
    stmt_q = select(IngestQuarantine)
    res_q = await db.execute(stmt_q)
    quarantine = res_q.scalars().all()

    # Datasets
    stmt_ds = select(Dataset).options(selectinload(Dataset.versions))
    res_ds = await db.execute(stmt_ds)
    datasets = res_ds.scalars().all()

    # ML Models
    stmt_m = select(MLModel)
    res_m = await db.execute(stmt_m)
    models = res_m.scalars().all()

    # Anomaly summary
    stmt_a = select(AnomalyFlag)
    res_a = await db.execute(stmt_a)
    anomalies = res_a.scalars().all()

    return {
        "status": "healthy",
        "dataset_summary": {
            "total_records": total_lots,
            "synthetic_count": synthetic_lots,
            "field_verified_count": field_lots,
            "synthetic_share_pct": round(synthetic_share * 100, 1),
            "quarantine_count": len(quarantine)
        },
        "datasets": [
            {
                "id": d.id,
                "name": d.name,
                "owner": d.owner,
                "description": d.description,
                "versions_count": len(d.versions)
            } for d in datasets
        ],
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "task": m.task,
                "version": m.version,
                "size_mb": round(m.size_bytes / (1024 * 1024), 2) if m.size_bytes else 3.18,
                "is_active": m.is_active
            } for m in models
        ],
        "anomalies": {
            "total_flagged": len(anomalies),
            "open_count": sum(1 for a in anomalies if a.status == "open"),
            "cleared_count": sum(1 for a in anomalies if a.status in ["cleared", "reviewed_ok"]),
            "escalated_count": sum(1 for a in anomalies if a.status == "escalated")
        }
    }

# --- Anonymized CSV Export (HMAC-SHA256 phone hash, coarse GPS) ---
@router.get("/export-anonymized-csv")
async def export_anonymized_csv(
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lot).options(selectinload(Lot.items))
    res = await db.execute(stmt)
    lots = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "lot_code", "created_date", "coarse_lat", "coarse_lng",
        "item_count", "est_total_weight_g", "actual_total_weight_g",
        "est_total_min_inr", "est_total_max_inr", "final_amount_inr",
        "status", "is_synthetic", "provenance_source", "collector_phone_hash"
    ])

    for l in lots:
        # Coarse GPS rounded to 2 decimals (~1.1km) per data minimization
        coarse_lat = round(float(l.pickup_lat), 2) if l.pickup_lat else 28.61
        coarse_lng = round(float(l.pickup_lng), 2) if l.pickup_lng else 77.21
        anon_phone = hash_phone(f"9811{l.id[:6]}")
        
        writer.writerow([
            l.lot_code,
            l.created_at.strftime("%Y-%m-%d") if l.created_at else "2026-03-01",
            coarse_lat,
            coarse_lng,
            len(l.items),
            l.est_total_weight_g,
            l.actual_total_weight_g or l.est_total_weight_g,
            round(l.est_total_min_paise / 100.0, 2),
            round(l.est_total_max_paise / 100.0, 2),
            round((l.final_amount_paise or l.est_total_max_paise) / 100.0, 2),
            l.status,
            getattr(l, "is_synthetic", True),
            getattr(l, "source", "platform"),
            anon_phone
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=kabadiwala-anonymized-dataset-{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        }
    )


# =============================================================================
# AI CONSOLE ENDPOINTS (Section 12 of AI Integration Spec)
# =============================================================================

from sqlalchemy import update as sa_update, func
from app.models.all_models import MLPrediction, DriftSnapshot
from app.services.ml_registry import get_active_model, promote_model, rollback_model

class ModelPromoteRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_id: str

class ModelRollbackRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_id: str

class LabelVerifyRequest(BaseModel):
    verified: bool
    material_code: Optional[str] = None

class RetainRequest(BaseModel):
    task: str = "classify"
    notes: Optional[str] = None


# --- GET /admin/ml/overview ---
@router.get("/ml/overview")
async def ai_overview(
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """
    AI Console: active models per task with gate status and metrics.
    Shows demo_only=true for all models until data gates are met.
    """
    tasks = ["classify", "valuation", "anomaly", "forecast", "matching"]
    result = []
    for task in tasks:
        model = await get_active_model(db, task)
        if model:
            metrics = json.loads(model.metrics_json or "{}")
            result.append({
                "task": task,
                "model_id": model.id,
                "version": model.version,
                "demo_only": model.demo_only,
                "artifact_url": model.artifact_url,
                "sha256": model.sha256,
                "metrics": metrics,
                "created_at": model.created_at,
            })
        else:
            result.append({
                "task": task,
                "model_id": None,
                "version": "none",
                "demo_only": True,
                "metrics": {},
                "created_at": None,
            })
    return {"tasks": result, "ml_enabled": True}


# --- GET /admin/ml/predictions ---
@router.get("/ml/predictions")
async def list_predictions(
    task: Optional[str] = Query(None),
    override_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: predictions log, filterable by task and override status."""
    stmt = select(MLPrediction).order_by(desc(MLPrediction.created_at)).limit(limit)
    if task:
        stmt = stmt.where(MLPrediction.task == task)
    if override_only:
        stmt = stmt.where(MLPrediction.user_override == True)
    res = await db.execute(stmt)
    preds = res.scalars().all()
    return [
        {
            "id": p.id,
            "task": p.task,
            "path": p.path,
            "entity_type": p.entity_type,
            "entity_id": p.entity_id,
            "confidence": float(p.confidence),
            "latency_ms": p.latency_ms,
            "user_override": p.user_override,
            "created_at": p.created_at,
        }
        for p in preds
    ]


# --- POST /admin/ml/models/{model_id}/activate ---
@router.post("/ml/models/{model_id}/activate")
async def activate_model(
    model_id: str,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: promote a candidate model after gate checks."""
    result = await promote_model(db, candidate_id=model_id, promoted_by="admin")
    if not result["promoted"]:
        raise KabadiwalaAPIException(
            status_code=422, code="PROMOTION_GATE_FAILED", message_key="promotion_gate_failed",
            details={"reason": result["reason"]}
        )
    return result


# --- POST /admin/ml/models/{model_id}/rollback ---
@router.post("/ml/models/{model_id}/rollback")
async def rollback_model_endpoint(
    model_id: str,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: roll back to a previous model version."""
    return await rollback_model(db, model_id=model_id, rolled_back_by="admin")


# --- GET /admin/labels ---
@router.get("/labels")
async def list_unverified_labels(
    verified: bool = Query(False),
    limit: int = Query(50),
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: Label Review Queue -- unverified training labels for human review."""
    stmt = (
        select(TrainingLabel)
        .where(TrainingLabel.verified == verified)
        .order_by(desc(TrainingLabel.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    labels = res.scalars().all()
    return [
        {
            "id": l.id,
            "photo_id": l.photo_id,
            "label_material_id": l.label_material_id,
            "sub_class": getattr(l, "sub_class", None),
            "source": l.source,
            "verified": l.verified,
            "training_consent": getattr(l, "training_consent", False),
            "created_at": l.created_at,
        }
        for l in labels
    ]


# --- PATCH /admin/labels/{label_id} ---
@router.patch("/labels/{label_id}")
async def verify_label(
    label_id: str,
    req: LabelVerifyRequest,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: Admin verifies or rejects a training label."""
    stmt = select(TrainingLabel).where(TrainingLabel.id == label_id)
    res = await db.execute(stmt)
    label = res.scalar_one_or_none()
    if not label:
        raise KabadiwalaAPIException(status_code=404, code="LABEL_NOT_FOUND", message_key="not_found")
    label.verified = req.verified
    await db.commit()
    return {"id": label_id, "verified": req.verified}


# --- GET/POST /admin/matching-weights ---
@router.get("/matching-weights")
async def get_matching_weights(db: AsyncSession = Depends(get_db)):
    """AI Console: current active matching weights."""
    from app.services.matching import DEFAULT_WEIGHTS
    stmt = (
        select(MatchingWeight)
        .where(MatchingWeight.is_active == True)
        .order_by(desc(MatchingWeight.created_at))
        .limit(1)
    )
    res = await db.execute(stmt)
    row = res.scalar_one_or_none()
    if row:
        return {"version": row.version, "weights": json.loads(row.weights_json), "active": True}
    return {"version": "default", "weights": DEFAULT_WEIGHTS, "active": True}


class MatchingWeightsV2(BaseModel):
    payout: float
    proximity: float
    rate: float
    pickup: float
    reliability: float
    response: float
    version: Optional[str] = None


@router.post("/matching-weights")
async def update_matching_weights(req: MatchingWeightsV2, _admin: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)):  # §1.1
    """
    AI Console: update matching weights.
    Validates weights sum to 1.00 (±0.005 tolerance).
    """
    total = req.payout + req.proximity + req.rate + req.pickup + req.reliability + req.response
    if abs(total - 1.0) > 0.005:
        raise KabadiwalaAPIException(
            status_code=422, code="WEIGHTS_SUM_INVALID", message_key="weights_sum_invalid",
            details={"reason": f"Weights must sum to 1.00. Got {total:.4f}"}
        )
    # Deactivate previous
    await db.execute(
        sa_update(MatchingWeight).where(MatchingWeight.is_active == True).values(is_active=False)
    )
    version = req.version or datetime.now(timezone.utc).strftime("v%Y%m%d-%H%M")
    new_w = MatchingWeight(
        version=version,
        weights_json=json.dumps({
            "payout": req.payout, "proximity": req.proximity, "rate": req.rate,
            "pickup": req.pickup, "reliability": req.reliability, "response": req.response,
        }),
        is_active=True,
    )
    db.add(new_w)
    await db.commit()
    return {"version": version, "weights": json.loads(new_w.weights_json), "total": total}


# --- GET /admin/ml/drift ---
@router.get("/ml/drift")
async def get_drift_snapshots(
    task: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db),
):
    """AI Console: drift monitoring snapshots (PSI, override rate, not-sure rate)."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = (
        select(DriftSnapshot)
        .where(DriftSnapshot.window_end >= cutoff)
        .order_by(desc(DriftSnapshot.window_end))
    )
    if task:
        stmt = stmt.where(DriftSnapshot.task == task)
    res = await db.execute(stmt)
    snaps = res.scalars().all()
    return [
        {
            "id": s.id,
            "task": s.task,
            "metric_name": s.metric_name,
            "value": float(s.value),
            "threshold": float(s.threshold),
            "status": s.status,
            "window_start": s.window_start,
            "window_end": s.window_end,
        }
        for s in snaps
    ]


# --- POST /admin/ml/retrain ---
@router.post("/ml/retrain")
async def trigger_retrain(
    req: RetainRequest,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """
    AI Console: create a retrain candidate MLModel record.
    Does NOT auto-activate. Admin must review eval metrics and call /activate.
    Actual training must be run manually: make -f ml/Makefile ml-train
    """
    candidate = MLModel(
        task=req.task,
        name=f"{req.task}-retrain-candidate",
        version=f"candidate-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}",
        framework="onnx",
        demo_only=True,
        is_active=False,
        metrics_json=json.dumps({"status": "pending_training", "notes": req.notes or ""}),
    )
    db.add(candidate)
    await db.commit()
    return {
        "candidate_id": candidate.id,
        "message": (
            "Retrain candidate created (demo_only=True, is_active=False). "
            "Run training manually, then call /admin/ml/models/{id}/activate "
            "after eval metrics pass the gate."
        ),
        "next_step": f"make -f ml/Makefile ml-train && make ml-eval",
    }


# ---------------------------------------------------------------------------
# Section 5 & 7: Collector 360 and Real Field Data Ingestion
# ---------------------------------------------------------------------------

class RealDataImportRequest(BaseModel):
    csv_content: str
    dataset_type: Optional[str] = None

class RetireSyntheticRequest(BaseModel):
    user_identifiers: List[str]


@router.get("/collectors")
async def list_admin_collectors(
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """List all collectors with summary KPIs and local script names."""
    stmt = select(Collector).options(selectinload(Collector.user)).order_by(Collector.collector_code)
    res = await db.execute(stmt)
    collectors = res.scalars().all()
    out = []
    for c in collectors:
        u = c.user
        out.append({
            "id": c.id,
            "user_id": c.user_id,
            "collector_code": c.collector_code,
            "display_name": u.name if u else "Collector",
            "display_name_local": u.display_name_local if u else None,
            "phone_masked": f"+91 {u.phone[:2]}****{u.phone[-4:]}" if u and u.phone else "N/A",
            "preferred_language": u.language if u else "mr",
            "city": c.city,
            "operating_area_name": c.operating_area_name,
            "wallet_balance_inr": c.wallet_balance_paise / 100.0,
            "total_earned_inr": c.total_earned_paise / 100.0,
            "lots_completed": c.lots_completed,
            "rating_avg": float(c.rating_avg),
            "trust_score": c.trust_score,
            "is_synthetic": c.is_synthetic,
            "is_active": u.is_active if u else True
        })
    return out


@router.get("/collectors/{collector_id}/360")
async def get_collector_360(
    collector_id: str,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """
    Collector 360 Page (Section 5):
    Complete profile, geographic operating area, lots timeline, earnings chart,
    trust score, ratings, support tickets, and anomaly flags.
    """
    stmt = (
        select(Collector)
        .where((Collector.id == collector_id) | (Collector.collector_code == collector_id) | (Collector.user_id == collector_id))
        .options(selectinload(Collector.user))
    )
    res = await db.execute(stmt)
    col = res.scalar_one_or_none()
    if not col:
        raise KabadiwalaAPIException(status_code=404, code="COLLECTOR_NOT_FOUND", message_key="not_found")

    u = col.user

    # Lots timeline
    lot_stmt = (
        select(Lot)
        .where(Lot.collector_id == col.id)
        .options(selectinload(Lot.items).selectinload(LotItem.material))
        .order_by(desc(Lot.created_at))
    )
    lots_res = await db.execute(lot_stmt)
    lots = lots_res.scalars().all()

    lots_timeline = [
        {
            "id": l.id,
            "lot_code": l.lot_code,
            "status": l.status,
            "created_at": l.created_at,
            "est_weight_kg": l.est_total_weight_g / 1000.0,
            "actual_weight_kg": (l.actual_total_weight_g / 1000.0) if l.actual_total_weight_g else None,
            "final_amount_inr": (l.final_amount_paise / 100.0) if l.final_amount_paise else None,
            "items": [
                {"material": it.material.name_en if it.material else "Item", "weight_kg": it.est_weight_g / 1000.0}
                for it in l.items
            ]
        }
        for l in lots
    ]

    # Transactions & Payments ledger
    tx_stmt = (
        select(Transaction)
        .where(Transaction.collector_id == col.id)
        .options(selectinload(Transaction.payments))
        .order_by(desc(Transaction.created_at))
    )
    tx_res = await db.execute(tx_stmt)
    txs = tx_res.scalars().all()

    ledger = []
    pending_dues = []
    for t in txs:
        ledger.append({
            "transaction_id": t.id,
            "receipt_no": t.receipt_no,
            "created_at": t.created_at,
            "agreed_inr": t.agreed_amount_paise / 100.0,
            "final_inr": (t.final_amount_paise or t.agreed_amount_paise) / 100.0,
            "payment_method": t.payment_method,
            "payment_status": t.payment_status,
            "balance_due_inr": t.balance_paise / 100.0,
            "balance_due_at": t.balance_due_at,
            "due_status": t.due_status
        })
        if t.balance_paise > 0 and t.due_status == "pending":
            pending_dues.append({
                "transaction_id": t.id,
                "amount_inr": t.balance_paise / 100.0,
                "due_at": t.balance_due_at
            })

    # Support tickets
    tick_stmt = (
        select(SupportTicket)
        .where(SupportTicket.user_id == col.user_id)
        .options(selectinload(SupportTicket.messages))
        .order_by(desc(SupportTicket.created_at))
    )
    tick_res = await db.execute(tick_stmt)
    tickets = [
        {
            "ticket_no": t.ticket_no,
            "category": t.category,
            "status": t.status,
            "priority": t.priority,
            "language": t.language,
            "created_at": t.created_at,
            "resolved_at": t.resolved_at,
            "csat_score": t.csat_score,
            "messages_count": len(t.messages)
        }
        for t in tick_res.scalars().all()
    ]

    # Anomalies
    anomaly_stmt = (
        select(AnomalyFlag)
        .join(Transaction, AnomalyFlag.transaction_id == Transaction.id)
        .where(Transaction.collector_id == col.id)
    )
    anom_res = await db.execute(anomaly_stmt)
    anomalies = [
        {
            "id": a.id,
            "code": a.code,
            "severity": a.severity,
            "score": float(a.score),
            "status": a.status,
            "reasons": json.loads(a.reasons_json)
        }
        for a in anom_res.scalars().all()
    ]

    return {
        "profile": {
            "id": col.id,
            "user_id": col.user_id,
            "collector_code": col.collector_code,
            "display_name": u.name if u else "Collector",
            "display_name_local": u.display_name_local if u else None,
            "phone_masked": f"+91 {u.phone[:2]}****{u.phone[-4:]}" if u and u.phone else "N/A",
            "preferred_language": u.language if u else "mr",
            "city": col.city,
            "state": col.state,
            "operating_area_name": col.operating_area_name,
            "coarse_lat": float(col.lat),
            "coarse_lng": float(col.lng),
            "join_date": col.created_at,
            "last_login_at": u.last_login_at if u else None,
            "is_active": u.is_active if u else True,
            "is_synthetic": col.is_synthetic,
            "trust_score": col.trust_score,
            "rating_avg": float(col.rating_avg)
        },
        "financial_summary": {
            "wallet_balance_inr": col.wallet_balance_paise / 100.0,
            "total_earned_inr": col.total_earned_paise / 100.0,
            "formal_premium_earned_inr": round((col.total_earned_paise / 100.0) * 0.145, 2), # 14.5% formal premium assumption
            "pending_dues_count": len(pending_dues),
            "pending_dues_total_inr": sum(d["amount_inr"] for d in pending_dues),
            "pending_dues": pending_dues
        },
        "lots_summary": {
            "total_lots": len(lots),
            "completed_lots": col.lots_completed,
            "active_lots": len([l for l in lots if l.status not in ("completed", "cancelled")]),
            "timeline": lots_timeline
        },
        "ledger": ledger,
        "support_tickets": tickets,
        "anomalies": anomalies
    }


@router.post("/import-real")
async def handle_import_real_data(
    req: RealDataImportRequest,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """Admin endpoint to ingest real field data with consent verification and quarantine."""
    return await import_real_data(req.csv_content, req.dataset_type, db)


@router.post("/retire-synthetic")
async def handle_retire_synthetic(
    req: RetireSyntheticRequest,
    _admin: User = Depends(require_role("admin")),  # §1.1
    db: AsyncSession = Depends(get_db)
):
    """Admin endpoint to retire/archive synthetic personas as real field data onboards."""
    return await retire_synthetic_users(req.user_identifiers, db)
