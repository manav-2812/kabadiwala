"""
Recycler Matching & Ranking Service
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Explainable weighted score (no black box).
Formula identical to TypeScript twin in web/src/features/collector/matching.ts.
Shared golden vectors: ml/golden/matching_golden.json

Score = w_payout*payout_norm + w_proximity*proximity_norm + w_rate*rate_norm
      + w_pickup*pickup_score + w_reliability*reliability_norm + w_response*response_norm

All weights loaded from the active MatchingWeight DB row (versioned, admin-editable).
Default weights (must sum to 1.00): payout=0.30, proximity=0.25, rate=0.20,
  pickup=0.10, reliability=0.10, response=0.05
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Default weights (used when DB has no active MatchingWeight row)
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS: dict[str, float] = {
    "payout":      0.30,
    "proximity":   0.25,
    "rate":        0.20,
    "pickup":      0.10,
    "reliability": 0.10,
    "response":    0.05,
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def _derive_reasons(
    norm_payout: float,
    dist_km: float,
    pickup_available: bool,
    reliability_norm: float,
    response_norm: float,
    norm_rate: float,
) -> list[str]:
    """Return up to 3 reason codes from the spec."""
    reasons: list[str] = []
    if norm_payout >= 0.80:
        reasons.append("HIGHEST_PAYOUT")
    if dist_km <= 5.0 and "HIGHEST_PAYOUT" not in reasons or dist_km <= 5.0:
        reasons.append("NEAREST")
    if pickup_available and len(reasons) < 3:
        reasons.append("PICKUP_AVAILABLE")
    if reliability_norm >= 0.90 and len(reasons) < 3:
        reasons.append("TRUSTED")
    if response_norm >= 0.80 and len(reasons) < 3:
        reasons.append("FAST_RESPONSE")
    # Always emit at least one reason
    if not reasons:
        reasons.append("NEAREST" if dist_km <= 10.0 else "HIGHEST_PAYOUT")
    return reasons[:3]


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def rank_recyclers_for_lot(
    collector_lat: float,
    collector_lng: float,
    lot_est_paise: int,
    lot_materials: list[str],
    recyclers: Sequence[Any],
    weights: dict[str, float] | None = None,
    weights_version: str = "default",
) -> list[dict[str, Any]]:
    """
    Rank recyclers with 6-factor explainable score.

    Hard filters applied first (never overridden):
      - authorization_status == 'verified'
      - license_valid_to >= now
    """
    w = weights or DEFAULT_WEIGHTS
    now = datetime.now(timezone.utc)
    candidates = []

    for r in recyclers:
        auth_status = _get(r, "authorization_status")
        if auth_status != "verified":
            continue

        valid_to = _get(r, "license_valid_to")
        if valid_to:
            if isinstance(valid_to, str):
                try:
                    valid_to = datetime.fromisoformat(valid_to.replace("Z", "+00:00"))
                except ValueError:
                    pass
            if isinstance(valid_to, datetime):
                if valid_to.tzinfo is None:
                    valid_to = valid_to.replace(tzinfo=timezone.utc)
                if valid_to < now:
                    continue

        lat = float(_get(r, "lat", 0.0))
        lng = float(_get(r, "lng", 0.0))
        dist_km = haversine_km(collector_lat, collector_lng, lat, lng)

        rel_score = float(_get(r, "reliability_score", 80))
        rating_avg = float(_get(r, "rating_avg", 4.5))
        pickup = bool(_get(r, "pickup_available", False))

        # Payout factor: reliability modifies estimated payout ±5 %
        rate_modifier = 1.0 + (float(rel_score - 80) / 200.0)
        est_payout = round(lot_est_paise * rate_modifier)

        candidates.append({
            "recycler": r,
            "dist_km": dist_km,
            "est_payout": est_payout,
            "rating": rating_avg,
            "reliability": rel_score,
            "pickup": pickup,
            "response_speed": rel_score / 100.0,
        })

    if not candidates:
        return []

    # ---------------------------------------------------------------
    # Normalise each dimension across the candidate set
    # ---------------------------------------------------------------
    def _norm(vals: list[float], val: float, invert: bool = False) -> float:
        lo, hi = min(vals), max(vals)
        if hi == lo:
            return 1.0
        n = (val - lo) / (hi - lo)
        return round(1.0 - n if invert else n, 4)

    payouts = [c["est_payout"] for c in candidates]
    dists = [c["dist_km"] for c in candidates]
    reliabilities = [c["reliability"] for c in candidates]
    responses = [c["response_speed"] for c in candidates]

    ranked = []
    for c in candidates:
        r = c["recycler"]

        norm_payout = _norm(payouts, c["est_payout"])
        norm_proximity = _norm(dists, c["dist_km"], invert=True)  # closer = better
        norm_rate = norm_payout  # rate_norm ≈ payout_norm (same data source)
        pickup_score = 1.0 if c["pickup"] else 0.2
        norm_reliability = _norm(reliabilities, c["reliability"])
        norm_response = _norm(responses, c["response_speed"])

        score = round(
            w["payout"] * norm_payout
            + w["proximity"] * norm_proximity
            + w["rate"] * norm_rate
            + w["pickup"] * pickup_score
            + w["reliability"] * norm_reliability
            + w["response"] * norm_response,
            4
        )

        reasons = _derive_reasons(
            norm_payout, c["dist_km"], c["pickup"],
            norm_reliability, norm_response, norm_rate
        )

        ranked.append({
            "id": _get(r, "id"),
            "company_name": _get(r, "company_name", ""),
            "contact_person": _get(r, "contact_person", ""),
            "address": _get(r, "address", ""),
            "city": _get(r, "city", ""),
            "lat": float(_get(r, "lat", 0.0)),
            "lng": float(_get(r, "lng", 0.0)),
            "distance_km": c["dist_km"],
            "cpcb_license_no": _get(r, "cpcb_license_no", ""),
            "spcb_authorization_no": _get(r, "spcb_authorization_no", ""),
            "license_valid_to": _get(r, "license_valid_to"),
            "authorization_status": _get(r, "authorization_status"),
            "rating_avg": float(_get(r, "rating_avg", 0.0)),
            "reliability_score": _get(r, "reliability_score"),
            "pickup_available": c["pickup"],
            "estimated_payout_paise": c["est_payout"],
            "ranking_score": score,
            "ranking_reason": reasons[0] if reasons else "NEAREST",  # legacy compat
            "reasons": reasons,
            "weights_version": weights_version,
        })

    ranked.sort(key=lambda x: x["ranking_score"], reverse=True)
    return ranked
