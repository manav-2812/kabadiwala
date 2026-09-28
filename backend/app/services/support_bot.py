
BOT_TEMPLATES = {
    "payment": {
        "en": "Namaste! Your payment query has been registered. UPI payments typically settle within 15 minutes. Our team is verifying your transaction reference.",
        "hi": "नमस्ते! आपका भुगतान संबंधित प्रश्न दर्ज कर लिया गया है। यूपीआई भुगतान आमतौर पर 15 मिनट में जमा हो जाता है। हमारी टीम आपके लेनदेन की पुष्टि कर रही है।",
        "pa": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਤੁਹਾਡੀ ਭੁਗਤਾਨ ਸੰਬੰਧੀ ਪੁੱਛਗਿੱਛ ਦਰਜ ਕਰ ਲਈ ਗਈ ਹੈ। ਯੂਪੀਆਈ ਭੁਗਤਾਨ ਆਮ ਤੌਰ 'ਤੇ 15 ਮਿੰਟਾਂ ਵਿੱਚ ਜਮ੍ਹਾ ਹੋ ਜਾਂਦਾ ਹੈ।"
    },
    "dispute": {
        "en": "We have noted your weight/price discrepancy. An authorized supervisor has been assigned to inspect the digital weigh-in log.",
        "hi": "हमने वजन/मूल्य में अंतर नोट कर लिया है। डिजिटल वजन लॉग की जांच के लिए एक अधिकृत पर्यवेक्षक नियुक्त किया गया है।",
        "pa": "ਅਸੀਂ ਵਜ਼ਨ/ਕੀਮਤ ਵਿੱਚ ਅੰਤਰ ਨੋਟ ਕਰ ਲਿਆ ਹੈ। ਡਿਜੀਟਲ ਵਜ਼ਨ ਲੌਗ ਦੀ ਜਾਂਚ ਲਈ ਇੱਕ ਸੁਪਰਵਾਈਜ਼ਰ ਨਿਯੁਕਤ ਕੀਤਾ ਗਿਆ ਹੈ।"
    },
    "pickup": {
        "en": "The assigned recycler agent has received your pickup request. Live GPS tracking is active on your screen.",
        "hi": "नियुक्त रिसाइकिलर एजेंट को आपका पिकअप अनुरोध मिल गया है। आपकी स्क्रीन पर लाइव जीपीएस ट्रैकिंग सक्रिय है।",
        "pa": "ਨਿਯੁਕਤ ਰੀਸਾਈਕਲਰ ਏਜੰਟ ਨੂੰ ਤੁਹਾਡੀ ਪਿਕਅੱਪ ਬੇਨਤੀ ਮਿਲ ਗਈ ਹੈ। ਤੁਹਾਡੀ ਸਕ੍ਰੀਨ 'ਤੇ ਲਾਈਵ ਜੀਪੀਐਸ ਟਰੈਕਿੰਗ ਸਰਗਰਮ ਹੈ।"
    },
    "safety": {
        "en": "Safety priority notice: If handling swollen lithium batteries or cracked CRT monitors, please keep them in open sand/isolate them immediately. Do not inhale dust.",
        "hi": "सुरक्षा प्राथमिकता सूचना: यदि फूली हुई लिथियम बैटरी या टूटे हुए सीआरटी मॉनिटर को संभाल रहे हैं, तो तुरंत उन्हें अलग रखें और धूल सांस में न लें।",
        "pa": "ਸੁਰੱਖਿਆ ਪਹਿਲ ਸੂਚਨਾ: ਜੇਕਰ ਫੁੱਲੀਆਂ ਹੋਈਆਂ ਲਿਥੀਅਮ ਬੈਟਰੀਆਂ ਜਾਂ ਟੁੱਟੇ ਹੋਏ ਸੀਆਰਟੀ ਮਾਨੀਟਰਾਂ ਨੂੰ ਸੰਭਾਲ ਰਹੇ ਹੋ, ਤਾਂ ਉਹਨਾਂ ਨੂੰ ਤੁਰੰਤ ਵੱਖ ਰੱਖੋ।"
    },
    "default": {
        "en": "Hello! Your ticket has been logged and assigned to Kabadiwala Connect Support. A representative will contact you shortly.",
        "hi": "नमस्ते! आपकी शिकायत दर्ज कर ली गई है और कबाड़ीवाला कनेक्ट सहायता को सौंप दी गई है। प्रतिनिधि जल्द संपर्क करेंगे।",
        "pa": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਤੁਹਾਡੀ ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰ ਲਈ ਗਈ ਹੈ ਅਤੇ ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ ਸਹਾਇਤਾ ਨੂੰ ਸੌਂਪੀ ਗਈ ਹੈ।"
    }
}

def generate_bot_reply(category: str, user_text: str, language: str = "hi") -> str:
    lang = language.lower()
    if lang not in ["en", "hi", "pa"]:
        lang = "hi"

    cat = category.lower()
    text = user_text.lower()

    matched_cat = "default"
    if "pay" in text or "upi" in text or "paisa" in text or "paise" in text or cat == "payment":
        matched_cat = "payment"
    elif "vajan" in text or "weight" in text or "dispute" in text or cat == "dispute":
        matched_cat = "dispute"
    elif "agent" in text or "pickup" in text or "late" in text or cat == "pickup":
        matched_cat = "pickup"
    elif "fire" in text or "hazard" in text or "chemical" in text or cat == "safety":
        matched_cat = "safety"

    return BOT_TEMPLATES.get(matched_cat, BOT_TEMPLATES["default"]).get(lang, BOT_TEMPLATES["default"]["hi"])
