import asyncio
import hashlib
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import async_session_maker, engine
from app.models.all_models import (
    FAQ,
    Aggregator,
    AnomalyFlag,
    Collector,
    Dataset,
    DatasetVersion,
    Document,
    Lot,
    LotItem,
    LotPhoto,
    MatchingWeight,
    Material,
    MaterialComposition,
    MaterialSubcategory,
    MLModel,
    Notification,
    NotificationTemplate,
    Payment,
    PickupAgent,
    PriceHistory,
    Quote,
    Recycler,
    RecyclerRate,
    TraceabilityEvent,
    Transaction,
    User,
)
from app.services.trace import GENESIS_HASH, compute_event_hash

CITIES = [
    {"city": "Delhi NCR", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096}
]

RAW_MATERIALS: list[dict[str, Any]] = [
    {
        "code": "PCB", "name_en": "Circuit Boards (PCB)", "name_hi": "सर्किट बोर्ड (पीसीबी)", "name_mr": "सर्किट बोर्ड (PCB)", "name_pa": "ਸਰਕਟ ਬੋਰਡ (ਪੀਸੀਬੀ)",
        "icon_key": "cpu", "base": 42000, "floor": 32000, "ceil": 55000, "hazardous": True, "hazard_level": "medium",
        "hazard_note_en": "Contains lead solder and brominated flame retardants. Do not burn.",
        "hazard_note_hi": "लेड सोल्डर और केमिकल होते हैं। खुली आग में न जलाएं।",
        "hazard_note_mr": "लेड सोल्डर आणि ज्वाला मंदक रसायने असतात. उघड्यावर जाळू नका.",
        "hazard_note_pa": "ਲੀਡ ਸੋਲਡਰ ਅਤੇ ਕੈਮੀਕਲ ਹੁੰਦੇ ਹਨ। ਅੱਗ ਵਿੱਚ ਨਾ ਸਾੜੋ।",
        "safety_tip_en": "Wear gloves and dust mask. Store in dry containers.",
        "safety_tip_hi": "दस्ताने और मास्क पहनें। सूखी जगह रखें।",
        "safety_tip_mr": "हातमोजे आणि मास्क वापरा. कोरड्या जागी ठेवा.",
        "safety_tip_pa": "ਦਸਤਾਨੇ ਅਤੇ ਮਾਸਕ ਪਾਓ। ਸੁੱਕੀ ਥਾਂ 'ਤੇ ਰੱਖੋ।",
        "strategic": True,
        "comp": [("cu", 180.0), ("au", 0.35), ("ag", 1.2), ("pd", 0.08), ("sn", 35.0)],
        "subcategories": [
            ("PCB_MOTHERBOARD", "High-Grade Server / Motherboard", "उच्च-श्रेणी मदरबोर्ड / सर्वर", "उच्च-दर्जाचा मदरबोर्ड / सर्व्हर", "ਉੱਚ-ਦਰਜੇ ਦਾ ਮਦਰਬੋਰਡ"),
            ("PCB_RAM_IC", "RAM & IC Gold Pin Boards", "रैम और आईसी गोल्ड पिन बोर्ड", "रॅम आणि आयसी गोल्ड पिन बोर्ड", "ਰੈਮ ਅਤੇ ਆਈਸੀ ਗੋਲਡ ਪਿੰਨ ਬੋਰਡ"),
            ("PCB_POWER_SUPPLY", "Low-Grade Power Supply / TV Board", "कम-श्रेणी पावर सप्लाई / टीवी बोर्ड", "कमी-दर्जाचा पॉवर सप्लाय / टीव्ही बोर्ड", "ਘੱਟ-ਦਰਜੇ ਦਾ ਪਾਵਰ ਸਪਲਾਈ ਬੋਰਡ")
        ]
    },
    {
        "code": "BATTERY_LI", "name_en": "Lithium-Ion Batteries", "name_hi": "लिथियम-आयन बैटरी", "name_mr": "लिथियम-आयन बॅटरी", "name_pa": "ਲਿਥੀਅਮ-ਆਇਨ ਬੈਟਰੀ",
        "icon_key": "battery-charging", "base": 18500, "floor": 14000, "ceil": 24000, "hazardous": True, "hazard_level": "high",
        "hazard_note_en": "Severe thermal runaway fire risk if punctured or wet.",
        "hazard_note_hi": "पंचर या गीली होने पर भयंकर आग का खतरा।",
        "hazard_note_mr": "छिद्र पडल्यास किंवा ओले झाल्यास भीषण आगीचा धोका.",
        "hazard_note_pa": "ਪੰਕਚਰ ਜਾਂ ਗਿੱਲੀ ਹੋਣ 'ਤੇ ਅੱਗ ਲੱਗਣ ਦਾ ਗੰਭੀਰ ਖ਼ਤਰਾ।",
        "safety_tip_en": "Tape terminals, never puncture, store in sand bucket away from sun.",
        "safety_tip_hi": "टर्मिनल पर टेप लगाएं, कभी छेद न करें, रेत की बाल्टी में रखें।",
        "safety_tip_mr": "टर्मिनल्सवर टेप लावा, छिद्र पाडू नका, वाळूच्या बादलीत ठेवा.",
        "safety_tip_pa": "ਟਰਮੀਨਲਾਂ 'ਤੇ ਟੇਪ ਲਗਾਓ, ਕਦੇ ਵੀ ਪੰਕਚਰ ਨਾ ਕਰੋ, ਰੇਤ ਵਿੱਚ ਰੱਖੋ।",
        "strategic": True,
        "comp": [("co", 140.0), ("li", 15.0), ("cu", 85.0), ("al", 50.0)],
        "subcategories": [
            ("BAT_18650", "Cylindrical 18650/21700 Cells", "बेलनाकार 18650 सेल", "दंडगोलाकार 18650 सेल्स", "ਸਿਲੰਡਰ 18650 ਸੈੱਲ"),
            ("BAT_POUCH", "Smartphone & Tablet Pouch Cells", "स्मार्टफोन पाउच बैटरी", "स्मार्टफोन पाउच बॅटरी", "ਸਮਾਰਟਫੋਨ ਪਾਊਚ ਬੈਟਰੀ"),
            ("BAT_EV_PACK", "EV / Solar LiFePO4 Module", "ईवी / सोलर लिथियम मॉड्यूल", "ईव्ही / सोलर लिथियम मॉड्यूल", "ਈਵੀ / ਸੋਲਰ ਲਿਥੀਅਮ ਮੌਡਿਊਲ")
        ]
    },
    {
        "code": "MAGNET", "name_en": "Rare-Earth Magnets (HDD/Motor)", "name_hi": "चुंबकीय पुर्जे (हार्डडिस्क/मोटर)", "name_mr": "दुर्मीळ-पृथ्वी चुंबक (HDD/मोटर)", "name_pa": "ਚੁੰਬਕੀ ਹਿੱਸੇ (ਹਾਰਡ ਡਿਸਕ/ਮੋਟਰ)",
        "icon_key": "magnet", "base": 24000, "floor": 19000, "ceil": 31000, "hazardous": False, "hazard_level": "low",
        "hazard_note_en": "High pinching risk for fingers; brittle NdFeB alloy.",
        "hazard_note_hi": "उंगलियों में चोट का जोखिम, भंगुर मिश्र धातु।",
        "hazard_note_mr": "बोटे चेपण्याचा धोका; नाजूक मिश्रधातू.",
        "hazard_note_pa": "ਉਂਗਲਾਂ ਨੂੰ ਚਿਪਕਣ ਦਾ ਖ਼ਤਰਾ, ਨਾਜ਼ੁਕ ਮਿਸ਼ਰਤ ਧਾਤੂ।",
        "safety_tip_en": "Keep separated with cardboard spacers; keep away from pace-makers.",
        "safety_tip_hi": "कार्डबोर्ड स्पैसर से अलग रखें; मोबाइल से दूर रखें।",
        "safety_tip_mr": "कार्डबोर्ड स्पेसरने वेगळे ठेवा; पेसमेकरपासून लांब ठेवा.",
        "safety_tip_pa": "ਗੱਤੇ ਦੇ ਸਪੇਸਰਾਂ ਨਾਲ ਵੱਖ ਰੱਖੋ; ਪੇਸ-ਮੇਕਰਾਂ ਤੋਂ ਦੂਰ ਰੱਖੋ।",
        "strategic": True,
        "comp": [("nd", 185.0), ("fe", 640.0)],
        "subcategories": [
            ("MAG_NDFEB_BLOCK", "High-Grade NdFeB Magnet Block", "उच्च-ग्रेड नियोडिमियम ब्लॉक", "उच्च-दर्जाचा निओडिमियम ब्लॉक", "ਨਿਓਡੀਮੀਅਮ ਬਲਾਕ"),
            ("MAG_HDD_VOICE", "HDD Voice Coil Actuator Magnet", "हार्ड डिस्क क्वाइल चुंबक", "हार्ड डिस्क कॉइल चुंबक", "ਹਾਰਡ ਡਿਸਕ ਕਵਾਇਲ ਚੁੰਬਕ")
        ]
    },
    {
        "code": "CRT", "name_en": "CRT Monitors & TV Glass", "name_hi": "सीआरटी स्क्रीन व कांच", "name_mr": "सीआरटी मॉनिटर्स आणि टीव्ही काच", "name_pa": "ਸੀਆਰਟੀ ਸਕ੍ਰੀਨ ਅਤੇ ਕੱਚ",
        "icon_key": "tv", "base": 1200, "floor": 800, "ceil": 1800, "hazardous": True, "hazard_level": "high",
        "hazard_note_en": "Funnel glass contains 1.5-2.5 kg of toxic lead; screen has phosphor.",
        "hazard_note_hi": "कांच में 2 किलो तक जहरीला सीसा (Lead) और फॉस्फोर होता है।",
        "hazard_note_mr": "काचेत 2 किलोपर्यंत विषारी शिसे (Lead) आणि फॉस्फर असते.",
        "hazard_note_pa": "ਕੱਚ ਵਿੱਚ 2 ਕਿਲੋ ਤੱਕ ਜ਼ਹਿਰੀਲਾ ਸਿੱਕਾ (Lead) ਹੁੰਦਾ ਹੈ।",
        "safety_tip_en": "Never break glass. Carry upright with 2 persons wearing eye protection.",
        "safety_tip_hi": "कांच कभी न फोड़ें। चश्मा पहनकर सावधानी से उठाएं।",
        "safety_tip_mr": "काच कधीही फोडू नका. संरक्षणात्मक गॉगल घालून उचला.",
        "safety_tip_pa": "ਕਦੇ ਵੀ ਕੱਚ ਨਾ ਤੋੜੋ। ਅੱਖਾਂ ਦੀ ਸੁਰੱਖਿਆ ਰੱਖੋ।",
        "strategic": False,
        "comp": [("pb", 120.0), ("fe", 80.0), ("cu", 40.0)],
        "subcategories": [
            ("CRT_MONITOR", "Computer CRT Monitor (Colour)", "कंप्यूटर सीआरटी मॉनिटर", "संगणक सीआरटी मॉनिटर", "ਕੰਪਿਊਟਰ ਸੀਆਰਟੀ ਮਾਨੀਟਰ"),
            ("CRT_TV_HEAVY", "Heavy Television Tube (>21 inch)", "बड़ा टीवी ट्यूब", "मोठा टीव्ही ट्यूब", "ਵੱਡਾ ਟੀਵੀ ਟਿਊਬ")
        ]
    },
    {
        "code": "LCD", "name_en": "LCD / LED Displays", "name_hi": "एलसीडी / एलईडी डिस्प्ले", "name_mr": "एलसीडी / एलईडी डिस्प्ले", "name_pa": "ਐਲਸੀਡੀ / ਐਲਈਡੀ ਡਿਸਪਲੇ",
        "icon_key": "monitor", "base": 6500, "floor": 4500, "ceil": 9000, "hazardous": True, "hazard_level": "medium",
        "hazard_note_en": "Cold cathode backlights in older LCDs contain toxic mercury vapour.",
        "hazard_note_hi": "पुरानी स्क्रीन में पारा (मरकरी) गैस की नलियां होती हैं।",
        "hazard_note_mr": "जुन्या पडद्यांमध्ये विषारी पारा (मर्क्युरी) वायू असतो.",
        "hazard_note_pa": "ਪੁਰਾਣੀਆਂ ਸਕ੍ਰੀਨਾਂ ਵਿੱਚ ਪਾਰਾ (ਮਰਕਰੀ) ਗੈਸ ਹੁੰਦੀ ਹੈ।",
        "safety_tip_en": "Keep panels flat. Do not twist or puncture backlight assembly.",
        "safety_tip_hi": "पैनल को सीधा रखें, मरोड़ें या तोड़ें नहीं।",
        "safety_tip_mr": "पॅनेल सपाट ठेवा. वाकवू नका किंवा काच फोडू नका.",
        "safety_tip_pa": "ਪੈਨਲਾਂ ਨੂੰ ਸਮਤਲ ਰੱਖੋ, ਮਰੋੜੋ ਜਾਂ ਤੋੜੋ ਨਾ।",
        "strategic": False,
        "comp": [("al", 90.0), ("cu", 30.0), ("sn", 10.0)],
        "subcategories": [
            ("LCD_LED_PANEL", "LED Backlit Slim Panel", "एलईडी स्लिम डिस्प्ले पैनल", "एलईडी स्लिम डिस्प्ले पॅनेल", "ਐਲਈਡੀ ਸਲਿਮ ਪੈਨਲ"),
            ("LCD_CCFL_PANEL", "CCFL Mercury Tube Panel", "सीसीएफएल मरकरी ट्यूब पैनल", "सीसीएफएल मर्क्युरी ट्यूब पॅनेल", "ਮਰਕਰੀ ਟਿਊਬ ਪੈਨਲ")
        ]
    },
    {
        "code": "CABLE", "name_en": "Copper Cables & Wires", "name_hi": "तांबे के तार व केबल", "name_mr": "तांब्याची वायर आणि केबल्स", "name_pa": "ਤਾਂਬੇ ਦੀਆਂ ਤਾਰਾਂ ਅਤੇ ਕੇਬਲ",
        "icon_key": "cable", "base": 51000, "floor": 42000, "ceil": 62000, "hazardous": False, "hazard_level": "low",
        "hazard_note_en": "Open burning PVC insulation releases toxic dioxins into air.",
        "hazard_note_hi": "तारों को खुले में जलाने से कैंसरकारी धुआं निकलता है। कभी न जलाएं।",
        "hazard_note_mr": "वायर उघड्यावर जाळल्याने विषारी धूर निघतो.",
        "hazard_note_pa": "ਤਾਰਾਂ ਨੂੰ ਸਾੜਨ ਨਾਲ ਜ਼ਹਿਰੀਲਾ ਧੂੰਆਂ ਨਿਕਲਦਾ ਹੈ। ਕਦੇ ਨਾ ਸਾੜੋ।",
        "safety_tip_en": "Never burn cables. Use mechanical wire strippers or sell insulated.",
        "safety_tip_hi": "तार न जलाएं, स्ट्रिपर का प्रयोग करें या इंसुलेटेड ही बेचें।",
        "safety_tip_mr": "वायर जाळू नका, मेकॅनिकल स्ट्रिपर वापरा किंवा इन्सुलेटेड विका.",
        "safety_tip_pa": "ਤਾਰਾਂ ਨਾ ਸਾੜੋ, ਮਸ਼ੀਨੀ ਸਟ੍ਰਿਪਰ ਦੀ ਵਰਤੋਂ ਕਰੋ।",
        "strategic": True,
        "comp": [("cu", 550.0), ("al", 50.0)],
        "subcategories": [
            ("CABLE_MILLBERRY", "Bare Bright Copper Wire (Millberry)", "चमकदार तांबा तार (मिलबेरी)", "लख्ख तांब्याची वायर (मिलबेरी)", "ਚਮਕਦਾਰ ਤਾਂਬਾ ਤਾਰ"),
            ("CABLE_INSULATED_THIN", "Insulated Single-Core Wire", "इंसुलेटेड पतली तार", "इन्सुलेटेड बारीक वायर", "ਇੰਸੂਲੇਟਿਡ ਪਤਲੀ ਤਾਰ"),
            ("CABLE_HEAVY_ARMOURED", "Heavy Armoured Industrial Cable", "भारी आर्मर्ड औद्योगिक केबल", "हेव्ही आर्मर्ड औद्योगिक केबल", "ਭਾਰੀ ਆਰਮਰਡ ਕੇਬਲ")
        ]
    },
    {
        "code": "MOTOR", "name_en": "Electric Motors & Transformers", "name_hi": "इलेक्ट्रिक मोटर व ट्रांसफार्मर", "name_mr": "इलेक्ट्रिक मोटर्स आणि ट्रान्सफॉर्मर्स", "name_pa": "ਇਲੈਕਟ੍ਰਿਕ ਮੋਟਰਾਂ ਅਤੇ ਟ੍ਰਾਂਸਫਾਰਮਰ",
        "icon_key": "cog", "base": 22000, "floor": 18000, "ceil": 28000, "hazardous": False, "hazard_level": "low",
        "hazard_note_en": "Heavy lifting hazard; sharp copper winding ends.",
        "hazard_note_hi": "भारी वजन; तांबे के नुकीले तार से चोट का खतरा।",
        "hazard_note_mr": "जड वजन; तांब्याच्या टोकदार तारांनी जखम होण्याचा धोका.",
        "hazard_note_pa": "ਭਾਰੀ ਵਜ਼ਨ; ਤਾਂਬੇ ਦੀਆਂ ਤਾਰਾਂ ਤੋਂ ਸੱਟ ਲੱਗਣ ਦਾ ਖ਼ਤਰਾ।",
        "safety_tip_en": "Bend knees when lifting; wear reinforced leather work gloves.",
        "safety_tip_hi": "उठाते समय घुटने मोड़ें; चमड़े के मजबूत दस्ताने पहनें।",
        "safety_tip_mr": "उचलताना गुडघे वाकवा; लेदरचे मजबूत हातमोजे वापरा.",
        "safety_tip_pa": "ਚੁੱਕਣ ਸਮੇਂ ਗੋਡੇ ਮੋੜੋ; ਚਮੜੇ ਦੇ ਦਸਤਾਨੇ ਪਾਓ।",
        "strategic": True,
        "comp": [("cu", 160.0), ("fe", 720.0), ("al", 40.0)],
        "subcategories": [
            ("MOT_COPPER_WOUND", "Copper Wound Industrial Motor", "तांबे की वाइंडिंग मोटर", "तांब्याची वाइंडिंग मोटर", "ਤਾਂਬੇ ਦੀ ਵਾਇੰਡਿੰਗ ਮੋਟਰ"),
            ("MOT_ALUM_WOUND", "Aluminium Wound Domestic Motor", "एल्युमिनियम वाइंडिंग मोटर", "अ‍ॅल्युमिनियम वाइंडिंग मोटर", "ਐਲੂਮੀਨੀਅਮ ਵਾਇੰਡਿੰਗ ਮੋਟਰ")
        ]
    },
    {
        "code": "PLASTIC_MIXED", "name_en": "E-Waste Mixed Plastics", "name_hi": "ई-कचरा मिश्रित प्लास्टिक", "name_mr": "ई-कचरा मिश्र प्लास्टिक", "name_pa": "ਈ-ਕੂੜਾ ਮਿਕਸਡ ਪਲਾਸਟਿਕ",
        "icon_key": "recycle", "base": 2500, "floor": 1800, "ceil": 3500, "hazardous": False, "hazard_level": "low",
        "hazard_note_en": "ABS/HIPS casings with flame retardants.",
        "hazard_note_hi": "कैबिनेट का प्लास्टिक।",
        "hazard_note_mr": "कॅबिनेटचे एबीएस प्लास्टिक.",
        "hazard_note_pa": "ਕੈਬਨਿਟ ਦਾ ਪਲਾਸਟਿਕ।",
        "safety_tip_en": "Sort by color; keep clean from dirt and grease.",
        "safety_tip_hi": "रंग के अनुसार छांटें, धूल-मिट्टी से बचाएं।",
        "safety_tip_mr": "रंगानुसार वेगळे करा, धूळ-मातीपासून वाचवा.",
        "safety_tip_pa": "ਰੰਗ ਅਨੁਸਾਰ ਵੱਖ ਕਰੋ, ਸਾਫ਼ ਰੱਖੋ।",
        "strategic": False,
        "comp": [("fe", 10.0)],
        "subcategories": [
            ("PLASTIC_ABS_BLACK", "Clean Black ABS Computer Casings", "काला एबीएस प्लास्टिक कैबिनेट", "काळा एबीएस प्लास्टिक कॅबिनेट", "ਕਾਲਾ ਏਬੀਐਸ ਪਲਾਸਟਿਕ"),
            ("PLASTIC_HIPS_WHITE", "White HIPS Appliance Plastic", "सफेद एचआईपीएस प्लास्टिक", "पांढरा एचआयपीएस प्लास्टिक", "ਚਿੱਟਾ ਐਚਆਈਪੀਐਸ ਪਲਾਸਟਿਕ")
        ]
    },
    {
        "code": "BATTERY_PB", "name_en": "Lead-Acid UPS Batteries", "name_hi": "लेड-एसिड इन्वर्टर बैटरी", "name_mr": "लेड-अ‍ॅसिड इन्व्हर्टर बॅटरी", "name_pa": "ਲੈੱਡ-ਐਸਿਡ ਇਨਵਰਟਰ ਬੈਟਰੀ",
        "icon_key": "battery-warning", "base": 9500, "floor": 7500, "ceil": 12000, "hazardous": True, "hazard_level": "high",
        "hazard_note_en": "Contains concentrated sulphuric acid and soluble lead compounds.",
        "hazard_note_hi": "सल्फ्यूरिक एसिड (तेजाब) और सीसा होता है। जलने का खतरा।",
        "hazard_note_mr": "सल्फ्यूरिक अ‍ॅसिड आणि शिसे असते. त्वचा जळण्याचा धोका.",
        "hazard_note_pa": "ਤੇਜ਼ਾਬ ਅਤੇ ਸਿੱਕਾ ਹੁੰਦਾ ਹੈ। ਚਮੜੀ ਸੜਨ ਦਾ ਗੰਭੀਰ ਖ਼ਤਰਾ।",
        "safety_tip_en": "Keep upright; never drain acid into sewer; use rubber apron & boots.",
        "safety_tip_hi": "सीधा रखें; तेजाब नाली में न बहाएं; रबड़ के दस्ताने पहनें।",
        "safety_tip_mr": "उभी ठेवा; अ‍ॅसिड गटारात वाहू देऊ नका; रबरी हातमोजे वापरा.",
        "safety_tip_pa": "ਸਿੱਧਾ ਰੱਖੋ; ਤੇਜ਼ਾਬ ਨਾਲੀ ਵਿੱਚ ਨਾ ਸੁੱਟੋ; ਰਬੜ ਦੇ ਦਸਤਾਨੇ ਪਾਓ।",
        "strategic": False,
        "comp": [("pb", 580.0)],
        "subcategories": [
            ("BAT_PB_INVERTER", "Tall Tubular Inverter Battery", "ट्यूबलर इन्वर्टर बैटरी", "ट्युब्युलर इन्व्हर्टर बॅटरी", "ਟਿਊਬਲਰ ਇਨਵਰਟਰ ਬੈਟਰੀ"),
            ("BAT_PB_AUTOMOTIVE", "Automotive 12V Starter Battery", "ऑटोमोटिव 12V बैटरी", "ऑटोमोटिव्ह 12V बॅटरी", "ਆਟੋਮੋਟਿਵ 12V ਬੈਟਰੀ")
        ]
    },
    {
        "code": "OTHER", "name_en": "Mixed Electronic Appliances", "name_hi": "अन्य मिश्रित इलेक्ट्रॉनिक उपकरण", "name_mr": "इतर मिश्र इलेक्ट्रॉनिक उपकरणे", "name_pa": "ਹੋਰ ਮਿਕਸਡ ਇਲੈਕਟ੍ਰਾਨਿਕ ਸਮਾਨ",
        "icon_key": "package", "base": 4500, "floor": 3000, "ceil": 6500, "hazardous": False, "hazard_level": "low",
        "hazard_note_en": "Mixed composition of metals and polymers.",
        "hazard_note_hi": "विभिन्न धातुओं और प्लास्टिक का मिश्रण।",
        "hazard_note_mr": "विविध धातू आणि प्लास्टिकचे मिश्रण.",
        "hazard_note_pa": "ਵੱਖ-ਵੱਖ ਧਾਤਾਂ ਅਤੇ ਪਲਾਸਟਿਕ ਦਾ ਮਿਸ਼ਰਣ।",
        "safety_tip_en": "Unplug before disassembly; inspect for battery compartments.",
        "safety_tip_hi": "अलग करने से पहले प्लग निकालें; बैटरी पहले निकालें।",
        "safety_tip_mr": "उघडण्यापूर्वी प्लग काढा; बॅटरी आधी वेगळी करा.",
        "safety_tip_pa": "ਖੋਲ੍ਹਣ ਤੋਂ ਪਹਿਲਾਂ ਪਲੱਗ ਕੱਢੋ; ਬੈਟਰੀ ਪਹਿਲਾਂ ਵੱਖ ਕਰੋ।",
        "strategic": False,
        "comp": [("fe", 400.0), ("al", 80.0), ("cu", 50.0)],
        "subcategories": [
            ("OTHER_SM_APPLIANCE", "Small Appliances (Iron/Mixer)", "छोटे घरेलू उपकरण", "लहान घरगुती उपकरणे", "ਛੋਟੇ ਘਰੇਲੂ ਉਪਕਰਣ"),
            ("OTHER_IT_EQUIP", "Printers / Scanners / Networking", "प्रिंटर / स्कैनर / नेटवर्किंग", "प्रिंटर / स्कॅनर / नेटवर्किंग", "ਪ੍ਰਿੰਟਰ / ਸਕੈਨਰ")
        ]
    }
]

COLLECTOR_PROFILES = [
    ("Ram Lal", "9876543210", "Delhi NCR", "hi", "DL 1L AA 4012"),
    ("Surinder Kumar", "9876543211", "Chandigarh", "pa", "CH 01 TA 1923"),
    ("Mukesh Sharma", "9876543212", "Jaipur", "hi", "RJ 14 EA 9920"),
    ("Santosh Gaikwad", "9876543213", "Mumbai", "mr", "MH 01 AB 3412"),
    ("Shivappa Pujar", "9876543214", "Bengaluru", "en", "KA 05 TR 5501"),
    ("Birju Soren", "9876543215", "Ranchi", "hi", "JH 01 M 8812"),
    ("Harpreet Singh", "9876543216", "Ludhiana", "pa", "PB 10 Z 4091"),
    ("Pawan Verma", "9876543217", "Lucknow", "hi", "UP 32 BK 2219"),
    ("Jagtar Singh", "9876543218", "Amritsar", "pa", "PB 02 C 6744"),
    ("Arjun Kale", "9876543219", "Mumbai", "mr", "MH 03 TC 1109")
]

AGGREGATOR_PROFILES = [
    ("Mayapuri Metal Hub", "9812345670", "Delhi NCR", 400, "DL 01 AH 5510"),
    ("Ludhiana Industrial Scrap Corp", "9812345671", "Ludhiana", 350, "PB 10 CK 8920"),
    ("Dharavi Sustainable Circularity", "9812345672", "Mumbai", 450, "MH 01 CD 4410"),
    ("Jaipur E-Metal Aggregators", "9812345673", "Jaipur", 380, "RJ 14 GH 7812"),
    ("Peenya Eco Recoveries", "9812345674", "Bengaluru", 420, "KA 05 LM 9912")
]

RECYCLER_PROFILES = [
    ("EcoBirba Circular Recyclers", "9819810001", "Delhi NCR", "CPCB-REG-DL-2023-019", "SPCB-AUTH-DEL-9912"),
    ("Satluj Sustainable Refiners", "9819810002", "Ludhiana", "CPCB-REG-PB-2022-041", "SPCB-AUTH-PUN-3310"),
    ("Avishkar CleanTech Solutions", "9819810003", "Mumbai", "CPCB-REG-MH-2024-008", "SPCB-AUTH-MAH-8821"),
    ("Bharat Critical Minerals Recovery", "9819810004", "Jaipur", "CPCB-REG-RJ-2023-112", "SPCB-AUTH-RAJ-5519"),
    ("Karnataka Eco-Smelters", "9819810005", "Bengaluru", "CPCB-REG-KA-2022-077", "SPCB-AUTH-KAR-1290"),
    ("Jharkhand Rare Mineral Extractors", "9819810006", "Ranchi", "CPCB-REG-JH-2023-033", "SPCB-AUTH-JHK-7721"),
    ("GreenPulse Metals & E-Waste Ltd", "9819810007", "Chandigarh", "CPCB-REG-CH-2024-055", "SPCB-AUTH-CHD-6612")
]

PICKUP_AGENTS = [
    ("Vikram Yadav", "9811122201", "DL 1C AA 1102", "EcoBirba Circular Recyclers"),
    ("Kuldeep Singh", "9811122202", "PB 10 CT 8921", "GreenPulse Metals & E-Waste Ltd"),
    ("Amandeep Singh", "9811122203", "CH 01 BG 3319", "Satluj Sustainable Refiners"),
    ("Suresh Meena", "9811122204", "RJ 14 ED 5012", "Bharat Critical Minerals Recovery"),
    ("Pravin Sawant", "9811122205", "MH 02 CK 7711", "Avishkar CleanTech Solutions"),
    ("Ganesh Rao", "9811122206", "KA 05 MN 9023", "Karnataka Eco-Smelters"),
    ("Deepak Munda", "9811122207", "JH 01 BZ 4182", "Jharkhand Rare Mineral Extractors"),
    ("Mohan Lal", "9811122208", "DL 3C BB 1029", "EcoBirba Circular Recyclers")
]

FAQS_LIST = [
    ("pricing", "How is my scrap price calculated?", "मेरा कबाड़ मूल्य कैसे तय होता है?", "माझ्या भंगाराचा भाव कसा ठरवला जातो?", "ਮੇਰੇ ਕਬਾੜ ਦੀ ਕੀਮਤ ਕਿਵੇਂ ਤੈਅ ਹੁੰਦੀ ਹੈ?",
     "Prices are based on daily verified metal indices (copper, gold, lithium) multiplied by condition factor and weighed on certified digital scales.",
     "कीमतें दैनिक धातु सूचकांक (तांबा, सोना, लिथियम) और स्थिति गुणक पर आधारित होती हैं और प्रमाणित डिजिटल तराजू पर तौली जाती हैं।",
     "दररोजच्या प्रमाणित धातू निर्देशांकांवर (तांबे, सोने, लिथियम) आणि स्थिती गुणकावर भाव ठरतात आणि प्रमाणित डिजिटल काट्यावर वजन केले जाते.",
     "ਕੀਮਤਾਂ ਰੋਜ਼ਾਨਾ ਪ੍ਰਮਾਣਿਤ ਧਾਤੂ ਸੂਚਕਾਂਕ ਅਤੇ ਸਥਿਤੀ ਗੁਣਕ 'ਤੇ ਅਧਾਰਤ ਹੁੰਦੀਆਂ ਹਨ ਅਤੇ ਪ੍ਰਮਾਣਿਤ ਡਿਜੀਟਲ ਤੋਲ 'ਤੇ ਤੋਲੀਆਂ ਜਾਂਦੀਆਂ ਹਨ।"),
    ("payment", "How fast do I get paid?", "मुझे भुगतान कितनी जल्दी मिलता है?", "मला पैसे कधी मिळतात?", "ਮੈਨੂੰ ਭੁਗਤਾਨ ਕਿੰਨੀ ਜਲਦੀ ਮਿਲਦਾ ਹੈ?",
     "Cash is paid immediately upon digital handover confirmation. Instant UPI is also available if you enable digital payments.",
     "डिजिटल हैंडओवर की पुष्टि होते ही तुरंत नकद भुगतान मिल जाता है। यदि आप डिजिटल विकल्प चुनें तो यूपीआई भी उपलब्ध है।",
     "डिजिटल हस्तांतरणाची खात्री होताच जागेवर रोख पैसे मिळतात. आपण डिजिटल पर्याय निवडल्यास तात्काळ युपीआय देखील उपलब्ध आहे.",
     "ਡਿਜੀਟਲ ਹੈਂਡਓਵਰ ਦੀ ਪੁਸ਼ਟੀ ਹੁੰਦੇ ਹੀ ਤੁਰੰਤ ਨਕਦ ਭੁਗਤਾਨ ਮਿਲਦਾ ਹੈ। ਜੇਕਰ ਚਾਹੋ ਤਾਂ ਯੂਪੀਆਈ ਵੀ ਉਪਲਬਧ ਹੈ।"),
    ("dispute", "What if the buyer's scale shows less weight?", "यदि खरीदार का कांटा कम वजन दिखाए तो?", "खरेदीदाराचा काटा कमी वजन दाखवत असेल तर?", "ਜੇ ਖਰੀਦਦਾਰ ਦਾ ਕੰਡਾ ਘੱਟ ਵਜ਼ਨ ਦਿਖਾਵੇ ਤਾਂ ਕੀ ਕਰੀਏ?",
     "If variance is over 10%, the system alerts you immediately. You can accept the revised offer or tap 'Raise Dispute' to halt the transaction without penalty.",
     "यदि 10% से अधिक अंतर है, तो ऐप तुरंत सचेत करता है। आप संशोधित मूल्य स्वीकार कर सकते हैं या बिना किसी जुर्माने के 'विवाद दर्ज करें' चुन सकते हैं।",
     "जर वजनात 10% पेक्षा जास्त तफावत असेल, तर प्रणाली त्वरित सूचना देते. आपण व्यवहार थांबवून विनामूल्य तक्रार नोंदवू शकता.",
     "ਜੇਕਰ 10% ਤੋਂ ਵੱਧ ਅੰਤਰ ਹੈ, ਤਾਂ ਸਿਸਟਮ ਤੁਰੰਤ ਸੁਚੇਤ ਕਰਦਾ ਹੈ। ਤੁਸੀਂ 'ਵਿਵਾਦ ਦਰਜ ਕਰੋ' ਚੁਣ ਕੇ ਲੈਣ-ਦੇਣ ਰੋਕ ਸਕਦੇ ਹੋ।"),
    ("safety", "Why is open burning of wires prohibited?", "तारों को खुले में जलाना क्यों मना है?", "वायर उघड्यावर जाळण्यास बंदी का आहे?", "ਤਾਰਾਂ ਨੂੰ ਖੁੱਲ੍ਹੇ ਵਿੱਚ ਸਾੜਨਾ ਕਿਉਂ ਮਨ੍ਹਾ ਹੈ?",
     "Burning releases deadly cancer-causing dioxins and ruins valuable copper purity. Our authorized recyclers pay extra for unburnt cables.",
     "तार जलाने से कैंसर पैदा करने वाला जहरीला धुआं निकलता है और तांबे की शुद्धता घटती है। अधिकृत रिसाइकिलर बिना जली तारों के अधिक पैसे देते हैं।",
     "वायर जाळल्याने कर्करोग निर्माण करणारा विषारी धूर निघतो आणि तांब्याची गुणवत्ता घसरते. अधिकृत पुनर्वापरदार न जाळलेल्या वायरचे जास्त पैसे देतात.",
     "ਤਾਰਾਂ ਸਾੜਨ ਨਾਲ ਜ਼ਹਿਰੀਲਾ ਧੂੰਆਂ ਨਿਕਲਦਾ ਹੈ ਅਤੇ ਤਾਂਬੇ ਦੀ ਸ਼ੁੱਧਤਾ ਘਟਦੀ ਹੈ। ਅਧਿਕਾਰਤ ਰੀਸਾਈਕਲਰ ਬਿਨਾਂ ਸਾੜੀਆਂ ਤਾਰਾਂ ਦੇ ਵੱਧ ਪੈਸੇ ਦਿੰਦੇ ਹਨ।"),
    ("recycler", "What is a CPCB/SPCB authorized recycler?", "सीपीसीबी अधिकृत रिसाइकिलर क्या है?", "सीपीसीबी अधिकृत पुनर्वापरदार म्हणजे काय?", "ਸੀਪੀਸੀਬੀ ਅਧਿਕਾਰਤ ਰੀਸਾਈਕਲਰ ਕੀ ਹੈ?",
     "These are government-licensed facilities under E-Waste Rules 2022 that safely extract critical minerals and issue official pollution board certificates.",
     "ये ई-कचरा नियम 2022 के तहत सरकार द्वारा लाइसेंस प्राप्त स्वच्छ संयंत्र हैं जो पर्यावरण अनुकूल तरीके से महत्वपूर्ण खनिज निकालते हैं।",
     "हे ई-कचरा नियम 2022 अंतर्गत शासनाकडून परवानाप्राप्त स्वच्छ प्रकल्प आहेत जे सुरक्षितपणे महत्त्वपूर्ण खनिजे काढतात आणि प्रदूषण नियंत्रण प्रमाणपत्र देतात.",
     "ਇਹ ਈ-ਕੂੜਾ ਨਿਯਮ 2022 ਅਧੀਨ ਸਰਕਾਰ ਦੁਆਰਾ ਲਾਇਸੰਸਸ਼ੁਦਾ ਸਵੱਛ ਪਲਾਂਟ ਹਨ ਜੋ ਵਾਤਾਵਰਣ ਅਨੁਕੂਲ ਢੰਗ ਨਾਲ ਮਹੱਤਵਪੂਰਨ ਧਾਤਾਂ ਕੱਢਦੇ ਹਨ।")
]

NOTIFICATION_TEMPLATES_SEED = [
    ("quote_received", "New Quote Received", "नया कोटेशन मिला", "नवीन कोटेशन मिळाले", "ਨਵੀਂ ਕੋਟੇਸ਼ਨ ਮਿਲੀ",
     "Authorized recycler has offered a quote for your scrap lot.",
     "एक अधिकृत रिसाइकिलर ने आपके कबाड़ लॉट के लिए कोटेशन दिया है।",
     "अधिकृत पुनर्वापरदाराने आपल्या स्क्रॅप लॉटसाठी कोटेशन दिले आहे.",
     "ਇੱਕ ਅਧਿਕਾਰਤ ਰੀਸਾਈਕਲਰ ਨੇ ਤੁਹਾਡੇ ਕਬਾੜ ਲਾਟ ਲਈ ਕੋਟੇਸ਼ਨ ਭੇਜੀ ਹੈ।",
     "KC Alert: New quote received for your scrap lot. Open app to view.",
     "केसी अलर्ट: आपके कबाड़ लॉट के लिए नया कोटेशन मिला है। देखने के लिए ऐप खोलें।",
     "केसी अलर्ट: आपल्या स्क्रॅप लॉटसाठी नवीन कोटेशन आले आहे. पाहण्यासाठी ॲप उघडा.",
     "ਕੇਸੀ ਅਲਰਟ: ਤੁਹਾਡੇ ਕਬਾੜ ਲਾਟ ਲਈ ਨਵੀਂ ਕੋਟੇਸ਼ਨ ਮਿਲੀ ਹੈ। ਐਪ ਖੋਲ੍ਹੋ।"),
    ("agent_assigned", "Pickup Agent Assigned", "पिकअप एजेंट नियुक्त हुआ", "पिकअप एजंट नियुक्त झाला", "ਪਿਕਅੱਪ ਏਜੰਟ ਨਿਯੁਕਤ ਹੋਇਆ",
     "Pickup agent is en route. Live tracking is active.",
     "पिकअप एजेंट रास्ते में है। लाइव ट्रैकिंग सक्रिय है।",
     "पिकअप एजंट वाटेत आहे. थेट ट्रॅकिंग सुरू आहे.",
     "ਪਿਕਅੱਪ ਏਜੰਟ ਰਸਤੇ ਵਿੱਚ ਹੈ। ਲਾਈਵ ਟਰੈਕਿੰਗ ਸਰਗਰਮ ਹੈ।",
     "KC Alert: Agent en route for pickup. Track live in app.",
     "केसी अलर्ट: एजेंट पिकअप के लिए रास्ते में है। ऐप में लाइव देखें।",
     "केसी अलर्ट: एजंट पिकअपसाठी येत आहे. ॲपमध्ये थेट पहा.",
     "ਕੇਸੀ ਅਲਰਟ: ਏਜੰਟ ਪਿਕਅੱਪ ਲਈ ਰਸਤੇ ਵਿੱਚ ਹੈ। ਐਪ ਵਿੱਚ ਟਰੈਕ ਕਰੋ।"),
    ("payment_success", "Cash Payment Completed", "नकद भुगतान पूरा हुआ", "रोख पैसे मिळाले", "ਨਕਦ ਭੁਗਤਾਨ ਪੂਰਾ ਹੋਇਆ",
     "Cash payout has been verified and logged in your Earnings Ledger.",
     "नकद भुगतान सत्यापित हो गया है और आपकी कमाई बहीखाते में दर्ज हो गया है।",
     "रोख रक्कम पडताळली गेली असून आपल्या कमाई नोंदवहीत नोंदवली गेली आहे.",
     "ਨਕਦ ਭੁਗਤਾਨ ਦੀ ਪੁਸ਼ਟੀ ਹੋ ਗਈ ਹੈ ਅਤੇ ਤੁਹਾਡੀ ਕਮਾਈ ਬਹੀਖਾਤੇ ਵਿੱਚ ਦਰਜ ਹੋ ਗਿਆ ਹੈ।",
     "KC Alert: Cash payment logged in Earnings Ledger. View receipt in app.",
     "केसी अलर्ट: नकद भुगतान बहीखाते में दर्ज हो गया है। रसीद ऐप में देखें।",
     "केसी अलर्ट: रोख रक्कम नोंदवहीत नोंदवली गेली आहे. पावती ॲपमध्ये पहा.",
     "ਕੇਸੀ ਅਲਰਟ: ਨਕਦ ਭੁਗਤਾਨ ਬਹੀਖਾਤੇ ਵਿੱਚ ਦਰਜ ਹੋ ਗਿਆ ਹੈ। ਰਸੀਦ ਦੇਖੋ।")
]

async def seed_database():
    print("Starting Kabadiwala Connect database reset and deterministic seeding...")

    # Recreate tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # 1. Admin User
        admin_user = User(
            phone="9999999999",
            name="JNARDDC / Ministry Admin",
            role="admin",
            language="en",
            otp_hash=get_password_hash("123456"),
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=admin"
        )
        db.add(admin_user)
        await db.flush()

        # 2. Materials & Compositions & Subcategories
        material_map = {}
        subcategory_map = {}
        for m_data in RAW_MATERIALS:
            mat = Material(
                code=m_data["code"],
                name_en=m_data["name_en"],
                name_hi=m_data["name_hi"],
                name_mr=m_data["name_mr"],
                name_pa=m_data["name_pa"],
                icon_key=m_data["icon_key"],
                base_price_paise_per_kg=m_data["base"],
                price_floor_paise=m_data["floor"],
                price_ceiling_paise=m_data["ceil"],
                is_hazardous=m_data["hazardous"],
                hazard_level=m_data["hazard_level"],
                hazard_note_en=m_data["hazard_note_en"],
                hazard_note_hi=m_data["hazard_note_hi"],
                hazard_note_mr=m_data["hazard_note_mr"],
                hazard_note_pa=m_data["hazard_note_pa"],
                safety_tip_en=m_data["safety_tip_en"],
                safety_tip_hi=m_data["safety_tip_hi"],
                safety_tip_mr=m_data["safety_tip_mr"],
                safety_tip_pa=m_data["safety_tip_pa"],
                strategic_flag=m_data["strategic"],
                source="cpcb_schedule_1",
                is_synthetic=False
            )
            db.add(mat)
            await db.flush()
            material_map[m_data["code"]] = mat

            # Subcategories
            subcategories: list[Any] = m_data.get("subcategories", [])
            for sub_item in subcategories:
                sub_code, sub_en, sub_hi, sub_mr, sub_pa = sub_item
                sub = MaterialSubcategory(
                    material_id=mat.id,
                    code=sub_code,
                    name_en=sub_en,
                    name_hi=sub_hi,
                    name_mr=sub_mr,
                    name_pa=sub_pa
                )
                db.add(sub)
                await db.flush()
                subcategory_map[sub_code] = sub

            # Compositions
            comp_list: list[Any] = m_data.get("comp", [])
            for comp_item in comp_list:
                elem, g_kg = comp_item
                comp = MaterialComposition(
                    material_id=mat.id,
                    element=elem,
                    grams_per_kg=g_kg,
                    source_note="JNARDDC validated baseline study 2024"
                )
                db.add(comp)

        # 3. 90-Day Price History with realistic spike & dip
        base_date = datetime.now(timezone.utc).date() - timedelta(days=90)
        for d in range(91):
            cur_date = base_date + timedelta(days=d)
            date_str = cur_date.isoformat()

            for code, mat in material_map.items():
                base_p = mat.base_price_paise_per_kg
                noise = random.randint(-400, 400)
                if code in ["CABLE", "MOTOR"] and 35 <= d <= 50:
                    spike = int(base_p * 0.18 * ((15 - abs(d - 42)) / 15))
                    p = base_p + spike + noise
                elif code == "BATTERY_LI" and 60 <= d <= 75:
                    dip = int(base_p * 0.12 * ((15 - abs(d - 67)) / 15))
                    p = base_p - dip + noise
                else:
                    p = base_p + noise

                ph = PriceHistory(
                    material_id=mat.id,
                    city=None, # National
                    date=date_str,
                    price_paise_per_kg=p,
                    min_paise=int(p * 0.92),
                    max_paise=int(p * 1.08),
                    unit="kg",
                    buying_price_paise=int(p * 0.95),
                    quoted_price_paise=p,
                    source="mcx_and_recycler_composite",
                    is_synthetic=True
                )
                db.add(ph)

        # 4. Aggregators
        aggregator_objects = []
        for name, phone, city, comm, veh in AGGREGATOR_PROFILES:
            city_info = next(c for c in CITIES if c["city"] == city)
            u = User(
                phone=phone,
                name=f"{name} (Owner)",
                role="aggregator",
                language="hi" if city != "Mumbai" else "mr",
                otp_hash=get_password_hash("123456"),
                avatar_url=f"https://api.dicebear.com/7.x/identicon/svg?seed={phone}"
            )
            db.add(u)
            await db.flush()

            agg = Aggregator(
                user_id=u.id,
                business_name=name,
                city=city_info["city"],
                state=city_info["state"],
                lat=city_info["lat"] + random.uniform(-0.02, 0.02),
                lng=city_info["lng"] + random.uniform(-0.02, 0.02),
                commission_bps=comm,
                verification_status="verified",
                service_radius_km=30,
                service_area_geojson=json.dumps({"type": "Circle", "radius_km": 30})
            )
            db.add(agg)
            await db.flush()
            aggregator_objects.append(agg)

        # 5. Recyclers
        recycler_objects = []
        for name, phone, city, cpcb, spcb in RECYCLER_PROFILES:
            city_info = next(c for c in CITIES if c["city"] == city)
            u = User(
                phone=phone,
                name=f"{name} (Compliance)",
                role="recycler",
                language="en",
                otp_hash=get_password_hash("123456"),
                avatar_url=f"https://api.dicebear.com/7.x/identicon/svg?seed={phone}"
            )
            db.add(u)
            await db.flush()

            rec = Recycler(
                user_id=u.id,
                company_name=name,
                contact_person="Director Operations",
                address=f"Industrial Area Phase 2, {city_info['city']}",
                city=city_info["city"],
                state=city_info["state"],
                lat=city_info["lat"] + random.uniform(-0.05, 0.05),
                lng=city_info["lng"] + random.uniform(-0.05, 0.05),
                cpcb_license_no=cpcb,
                spcb_authorization_no=spcb,
                license_valid_from=datetime.now(timezone.utc) - timedelta(days=200),
                license_valid_to=datetime.now(timezone.utc) + timedelta(days=530),
                authorization_status="authorized",
                accepted_material_codes="PCB,BATTERY_LI,MAGNET,CABLE,MOTOR,BATTERY_PB,CRT,LCD,PLASTIC_MIXED,OTHER",
                capacity_kg_per_month=50000,
                pickup_available=True,
                pickup_radius_km=75,
                rating_avg=round(random.uniform(4.2, 4.9), 2),
                reliability_score=random.randint(88, 98),
                epr_registered=True,
                gstin=f"07AAACR{random.randint(1000,9999)}A1Z5",
                service_area_geojson=json.dumps({"type": "Polygon", "description": "National collection corridor"})
            )
            db.add(rec)
            await db.flush()
            recycler_objects.append(rec)

            # Seed Recycler Rates for each material & subcategory
            for mat_code, mat_obj in material_map.items():
                rate = int(mat_obj.base_price_paise_per_kg * random.uniform(0.95, 1.05))
                rr = RecyclerRate(
                    recycler_id=rec.id,
                    material_id=mat_obj.id,
                    sub_category_id=None,
                    rate_paise_per_kg=rate,
                    valid_from=datetime.now(timezone.utc) - timedelta(days=30),
                    valid_to=datetime.now(timezone.utc) + timedelta(days=30),
                    source="contract_rate",
                    is_synthetic=True
                )
                db.add(rr)

        # 6. Collectors
        collector_objects = []
        for name, phone, city, lang, plate in COLLECTOR_PROFILES:
            city_info = next(c for c in CITIES if c["city"] == city)
            u = User(
                phone=phone,
                name=name,
                role="collector",
                language=lang,
                otp_hash=get_password_hash("123456"),
                avatar_url=f"https://api.dicebear.com/7.x/identicon/svg?seed={phone}"
            )
            db.add(u)
            await db.flush()

            col = Collector(
                user_id=u.id,
                city=city_info["city"],
                state=city_info["state"],
                lat=city_info["lat"] + random.uniform(-0.015, 0.015),
                lng=city_info["lng"] + random.uniform(-0.015, 0.015),
                upi_id=f"{phone}@upi",
                kyc_status="verified",
                wallet_balance_paise=random.randint(45000, 280000),
                total_earned_paise=random.randint(1200000, 6500000),
                lots_completed=random.randint(15, 60),
                rating_avg=round(random.uniform(4.5, 5.0), 2),
                trust_score=random.randint(85, 99)
            )
            db.add(col)
            await db.flush()
            collector_objects.append(col)

        # 7. Pickup Agents
        agent_objects = []
        for name, phone, veh_plate, employer in PICKUP_AGENTS:
            u = User(
                phone=phone,
                name=name,
                role="pickup_agent",
                language="hi",
                otp_hash=get_password_hash("123456"),
                avatar_url=f"https://api.dicebear.com/7.x/identicon/svg?seed={phone}"
            )
            db.add(u)
            await db.flush()

            rec_match = next((r for r in recycler_objects if r.company_name == employer), recycler_objects[0])
            agent = PickupAgent(
                recycler_id=rec_match.id,
                name=name,
                phone=phone,
                vehicle_no=veh_plate,
                photo_url=f"https://api.dicebear.com/7.x/identicon/svg?seed={phone}",
                is_active=True
            )
            db.add(agent)
            await db.flush()
            agent_objects.append(agent)

        # 8. Seed Lots, Items, Quotes, Transactions, and Hash Chain Events
        print("Generating 25 Realistic E-Waste Lots with Provenance and Cash-First Handover Records...")
        mat_keys = list(material_map.keys())
        statuses = [
            "completed", "completed", "completed", "completed", "completed",
            "completed", "completed", "completed", "completed", "completed",
            "completed", "completed", "weighed", "arrived", "in_transit",
            "pickup_scheduled", "accepted", "quoted", "listed", "draft",
            "disputed", "completed", "completed", "completed", "completed"
        ]

        created_transactions = []
        for lot_i in range(1, 26):
            col = collector_objects[(lot_i - 1) % len(collector_objects)]
            status = statuses[lot_i - 1]
            lot_code = f"KC-LOT-{lot_i:04d}"

            lot = Lot(
                collector_id=col.id,
                lot_code=lot_code,
                pickup_address=f"Gali No. {lot_i % 8 + 1}, {col.city}",
                pickup_lat=col.lat,
                pickup_lng=col.lng,
                status=status,
                source="collector_app",
                is_synthetic=True
            )
            db.add(lot)
            await db.flush()

            # Add 1 to 2 items
            num_items = 1 if lot_i % 2 == 0 else 2
            total_min = 0
            total_max = 0
            total_wt_g = 0

            for item_idx in range(num_items):
                mat_k = mat_keys[(lot_i + item_idx) % len(mat_keys)]
                mat = material_map[mat_k]
                wt_kg = random.choice([3.0, 5.5, 12.0, 18.0, 24.0])
                wt_g = int(wt_kg * 1000)
                cond = random.choice(["working", "broken", "burnt"])
                cond_factor = 1.1 if cond == "working" else (0.7 if cond == "burnt" else 1.0)

                min_p = int(round(mat.base_price_paise_per_kg * 0.9 * wt_kg * cond_factor))
                max_p = int(round(mat.base_price_paise_per_kg * 1.1 * wt_kg * cond_factor))
                total_min += min_p
                total_max += max_p
                total_wt_g += wt_g

                item = LotItem(
                    lot_id=lot.id,
                    material_id=mat.id,
                    sub_category_id=None,
                    est_weight_g=wt_g,
                    actual_weight_g=wt_g if status in ["weighed", "completed", "disputed"] else None,
                    condition=cond,
                    est_value_min_paise=min_p,
                    est_value_max_paise=max_p,
                    final_value_paise=int((min_p + max_p) / 2) if status == "completed" else None,
                    source_type="collector"
                )
                db.add(item)
                await db.flush()

                # Add 1 photo
                photo = LotPhoto(
                    lot_item_id=item.id,
                    storage_url="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400",
                    thumb_url="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=100",
                    size_bytes=142000,
                    sha256=hashlib.sha256(f"seed-photo-{lot_code}-{item_idx}".encode()).hexdigest(),
                    phash="a1b2c3d4e5f60718",
                    quality_score=0.925
                )
                db.add(photo)

            lot.est_total_min_paise = total_min
            lot.est_total_max_paise = total_max
            lot.est_total_weight_g = total_wt_g

            # Build Quote and Handover Transaction if applicable
            rec = recycler_objects[(lot_i) % len(recycler_objects)]
            agreed_amt = int((total_min + total_max) / 2)

            if status in ["quoted", "accepted", "pickup_scheduled", "in_transit", "arrived", "weighed", "completed", "disputed"]:
                q = Quote(
                    lot_id=lot.id,
                    recycler_id=rec.id,
                    price_paise_total=agreed_amt,
                    pickup_mode="pickup",
                    pickup_eta_at=datetime.now(timezone.utc) + timedelta(hours=2),
                    valid_until=datetime.now(timezone.utc) + timedelta(days=2),
                    status="accepted" if status != "quoted" else "sent",
                    note="Verified CPCB doorstep collection"
                )
                db.add(q)
                await db.flush()

                if status != "quoted":
                    rct_no = f"KC-RCT-2026-{lot_i:05d}"
                    agent = agent_objects[lot_i % len(agent_objects)]

                    # Cash-first configuration
                    is_cash = True if lot_i % 3 != 0 else False
                    is_partial_due = (lot_i == 1) # First lot has active pending due for demo!

                    p_status = "partial" if is_partial_due else ("paid" if status == "completed" else "unpaid")
                    adv_p = (agreed_amt // 2) if is_partial_due else (agreed_amt if status == "completed" else 0)
                    bal_p = (agreed_amt - adv_p) if is_partial_due else 0
                    due_st = "pending" if is_partial_due else "cleared"

                    tx = Transaction(
                        lot_id=lot.id,
                        quote_id=q.id,
                        collector_id=col.id,
                        buyer_type="recycler",
                        buyer_id=rec.id,
                        agreed_amount_paise=agreed_amt,
                        final_amount_paise=agreed_amt if status == "completed" else None,
                        weight_variance_pct=0.0 if status == "completed" else (12.5 if status == "disputed" else None),
                        payment_method="cash" if is_cash else "upi",
                        payment_status=p_status,
                        handover_ref=f"KC-HO-{lot_code[-4:]}-{lot_i:04d}",
                        collection_lat=col.lat,
                        collection_lng=col.lng,
                        handover_lat=rec.lat,
                        handover_lng=rec.lng,
                        handover_otp_hash=get_password_hash("123456"),
                        handover_qr_token=f"QR-AUTH-{lot_code}",
                        collector_confirmed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if status == "completed" else None,
                        buyer_confirmed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if status == "completed" else None,
                        recycler_confirmed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if status == "completed" else None,
                        recycler_confirmed_by=rec.user_id if status == "completed" else None,
                        cash_confirmed_by_collector=True if (is_cash and status == "completed") else False,
                        cash_confirmed_collector_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if (is_cash and status == "completed") else None,
                        collector_confirm_lat=col.lat,
                        collector_confirm_lng=col.lng,
                        cash_confirmed_by_buyer=True if (is_cash and status == "completed") else False,
                        cash_confirmed_buyer_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if (is_cash and status == "completed") else None,
                        buyer_confirm_lat=rec.lat,
                        buyer_confirm_lng=rec.lng,
                        advance_paise=adv_p,
                        balance_paise=bal_p,
                        balance_due_at=datetime.now(timezone.utc) + timedelta(days=3) if is_partial_due else None,
                        due_status=due_st,
                        status="completed" if status == "completed" else ("disputed" if status == "disputed" else "scheduled"),
                        receipt_no=rct_no,
                        agent_id=agent.id,
                        dispute_reason="Scale variance 12.5% at facility" if status == "disputed" else None,
                        source="collector_app",
                        is_synthetic=True
                    )
                    db.add(tx)
                    await db.flush()
                    created_transactions.append(tx)

                    if status == "completed":
                        lot.final_amount_paise = agreed_amt
                        lot.actual_total_weight_g = total_wt_g
                        pay = Payment(
                            transaction_id=tx.id,
                            amount_paise=agreed_amt,
                            method="cash" if is_cash else "upi",
                            status="success",
                            completed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 45)),
                            gateway_ref=None if is_cash else f"GW-{uuid.uuid4().hex[:10]}",
                            upi_ref=None if is_cash else f"KCUPI{random.randint(1000000000, 9999999999)}",
                            retry_count=0
                        )
                        db.add(pay)

                        # Add Document
                        doc_rec = Document(
                            type="receipt",
                            number=rct_no,
                            lot_id=lot.id,
                            transaction_id=tx.id,
                            user_id=col.user_id,
                            storage_url=f"/api/documents/{rct_no}/pdf",
                            sha256=hashlib.sha256(rct_no.encode()).hexdigest()
                        )
                        db.add(doc_rec)

            # Build Hash Chain Traceability Events
            prev_hash = GENESIS_HASH
            events_to_add = ["lot_created", "listed"]
            if status in ["quoted", "accepted", "pickup_scheduled", "in_transit", "arrived", "weighed", "completed", "disputed"]:
                events_to_add.extend(["quote_received", "quote_accepted", "pickup_scheduled"])
            if status in ["in_transit", "arrived", "weighed", "completed", "disputed"]:
                events_to_add.append("arrived")
            if status in ["weighed", "completed", "disputed"]:
                events_to_add.append("weighed")
            if status == "completed":
                events_to_add.extend(["handover_confirmed", "payment_made", "processed"])
            elif status == "disputed":
                events_to_add.append("disputed")

            base_event_time = datetime.now(timezone.utc) - timedelta(days=random.randint(2, 40))
            for s_idx, ev_type in enumerate(events_to_add, start=1):
                ev_time = base_event_time + timedelta(minutes=s_idx * 15)
                payload = {"lot_code": lot_code, "status": ev_type, "note": f"Step {s_idx} completed"}
                ev_hash = compute_event_hash(
                    prev_hash=prev_hash,
                    seq=s_idx,
                    event_type=ev_type,
                    payload=payload,
                    occurred_at=ev_time
                )

                # If lot_i == 10 and s_idx == 3: deliberately corrupt event_hash for the tamper demo test lot!
                if lot_i == 10 and s_idx == 3:
                    ev_hash = "deadbeef" + ev_hash[8:]

                t_ev = TraceabilityEvent(
                    lot_id=lot.id,
                    seq=s_idx,
                    event_type=ev_type,
                    actor_user_id=col.user_id,
                    actor_role="collector",
                    payload_json=json.dumps(payload),
                    geo_lat=col.lat,
                    geo_lng=col.lng,
                    occurred_at=ev_time,
                    prev_hash=prev_hash,
                    event_hash=ev_hash
                )
                db.add(t_ev)
                prev_hash = ev_hash

        # 9. Seed 6 Deliberate Anomalies for Demo (Section 5)
        print("Seeding 6 Deliberate Anomalies in AnomalyFlags...")
        if len(created_transactions) >= 6:
            anomaly_seeds = [
                # 2 Price Outliers
                (created_transactions[0].id, "price_outlier", 3.85, ["Quoted rate ₹1,200/kg exceeds 3.5 MAD threshold from rolling city mean of ₹420/kg."], "critical"),
                (created_transactions[1].id, "price_outlier", 2.92, ["Rate for Li-Ion battery pack exceeds 99th percentile across North Zone."], "high"),
                # 2 Weight Variance Anomalies
                (created_transactions[2].id, "weight_variance", 2.45, ["18.4% scale weight drop between pickup agent digital scale and recycler inlet hopper."], "high"),
                (created_transactions[3].id, "weight_variance", 1.95, ["14.2% variance in CRT glass gross weight after moisture reduction check."], "medium"),
                # 2 Rapid Succession / Velocity Anomalies
                (created_transactions[4].id, "impossible_velocity", 4.10, ["Collector recorded handovers in Delhi NCR and Ludhiana within 22 minutes (distance 310km)."], "critical"),
                (created_transactions[5].id, "rapid_succession", 2.65, ["4 consecutive high-value transactions completed within 90 seconds from same IP subnet."], "medium")
            ]
            for tx_id, a_type, score, reasons, sev in anomaly_seeds:
                flag = AnomalyFlag(
                    transaction_id=tx_id,
                    code=a_type.upper(),  # §2.1 fix: code is NOT NULL — use type as structured code
                    type=a_type,
                    score=score,
                    reasons_json=json.dumps(reasons),
                    severity=sev,
                    status="open"
                )
                db.add(flag)

        # 10. Seed AI/ML Models & Explainable Matching Weights
        print("Seeding ML Models & Matching Weights...")
        mw = MatchingWeight(
            version="1.0",
            weights_json=json.dumps({
                "distance_km": 0.35,
                "price_rate": 0.35,
                "rating": 0.15,
                "epr_capacity": 0.15
            }),
            created_by=admin_user.id,
            is_active=True
        )
        db.add(mw)

        ml_clf = MLModel(
            task="classification",
            name="MobileNetV3-Small-INT8",
            version="1.0.0",
            framework="tflite",
            size_bytes=3980000,
            trained_on_version="v1.0.0",
            metrics_json=json.dumps({
                "top1_accuracy": 0.914,
                "top3_accuracy": 0.982,
                "macro_f1": 0.908,
                "latency_ms": 42
            }),
            demo_only=True,
            is_active=True
        )
        db.add(ml_clf)

        ml_val = MLModel(
            task="valuation",
            name="QuantileRegressor-v1",
            version="1.0.0",
            framework="scikit-learn",
            size_bytes=420000,
            trained_on_version="v1.0.0",
            metrics_json=json.dumps({
                "p10_p90_coverage": 0.892,
                "mae_paise": 1850,
                "r2_score": 0.884
            }),
            demo_only=True,
            is_active=True
        )
        db.add(ml_val)

        # 11. Living Data Pipeline Datasets
        print("Seeding Datasets & Living Data Versions...")
        ds1 = Dataset(
            name="e_waste_transactions",
            description="Verified e-waste collection and recycler handover transactions across North and West India",
            owner="Ministry of Mines / JNARDDC"
        )
        db.add(ds1)
        await db.flush()

        dsv1 = DatasetVersion(
            dataset_id=ds1.id,
            version="v1.0.0",
            row_count=5280,
            date_from=datetime.now(timezone.utc) - timedelta(days=180),
            date_to=datetime.now(timezone.utc),
            synthetic_share=0.850,
            checksum="a8f3b2c1d0e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0",
            exported_anonymized=True
        )
        db.add(dsv1)

        ds2 = Dataset(
            name="material_price_index",
            description="Daily verified critical mineral and scrap metal price indices from MCX and London Metal Exchange",
            owner="JNARDDC Analytics Cell"
        )
        db.add(ds2)
        await db.flush()

        dsv2 = DatasetVersion(
            dataset_id=ds2.id,
            version="v1.0.0",
            row_count=1840,
            date_from=datetime.now(timezone.utc) - timedelta(days=90),
            date_to=datetime.now(timezone.utc),
            synthetic_share=0.200,
            checksum="b9c0d1e2f3a4b5c6d7e8f9a0a8f3b2c1d0e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8",
            exported_anonymized=True
        )
        db.add(dsv2)

        # 12. Seed FAQs
        print("Generating Multilingual FAQs (English, Hindi, Marathi, Punjabi)...")
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
                sort_order=1,
                is_active=True
            )
            db.add(faq)

        # 13. Seed Notification Templates
        print("Generating Notification Templates...")
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

        # Seed sample notifications for first collector
        prime_col = collector_objects[0]
        n1 = Notification(
            user_id=prime_col.user_id,
            type="quote_received",
            title_en="New Quote: ₹2,450",
            title_hi="नया कोटेशन: ₹2,450",
            title_mr="नवीन कोटेशन: ₹2,450",
            title_pa="ਨਵੀਂ ਕੋਟੇਸ਼ਨ: ₹2,450",
            body_en="EcoBirba Circular Recyclers offered ₹2,450 for your PCB scrap lot.",
            body_hi="इकोबिर्बा सर्कुलर रिसाइकिलर्स ने आपके पीसीबी लॉट के लिए ₹2,450 का ऑफर दिया।",
            body_mr="इकोबिर्बा सर्कुलर रिसायकलरने आपल्या पीसीबी लॉटसाठी ₹2,450 ची ऑफर दिली आहे.",
            body_pa="ਇਕੋਬਿਰਬਾ ਰੀਸਾਈਕਲਰਜ਼ ਨੇ ਤੁਹਾਡੇ ਪੀਸੀਬੀ ਲਾਟ ਲਈ ₹2,450 ਦੀ ਪੇਸ਼ਕਸ਼ ਕੀਤੀ।",
            payload_json=json.dumps({"lot_code": "KC-LOT-0001", "amount": 2450}),
            channel="in_app"
        )
        db.add(n1)

        await db.commit()
        print("Deterministic database seeding completed successfully!")

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    try:
        from seed.generate_realistic import seed_realistic_database
        asyncio.run(seed_realistic_database())
    except Exception as e:
        print(f"[WARN] Delegating to internal seed_database due to: {e}")
        asyncio.run(seed_database())
