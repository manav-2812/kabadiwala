from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.models.all_models import Material, PriceHistory
from app.schemas.all_schemas import PriceHistoryItem, PriceSummaryItem
from app.services.trends import get_price_trends

router = APIRouter(prefix="/prices", tags=["prices"])

REASONS = {
    "PCB": {
        "en": "Global demand for recovered gold & palladium up 4.2%",
        "hi": "पुनर्प्राप्त सोने और पैलेडियम की वैश्विक मांग 4.2% बढ़ी",
        "mr": "पुनर्प्राप्त सोने आणि पॅलेडियमची जागतिक मागणी ४.२% वाढली",
        "pa": "ਸੋਨੇ ਅਤੇ ਪੈਲੇਡੀਅਮ ਦੀ ਗਲੋਬਲ ਮੰਗ 4.2% ਵਧੀ"
    },
    "BATTERY_LI": {
        "en": "Lithium hydroxide benchmark steady with active cell recycling",
        "hi": "लिथियम हाइड्रोक्साइड का बेंचमार्क स्थिर, सक्रिय रिसाइक्लिंग",
        "mr": "सक्रिय सेल पुनर्वापरासह लिथियम हायड्रॉक्साईड बेंचमार्क स्थिर",
        "pa": "ਲਿਥੀਅਮ ਹਾਈਡ੍ਰੋਕਸਾਈਡ ਬੈਂਚਮਾਰਕ ਸਥਿਰ ਹੈ"
    },
    "CABLE": {
        "en": "MCX Copper futures rallied on infrastructure supply tightening",
        "hi": "तांबे के वायदा भाव में बुनियादी ढांचे की मांग से उछाल",
        "mr": "पायाभूत सुविधांच्या मागणीमुळे तांब्याच्या दरात वाढ झाली",
        "pa": "ਤਾਂਬੇ ਦੀਆਂ ਕੀਮਤਾਂ ਵਿੱਚ ਵਾਧਾ ਦਰਜ ਕੀਤਾ ਗਿਆ"
    },
    "MAGNET": {
        "en": "Neodymium permanent magnet export quota constraints",
        "hi": "नियोडिमियम दुर्लभ चुंबक की मांग में वृद्धि",
        "mr": "निओडीमियम कायमस्वरूपी चुंबक निर्यातीवर निर्बंध",
        "pa": "ਦੁਰਲੱਭ ਚੁੰਬਕਾਂ ਦੀ ਮੰਗ ਵਿੱਚ ਵਾਧਾ"
    },
    "default": {
        "en": "Stable formal recycler buy-back pricing under EPR compliance",
        "hi": "ईपीआर नियमों के तहत अधिकृत रिसाइकिलर की स्थिर खरीद दर",
        "mr": "EPR नियमांनुसार अधिकृत पुनर्वापरदारांचे स्थिर खरेदी दर",
        "pa": "ਈਪੀਆਰ ਨਿਯਮਾਂ ਅਧੀਨ ਸਥਿਰ ਖਰੀਦ ਦਰ"
    }
}

@router.get("/summary", response_model=List[PriceSummaryItem])
async def get_price_summary(city: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Material)
    res = await db.execute(stmt)
    materials = res.scalars().all()
    
    summary = []
    for m in materials:
        # Fetch last 14 days prices
        p_stmt = (
            select(PriceHistory)
            .where(PriceHistory.material_id == m.id)
            .order_by(desc(PriceHistory.date))
            .limit(14)
        )
        p_res = await db.execute(p_stmt)
        history = list(reversed(p_res.scalars().all()))
        
        sparkline = [h.price_paise_per_kg for h in history] if history else [m.base_price_paise_per_kg]
        current_p = sparkline[-1]
        start_p = sparkline[0] if len(sparkline) > 1 else current_p
        
        pct_change = round(((current_p - start_p) / float(start_p)) * 100.0, 1) if start_p else 0.0
        r_meta = REASONS.get(m.code, REASONS["default"])

        summary.append(PriceSummaryItem(
            material_id=m.id,
            material_code=m.code,
            name_en=m.name_en,
            name_hi=m.name_hi,
            name_mr=m.name_mr or m.name_hi or m.name_en,
            name_pa=m.name_pa,
            current_price_paise_per_kg=current_p,
            change_pct_14d=pct_change,
            trend_reason_en=r_meta["en"],
            trend_reason_hi=r_meta["hi"],
            trend_reason_mr=r_meta.get("mr", r_meta["hi"]),
            trend_reason_pa=r_meta["pa"],
            sparkline=sparkline,
            is_hazardous=m.is_hazardous
        ))
    return summary

@router.get("", response_model=List[PriceHistoryItem])
async def get_prices(
    material_id: Optional[str] = None,
    city: Optional[str] = None,
    days: int = Query(14, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PriceHistory)
    if material_id:
        stmt = stmt.where(PriceHistory.material_id == material_id)
    stmt = stmt.order_by(desc(PriceHistory.date)).limit(days)
    res = await db.execute(stmt)
    rows = list(reversed(res.scalars().all()))
    
    return [
        PriceHistoryItem(
            date=r.date,
            price_paise_per_kg=r.price_paise_per_kg,
            min_paise=r.min_paise,
            max_paise=r.max_paise
        ) for r in rows
    ]


@router.get("/trends")
async def get_trends(
    material: str = Query(..., description="Material code, e.g. PCB, CABLE, BATTERY_LI"),
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns MA7/MA14/MA30, weekly slope %, trend arrow (Rising/Falling/Steady),
    vs-last-week %, sparkline (14 days), and a gated 7-day forecast.

    Forecast is only shown when >= ML_FORECAST_MIN_DAYS of REAL price data exist.
    is_demo=true when data is synthetic-only.
    """
    return await get_price_trends(db, material_code=material, city=city)
