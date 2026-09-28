"""
Price Trends Service
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Computes MA7 / MA14 / MA30, weekly slope %, and trend arrow.
Forecast (Holt-Winters or linear) is gated behind ML_FORECAST_MIN_DAYS
of REAL (non-synthetic) daily price data.

Anything derived from synthetic data is tagged is_demo=true.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.all_models import Material, PriceHistory


def _moving_average(prices: list[float], n: int) -> float | None:
    """Simple moving average of last n values. Returns None if not enough data."""
    if len(prices) < n:
        return None
    return round(sum(prices[-n:]) / n, 2)


def _weekly_slope_pct(prices: list[float]) -> float | None:
    """
    Weekly slope as percentage: (mean of last 7 days - mean of prior 7 days)
    / mean of prior 7 days * 100.
    Returns None if not enough data (< 14 data points).
    """
    if len(prices) < 14:
        return None
    recent = sum(prices[-7:]) / 7
    prior = sum(prices[-14:-7]) / 7
    if prior == 0:
        return None
    return round((recent - prior) / prior * 100, 2)


def _arrow(slope: float | None) -> str:
    """Rising if slope > +3%/week, Falling if < -3%/week, else Steady."""
    if slope is None:
        return "Steady"
    if slope > 3.0:
        return "Rising"
    if slope < -3.0:
        return "Falling"
    return "Steady"


async def get_price_trends(
    db: AsyncSession,
    material_code: str,
    city: str | None = None,
) -> dict[str, Any]:
    """
    Returns trend data for a material.
    Forecast returned only if >= ML_FORECAST_MIN_DAYS of real data exist.
    """
    # Fetch material
    m_stmt = select(Material).where(Material.code == material_code)
    m_res = await db.execute(m_stmt)
    material = m_res.scalar_one_or_none()
    if not material:
        return {"error": f"Material {material_code} not found"}

    # Fetch last 90 days of price history (real + synthetic)
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    stmt = (
        select(PriceHistory)
        .where(
            PriceHistory.material_id == material.id,
            PriceHistory.date >= cutoff,
        )
        .order_by(PriceHistory.date.asc())
    )
    res = await db.execute(stmt)
    history = res.scalars().all()

    if not history:
        return {
            "material_code": material_code,
            "ma7": None,
            "ma14": None,
            "ma30": None,
            "slope_pct_week": None,
            "arrow": "Steady",
            "vs_last_week_pct": None,
            "forecast": None,
            "is_demo": True,
            "note": "No price history available yet",
        }

    prices = [float(h.price_paise_per_kg) for h in history]
    is_synthetic = all(getattr(h, "is_synthetic", True) for h in history)

    ma7 = _moving_average(prices, 7)
    ma14 = _moving_average(prices, 14)
    ma30 = _moving_average(prices, 30)
    slope = _weekly_slope_pct(prices)
    arrow = _arrow(slope)

    # vs last week
    vs_last_week = None
    if len(prices) >= 8:
        curr = prices[-1]
        week_ago = prices[-8]
        if week_ago:
            vs_last_week = round((curr - week_ago) / week_ago * 100, 1)

    # Forecast gate: only show if >= ML_FORECAST_MIN_DAYS of REAL days
    real_days = len([h for h in history if not getattr(h, "is_synthetic", True)])
    forecast = None
    forecast_note = None
    if real_days >= settings.ML_FORECAST_MIN_DAYS and len(prices) >= settings.ML_FORECAST_MIN_DAYS:
        # Simple linear trend forecast for 7 days
        n = len(prices)
        x_mean = (n - 1) / 2
        y_mean = sum(prices) / n
        num = sum((i - x_mean) * (p - y_mean) for i, p in enumerate(prices))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope_val = num / den if den != 0 else 0
        intercept = y_mean - slope_val * x_mean
        forecast_points = [
            round(intercept + slope_val * (n + d), 2) for d in range(7)
        ]
        forecast = {
            "days": 7,
            "points": forecast_points,
            "band_width_pct": 5.0,  # ±5% confidence band
            "method": "linear_trend",
            "note": "Linear trend forecast — gated, only shown with real data",
        }
    else:
        if real_days > 0:
            forecast_note = (
                f"Forecast needs {settings.ML_FORECAST_MIN_DAYS} days of real data "
                f"(currently {real_days} real days). Trend arrow shown instead."
            )
        else:
            forecast_note = (
                "No real price data yet. Trend arrow only. "
                "Forecast will appear after real transactions establish price history."
            )

    return {
        "material_code": material_code,
        "material_name_en": material.name_en,
        "ma7": ma7,
        "ma14": ma14,
        "ma30": ma30,
        "slope_pct_week": slope,
        "arrow": arrow,
        "vs_last_week_pct": vs_last_week,
        "sparkline_14d": prices[-14:] if len(prices) >= 2 else prices,
        "forecast": forecast,
        "forecast_note": forecast_note,
        "is_demo": is_synthetic,
        "real_days_available": real_days,
        "forecast_min_days": settings.ML_FORECAST_MIN_DAYS,
    }
