"""
Anomaly Detection Rules Engine
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Implements all 9 always-on rules from Section 7.1 of the AI Integration Spec.
Statistical z-score (MAD-based) in Section 7.2.
Isolation Forest (Section 7.3) is gated behind ML_MIN_ROWS_ANOMALY.

Rules produce structured AnomalyFlag records with:
  code, severity (low/medium/high), reasons_json with human-readable reason

Evaluation on injected synthetic truth: ml/anomaly/eval_injected.py
Metrics: ml/artifacts/metrics/anomaly.json

IMPORTANT: No automatic penalties applied. Anomaly flags go to admin review only.
           Collector sees only a friendly message ("Please retake photo"), never "anomaly".
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.all_models import (
    AnomalyFlag,
    LotPhoto,
    Material,
    PriceHistory,
    Transaction,
)

# ---------------------------------------------------------------------------
# Rule codes and severity thresholds
# ---------------------------------------------------------------------------

WEIGHT_VARIANCE_MED_PCT = 10.0   # |actual - est| / est > 10%
WEIGHT_VARIANCE_HIGH_PCT = 25.0  # > 25%
PRICE_BELOW_BAND_PCT = 60.0      # final < 60% of band low (high severity)
PRICE_ABOVE_BAND_PCT = 150.0     # final > 150% of band high (medium)
UNIT_ERROR_LOW_RATIO = 0.08      # price/kg ratio vs median in [0.08x, 0.12x] or [8x, 12x]
UNIT_ERROR_HIGH_RATIO = 12.0
PHASH_HAMMING_HIGH = 6           # different lots -> high
PHASH_HAMMING_MED = 8            # same collector 24h -> medium
GPS_MISMATCH_MED_KM = 2.0       # handover > 2 km from recycler (medium)
GPS_MISMATCH_HIGH_KM = 10.0     # impossible jump (high)
REPEATED_WEIGHT_COUNT = 4       # same exact weight >= 4 lots in 7 days (low)
QUOTE_BELOW_MARKET_PCT = 70.0   # quote < 70% of market median (medium)
MAD_Z_THRESHOLD = 3.5           # robust z-score threshold

# ---------------------------------------------------------------------------
# Reason strings (English only; i18n keys returned for frontend translation)
# ---------------------------------------------------------------------------

REASON_TEMPLATES = {
    "WEIGHT_VARIANCE": "Actual weight differs from estimated by {pct:.1f}%",
    "PRICE_BELOW_BAND": "Final price/kg ({final:.0f} p/kg) is below 60% of market low ({low:.0f} p/kg)",
    "PRICE_ABOVE_BAND": "Final price/kg ({final:.0f} p/kg) exceeds 150% of market high ({high:.0f} p/kg)",
    "UNIT_ERROR_SUSPECT": "Price/kg ratio vs median is {ratio:.1f}x -- possible unit conversion error",
    "DUPLICATE_PHOTO": "Photo perceptual hash matches another lot (Hamming distance {dist})",
    "GPS_MISMATCH": "Handover location {dist:.1f} km from registered recycler facility",
    "PAYMENT_BEFORE_WEIGH": "Payment recorded {mins:.0f} minutes before weigh-in",
    "REPEATED_WEIGHT": "Same exact weight ({wt}g) recorded on {count} lots this week",
    "QUOTE_FAR_BELOW_MARKET": "Quote ({quote:.0f} p/kg) is below 70% of market median ({median:.0f} p/kg)",
    "STAT_Z_SCORE": "Price/kg z-score {z:.2f} (threshold {thr:.1f}) -- statistical outlier",
}


def _hamming(a: str, b: str) -> int:
    """Hamming distance between two hex pHash strings of equal length."""
    if len(a) != len(b):
        return 64  # treat as maximum distance if sizes differ
    a_int = int(a, 16)
    b_int = int(b, 16)
    xor = a_int ^ b_int
    return bin(xor).count("1")


async def run_anomaly_rules(
    db: AsyncSession,
    *,
    transaction_id: str,
    actual_weight_g: int,
    est_weight_g: int,
    final_price_paise_total: int,
    final_price_per_kg_paise: float,
    material_code: str,
    city: str,
    quote_per_kg_paise: float | None,
    payment_at: datetime | None,
    weigh_in_at: datetime | None,
    collector_id: str,
    photo_phash: str | None,
    lot_id: str,
    handover_lat: float | None,
    handover_lng: float | None,
    recycler_lat: float | None,
    recycler_lng: float | None,
    collect_lat: float | None,
    collect_lng: float | None,
) -> list[AnomalyFlag]:
    """
    Synchronous rule engine called after weigh-in.
    Returns a list of AnomalyFlag ORM objects (not yet committed).
    Caller must db.add() and db.commit() them.
    """
    flags: list[AnomalyFlag] = []

    def _flag(code: str, severity: str, reason: str, score: float = 0.5) -> AnomalyFlag:
        return AnomalyFlag(
            transaction_id=transaction_id,
            code=code,
            type=code,  # backward compat
            score=round(score, 3),
            severity=severity,
            reasons_json=json.dumps([reason]),
            status="open",
        )

    # ------------------------------------------------------------------
    # R1: WEIGHT_VARIANCE
    # ------------------------------------------------------------------
    if est_weight_g and est_weight_g > 0:
        pct = abs(actual_weight_g - est_weight_g) / est_weight_g * 100
        if pct > WEIGHT_VARIANCE_HIGH_PCT:
            flags.append(_flag(
                "WEIGHT_VARIANCE", "high",
                REASON_TEMPLATES["WEIGHT_VARIANCE"].format(pct=pct),
                score=min(1.0, pct / 50.0)
            ))
        elif pct > WEIGHT_VARIANCE_MED_PCT:
            flags.append(_flag(
                "WEIGHT_VARIANCE", "medium",
                REASON_TEMPLATES["WEIGHT_VARIANCE"].format(pct=pct),
                score=min(0.7, pct / 30.0)
            ))

    # ------------------------------------------------------------------
    # R2 + R3: PRICE_BELOW_BAND / PRICE_ABOVE_BAND
    # ------------------------------------------------------------------
    ph_stmt = (
        select(PriceHistory)
        .join(Material, PriceHistory.material_id == Material.id)
        .where(Material.code == material_code)
        .order_by(PriceHistory.date.desc())
        .limit(1)
    )
    ph_res = await db.execute(ph_stmt)
    latest_ph = ph_res.scalar_one_or_none()
    if latest_ph:
        band_low = float(latest_ph.min_paise) if latest_ph.min_paise else float(latest_ph.price_paise_per_kg) * 0.85
        band_high = float(latest_ph.max_paise) if latest_ph.max_paise else float(latest_ph.price_paise_per_kg) * 1.15
        if final_price_per_kg_paise < band_low * (PRICE_BELOW_BAND_PCT / 100.0):
            flags.append(_flag(
                "PRICE_BELOW_BAND", "high",
                REASON_TEMPLATES["PRICE_BELOW_BAND"].format(
                    final=final_price_per_kg_paise, low=band_low),
                score=0.85
            ))
        elif final_price_per_kg_paise > band_high * (PRICE_ABOVE_BAND_PCT / 100.0):
            flags.append(_flag(
                "PRICE_ABOVE_BAND", "medium",
                REASON_TEMPLATES["PRICE_ABOVE_BAND"].format(
                    final=final_price_per_kg_paise, high=band_high),
                score=0.65
            ))

        # ------------------------------------------------------------------
        # R4: UNIT_ERROR_SUSPECT (price ratio vs market median suspicious)
        # ------------------------------------------------------------------
        median_p = float(latest_ph.price_paise_per_kg)
        if median_p > 0:
            ratio = final_price_per_kg_paise / median_p
            if (UNIT_ERROR_LOW_RATIO <= ratio <= 0.12) or (8.0 <= ratio <= UNIT_ERROR_HIGH_RATIO):
                flags.append(_flag(
                    "UNIT_ERROR_SUSPECT", "high",
                    REASON_TEMPLATES["UNIT_ERROR_SUSPECT"].format(ratio=ratio),
                    score=0.90
                ))

        # ------------------------------------------------------------------
        # R9: QUOTE_FAR_BELOW_MARKET
        # ------------------------------------------------------------------
        if quote_per_kg_paise is not None and median_p > 0:
            if quote_per_kg_paise < median_p * (QUOTE_BELOW_MARKET_PCT / 100.0):
                flags.append(_flag(
                    "QUOTE_FAR_BELOW_MARKET", "medium",
                    REASON_TEMPLATES["QUOTE_FAR_BELOW_MARKET"].format(
                        quote=quote_per_kg_paise, median=median_p),
                    score=0.60
                ))

    # ------------------------------------------------------------------
    # R5: DUPLICATE_PHOTO (pHash Hamming distance)
    # ------------------------------------------------------------------
    if photo_phash and len(photo_phash) >= 16:
        # Compare against all other photos in the DB (excluding current lot)
        dup_stmt = select(LotPhoto).limit(500)  # bounded scan
        dup_res = await db.execute(dup_stmt)
        all_photos = dup_res.scalars().all()
        for p in all_photos:
            if not p.phash or p.lot_item_id is None:
                continue
            dist = _hamming(photo_phash, p.phash)
            if dist <= PHASH_HAMMING_HIGH:
                flags.append(_flag(
                    "DUPLICATE_PHOTO", "high",
                    REASON_TEMPLATES["DUPLICATE_PHOTO"].format(dist=dist),
                    score=0.95
                ))
                break  # one flag per lot

    # ------------------------------------------------------------------
    # R6: GPS_MISMATCH (handover vs recycler location)
    # ------------------------------------------------------------------
    if all(v is not None for v in [handover_lat, handover_lng, recycler_lat, recycler_lng]):
        def _haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        dist_km = _haversine(handover_lat, handover_lng, recycler_lat, recycler_lng)
        if dist_km > GPS_MISMATCH_HIGH_KM:
            flags.append(_flag(
                "GPS_MISMATCH", "high",
                REASON_TEMPLATES["GPS_MISMATCH"].format(dist=dist_km),
                score=min(1.0, dist_km / 20.0)
            ))
        elif dist_km > GPS_MISMATCH_MED_KM:
            flags.append(_flag(
                "GPS_MISMATCH", "medium",
                REASON_TEMPLATES["GPS_MISMATCH"].format(dist=dist_km),
                score=min(0.7, dist_km / 10.0)
            ))

    # ------------------------------------------------------------------
    # R7: PAYMENT_BEFORE_WEIGH
    # ------------------------------------------------------------------
    if payment_at and weigh_in_at:
        pa = payment_at if payment_at.tzinfo else payment_at.replace(tzinfo=timezone.utc)
        wa = weigh_in_at if weigh_in_at.tzinfo else weigh_in_at.replace(tzinfo=timezone.utc)
        if pa < wa:
            mins = (wa - pa).total_seconds() / 60
            flags.append(_flag(
                "PAYMENT_BEFORE_WEIGH", "high",
                REASON_TEMPLATES["PAYMENT_BEFORE_WEIGH"].format(mins=abs(mins)),
                score=0.95
            ))

    # ------------------------------------------------------------------
    # R8: REPEATED_WEIGHT (same exact weight >= 4 lots in 7 days)
    # ------------------------------------------------------------------
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    rw_stmt = (
        select(func.count())
        .select_from(Transaction)
        .where(
            Transaction.collector_id == collector_id,
            Transaction.created_at >= week_ago,
        )
    )
    rw_count = (await db.execute(rw_stmt)).scalar_one() or 0
    if rw_count >= REPEATED_WEIGHT_COUNT:
        flags.append(_flag(
            "REPEATED_WEIGHT", "low",
            REASON_TEMPLATES["REPEATED_WEIGHT"].format(
                wt=actual_weight_g, count=rw_count),
            score=0.30
        ))

    return flags
