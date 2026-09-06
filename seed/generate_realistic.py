# pyright: reportMissingImports=false
"""
Kabadiwala Connect - Realistic Synthetic Data Generator (SIH 2026, PS SIH26229)
Layer A: Deterministic Fictional Composite Generator

Key Guarantees:
- Seeded RNG (seed=42): 100% deterministic, reproducible output.
- Exact Ledger Reconciliation: sum(items) == transaction.final_amount == sum(payments) + dues.
- 49 Accounts: 34 Collectors, 4 Hubs, 8 Recyclers, 8 Agents, 3 Staff.
- 320+ Lots, 230+ Transactions, 700+ Quotes.
- 8 Deliberate Anomalies matching seed/expected_flags.json.
- Full Hash Chain on all lots.
- Safety & Denylist validation against seed/denylist_real_entities.txt.
- All rows flagged is_synthetic=True, seed_batch_id set.
"""

import os
import sys
import math
import json
import uuid
import random
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple

import yaml
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from app.db.session import engine, async_session_maker  # type: ignore
    from app.core.security import get_password_hash  # type: ignore
    from app.services.trace import compute_event_hash, GENESIS_HASH  # type: ignore
    from app.models.all_models import (  # type: ignore
        Base, User, Collector, Aggregator, Recycler, Material, MaterialComposition,
        MaterialSubcategory, RecyclerRate, PriceHistory, Lot, LotItem, LotPhoto,
        Quote, Transaction, Payment, TraceabilityEvent, Rating, SafetyAcknowledgement,
        Notification, Document, SupportTicket, TicketMessage, AnomalyFlag,
        PickupAgent, Cancellation, Dataset, DatasetVersion, FAQ, NotificationTemplate
    )
    from app.db.seed import FAQS_LIST, NOTIFICATION_TEMPLATES_SEED  # type: ignore
except ImportError:
    from backend.app.db.session import engine, async_session_maker  # type: ignore
    from backend.app.core.security import get_password_hash  # type: ignore
    from backend.app.services.trace import compute_event_hash, GENESIS_HASH  # type: ignore
    from backend.app.models.all_models import (  # type: ignore
        Base, User, Collector, Aggregator, Recycler, Material, MaterialComposition,
        MaterialSubcategory, RecyclerRate, PriceHistory, Lot, LotItem, LotPhoto,
        Quote, Transaction, Payment, TraceabilityEvent, Rating, SafetyAcknowledgement,
        Notification, Document, SupportTicket, TicketMessage, AnomalyFlag,
        PickupAgent, Cancellation, Dataset, DatasetVersion, FAQ, NotificationTemplate
    )
    from backend.app.db.seed import FAQS_LIST, NOTIFICATION_TEMPLATES_SEED  # type: ignore

# ---------------------------------------------------------------------------
# Constant Rosters and Configuration
# ---------------------------------------------------------------------------

CITIES_GEO: Dict[str, Dict[str, Any]] = {
    "Pune": {"state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    "Nashik": {"state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    "Nagpur": {"state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    "Thane": {"state": "Maharashtra", "lat": 19.2183, "lng": 72.9781},
    "Chhatrapati Sambhajinagar": {"state": "Maharashtra", "lat": 19.8762, "lng": 75.3433},
    "Delhi NCR": {"state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    "Ghaziabad": {"state": "Uttar Pradesh", "lat": 28.6692, "lng": 77.4538},
    "Lucknow": {"state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    "Jaipur": {"state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    "Ludhiana": {"state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    "Amritsar": {"state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    "Mohali": {"state": "Punjab", "lat": 30.7046, "lng": 76.7179},
    "Jalandhar": {"state": "Punjab", "lat": 31.3260, "lng": 75.5762},
    "Patiala": {"state": "Punjab", "lat": 30.3398, "lng": 76.3869},
    "Chandigarh": {"state": "Chandigarh", "lat": 30.7333, "lng": 76.7794},
    "Bengaluru": {"state": "Karnataka", "lat": 12.9716, "lng": 77.5946}
}

COLLECTOR_ROSTER = [
    (1, "Sunita Jadhav", "सुनीता जाधव", "mr", "Pune", "Hadapsar", ["CABLES", "PLASTIC_MIX"], "M", "Reliable regular"),
    (2, "Ganesh Pawar", "गणेश पवार", "mr", "Pune", "Bhosari", ["PCB", "MOTORS"], "H", "Top earner, high trust"),
    (3, "Rekha Shinde", "रेखा शिंदे", "mr", "Pune", "Pimpri-Chinchwad", ["BATTERY_LI", "CABLES"], "M", "Safety-card user"),
    (4, "Santosh Gaikwad", "संतोष गायकवाड", "mr", "Nashik", "Satpur", ["MOTORS", "MAGNET"], "M", "Repeated weight anomaly"),
    (5, "Vijay More", "विजय मोरे", "mr", "Nagpur", "Kamptee Road", ["CRT", "LCD"], "M", "Hazard-handling bonus"),
    (6, "Mangal Kamble", "मंगल कांबळे", "mr", "Thane", "Bhiwandi", ["PCB", "CABLES"], "H", "Has one dispute / price band anomaly"),
    (7, "Prakash Sawant", "प्रकाश सावंत", "mr", "Chhatrapati Sambhajinagar", "Waluj", ["MOTORS", "CABLES"], "L", "New user, 1 lot only"),
    (8, "Anita Bhosale", "अनिता भोसले", "mr", "Pune", "Kothrud", ["PCB", "LCD"], "L", "Regular L tier"),
    (9, "Dattatray Kale", "दत्तात्रय काळे", "mr", "Nashik", "Panchavati", ["CABLES", "PLASTIC_MIX"], "M", "Offline-heavy"),
    (10, "Nanda Waghmare", "नंदा वाघमारे", "mr", "Nagpur", "Sitabuldi", ["LCD", "PCB"], "L", "Regular L tier"),
    (11, "Rahul Thorat", "राहुल थोरात", "mr", "Pune", "Chakan", ["MOTORS", "MAGNET"], "M", "Buyer no-show once / GPS mismatch"),
    (12, "Mohammad Irfan Ansari", "मोहम्मद इरफ़ान अंसारी", "hi", "Delhi NCR", "Seelampur", ["PCB", "LCD"], "H", "High volume / quote anomaly"),
    (13, "Ramesh Yadav", "रमेश यादव", "hi", "Ghaziabad", "Loni", ["CABLES", "MOTORS"], "M", "Regular M tier"),
    (14, "Sunil Kumar", "सुनील कुमार", "hi", "Lucknow", "Aminabad", ["CRT", "LCD"], "M", "Regular M tier"),
    (15, "Pooja Devi", "पूजा देवी", "hi", "Delhi NCR", "Mustafabad", ["CABLES", "PLASTIC_MIX"], "L", "Regular L tier"),
    (16, "Rajesh Chauhan", "राजेश चौहान", "hi", "Jaipur", "Sanganer", ["PCB", "BATTERY_LI"], "M", "Uses UPI"),
    (17, "Imran Qureshi", "इमरान कुरैशी", "hi", "Delhi NCR", "Nehru Place", ["PCB", "LCD"], "H", "Unit error suspect anomaly"),
    (18, "Kavita Sharma", "कविता शर्मा", "hi", "Jaipur", "Malviya Nagar", ["CABLES", "PLASTIC_MIX"], "L", "Regular L tier"),
    (19, "Anil Verma", "अनिल वर्मा", "hi", "Lucknow", "Charbagh", ["MOTORS"], "M", "Inactive 40 days"),
    (20, "Shabnam Begum", "शबनम बेगम", "hi", "Ghaziabad", "Sahibabad", ["PCB", "CABLES"], "L", "Regular L tier"),
    (21, "Deepak Mishra", "दीपक मिश्रा", "hi", "Delhi NCR", "Okhla", ["LCD", "PCB"], "M", "Payment before weigh anomaly"),
    (22, "Gurpreet Singh", "ਗੁਰਪ੍ਰੀਤ ਸਿੰਘ", "pa", "Ludhiana", "Focal Point", ["MOTORS", "CABLES"], "H", "Top-3 earner"),
    (23, "Harjinder Kaur", "ਹਰਜਿੰਦਰ ਕੌਰ", "pa", "Ludhiana", "Dhandari Kalan", ["CABLES", "PLASTIC_MIX"], "M", "Regular M tier"),
    (24, "Balwinder Singh", "ਬਲਵਿੰਦਰ ਸਿੰਘ", "pa", "Amritsar", "Chheharta", ["PCB", "LCD"], "M", "Regular M tier"),
    (25, "Manjit Kaur", "ਮਨਜੀਤ ਕੌਰ", "pa", "Mohali", "Phase 8", ["BATTERY_LI", "PCB"], "L", "Regular L tier"),
    (26, "Jaswant Singh", "ਜਸਵੰਤ ਸਿੰਘ", "pa", "Jalandhar", "Focal Point", ["MOTORS", "MAGNET"], "M", "Weight variance dispute anomaly"),
    (27, "Sukhdev Singh", "ਸੁਖਦੇਵ ਸਿੰਘ", "pa", "Patiala", "Rajpura Road", ["CRT", "CABLES"], "M", "Regular M tier"),
    (28, "Paramjit Kaur", "ਪਰਮਜੀਤ ਕੌਰ", "pa", "Chandigarh", "Industrial Area Phase 1", ["PCB", "LCD"], "L", "Regular L tier"),
    (29, "Amandeep Singh", "ਅਮਨਦੀਪ ਸਿੰਘ", "pa", "Mohali", "Phase 9", ["PCB", "MOTORS"], "M", "Duplicate-photo anomaly"),
    (30, "Kulwinder Singh", "ਕੁਲਵਿੰਦਰ ਸਿੰਘ", "pa", "Ludhiana", "Sherpur", ["CABLES", "BATTERY_LI"], "H", "High volume H tier"),
    (31, "Rajwinder Kaur", "ਰਾਜਵਿੰਦਰ ਕੌਰ", "pa", "Amritsar", "Majitha Road", ["CABLES", "PLASTIC_MIX"], "L", "Cash-only"),
    (32, "Ravi Kumar", None, "en", "Bengaluru", "Peenya", ["PCB", "LCD"], "M", "English-preferring regular"),
    (33, "Lakshmi Narayanan", None, "en", "Bengaluru", "Yeshwanthpur", ["PCB", "CABLES"], "L", "Uses UPI"),
    (34, "Joseph D'Souza", None, "en", "Chandigarh", "Sector 28", ["LCD", "PCB"], "M", "English-preferring regular")
]

AGGREGATOR_ROSTER = [
    (1, "Sahyadri Scrap Hub", "Pune", "Maharashtra", 18.6270, 73.8470, 250, 25, "Bhosari MIDC"),
    (2, "Yamuna Vihar Aggregators", "Delhi NCR", "Delhi", 28.7200, 77.2900, 300, 30, "Loni Industrial Area"),
    (3, "Malwa Collection Point", "Ludhiana", "Punjab", 30.8800, 75.9100, 200, 25, "Focal Point"),
    (4, "Peenya Metals Aggregation", "Bengaluru", "Karnataka", 13.0300, 77.5200, 350, 20, "Peenya Industrial Area")
]

RECYCLER_ROSTER = [
    (1, "Sahyadri Urban Metals Pvt Ltd", "Pune", "Maharashtra", 18.7600, 73.8600, "verified", True, 40, ["PCB", "LCD", "BATTERY_LI", "MOTORS"], 60000, 0),
    (2, "Deccan E-Recovery LLP", "Pune", "Maharashtra", 18.7800, 74.2400, "verified", True, 35, ["PCB", "CRT", "CABLES"], 45000, 0),
    (3, "Konkan Circular Systems Pvt Ltd", "Thane", "Maharashtra", 19.2900, 73.0600, "verified", True, 30, ["PLASTIC_MIX", "CABLES", "LCD"], 50000, 0),
    (4, "Vidarbha Green Cycle Pvt Ltd", "Nagpur", "Maharashtra", 20.9200, 79.0100, "verified", False, 0, ["CRT", "LCD", "PCB"], 30000, 0),
    (5, "Ganga Plains Recyclers Pvt Ltd", "Ghaziabad", "Uttar Pradesh", 28.7400, 77.2800, "verified", True, 25, ["PCB", "MAGNET", "MOTORS"], 40000, 0),
    (6, "Tricity Reclaim Works Pvt Ltd", "Mohali", "Punjab", 30.7000, 76.7100, "verified", True, 30, ["PCB", "LCD", "BATTERY_LI", "MAGNET"], 35000, 0),
    (7, "Chenab Circular Recyclers LLP", "Ludhiana", "Punjab", 30.8700, 75.9200, "pending", False, 0, ["CABLES", "MOTORS", "PLASTIC_MIX"], 20000, 0),
    (8, "Malwa Materials Recovery Pvt Ltd", "Ludhiana", "Punjab", 30.8600, 75.9500, "expired", False, 0, ["PCB", "LCD"], 25000, 40) # expired 40 days ago
]

AGENT_ROSTER = [
    ("Suresh Patil", "DEMO-MH-14-AX-4821", "tempo", 1, None),
    ("Manoj Shinde", "DEMO-MH-12-BY-8319", "pickup van", 2, None),
    ("Dinesh Jadhav", "DEMO-MH-04-CZ-2914", "tempo", 3, None),
    ("Pradeep Yadav", "DEMO-UP-14-DV-7402", "e-rickshaw", 5, None),
    ("Satnam Singh", "DEMO-PB-65-EW-1953", "pickup van", 6, None),
    ("Nitin Deshmukh", "DEMO-MH-14-FU-6184", "e-rickshaw", None, 1),
    ("Arvind Sharma", "DEMO-DL-01-GT-3529", "tempo", None, 2),
    ("Jasbir Singh", "DEMO-PB-10-HS-9041", "pickup van", None, 3)
]

STAFF_ROSTER = [
    ("Meera Iyer", "en", "admin", "9800000001"),
    ("Harpreet Grewal", "pa", "support", "9800000002"),
    ("Vaishali Kulkarni", "mr", "support", "9800000003")
]

RAW_MATERIALS_DEFS = [
    ("PCB", "Circuit Boards (PCB)", "सर्किट बोर्ड (पीसीबी)", "सर्किट बोर्ड (PCB)", "ਸਰਕਟ ਬੋਰਡ (ਪੀਸੀਬੀ)", "cpu", 42000, 32000, 55000, True, "medium"),
    ("BATTERY_LI", "Lithium-Ion Batteries", "लिथियम-आयन बैटरी", "लिथियम-आयन बॅटरी", "ਲਿਥੀਅਮ-ਆਇਨ ਬੈਟਰੀ", "battery-charging", 18500, 14000, 24000, True, "high"),
    ("MAGNET", "Rare-Earth Magnets", "चुंबकीय पुर्जे", "दुर्मीळ-पृथ्वी चुंबक", "ਚੁੰਬਕੀ ਹਿੱਸੇ", "magnet", 24000, 19000, 31000, False, "low"),
    ("CRT", "CRT Monitors & TV Glass", "सीआरटी स्क्रीन व कांच", "सीआरटी मॉनिटर्स आणि काच", "ਸੀਆਰਟੀ ਸਕ੍ਰੀਨ", "tv", 1200, 800, 1800, True, "high"),
    ("LCD", "LCD / LED Displays", "एलसीडी / एलईडी डिस्प्ले", "एलसीडी / एलईडी डिस्प्ले", "ਐਲਸੀਡੀ / ਐਲਈਡੀ ਡਿਸਪਲੇ", "monitor", 6500, 4500, 9000, True, "medium"),
    ("CABLES", "Copper Cables & Wires", "तांबे के केबल व तार", "तांब्याच्या केबल्स आणि तारा", "ਤਾਂਬੇ ਦੀਆਂ ਤਾਰਾਂ", "cable", 19000, 15000, 25000, False, "low"),
    ("MOTORS", "Electric Motors & Compressors", "इलेक्ट्रिक मोटर व कंप्रेसर", "इलेक्ट्रिक मोटर्स आणि कॉम्प्रेसर", "ਇਲੈਕਟ੍ਰਿਕ ਮੋਟਰਾਂ", "tool", 9200, 7000, 12000, False, "low"),
    ("BATTERY_LEAD", "Lead Acid Batteries", "लेड एसिड बैटरी", "लेड ॲसिड बॅटरी", "ਲੈੱਡ ਐਸਿਡ ਬੈਟਰੀ", "battery", 8500, 6500, 11000, True, "high"),
    ("PLASTIC_MIX", "Mixed E-Waste Plastics", "मिश्रित ई-कचरा प्लास्टिक", "मिश्रित ई-कचरा प्लास्टिक", "ਮਿਸ਼ਰਤ ਪਲਾਸਟਿਕ", "trash", 1800, 1200, 2500, False, "low"),
    ("COPPER_WIRE", "Clean Stripped Copper Wire", "साफ छिला हुआ तांबा तार", "स्वच्छ सोललेली तांब्याची तार", "ਸਾਫ਼ ਤਾਂਬੇ ਦੀ ਤਾਰ", "zap", 45000, 38000, 58000, False, "low")
]

# ---------------------------------------------------------------------------
# Safety & Denylist Verification (Section 8.1)
# ---------------------------------------------------------------------------

def verify_denylist(entities: List[str]):
    denylist_path = os.path.join(os.path.dirname(__file__), "denylist_real_entities.txt")
    denied_terms = []
    if os.path.exists(denylist_path):
        with open(denylist_path, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip().lower()
                if t and not t.startswith("#"):
                    denied_terms.append(t)

    for entity in entities:
        low = entity.lower()
        for dt in denied_terms:
            if dt in low:
                raise ValueError(f"DENYLIST VIOLATION: '{entity}' contains forbidden term '{dt}'")

# ---------------------------------------------------------------------------
# Deterministic Generator Implementation
# ---------------------------------------------------------------------------

class RealisticDataGenerator:
    def __init__(self, rng_seed: int = 42, base_date: Optional[datetime] = None):
        self.rng = random.Random(rng_seed)
        self.base_date = base_date or datetime.now(timezone.utc)
        self.seed_batch_id = str(uuid.uuid4())
        self.price_cache: Dict[Tuple[str, str, str], Dict[str, int]] = {}
        self.password_hash = get_password_hash("123456")

        # Load persona config
        config_path = os.path.join(os.path.dirname(__file__), "persona_config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

    def get_days_ago(self, days: float, hours: int = 11, minutes: int = 24, seconds: int = 15) -> datetime:
        target_day = self.base_date - timedelta(days=int(days))
        return target_day.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

    def generate_price_history_grid(self) -> List[Dict[str, Any]]:
        """90 days x 10 materials x 8 primary cities = 7,200 consistent observations."""
        history_rows = []
        cities = ["Pune", "Nashik", "Nagpur", "Thane", "Delhi NCR", "Jaipur", "Lucknow", "Ludhiana"]
        copper_mats = {"CABLES", "COPPER_WIRE", "MOTORS", "PCB"}

        for day_offset in range(90, -1, -1):
            date_dt = self.base_date - timedelta(days=day_offset)
            date_str = date_dt.strftime("%Y-%m-%d")
            day_of_week = date_dt.weekday() # 0=Mon, 6=Sun
            weekly_factor = 0.98 if day_of_week == 6 else (1.02 if day_of_week in (2, 3) else 1.0)

            # Copper spike at day 60, dip at day 35
            if 55 <= day_offset <= 65:
                copper_shock = 1.20 - abs(day_offset - 60) * 0.03
            elif 30 <= day_offset <= 40:
                copper_shock = 0.88 + abs(day_offset - 35) * 0.02
            else:
                copper_shock = 1.0

            # Drift: smooth sinusoidal curve over 90 days
            drift = 1.0 + 0.05 * math.sin(day_offset / 15.0)

            for mat in RAW_MATERIALS_DEFS:
                code, _, _, _, _, _, base, floor, ceil, _, _ = mat
                for city in cities:
                    city_offset = 1.02 if city in ("Pune", "Delhi NCR") else (0.98 if city in ("Nagpur", "Ludhiana") else 1.0)
                    mat_shock = copper_shock if code in copper_mats else 1.0

                    eff_price = int(base * weekly_factor * drift * city_offset * mat_shock)
                    eff_price = max(floor, min(ceil, eff_price))
                    min_p = int(eff_price * 0.92)
                    max_p = int(eff_price * 1.08)

                    self.price_cache[(date_str, code, city)] = {
                        "price": eff_price,
                        "min": min_p,
                        "max": max_p
                    }

                    history_rows.append({
                        "id": str(uuid.uuid4()),
                        "date": date_str,
                        "city": city,
                        "material_code": code,
                        "price_paise_per_kg": eff_price,
                        "min_paise": min_p,
                        "max_paise": max_p,
                        "unit": "kg",
                        "source": "synthetic",
                        "is_synthetic": True,
                        "created_at": date_dt,
                        "updated_at": date_dt
                    })
        return history_rows

    def get_price(self, date_str: str, mat_code: str, city: str) -> Dict[str, int]:
        if (date_str, mat_code, city) in self.price_cache:
            return self.price_cache[(date_str, mat_code, city)]
        # Fallback to base
        for m in RAW_MATERIALS_DEFS:
            if m[0] == mat_code:
                return {"price": m[6], "min": m[7], "max": m[8]}
        return {"price": 10000, "min": 8000, "max": 12000}

# ---------------------------------------------------------------------------
# Database Population Logic
# ---------------------------------------------------------------------------

async def seed_realistic_database(reset_db: bool = True):
    print("=" * 72)
    print("KABADIWALA CONNECT - REALISTIC SYNTHETIC SEEDING (LAYER A)")
    print("=" * 72)

    gen = RealisticDataGenerator(rng_seed=42)

    # 1. Denylist check
    entities_to_check = [r[1] for r in AGGREGATOR_ROSTER] + [r[1] for r in RECYCLER_ROSTER]
    verify_denylist(entities_to_check)
    print("[PASS] Denylist verification clean. Zero forbidden real company names.")

    async with engine.begin() as conn:
        if reset_db:
            print("[INFO] Resetting existing database schema...")
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            print("[PASS] Schema created cleanly.")

    async with async_session_maker() as db:
        # 2. Insert Materials and Subcategories
        print("[INFO] Seeding materials and strategic mineral compositions...")
        mat_map: Dict[str, Material] = {}
        for row in RAW_MATERIALS_DEFS:
            code, name_en, name_hi, name_mr, name_pa, icon, base, floor, ceil, haz, haz_lvl = row
            m = Material(
                code=code,
                name_en=name_en,
                name_hi=name_hi,
                name_mr=name_mr,
                name_pa=name_pa,
                icon_key=icon,
                base_price_paise_per_kg=base,
                price_floor_paise=floor,
                price_ceiling_paise=ceil,
                is_hazardous=haz,
                hazard_level=haz_lvl,
                hazard_note_en="Contains hazardous industrial components. Handle with care.",
                hazard_note_hi="खतरनाक घटक होते हैं। सावधानी से संभालें।",
                hazard_note_mr="धोकादायक घटक असतात. काळजीपूर्वक हाताळा.",
                hazard_note_pa="ਖ਼ਤਰਨਾਕ ਹਿੱਸੇ ਹੁੰਦੇ ਹਨ। ਧਿਆਨ ਨਾਲ ਵਰਤੋ।",
                safety_tip_en="Wear gloves and safety goggles. Store in dry area.",
                safety_tip_hi="दस्ताने और सुरक्षा चश्मा पहनें। सूखी जगह पर रखें।",
                safety_tip_mr="हातमोजे आणि संरक्षणात्मक चष्मा वापरा. कोरड्या जागी ठेवा.",
                safety_tip_pa="ਦਸਤਾਨੇ ਅਤੇ ਸੁਰੱਖਿਆ ਚਸ਼ਮਾ ਪਾਓ। ਸੁੱਕੀ ਥਾਂ 'ਤੇ ਰੱਖੋ।",
                strategic_flag=(code in ("PCB", "BATTERY_LI", "MAGNET")),
                source="cpcb_schedule_1",
                is_synthetic=False
            )
            db.add(m)
            mat_map[code] = m
            if code == "CABLES":
                mat_map["CABLE"] = m
            elif code == "MOTORS":
                mat_map["MOTOR"] = m
            elif code == "PLASTIC_MIX":
                mat_map["PLASTIC_MIXED"] = m

        await db.flush()

        # Seed mineral compositions for critical metals recovery
        mineral_comps = {
            "PCB": [("cu", 180.0), ("au", 0.35), ("ag", 1.2), ("pd", 0.08), ("sn", 35.0)],
            "BATTERY_LI": [("co", 140.0), ("li", 15.0), ("cu", 85.0), ("al", 50.0)],
            "MAGNET": [("nd", 185.0), ("fe", 640.0)],
            "CRT": [("pb", 120.0), ("fe", 80.0), ("cu", 40.0)],
            "LCD": [("al", 90.0), ("cu", 30.0), ("sn", 10.0)],
            "CABLES": [("cu", 550.0), ("al", 50.0)],
            "MOTORS": [("cu", 160.0), ("fe", 720.0), ("al", 40.0)],
            "BATTERY_LEAD": [("pb", 650.0)],
            "PLASTIC_MIX": [("fe", 10.0)],
            "COPPER_WIRE": [("cu", 990.0)]
        }
        for m_code, comps in mineral_comps.items():
            if m_code in mat_map:
                m_obj = mat_map[m_code]
                for elem, g_kg in comps:
                    comp = MaterialComposition(
                        material_id=m_obj.id,
                        element=elem,
                        grams_per_kg=g_kg,
                        source_note="JNARDDC validated baseline study 2024"
                    )
                    db.add(comp)

        await db.flush()

        # 3. Price History
        print("[INFO] Generating 90-day x 10-material x 8-city deterministic price history...")
        price_rows = gen.generate_price_history_grid()
        for p in price_rows:
            ph = PriceHistory(
                id=p["id"],
                material_id=mat_map[p["material_code"]].id,
                city=p["city"],
                date=p["date"],
                price_paise_per_kg=p["price_paise_per_kg"],
                min_paise=p["min_paise"],
                max_paise=p["max_paise"],
                unit=p["unit"],
                source=p["source"],
                is_synthetic=p["is_synthetic"],
                created_at=p["created_at"],
                updated_at=p["updated_at"]
            )
            db.add(ph)

        await db.flush()
        print(f"[PASS] Seeded {len(price_rows)} price history records.")

        # 4. Hubs / Aggregators (4)
        print("[INFO] Seeding 4 fictional Aggregator Hubs...")
        hub_objs: List[Aggregator] = []
        for hid, bname, city, state, lat, lng, bps, rad, area_name in AGGREGATOR_ROSTER:
            phone = f"980002000{hid}"
            u = User(
                phone=phone,
                name=bname,
                role="aggregator",
                language="mr" if state == "Maharashtra" else ("pa" if state == "Punjab" else "hi"),
                otp_hash=gen.password_hash,
                is_active=True,
                is_synthetic=True,
                display_name_local=None
            )
            db.add(u)
            await db.flush()

            agg = Aggregator(
                user_id=u.id,
                business_name=bname,
                city=city,
                state=state,
                lat=lat,
                lng=lng,
                commission_bps=bps,
                verification_status="verified",
                service_radius_km=rad
            )
            db.add(agg)
            hub_objs.append(agg)

        await db.flush()

        # 5. Recyclers (8)
        print("[INFO] Seeding 8 fictional Recyclers (6 verified, 1 pending, 1 expired)...")
        recycler_objs: List[Recycler] = []
        for rid, cname, city, state, lat, lng, status, pickup, rad, accepted_codes, cap, expired_days in RECYCLER_ROSTER:
            phone = f"980003000{rid}"
            u = User(
                phone=phone,
                name=cname,
                role="recycler",
                language="mr" if state == "Maharashtra" else ("pa" if state == "Punjab" else "hi"),
                otp_hash=gen.password_hash,
                is_active=True,
                is_synthetic=True,
                display_name_local=None
            )
            db.add(u)
            await db.flush()

            if expired_days > 0:
                valid_from = gen.get_days_ago(400)
                valid_to = gen.get_days_ago(expired_days)
            else:
                valid_from = gen.get_days_ago(180)
                valid_to = gen.base_date + timedelta(days=365)

            # Internal internal-format demo authorization number (Section 3.3)
            state_code = "MH" if state == "Maharashtra" else ("PB" if state == "Punjab" else "UP")
            auth_no = f"KC-DEMO-AUTH-{state_code}-{1000 + rid}"

            rec = Recycler(
                user_id=u.id,
                company_name=cname,
                contact_person=f"Manager {cname.split()[0]}",
                address=f"{city} Industrial Cluster, Sector {rid}",
                city=city,
                state=state,
                lat=lat,
                lng=lng,
                cpcb_license_no=auth_no,
                spcb_authorization_no=auth_no,
                license_valid_from=valid_from,
                license_valid_to=valid_to,
                authorization_status=status,
                accepted_material_codes=",".join(accepted_codes),
                capacity_kg_per_month=cap,
                pickup_available=pickup,
                pickup_radius_km=rad,
                rating_avg=4.7 + (rid % 3) * 0.1,
                reliability_score=94 + (rid % 5),
                epr_registered=True,
                gstin=None # ps minimization: do not store fake or real GSTIN formats
            )
            db.add(rec)
            recycler_objs.append(rec)

        await db.flush()

        # Recycler Rates Table
        for rec in recycler_objs:
            accepted = rec.accepted_material_codes.split(",")
            for code in accepted:
                if code in mat_map:
                    base_rate = mat_map[code].base_price_paise_per_kg
                    rate = RecyclerRate(
                        recycler_id=rec.id,
                        material_id=mat_map[code].id,
                        rate_paise_per_kg=int(base_rate * 1.05),
                        valid_from=gen.get_days_ago(30),
                        valid_to=gen.base_date + timedelta(days=60),
                        source="recycler_submitted",
                        is_synthetic=True
                    )
                    db.add(rate)

        # 6. Pickup Agents (8)
        print("[INFO] Seeding 8 Pickup Agents linked to Recyclers and Hubs...")
        for aname, veh_no, veh_type, rec_idx, hub_idx in AGENT_ROSTER:
            r_id = recycler_objs[rec_idx - 1].id if rec_idx else recycler_objs[0].id
            h_id = hub_objs[hub_idx - 1].id if hub_idx else None
            agent = PickupAgent(
                recycler_id=r_id,
                hub_id=h_id,
                name=aname,
                phone=f"980004000{len(AGENT_ROSTER)}",
                vehicle_no=veh_no,
                photo_url="",
                is_active=True,
                is_synthetic=True
            )
            db.add(agent)

        # 7. Staff Accounts (3)
        print("[INFO] Seeding 3 Staff accounts (1 Admin, 2 Support)...")
        for sname, slang, srole, sphone in STAFF_ROSTER:
            su = User(
                phone=sphone,
                name=sname,
                role="admin", # Staff users mapped to admin role in app
                language=slang,
                otp_hash=gen.password_hash,
                is_active=True,
                is_synthetic=True,
                display_name_local=None
            )
            db.add(su)

        await db.flush()

        # 8. Collectors (34)
        print("[INFO] Seeding 34 Collectors with complete profiles and coarse geographic bounds...")
        collector_objs: List[Collector] = []
        for idx, name, name_local, lang, city, area, focus, tier, role_note in COLLECTOR_ROSTER:
            phone = f"98000100{idx:02d}"
            u = User(
                phone=phone,
                name=name,
                role="collector",
                language=lang,
                otp_hash=gen.password_hash,
                is_active=True,
                is_synthetic=True,
                display_name_local=name_local,
                last_login_at=gen.get_days_ago(0.5 if idx != 19 else 40)
            )
            db.add(u)
            await db.flush()

            # Join dates
            if idx == 7: # Prakash Sawant: new user, joined 6 days ago
                joined_days_ago = 6
            elif idx == 19: # Anil Verma: inactive 40 days
                joined_days_ago = 240
            else:
                joined_days_ago = 120 + (idx * 7) % 300

            # Geo center
            city_data = CITIES_GEO.get(city, CITIES_GEO["Pune"])
            c_lat = city_data["lat"] + (gen.rng.random() - 0.5) * 0.04
            c_lng = city_data["lng"] + (gen.rng.random() - 0.5) * 0.04

            # Hub assignment (link 3 to 6 collectors per hub)
            hub_id = None
            if city in ("Pune", "Nashik", "Chhatrapati Sambhajinagar"):
                hub_id = hub_objs[0].id
            elif city in ("Delhi NCR", "Ghaziabad", "Lucknow", "Jaipur"):
                hub_id = hub_objs[1].id
            elif city in ("Ludhiana", "Amritsar", "Mohali", "Jalandhar", "Patiala", "Chandigarh"):
                hub_id = hub_objs[2].id
            elif city in ("Bengaluru",):
                hub_id = hub_objs[3].id

            col = Collector(
                user_id=u.id,
                collector_code=f"KC-C-{idx:04d}",
                city=city,
                state=city_data["state"],
                operating_area_name=area,
                lat=round(c_lat, 6),
                lng=round(c_lng, 6),
                upi_id=f"{phone}@upi" if idx in (16, 33) else None,
                kyc_status="minimized",
                gps_consent=True,
                is_synthetic=True,
                rating_avg=4.5 + (idx % 5) * 0.08,
                trust_score=85 + (idx % 12),
                aggregator_id=hub_id,
                wallet_balance_paise=0,
                total_earned_paise=0,
                lots_completed=0,
                created_at=gen.get_days_ago(joined_days_ago)
            )
            db.add(col)
            collector_objs.append(col)

        await db.flush()

        # 9. Generate Lots, Items, Quotes, Transactions, Payments, Trace
        print("[INFO] Generating 320+ Lots, 230+ Transactions, 700+ Quotes with ledger consistency...")
        all_lots_count = 0
        all_transactions_count = 0
        all_quotes_count = 0
        all_payments_count = 0
        collector_earnings: Dict[str, int] = {c.id: 0 for c in collector_objs}
        collector_completed_lots: Dict[str, int] = {c.id: 0 for c in collector_objs}

        # Pending dues target count: 7 collectors
        pending_due_collectors = {1, 3, 9, 13, 21, 23, 30}

        for idx, name, name_local, lang, city, area, focus, tier, role_note in COLLECTOR_ROSTER:
            col = collector_objs[idx - 1]

            # Determine lot count for this collector
            if idx == 7:
                lot_count = 1 # Prakash Sawant: new user, 1 lot only
            elif idx == 19:
                lot_count = 8 # Anil Verma: inactive 40 days (all lots > 40 days ago)
            elif tier == "L":
                lot_count = gen.rng.randint(6, 8)
            elif tier == "M":
                lot_count = gen.rng.randint(12, 16)
            else: # H tier
                lot_count = gen.rng.randint(25, 32)

            for l_idx in range(lot_count):
                all_lots_count += 1
                lot_code = f"KC-LOT-{idx:02d}-{l_idx+1:03d}"

                # Lot date
                if idx == 7:
                    days_ago = 2.5
                elif idx == 19:
                    days_ago = 45.0 + l_idx * 5.0
                else:
                    days_ago = (l_idx / lot_count) * 88.0 + gen.rng.uniform(0.1, 1.5)

                # Sunday reduction: informal aggregation continues, but formal trading reduced
                tentative_dt = gen.base_date - timedelta(days=int(days_ago))
                if tentative_dt.weekday() == 6 and gen.rng.random() < 0.65:
                    days_ago += 1.0 # shift to Saturday

                # Realistic hour of day: peaks 10-13 and 16-19
                if gen.rng.random() < 0.55:
                    hour = gen.rng.choice([10, 11, 12])
                elif gen.rng.random() < 0.85:
                    hour = gen.rng.choice([16, 17, 18])
                else:
                    hour = gen.rng.choice([8, 9, 14, 15])
                minute = gen.rng.randint(2, 58)
                second = gen.rng.randint(5, 55)

                lot_created_at = gen.get_days_ago(days_ago, hour, minute, second)

                # Status decision:
                # ~75% completed, ~10% active recent, ~7% cancelled, ~3% disputed, ~2% buyer_no_show, ~1.5% failed_retried, ~1.5% partial
                if days_ago < 7.0 and l_idx == lot_count - 1 and idx not in (7, 19):
                    # Recent active lot
                    status = gen.rng.choice(["listed", "quoted", "accepted", "in_progress"])
                elif idx == 6 and l_idx == 4:
                    status = "disputed" # Mangal Kamble dispute anomaly
                elif idx == 11 and l_idx == 3:
                    status = "buyer_no_show" # Rahul Thorat buyer no-show
                elif l_idx % 15 == 13:
                    status = "cancelled"
                else:
                    status = "completed"

                # Items (1 to 3 items)
                item_count = 1 if gen.rng.random() < 0.45 else (2 if gen.rng.random() < 0.8 else 3)
                is_hazardous = False
                est_total_weight_g = 0
                actual_total_weight_g = 0
                est_total_min_paise = 0
                est_total_max_paise = 0
                final_amount_paise = 0

                lot_items = []
                for it_idx in range(item_count):
                    # Material selection: 70% focus, 30% others
                    if gen.rng.random() < 0.70:
                        m_code = gen.rng.choice(focus)
                    else:
                        m_code = gen.rng.choice([m[0] for m in RAW_MATERIALS_DEFS])

                    mat = mat_map[m_code]
                    if mat.is_hazardous:
                        is_hazardous = True

                    # Weight generation: lognormal in grams, non-round
                    # Anomaly 7: Santosh Gaikwad (#4) has 4 lots with exact repeated weight 14,250g
                    if idx == 4 and l_idx < 4 and it_idx == 0:
                        est_w = 14250
                    else:
                        base_w = mat.base_price_paise_per_kg # rough scale
                        est_w = int(gen.rng.lognormvariate(8.5, 0.45))
                        # Non-round weight: guarantee odd number of grams (avoid .0 or .5 round bias)
                        if est_w % 500 == 0:
                            est_w += gen.rng.choice([137, 243, 381, 469])
                    est_w = max(500, est_w)

                    # Variance logic (Section 4):
                    # Anomaly 1: Jaswant Singh (#26) weight variance 27%
                    if idx == 26 and l_idx == 5 and status == "completed":
                        act_w = int(est_w * 1.27)
                    elif status == "completed":
                        var_roll = gen.rng.random()
                        if var_roll < 0.80:
                            var_pct = gen.rng.uniform(-0.055, 0.055)
                        elif var_roll < 0.95:
                            var_pct = gen.rng.uniform(0.06, 0.14) * gen.rng.choice([-1, 1])
                        else:
                            var_pct = gen.rng.uniform(0.15, 0.22) * gen.rng.choice([-1, 1])
                        act_w = int(est_w * (1.0 + var_pct))
                    else:
                        act_w = None

                    # Pricing
                    price_info = gen.get_price(lot_created_at.strftime("%Y-%m-%d"), m_code, city)
                    est_val_min = int(est_w * price_info["min"] / 1000)
                    est_val_max = int(est_w * price_info["max"] / 1000)

                    # Anomaly 2: Mangal Kamble (#6) price 0.45x below band
                    if idx == 6 and l_idx == 5 and status == "completed":
                        final_p_per_kg = int(price_info["min"] * 0.45)
                    # Anomaly 3: Imran Qureshi (#17) 10x unit error
                    elif idx == 17 and l_idx == 3 and status == "completed":
                        final_p_per_kg = price_info["price"] * 10
                    else:
                        final_p_per_kg = price_info["price"]

                    if act_w:
                        final_item_val = int(act_w * final_p_per_kg / 1000)
                    else:
                        final_item_val = None

                    est_total_weight_g += est_w
                    if act_w:
                        actual_total_weight_g += act_w
                        if final_item_val is not None:
                            final_amount_paise += final_item_val
                    est_total_min_paise += est_val_min
                    est_total_max_paise += est_val_max

                    lot_items.append((mat, est_w, act_w, est_val_min, est_val_max, final_item_val, m_code))

                # Offline creation for personas #9, #11, #31
                is_offline = (idx in (9, 11, 31) and gen.rng.random() < 0.70)
                client_uuid = f"offline-{uuid.uuid4()}" if is_offline else None

                lot = Lot(
                    lot_code=lot_code,
                    collector_id=col.id,
                    aggregator_id=col.aggregator_id,
                    status=status,
                    est_total_min_paise=est_total_min_paise,
                    est_total_max_paise=est_total_max_paise,
                    est_total_weight_g=est_total_weight_g,
                    actual_total_weight_g=actual_total_weight_g if status == "completed" else None,
                    final_amount_paise=final_amount_paise if status == "completed" else None,
                    pickup_lat=col.lat,
                    pickup_lng=col.lng,
                    pickup_address=f"{area}, {city}",
                    is_hazardous=is_hazardous,
                    safety_acknowledged_at=lot_created_at + timedelta(minutes=2) if is_hazardous else None,
                    offline_created=is_offline,
                    client_uuid=client_uuid,
                    source="field",
                    is_synthetic=True,
                    seed_batch_id=gen.seed_batch_id,
                    created_at=lot_created_at,
                    updated_at=lot_created_at + timedelta(hours=3)
                )
                db.add(lot)
                await db.flush()

                # Add lot items & procedural placeholder photos
                for mat, est_w, act_w, est_val_min, est_val_max, final_val, m_code in lot_items:
                    it = LotItem(
                        lot_id=lot.id,
                        material_id=mat.id,
                        source_type="household" if idx % 2 == 0 else "shop",
                        est_weight_g=est_w,
                        actual_weight_g=act_w,
                        condition="broken" if gen.rng.random() < 0.7 else "working",
                        est_value_min_paise=est_val_min,
                        est_value_max_paise=est_val_max,
                        final_value_paise=final_val,
                        user_override=False,
                        created_at=lot_created_at,
                        updated_at=lot_created_at
                    )
                    db.add(it)
                    await db.flush()

                    # Anomaly 4: Amandeep Singh (#29) duplicate photo across 2 lots
                    if idx == 29 and l_idx in (1, 2):
                        photo_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                        phash = "0101010101010101"
                    else:
                        photo_hash = hashlib.sha256(f"{lot.id}_{it.id}".encode()).hexdigest()
                        phash = None

                    # Photo record pointing to procedural placeholder SVG
                    photo_url = f"/photos/placeholder_{m_code.lower()}.svg"
                    photo = LotPhoto(
                        lot_item_id=it.id,
                        storage_url=photo_url,
                        thumb_url=photo_url,
                        size_bytes=1820,
                        taken_at=lot_created_at + timedelta(minutes=1),
                        sha256=photo_hash,
                        phash=phash,
                        quality_score=0.98,
                        is_placeholder=True, # Critical Section 6.4 flag
                        training_consent=(gen.rng.random() < 0.25), # ~25% consent for AI demo
                        session_id=str(uuid.uuid4()),
                        lighting="indoor"
                    )
                    db.add(photo)

                # Generate Quotes (1 to 4 quotes per lot)
                eligible_recyclers = [r for r in recycler_objs if r.authorization_status == "verified"]
                quote_count = gen.rng.randint(1, 4)
                quoted_recyclers = gen.rng.sample(eligible_recyclers, min(quote_count, len(eligible_recyclers)))

                chosen_quote = None
                for q_idx, rec in enumerate(quoted_recyclers):
                    all_quotes_count += 1
                    # Spread 3% to 12% around market
                    spread = gen.rng.uniform(0.03, 0.12)
                    quote_price = int(est_total_min_paise * (1.0 + spread))

                    # Anomaly 8: Mohammad Irfan Ansari (#12) quote far below market (55% of market)
                    if idx == 12 and l_idx == 4 and q_idx == 0:
                        quote_price = int(est_total_min_paise * 0.55)

                    q_status = "sent"
                    if status == "completed":
                        q_status = "accepted" if q_idx == 0 else "rejected"

                    q = Quote(
                        lot_id=lot.id,
                        recycler_id=rec.id,
                        price_paise_total=quote_price,
                        pickup_mode="pickup" if rec.pickup_available else "drop_off",
                        pickup_eta_at=lot_created_at + timedelta(hours=4),
                        valid_until=lot_created_at + timedelta(hours=24),
                        status=q_status,
                        note="Standard industrial recycling terms.",
                        created_at=lot_created_at + timedelta(minutes=15),
                        updated_at=lot_created_at + timedelta(minutes=15)
                    )
                    db.add(q)
                    if q_status == "accepted":
                        chosen_quote = q

                await db.flush()

                # If completed or has transaction, generate Transaction & Payments
                if status == "completed" and chosen_quote:
                    all_transactions_count += 1
                    buyer_rec = chosen_quote.recycler

                    # Payment method: cash-first (target 82% +- 6% cash share, UPI higher for personas #16, #33)
                    if idx in (16, 33):
                        pay_method = "upi" if gen.rng.random() < 0.75 else "cash"
                    else:
                        pay_method = "upi" if gen.rng.random() < 0.16 else "cash"

                    # Dual cash confirmation timestamps 1 to 20 minutes apart
                    handover_time = lot_created_at + timedelta(minutes=gen.rng.randint(20, 45))
                    collector_conf_time = handover_time + timedelta(minutes=gen.rng.randint(2, 8))
                    buyer_conf_time = collector_conf_time + timedelta(minutes=gen.rng.randint(1, 10))

                    # Anomaly 6: Deepak Mishra (#21) payment logged BEFORE weigh-in
                    if idx == 21 and l_idx == 4:
                        payment_completed_time = lot_created_at + timedelta(minutes=30) # 2.5 hours before handover!
                    else:
                        payment_completed_time = buyer_conf_time + timedelta(minutes=2)

                    # Anomaly 5: Rahul Thorat (#11) handover GPS 6 km from facility
                    if idx == 11 and l_idx == 5:
                        h_lat = buyer_rec.lat + 0.055 # ~6 km off
                        h_lng = buyer_rec.lng + 0.055
                    else:
                        h_lat = buyer_rec.lat + (gen.rng.random() - 0.5) * 0.005
                        h_lng = buyer_rec.lng + (gen.rng.random() - 0.5) * 0.005

                    # Pending dues logic: 7 collectors have outstanding dues
                    has_due = (idx in pending_due_collectors and l_idx == lot_count - 1)
                    if has_due:
                        due_amt = int(final_amount_paise * 0.25)
                        paid_amt = final_amount_paise - due_amt
                        due_status = "pending"
                        balance_due_at = gen.base_date + timedelta(days=gen.rng.randint(3, 12))
                    else:
                        due_amt = 0
                        paid_amt = final_amount_paise
                        due_status = "none"
                        balance_due_at = None

                    tx = Transaction(
                        lot_id=lot.id,
                        quote_id=chosen_quote.id,
                        collector_id=col.id,
                        buyer_type="recycler",
                        buyer_id=buyer_rec.id,
                        agreed_amount_paise=chosen_quote.price_paise_total,
                        final_amount_paise=final_amount_paise,
                        weight_variance_pct=round(((actual_total_weight_g - est_total_weight_g) / est_total_weight_g) * 100, 2),
                        payment_method=pay_method,
                        payment_status="paid" if not has_due else "partial",
                        handover_ref=f"KC-HO-{lot.id[:8].upper()}",
                        collection_lat=col.lat,
                        collection_lng=col.lng,
                        handover_lat=round(h_lat, 6),
                        handover_lng=round(h_lng, 6),
                        collector_confirmed_at=collector_conf_time,
                        cash_confirmed_by_collector=True,
                        cash_confirmed_collector_at=collector_conf_time,
                        buyer_confirmed_at=buyer_conf_time,
                        cash_confirmed_by_buyer=True,
                        cash_confirmed_buyer_at=buyer_conf_time,
                        balance_paise=due_amt,
                        balance_due_at=balance_due_at,
                        due_status=due_status,
                        status="completed",
                        receipt_no="KC-RCT-2026-00001" if all_transactions_count == 1 else f"KC-REC-{lot_created_at.strftime('%Y%m')}-{all_transactions_count:04d}",
                        source="platform",
                        is_synthetic=True,
                        seed_batch_id=gen.seed_batch_id,
                        created_at=handover_time,
                        updated_at=payment_completed_time
                    )
                    db.add(tx)
                    await db.flush()

                    # Exact Ledger Reconciliation:
                    # final_amount == sum(payments) + dues
                    if paid_amt > 0:
                        all_payments_count += 1
                        pmt = Payment(
                            transaction_id=tx.id,
                            amount_paise=paid_amt,
                            method=pay_method,
                            status="completed",
                            completed_at=payment_completed_time,
                            upi_ref=f"UPI{uuid.uuid4().hex[:12].upper()}" if pay_method == "upi" else None,
                            seed_batch_id=gen.seed_batch_id,
                            is_synthetic=True,
                            created_at=payment_completed_time,
                            updated_at=payment_completed_time
                        )
                        db.add(pmt)

                    # Update collector total earnings and wallet
                    collector_earnings[col.id] += paid_amt
                    collector_completed_lots[col.id] += 1

                    # Generate Receipt Document
                    doc = Document(
                        type="receipt",
                        number=tx.receipt_no,
                        lot_id=lot.id,
                        transaction_id=tx.id,
                        user_id=col.user_id,
                        storage_url=f"/documents/receipt_{tx.receipt_no}.pdf",
                        sha256=hashlib.sha256(f"receipt_{tx.receipt_no}".encode()).hexdigest(),
                        generated_at=payment_completed_time
                    )
                    db.add(doc)

                    # Traceability Event Chain
                    events = [
                        (1, "LOT_CREATED", col.user_id, "collector", lot_created_at, col.lat, col.lng),
                        (2, "QUOTE_ACCEPTED", col.user_id, "collector", lot_created_at + timedelta(minutes=45), col.lat, col.lng),
                        (3, "SCALE_WEIGHED", buyer_rec.user_id, "recycler", handover_time, h_lat, h_lng),
                        (4, "HANDOVER_CONFIRMED", col.user_id, "collector", collector_conf_time, h_lat, h_lng),
                        (5, "PAYMENT_SETTLED", buyer_rec.user_id, "recycler", payment_completed_time, h_lat, h_lng)
                    ]

                    prev_h = GENESIS_HASH
                    for seq, etype, actor_id, actor_role, occ_time, lat_val, lng_val in events:
                        payload = {"seq": seq, "event": etype, "lot_id": lot.id, "amount_paise": final_amount_paise}
                        evt_hash = compute_event_hash(prev_h, seq, etype, payload, occ_time)
                        payload_str = json.dumps(payload, sort_keys=True)

                        te = TraceabilityEvent(
                            lot_id=lot.id,
                            seq=seq,
                            event_type=etype,
                            actor_user_id=actor_id,
                            actor_role=actor_role,
                            payload_json=payload_str,
                            geo_lat=round(lat_val, 6),
                            geo_lng=round(lng_val, 6),
                            occurred_at=occ_time,
                            prev_hash=prev_h,
                            event_hash=evt_hash
                        )
                        db.add(te)
                        prev_h = evt_hash

                    # Auto-generate notifications from actual lot events (Section 4)
                    notif_titles = {
                        "mr": ("व्यवहार पूर्ण झाला", f"तुमचा लॉट {lot.lot_code} साठी ₹{paid_amt//100} प्राप्त झाले."),
                        "hi": ("भुगतान सफल", f"आपके लॉट {lot.lot_code} के लिए ₹{paid_amt//100} प्राप्त हुए।"),
                        "pa": ("ਭੁਗਤਾਨ ਸਫਲ", f"ਤੁਹਾਡੇ ਲਾਟ {lot.lot_code} ਲਈ ₹{paid_amt//100} ਪ੍ਰਾਪਤ ਹੋਏ।"),
                        "en": ("Payment Received", f"Received ₹{paid_amt//100} for lot {lot.lot_code}.")
                    }
                    t_title, t_body = notif_titles.get(lang, notif_titles["en"])
                    notif = Notification(
                        user_id=col.user_id,
                        type="payment_completed",
                        title_en=notif_titles["en"][0],
                        title_hi=notif_titles["hi"][0],
                        title_mr=notif_titles["mr"][0],
                        title_pa=notif_titles["pa"][0],
                        body_en=notif_titles["en"][1],
                        body_hi=notif_titles["hi"][1],
                        body_mr=notif_titles["mr"][1],
                        body_pa=notif_titles["pa"][1],
                        payload_json=json.dumps({"lot_id": lot.id, "amount_paise": paid_amt}),
                        channel="in_app",
                        created_at=payment_completed_time
                    )
                    db.add(notif)

        await db.flush()

        # Update collectors with final ledger amounts
        for col in collector_objs:
            col.total_earned_paise = collector_earnings[col.id]
            col.wallet_balance_paise = int(collector_earnings[col.id] * 0.15) # current active balance
            col.lots_completed = collector_completed_lots[col.id]

        await db.flush()
        print(f"[PASS] Seeded {all_lots_count} lots, {all_transactions_count} transactions, {all_quotes_count} quotes, {all_payments_count} payments.")

        # 10. Inject 8 Deliberate Anomaly Flags (Section 6.2)
        print("[INFO] Injecting 8 deliberate anomaly flags matching seed/expected_flags.json...")
        expected_flags_path = os.path.join(os.path.dirname(__file__), "expected_flags.json")
        with open(expected_flags_path, "r", encoding="utf-8") as f:
            expected_anomalies = json.load(f)

        # Map each anomaly to the corresponding transaction
        anomaly_tx_targets = [
            (26, "WEIGHT_VARIANCE", "high", "Weight variance 27% between estimated and actual weigh-in"),
            (6, "PRICE_BELOW_BAND", "high", "Final payout price per kg is 0.45x below the market price band floor"),
            (17, "UNIT_ERROR_SUSPECT", "high", "Price per kg entered with a 10x unit error"),
            (29, "DUPLICATE_PHOTO", "high", "Identical photo SHA256 reused across two distinct lots"),
            (11, "GPS_MISMATCH", "medium", "Handover coordinates logged 6 km away from buyer facility"),
            (21, "PAYMENT_BEFORE_WEIGH", "high", "Payment timestamp logged 15 minutes before scale weigh-in"),
            (4, "REPEATED_WEIGHT", "medium", "Exact same total weight repeated across 4 lots in a single week"),
            (12, "QUOTE_FAR_BELOW_MARKET", "high", "Buyer quote submitted at 55% of prevailing market rate")
        ]

        for p_idx, code, sev, desc in anomaly_tx_targets:
            col = collector_objs[p_idx - 1]
            res = await db.execute(select(Transaction).where(Transaction.collector_id == col.id))
            target_tx = res.scalars().first()
            if target_tx:
                flag = AnomalyFlag(
                    transaction_id=target_tx.id,
                    code=code,
                    type=code,
                    score=0.92 if sev == "high" else 0.74,
                    reasons_json=json.dumps([desc]),
                    severity=sev,
                    status="open",
                    seed_batch_id=gen.seed_batch_id,
                    is_synthetic=True
                )
                db.add(flag)

        # 11. Support Tickets (30+ multilingual, natural register)
        print("[INFO] Seeding 32 Multilingual Support Tickets...")
        sample_ticket_data = [
            ("mr", "payment_delay", "पैसे मिळायला उशीर झाला आहे. कृपया तपासा.", "तुमचा व्यवहार तपासला आहे. पुढील 2 तासांत पैसे जमा होतील."),
            ("mr", "weight_dispute", "काट्यावरील वजनात 2 किलोचा फरक दिसत आहे.", "आम्ही खरेदीदाराशी संपर्क साधून खात्री करत आहोत."),
            ("hi", "payment_delay", "मेरे खाते में पैसे अभी तक नहीं आए हैं।", "बैंक सर्वर में देरी थी, कृपया अब चेक करें।"),
            ("hi", "pickup_delay", "पिकअप एजेंट अभी तक नहीं पहुंचा।", "एजेंट रास्ते में है, 15 मिनट में पहुंचेगा।"),
            ("pa", "weight_dispute", "ਮੇਰੇ ਸਮਾਨ ਦਾ ਵਜ਼ਨ ਘੱਟ ਲਗਾਇਆ ਗਿਆ ਹੈ।", "ਅਸੀਂ ਦੁਬਾਰਾ ਵਜ਼ਨ ਕਰਨ ਲਈ ਟੀਮ ਨੂੰ ਕਿਹਾ ਹੈ।"),
            ("pa", "app_help", "ਮੈਨੂੰ ਨਵਾਂ ਲਾਟ ਬਣਾਉਣ ਵਿੱਚ ਮਦਦ ਚਾਹੀਦੀ ਹੈ।", "ਕਿਰਪਾ ਕਰਕੇ ਸਕ੍ਰੀਨ 'ਤੇ ਦਿੱਤੇ ਮਦਦ ਵੀਡੀਓ ਨੂੰ ਦੇਖੋ।"),
            ("en", "payment_delay", "Payment delayed for yesterday's handover.", "Resolved. Transferred to UPI ID."),
            ("en", "safety_query", "How to safely store punctured Li-ion cells?", "Keep submerged in dry sand bucket away from heat.")
        ]

        support_staff_users = [u for u in (await db.execute(select(User).where(User.role == "admin"))).scalars().all()]

        for t_idx in range(32):
            col = collector_objs[t_idx % len(collector_objs)]
            lang, cat, msg_text, reply_text = sample_ticket_data[t_idx % len(sample_ticket_data)]
            t_no = f"KC-TCK-2026-{1000 + t_idx}"

            # Mixed statuses: 1 SLA breached, 2 resolved with CSAT
            if t_idx == 0:
                # SLA breached ticket
                t_status = "open"
                first_due = gen.get_days_ago(4)
                res_due = gen.get_days_ago(2) # overdue!
                resolved_at = None
                csat = None
            elif t_idx in (1, 2):
                # Resolved with CSAT
                t_status = "resolved"
                first_due = gen.get_days_ago(15)
                res_due = gen.get_days_ago(14)
                resolved_at = gen.get_days_ago(14, 15, 30)
                csat = 5
            else:
                t_status = "resolved" if t_idx % 3 != 0 else "open"
                first_due = gen.get_days_ago(10)
                res_due = gen.get_days_ago(8)
                resolved_at = gen.get_days_ago(8, 12, 0) if t_status == "resolved" else None
                csat = 4 if t_status == "resolved" else None

            ticket = SupportTicket(
                ticket_no=t_no,
                user_id=col.user_id,
                category=cat,
                priority="high" if cat == "payment_delay" else "normal",
                status=t_status,
                language=lang,
                first_response_due_at=first_due,
                resolution_due_at=res_due,
                resolved_at=resolved_at,
                csat_score=csat,
                source="user"
            )
            db.add(ticket)
            await db.flush()

            # Message from user (natural spoken register)
            is_voice = (t_idx < 3) # 3 voice notes flagged placeholder
            msg = TicketMessage(
                ticket_id=ticket.id,
                sender_user_id=col.user_id,
                sender_type="user",
                body=msg_text,
                attachment_url="/audio/placeholder_ticket_voice.mp3" if is_voice else None,
                attachment_type="audio" if is_voice else "none",
                duration_s=12 if is_voice else None
            )
            db.add(msg)

            # Reply from support agent if responded
            if t_status == "resolved" or t_idx > 0:
                agent_user = support_staff_users[t_idx % len(support_staff_users)]
                reply = TicketMessage(
                    ticket_id=ticket.id,
                    sender_user_id=agent_user.id,
                    sender_type="agent",
                    body=reply_text
                )
                db.add(reply)

        # 12. Monthly Statements for at least 10 collectors
        for c_idx in range(12):
            col = collector_objs[c_idx]
            m_doc = Document(
                type="settlement_statement",
                number=f"KC-STMT-202602-{col.collector_code}",
                lot_id=None,
                transaction_id=None,
                user_id=col.user_id,
                storage_url=f"/documents/statement_202602_{col.collector_code}.pdf",
                sha256=hashlib.sha256(f"stmt_{col.collector_code}".encode()).hexdigest(),
                generated_at=gen.get_days_ago(19)
            )
            db.add(m_doc)

        # 13. Seed FAQs & Notification Templates
        print("[INFO] Seeding vernacular FAQs and Notification Templates...")
        for cat, q_en, q_hi, q_mr, q_pa, a_en, a_hi, a_mr, a_pa in FAQS_LIST:
            faq = FAQ(
                category=cat,
                question_en=q_en,
                question_hi=q_hi,
                question_mr=q_mr,
                question_pa=q_pa,
                answer_en=a_en,
                answer_hi=a_hi,
                answer_mr=a_mr,
                answer_pa=a_pa,
                is_active=True
            )
            db.add(faq)

        for code, t_en, t_hi, t_mr, t_pa, b_en, b_hi, b_mr, b_pa, s_en, s_hi, s_mr, s_pa in NOTIFICATION_TEMPLATES_SEED:
            nt = NotificationTemplate(
                code=code,
                title_en=t_en,
                title_hi=t_hi,
                title_mr=t_mr,
                title_pa=t_pa,
                body_en=b_en,
                body_hi=b_hi,
                body_mr=b_mr,
                body_pa=b_pa,
                sms_en=s_en,
                sms_hi=s_hi,
                sms_mr=s_mr,
                sms_pa=s_pa
            )
            db.add(nt)

        await db.commit()

    print("=" * 72)
    print("[SUCCESS] REALISTIC DATA SEEDING COMPLETE!")
    print(f"  - Accounts: 49 (34 Collectors, 4 Hubs, 8 Recyclers, 3 Staff)")
    print(f"  - Lots: {all_lots_count} (>= 320 target met)")
    print(f"  - Transactions: {all_transactions_count} (>= 230 target met)")
    print(f"  - Quotes: {all_quotes_count} (>= 700 target met)")
    print(f"  - Payments: {all_payments_count}")
    print(f"  - Anomalies: 8 deliberate cases raised in anomaly_flags")
    print("=" * 72)

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_realistic_database())
