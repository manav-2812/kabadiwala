import json
import os

new_keys = {
    # Auth & Login
    "tab_login": {
        "en": "Log In",
        "mr": "लॉग इन",
        "hi": "लॉग इन",
        "pa": "ਲਾਗ ਇਨ"
    },
    "tab_signup": {
        "en": "Sign Up",
        "mr": "नवीन नोंदणी",
        "hi": "नया खाता बनाएं",
        "pa": "ਨਵੀਂ ਰਜਿਸਟ੍ਰੇਸ਼ਨ"
    },
    "login_title": {
        "en": "Enter Mobile to Log In",
        "mr": "लॉग इन करण्यासाठी मोबाईल क्रमांक टाका",
        "hi": "लॉग इन करने के लिए मोबाइल नंबर दर्ज करें",
        "pa": "ਲਾਗ ਇਨ ਕਰਨ ਲਈ ਮੋਬਾਈਲ ਨੰਬਰ ਦਰਜ ਕਰੋ"
    },
    "login_subtitle": {
        "en": "Receive an instant SMS authentication code on your registered mobile number.",
        "mr": "आपल्या नोंदणीकृत मोबाईलवर त्वरित पडताळणी कोड मिळवा.",
        "hi": "अपने पंजीकृत मोबाइल पर तुरंत सत्यापन कोड प्राप्त करें।",
        "pa": "ਆਪਣੇ ਰਜਿਸਟਰਡ ਮੋਬਾਈਲ 'ਤੇ ਤੁਰੰਤ ਪੁਸ਼ਟੀ ਕੋਡ ਪ੍ਰਾਪਤ ਕਰੋ।"
    },
    "signup_title": {
        "en": "Register New Account",
        "mr": "नवीन खाते तयार करा",
        "hi": "नया खाता पंजीकृत करें",
        "pa": "ਨਵਾਂ ਖਾਤਾ ਬਣਾਓ"
    },
    "signup_subtitle": {
        "en": "Join Kabadiwala Connect as a verified collector, recycler, or hub.",
        "mr": "कबाडीवाला कनेक्टवर प्रमाणित संकलक, पुनर्वापरदार किंवा केंद्र म्हणून सामील व्हा.",
        "hi": "कबाड़ीवाला कनेक्ट पर प्रमाणित संकलक, रिसाइकिलर या हब के रूप में जुड़ें।",
        "pa": "ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ 'ਤੇ ਪ੍ਰਮਾਣਿਤ ਸੰਗ੍ਰਹਿਕਰਤਾ, ਰੀਸਾਈਕਲਰ ਜਾਂ ਹੱਬ ਵਜੋਂ ਜੁੜੋ।"
    },
    "otp_title": {
        "en": "Verify OTP Code",
        "mr": "ओटीपी पडताळणी",
        "hi": "ओटीपी सत्यापन",
        "pa": "ਓਟੀਪੀ ਪੁਸ਼ਟੀ"
    },
    "otp_subtitle": {
        "en": "Enter the 6-digit verification code sent to +91 {phone}",
        "mr": "+91 {phone} वर पाठवलेला ६-अंकी पडताळणी कोड टाका",
        "hi": "+91 {phone} पर भेजा गया 6-अंकीय सत्यापन कोड दर्ज करें",
        "pa": "+91 {phone} 'ਤੇ ਭੇਜਿਆ ਗਿਆ 6-ਅੰਕੀ ਪੁਸ਼ਟੀ ਕੋਡ ਦਰਜ ਕਰੋ"
    },
    "label_mobile": {
        "en": "Mobile Number",
        "mr": "मोबाईल क्रमांक",
        "hi": "मोबाइल नंबर",
        "pa": "ਮੋਬਾਈਲ ਨੰਬਰ"
    },
    "label_fullname": {
        "en": "Full Name",
        "mr": "पूर्ण नाव",
        "hi": "पूरा नाम",
        "pa": "ਪੂਰਾ ਨਾਂ"
    },
    "label_role": {
        "en": "Account Role",
        "mr": "खात्याची भूमिका",
        "hi": "खाता भूमिका",
        "pa": "ਖਾਤਾ ਭੂਮਿਕਾ"
    },
    "label_city": {
        "en": "Operating City",
        "mr": "कार्यक्षेत्र शहर",
        "hi": "कार्यक्षेत्र शहर",
        "pa": "ਕੰਮ ਦਾ ਸ਼ਹਿਰ"
    },
    "label_company": {
        "en": "Facility / Firm Name",
        "mr": "फर्म किंवा केंद्राचे नाव",
        "hi": "फर्म या संयंत्र का नाम",
        "pa": "ਫਰਮ ਜਾਂ ਪਲਾਂਟ ਦਾ ਨਾਂ"
    },
    "label_cpcb_license": {
        "en": "CPCB / SPCB License Number",
        "mr": "CPCB / SPCB परवाना क्रमांक",
        "hi": "सीपीसीबी / एसपीसीबी लाइसेंस संख्या",
        "pa": "ਸੀਪੀਸੀਬੀ / ਐਸਪੀਸੀਬੀ ਲਾਇਸੰਸ ਨੰਬਰ"
    },
    "btn_send_otp": {
        "en": "Send Login OTP",
        "mr": "लॉग इन ओटीपी पाठवा",
        "hi": "लॉग इन ओटीपी भेजें",
        "pa": "ਲਾਗ ਇਨ ਓਟੀਪੀ ਭੇਜੋ"
    },
    "btn_verify_otp": {
        "en": "Verify & Enter Portal",
        "mr": "पडताळणी करा आणि प्रवेश करा",
        "hi": "सत्यापित करें और प्रवेश करें",
        "pa": "ਪੁਸ਼ਟੀ ਕਰੋ ਅਤੇ ਦਾਖਲ ਹੋਵੋ"
    },
    "btn_resend_otp": {
        "en": "Resend Code",
        "mr": "कोड पुन्हा पाठवा",
        "hi": "कोड दोबारा भेजें",
        "pa": "ਕੋਡ ਦੁਬਾਰਾ ਭੇਜੋ"
    },
    "btn_change_phone": {
        "en": "Change Mobile Number",
        "mr": "मोबाईल क्रमांक बदला",
        "hi": "मोबाइल नंबर बदलें",
        "pa": "ਮੋਬਾਈਲ ਨੰਬਰ ਬਦਲੋ"
    },
    "prompt_new_user": {
        "en": "New to Kabadiwala Connect?",
        "mr": "कबाडीवाला कनेक्टवर नवीन आहात?",
        "hi": "कबाड़ीवाला कनेक्ट पर नए हैं?",
        "pa": "ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ 'ਤੇ ਨਵੇਂ ਹੋ?"
    },
    "prompt_existing_user": {
        "en": "Already registered?",
        "mr": "आधीच नोंदणीकृत आहात?",
        "hi": "पहले से पंजीकृत हैं?",
        "pa": "ਪਹਿਲਾਂ ਤੋਂ ਰਜਿਸਟਰਡ ਹੋ?"
    },
    "demo_quick_login": {
        "en": "Quick Demo Logins",
        "mr": "जलद डेमो लॉगिन",
        "hi": "त्वरित डेमो लॉगिन",
        "pa": "ਤੁਰੰਤ ਡੈਮੋ ਲਾਗਇਨ"
    },
    "demo_quick_desc": {
        "en": "Instant 1-click login into seed personas for testing",
        "mr": "फील्ड चाचण्यांसाठी १-क्लिक जलद लॉगिन",
        "hi": "फील्ड परीक्षण के लिए 1-क्लिक त्वरित लॉगिन",
        "pa": "ਫੀਲਡ ਟੈਸਟਿੰਗ ਲਈ 1-ਕਲਿੱਕ ਤੁਰੰਤ ਲਾਗਇਨ"
    },
    "label_role_desc": {
        "en": "Select your operational role in the supply chain:",
        "mr": "पुरवठा साखळीतील आपली कामकाजाची भूमिका निवडा:",
        "hi": "आपूर्ति श्रृंखला में अपनी परिचालन भूमिका चुनें:",
        "pa": "ਸਪਲਾਈ ਚੇਨ ਵਿੱਚ ਆਪਣੀ ਕਾਰਜਸ਼ੀਲ ਭੂਮਿਕਾ ਚੁਣੋ:"
    },

    # Step Timeline
    "timeline_listed": {
        "en": "Listed",
        "mr": "नोंदणीकृत",
        "hi": "सूचीबद्ध",
        "pa": "ਸੂਚੀਬੱਧ"
    },
    "timeline_quoted": {
        "en": "Quoted",
        "mr": "कोटेशन्स",
        "hi": "भाव प्राप्त",
        "pa": "ਕੋਟੇਸ਼ਨਾਂ"
    },
    "timeline_accepted": {
        "en": "Accepted",
        "mr": "स्वीकृत",
        "hi": "स्वीकृत",
        "pa": "ਮਨਜ਼ੂਰ"
    },
    "timeline_pickup": {
        "en": "Pickup",
        "mr": "पिकअप",
        "hi": "पिकअप",
        "pa": "ਪਿਕਅੱਪ"
    },
    "timeline_weighed": {
        "en": "Weighed",
        "mr": "वजन तपासणी",
        "hi": "वजन जांच",
        "pa": "ਵਜ਼ਨ ਜਾਂਚ"
    },
    "timeline_paid": {
        "en": "Paid",
        "mr": "रक्कम जमा",
        "hi": "भुगतान प्राप्त",
        "pa": "ਭੁਗਤਾਨ"
    },

    # Quotes & Recyclers
    "pickup_doorstep": {
        "en": "Doorstep Collection",
        "mr": "घरपोच पिकअप",
        "hi": "घर बैठे पिकअप",
        "pa": "ਘਰ ਬੈਠੇ ਪਿਕਅੱਪ"
    },
    "pickup_dropoff": {
        "en": "Self Drop-off",
        "mr": "स्वतः सुपूर्द करा",
        "hi": "स्वयं जमा करें",
        "pa": "ਖੁਦ ਜਮ੍ਹਾ ਕਰੋ"
    },
    "pickup_eta_desc": {
        "en": "Pickup ETA: within {hours} hours of acceptance",
        "mr": "पिकअप आगमन: स्वीकृतीनंतर {hours} तासांत",
        "hi": "पिकअप समय: स्वीकृति के {hours} घंटे के भीतर",
        "pa": "ਪਿਕਅੱਪ ਸਮਾਂ: ਮਨਜ਼ੂਰੀ ਤੋਂ {hours} ਘੰਟਿਆਂ ਦੇ ਅੰਦਰ"
    },
    "btn_request_quote": {
        "en": "Request Quote",
        "mr": "कोटेशनची विनंती करा",
        "hi": "भाव मांगें",
        "pa": "ਕੋਟੇਸ਼ਨ ਮੰਗੋ"
    },
    "nearby_buyers_title": {
        "en": "Nearby Verified Buyers ({count})",
        "mr": "जवळपासचे अधिकृत खरेदीदार ({count})",
        "hi": "नजदीकी सत्यापित खरीदार ({count})",
        "pa": "ਨੇੜਲੇ ਪ੍ਰਮਾਣਿਤ ਖਰੀਦਦਾਰ ({count})"
    },
    "sorted_net_payout": {
        "en": "Sorted by Net Payout",
        "mr": "सर्वोत्तम परताव्यानुसार",
        "hi": "अधिकतम मुनाफे अनुसार",
        "pa": "ਵੱਧ ਮੁਨਾਫ਼ੇ ਅਨੁਸਾਰ"
    },
    "est_net_payout": {
        "en": "Est. Net Payout",
        "mr": "अंदाजित निव्वळ परतावा",
        "hi": "अनुमानित शुद्ध मुनाफा",
        "pa": "ਅੰਦਾਜ਼ਨ ਕੁੱਲ ਮੁਨਾਫ਼ਾ"
    },
    "distance_km_away": {
        "en": "{distance} km away",
        "mr": "{distance} किमी अंतरावर",
        "hi": "{distance} किमी दूर",
        "pa": "{distance} ਕਿਲੋਮੀਟਰ ਦੂਰ"
    },
    "reliability_score_label": {
        "en": "Reliability: {score}%",
        "mr": "विश्वसनीयता: {score}%",
        "hi": "विश्वसनीयता: {score}%",
        "pa": "ਭਰੋਸੇਯੋਗਤਾ: {score}%"
    },
    "license_valid_until": {
        "en": "Valid until: {date}",
        "mr": "वैधता: {date}",
        "hi": "वैधता: {date}",
        "pa": "ਮਿਆਦ: {date}"
    },
    "cpcb_license_label": {
        "en": "License: {license}",
        "mr": "परवाना: {license}",
        "hi": "लाइसेंस: {license}",
        "pa": "ਲਾਇਸੰਸ: {license}"
    },
    "open_maps_directions": {
        "en": "Open Directions in Google Maps",
        "mr": "गुगल मॅप्सवर दिशा पहा",
        "hi": "गूगल मैप्स पर रास्ता देखें",
        "pa": "ਗੂਗਲ ਮੈਪਸ 'ਤੇ ਰਸਤਾ ਵੇਖੋ"
    },

    # Tracking
    "speed_kmh": {
        "en": "Speed: {speed} km/h",
        "mr": "गती: {speed} किमी/तास",
        "hi": "गति: {speed} किमी/घंटा",
        "pa": "ਰਫ਼ਤਾਰ: {speed} ਕਿਲੋਮੀਟਰ/ਘੰਟਾ"
    },
    "live_telemetry": {
        "en": "Live Telemetry Active",
        "mr": "थेट स्थान सक्रिय",
        "hi": "लाइव ट्रैकिंग सक्रिय",
        "pa": "ਲਾਈਵ ਟਰੈਕਿੰਗ ਚਾਲੂ"
    },
    "en_route_doorstep": {
        "en": "En Route to Your Doorstep",
        "mr": "आपल्या दिशेने येत आहे",
        "hi": "आपके स्थान की ओर आ रहा है",
        "pa": "ਤੁਹਾਡੇ ਵੱਲ ਆ ਰਿਹਾ ਹੈ"
    },
    "authorized_pickup_spec": {
        "en": "Authorized Pickup Specialist",
        "mr": "अधिकृत पिकअप प्रतिनिधी",
        "hi": "अधिकृत पिकअप विशेषज्ञ",
        "pa": "ਅਧਿਕਾਰਤ ਪਿਕਅੱਪ ਨੁਮਾਇੰਦਾ"
    },
    "tap_when_arrived": {
        "en": "Tap when the pickup specialist is at your doorstep to begin weigh-in",
        "mr": "प्रतिनिधी आल्यावर वजन तपासणी सुरू करण्यासाठी टॅप करा",
        "hi": "एजेंट के पहुंचने पर वजन जांच शुरू करने के लिए टैप करें",
        "pa": "ਏਜੰਟ ਦੇ ਪਹੁੰਚਣ 'ਤੇ ਵਜ਼ਨ ਜਾਂਚ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਟੈਪ ਕਰੋ"
    },
    "coarse_gps_label": {
        "en": "Coarse GPS: {lat}, {lng}",
        "mr": "जीपीएस स्थान: {lat}, {lng}",
        "hi": "जीपीएस स्थान: {lat}, {lng}",
        "pa": "ਜੀਪੀਐੱਸ ਸਥਾਨ: {lat}, {lng}"
    },
    "btn_open_maps": {
        "en": "Open Maps",
        "mr": "मॅप उघडा",
        "hi": "मैप खोलें",
        "pa": "ਨਕਸ਼ਾ ਖੋਲ੍ਹੋ"
    },

    # Handover & Weigh-in
    "receipt_number_label": {
        "en": "Handover Receipt #{receipt}",
        "mr": "हस्तांतरण पावती #{receipt}",
        "hi": "हैंडओवर रसीद #{receipt}",
        "pa": "ਹੈਂਡਓਵਰ ਰਸੀਦ #{receipt}"
    },
    "cpcb_verified_badge": {
        "en": "CPCB Verified",
        "mr": "CPCB प्रमाणित",
        "hi": "सीपीसीबी प्रमाणित",
        "pa": "ਸੀਪੀਸੀਬੀ ਪ੍ਰਮਾਣਿਤ"
    },
    "recycler_digital_scale": {
        "en": "Recycler Digital Scale Weigh-In (Demo Action)",
        "mr": "प्रकल्पावर डिजिटल वजन तपासणी (डेमो क्रिया)",
        "hi": "संयंत्र डिजिटल वजन जांच (डेमो क्रिया)",
        "pa": "ਪਲਾਂਟ ਡਿਜੀਟਲ ਵਜ਼ਨ ਜਾਂਚ (ਡੈਮੋ ਕਾਰਵਾਈ)"
    },
    "simulate_scale_desc": {
        "en": "Simulate digital scale weight input from recycler facility:",
        "mr": "प्रकल्पावरील डिजिटल वजन नोंदणी सिम्युलेट करा:",
        "hi": "संयंत्र से डिजिटल वजन इनपुट का अनुकरण करें:",
        "pa": "ਪਲਾਂਟ ਤੋਂ ਡਿਜੀਟਲ ਵਜ਼ਨ ਐਂਟਰੀ ਦਾ ਸਿਮੂਲੇਸ਼ਨ ਕਰੋ:"
    },
    "exact_weight_match": {
        "en": "Exact Weight (Match)",
        "mr": "अचूक वजन (जुळले)",
        "hi": "सटीक वजन (समान)",
        "pa": "ਸਹੀ ਵਜ਼ਨ (ਬਰਾਬਰ)"
    },
    "trigger_variance": {
        "en": "Trigger 12% Variance",
        "mr": "१२% फरक दाखवा",
        "hi": "12% अंतर दिखाएं",
        "pa": "12% ਫ਼ਰਕ ਵਿਖਾਓ"
    },
    "weight_breakdown_title": {
        "en": "Weight & Amount Breakdown",
        "mr": "वजन आणि रकमेचा तपशील",
        "hi": "वजन और राशि का विवरण",
        "pa": "ਵਜ਼ਨ ਅਤੇ ਰਕਮ ਦਾ ਵੇਰਵਾ"
    },
    "est_vs_actual": {
        "en": "Est: {est} → Actual: {actual}",
        "mr": "अंदाज: {est} → प्रत्यक्ष: {actual}",
        "hi": "अनुमान: {est} → वास्तविक: {actual}",
        "pa": "ਅੰਦਾਜ਼ਾ: {est} → ਅਸਲ: {actual}"
    },
    "total_payout_label": {
        "en": "Total Payout",
        "mr": "एकूण देय रक्कम",
        "hi": "कुल भुगतान राशि",
        "pa": "ਕੁੱਲ ਭੁਗਤਾਨ ਰਕਮ"
    },
    "cash_settlement_default": {
        "en": "Cash-First Settlement (Default)",
        "mr": "रोख-प्रथम व्यवहार (डीफॉल्ट)",
        "hi": "नकद-प्रथम निपटान (डिफ़ॉल्ट)",
        "pa": "ਨਕਦ-ਪਹਿਲਾਂ ਭੁਗਤਾਨ (ਮੂਲ)"
    },
    "dual_cash_title": {
        "en": "Dual Cash Handover Confirmation",
        "mr": "दुहेरी रोख हस्तांतरण पुष्टी",
        "hi": "दोहरी नकद सुपुर्दगी पुष्टि",
        "pa": "ਦੋਹਰੀ ਨਕਦ ਹੈਂਡਓਵਰ ਪੁਸ਼ਟੀ"
    },
    "dual_cash_desc": {
        "en": "Physical cash counted and handed over on-site with coarse GPS & timestamps.",
        "mr": "प्रत्यक्ष मोजून रोख रक्कम स्वीकारली, वेळ व जीपीएस स्थान नोंदवले गेले.",
        "hi": "हाथ में नकद गिनकर प्राप्त किया, समय और जीपीएस स्थान दर्ज हुआ।",
        "pa": "ਹੱਥ ਵਿੱਚ ਨਕਦ ਗਿਣ ਕੇ ਲਿਆ ਗਿਆ, ਸਮਾਂ ਅਤੇ ਜੀਪੀਐੱਸ ਸਥਾਨ ਦਰਜ ਹੋਇਆ।"
    },
    "partial_advance_toggle": {
        "en": "Partial Advance Payment (Balance Due Later)",
        "mr": "काही आगाऊ रक्कम (उर्वरित रक्कम नंतर)",
        "hi": "आंशिक अग्रिम भुगतान (बकाया बाद में)",
        "pa": "ਅੰਸ਼ਕ ਪੇਸ਼ਗੀ ਭੁਗਤਾਨ (ਬਾਕੀ ਬਾਅਦ ਵਿੱਚ)"
    },
    "advance_paid_label": {
        "en": "Advance Cash Paid",
        "mr": "दिलेली आगाऊ रोख रक्कम",
        "hi": "दी गई अग्रिम नकद राशि",
        "pa": "ਦਿੱਤੀ ਗਈ ਪੇਸ਼ਗੀ ਨਕਦ ਰਕਮ"
    },
    "remaining_balance_label": {
        "en": "Remaining Balance Due",
        "mr": "उर्वरित देय बाकी",
        "hi": "शेष बकाया राशि",
        "pa": "ਬਾਕੀ ਬਕਾਇਆ ਰਕਮ"
    },
    "collector_confirmed": {
        "en": "Collector Cash Confirmation",
        "mr": "संकलक रोख पावती पुष्टी",
        "hi": "संकलक नकद पावती पुष्टि",
        "pa": "ਸੰਗ੍ਰਹਿਕਰਤਾ ਨਕਦ ਰਸੀਦ ਪੁਸ਼ਟੀ"
    },
    "buyer_confirmed": {
        "en": "Buyer Cash Confirmation",
        "mr": "खरेदीदार रोख देयक पुष्टी",
        "hi": "खरीदार नकद भुगतान पुष्टि",
        "pa": "ਖਰੀਦਦਾਰ ਨਕਦ ਭੁਗਤਾਨ ਪੁਸ਼ਟੀ"
    },
    "btn_confirm_collector": {
        "en": "Mark Received (Collector)",
        "mr": "मिळाले म्हणून नोंद करा (संकलक)",
        "hi": "प्राप्त के रूप में चिह्नित करें (संकलक)",
        "pa": "ਪ੍ਰਾਪਤ ਵਜੋਂ ਦਰਜ ਕਰੋ (ਸੰਗ੍ਰਹਿਕਰਤਾ)"
    },
    "btn_confirm_buyer": {
        "en": "Mark Paid (Buyer)",
        "mr": "दिले म्हणून नोंद करा (खरेदीदार)",
        "hi": "भुगतान किया चिह्नित करें (खरीदार)",
        "pa": "ਭੁਗਤਾਨ ਕੀਤਾ ਦਰਜ ਕਰੋ (ਖਰੀਦਦਾਰ)"
    },
    "dual_confirmed_success": {
        "en": "Dual Cash Confirmation Recorded",
        "mr": "दुहेरी रोख हस्तांतरण यशस्वीपणे नोंदवले गेले",
        "hi": "दोहरी नकद पुष्टि सफलतापूर्वक दर्ज हुई",
        "pa": "ਦੋਹਰੀ ਨਕਦ ਪੁਸ਼ਟੀ ਸਫਲਤਾਪੂਰਵਕ ਦਰਜ ਹੋਈ"
    },

    # Wallet & Ledger
    "cash_in_hand_label": {
        "en": "Total Cash Earned (In Hand)",
        "mr": "एकूण मिळालेली प्रत्यक्ष रोख रक्कम",
        "hi": "कुल अर्जित नकद राशि (हाथ में)",
        "pa": "ਕੁੱਲ ਮਿਲੀ ਨਕਦ ਰਕਮ (ਹੱਥ ਵਿੱਚ)"
    },
    "cash_in_hand_sub": {
        "en": "Verified physical cash received upon handover",
        "mr": "हस्तांतरणाच्या वेळी प्रत्यक्ष मोजून घेतलेली रोख रक्कम",
        "hi": "हैंडओवर पर प्रत्यक्ष गिनकर प्राप्त की गई नकद राशि",
        "pa": "ਹੈਂਡਓਵਰ ਵੇਲੇ ਗਿਣ ਕੇ ਲਈ ਗਈ ਨਕਦ ਰਕਮ"
    },
    "trust_score_label": {
        "en": "Trust Score: {score}%",
        "mr": "विश्वास गुण: {score}%",
        "hi": "भरोसा स्कोर: {score}%",
        "pa": "ਭਰੋਸਾ ਸਕੋਰ: {score}%"
    },
    "digital_payout_title": {
        "en": "Digital Bank / UPI Payout",
        "mr": "डिजिटल बँक / UPI वर्ग",
        "hi": "डिजिटल बैंक / यूपीआई भुगतान",
        "pa": "ਡਿਜੀਟਲ ਬੈਂਕ / ਯੂਪੀਆਈ ਭੁਗਤਾਨ"
    },
    "payment_mode_cash": {
        "en": "Payment Mode: Cash in Hand",
        "mr": "पेमेंट पद्धत: प्रत्यक्ष रोख रक्कम",
        "hi": "भुगतान माध्यम: हाथ में नकद",
        "pa": "ਭੁਗਤਾਨ ਮੋਡ: ਹੱਥ ਵਿੱਚ ਨਕਦ"
    },
    "value_boost_label": {
        "en": "+20% Value Boost",
        "mr": "+२०% अतिरिक्त नफा",
        "hi": "+20% अतिरिक्त मुनाफा",
        "pa": "+20% ਵਾਧੂ ਮੁਨਾਫ਼ਾ"
    },
    "formal_channels_benefit": {
        "en": "by using CPCB certified formal channels.",
        "mr": "CPCB प्रमाणित अधिकृत मार्गांचा वापर करून.",
        "hi": "सीपीसीबी प्रमाणित अधिकृत माध्यमों का उपयोग करके।",
        "pa": "ਸੀਪੀਸੀਬੀ ਪ੍ਰਮਾਣਿਤ ਅਧਿਕਾਰਤ ਚੈਨਲਾਂ ਦੀ ਵਰਤੋਂ ਕਰਕੇ।"
    },
    "pending_dues_title": {
        "en": "Pending Buyer Dues",
        "mr": "खरेदीदाराकडून येणे बाकी रक्कम",
        "hi": "खरीदार की बकाया राशि",
        "pa": "ਖਰੀਦਦਾਰ ਦਾ ਬਕਾਇਆ"
    },
    "pending_dues_detail": {
        "en": "Balance credit owed to you by authorized recyclers",
        "mr": "अधिकृत खरेदीदारांकडून मिळायची बाकी असलेली शिल्लक",
        "hi": "अधिकृत खरीदारों द्वारा देय शेष राशि",
        "pa": "ਅਧਿਕਾਰਤ ਖਰੀਦਦਾਰਾਂ ਵੱਲ ਬਕਾਇਆ ਰਕਮ"
    },
    "all_settled_msg": {
        "en": "All buyer payments fully settled. No outstanding dues.",
        "mr": "सर्व खरेदीदारांचे हिशेब पूर्ण झाले. कोणतीही बाकी नाही.",
        "hi": "सभी खरीदारों का भुगतान पूर्ण हुआ। कोई बकाया नहीं है।",
        "pa": "ਸਾਰੇ ਖਰੀਦਦਾਰਾਂ ਦੇ ਭੁਗਤਾਨ ਮੁਕੰਮਲ ਹੋ ਗਏ। ਕੋਈ ਬਕਾਇਆ ਨਹੀਂ ਹੈ।"
    },
    "due_by_date": {
        "en": "Due by: {date}",
        "mr": "देय तारीख: {date}",
        "hi": "देय तिथि: {date}",
        "pa": "ਦੇਣ ਦੀ ਮਿਤੀ: {date}"
    },
    "btn_call_buyer": {
        "en": "Call Buyer ({phone})",
        "mr": "खरेदीदाराला कॉल करा ({phone})",
        "hi": "खरीदार को कॉल करें ({phone})",
        "pa": "ਖਰੀਦਦਾਰ ਨੂੰ ਕਾਲ ਕਰੋ ({phone})"
    },
    "btn_mark_cash_received": {
        "en": "Mark Received (Cash)",
        "mr": "रोख मिळाले म्हणून नोंदवा",
        "hi": "नकद प्राप्त दर्ज करें",
        "pa": "ਨਕਦ ਮਿਲਿਆ ਦਰਜ ਕਰੋ"
    },
    "cash_history_title": {
        "en": "Cash Handover History ({count})",
        "mr": "रोख हस्तांतरण इतिहास ({count})",
        "hi": "नकद हैंडओवर इतिहास ({count})",
        "pa": "ਨਕਦ ਹੈਂਡਓਵਰ ਇਤਿਹਾਸ ({count})"
    },
    "no_handovers_yet": {
        "en": "No completed handovers yet.",
        "mr": "अद्याप कोणतेही पूर्ण झालेले हस्तांतरण नाही.",
        "hi": "अभी तक कोई पूर्ण हैंडओवर नहीं हुआ।",
        "pa": "ਅਜੇ ਤੱਕ ਕੋਈ ਹੈਂਡਓਵਰ ਪੂਰਾ ਨਹੀਂ ਹੋਇਆ।"
    },
    "download_govt_receipt": {
        "en": "Download Government Receipt (PDF)",
        "mr": "सरकारी पावती डाउनलोड करा (PDF)",
        "hi": "सरकारी रसीद डाउनलोड करें (PDF)",
        "pa": "ਸਰਕਾਰੀ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (PDF)"
    },

    # Lot Detail & Cancel
    "scan_for_audit": {
        "en": "Scan for Audit",
        "mr": "तपासणीसाठी स्कॅन करा",
        "hi": "सत्यापन हेतु स्कैन करें",
        "pa": "ਜਾਂਚ ਲਈ ਸਕੈਨ ਕਰੋ"
    },
    "items_in_lot": {
        "en": "Items in this Lot ({count})",
        "mr": "या लॉटमधील वस्तू ({count})",
        "hi": "इस लॉट में वस्तुएं ({count})",
        "pa": "ਇਸ ਲਾਟ ਵਿੱਚ ਵਸਤੂਆਂ ({count})"
    },
    "final_settled_payout": {
        "en": "Final Settled Payout",
        "mr": "अंतिम जमा रक्कम",
        "hi": "अंतिम निपटान राशि",
        "pa": "ਅੰਤਿਮ ਨਿਪਟਾਰਾ ਰਕਮ"
    },
    "total_weight_label": {
        "en": "Total Weight: {weight}",
        "mr": "एकूण वजन: {weight}",
        "hi": "कुल वजन: {weight}",
        "pa": "ਕੁੱਲ ਵਜ਼ਨ: {weight}"
    },
    "waiting_recycler_quotes": {
        "en": "Waiting for authorized recyclers to submit quotes...",
        "mr": "अधिकृत पुनर्वापरदारांच्या कोटेशन्सची प्रतीक्षा करत आहे...",
        "hi": "अधिकृत रिसाइकिलरों के भाव की प्रतीक्षा की जा रही है...",
        "pa": "ਅਧਿਕਾਰਤ ਰੀਸਾਈਕਲਰਾਂ ਦੇ ਕੋਟੇਸ਼ਨਾਂ ਦੀ ਉਡੀਕ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ..."
    },
    "btn_cancel_lot": {
        "en": "Cancel this Lot",
        "mr": "हा लॉट रद्द करा",
        "hi": "यह लॉट रद्द करें",
        "pa": "ਇਹ ਲਾਟ ਰੱਦ ਕਰੋ"
    },
    "cancel_modal_title": {
        "en": "Cancel Scrap Lot",
        "mr": "भंगार लॉट रद्द करा",
        "hi": "कबाड़ लॉट रद्द करें",
        "pa": "ਕਬਾੜ ਲਾਟ ਰੱਦ ਕਰੋ"
    },
    "cancel_modal_sub": {
        "en": "Please select a reason (No penalty for informal collectors):",
        "mr": "कृपया कारण निवडा (असंघटित संकलकांवर कोणताही दंड नाही):",
        "hi": "कृपया कारण चुनें (संकलकों पर कोई जुर्माना नहीं):",
        "pa": "ਕਿਰਪਾ ਕਰਕੇ ਕਾਰਨ ਚੁਣੋ (ਸੰਗ੍ਰਹਿਕਰਤਾਵਾਂ 'ਤੇ ਕੋਈ ਜੁਰਮਾਨਾ ਨਹੀਂ):"
    },
    "reason_better_price": {
        "en": "Found better price elsewhere",
        "mr": "इतरत्र चांगला भाव मिळाला",
        "hi": "अन्यत्र बेहतर दाम मिला",
        "pa": "ਹੋਰ ਕਿਧਰੇ ਬਿਹਤਰ ਭਾਅ ਮਿਲਿਆ"
    },
    "reason_sold_locally": {
        "en": "Already sold locally",
        "mr": "स्थानिक पातळीवर आधीच विकले",
        "hi": "स्थानीय स्तर पर पहले ही बेच दिया",
        "pa": "ਪਹਿਲਾਂ ਹੀ ਸਥਾਨਕ ਤੌਰ 'ਤੇ ਵੇਚ ਦਿੱਤਾ"
    },
    "reason_not_ready": {
        "en": "Material not ready for pickup",
        "mr": "सामग्री पिकअपसाठी तयार नाही",
        "hi": "सामग्री पिकअप के लिए तैयार नहीं है",
        "pa": "ਸਮੱਗਰੀ ਪਿਕਅੱਪ ਲਈ ਤਿਆਰ ਨਹੀਂ ਹੈ"
    },
    "reason_wrong_weight": {
        "en": "Entered wrong weight/items",
        "mr": "चुकीचे वजन किंवा वस्तू नोंदवली गेली",
        "hi": "गलत वजन या वस्तुएं दर्ज की गईं",
        "pa": "ਗਲਤ ਵਜ਼ਨ ਜਾਂ ਵਸਤੂਆਂ ਦਰਜ ਹੋਈਆਂ"
    },
    "reason_other": {
        "en": "Other personal reason",
        "mr": "इतर वैयक्तिक कारण",
        "hi": "अन्य व्यक्तिगत कारण",
        "pa": "ਹੋਰ ਨਿੱਜੀ ਕਾਰਨ"
    },
    "btn_keep_lot": {
        "en": "Keep Lot",
        "mr": "लॉट ठेवा",
        "hi": "लॉट बनाए रखें",
        "pa": "ਲਾਟ ਰੱਖੋ"
    },
    "btn_confirm_cancel": {
        "en": "Confirm Cancel",
        "mr": "रद्द करण्याची पुष्टी करा",
        "hi": "रद्द करने की पुष्टि करें",
        "pa": "ਰੱਦ ਕਰਨ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ"
    },

    # Lot Builder & Add Scrap
    "step_progress": {
        "en": "Step {current} of {total}",
        "mr": "टप्पा {current} / {total}",
        "hi": "चरण {current} / {total}",
        "pa": "ਕਦਮ {current} / {total}"
    },
    "step1_desc": {
        "en": "Select the type of electronic or metal scrap",
        "mr": "इलेक्ट्रॉनिक किंवा धातू भंगाराचा प्रकार निवडा",
        "hi": "इलेक्ट्रॉनिक या धातु कबाड़ का प्रकार चुनें",
        "pa": "ਇਲੈਕਟ੍ਰਾਨਿਕ ਜਾਂ ਧਾਤੂ ਕਬਾੜ ਦੀ ਕਿਸਮ ਚੁਣੋ"
    },
    "btn_next_photos": {
        "en": "Next: Add Photos",
        "mr": "पुढे: फोटो जोडा",
        "hi": "आगे: फोटो जोड़ें",
        "pa": "ਅੱਗੇ: ਫੋਟੋ ਜੋੜੋ"
    },
    "step2_desc": {
        "en": "Take up to 4 clear photos for instant verified recycler quotes",
        "mr": "प्रमाणित पुनर्वापरदारांकडून अचूक भावासाठी ४ पर्यंत स्पष्ट फोटो घ्या",
        "hi": "सत्यापित रिसाइकिलर से सही भाव के लिए 4 तक स्पष्ट फोटो लें",
        "pa": "ਪ੍ਰਮਾਣਿਤ ਰੀਸਾਈਕਲਰਾਂ ਤੋਂ ਸਹੀ ਭਾਅ ਲਈ 4 ਤੱਕ ਸਾਫ਼ ਫੋਟੋਆਂ ਲਵੋ"
    },
    "capture_photo": {
        "en": "Capture Photo",
        "mr": "फोटो काढा",
        "hi": "फोटो खींचें",
        "pa": "ਫ਼ੋਟੋ ਖਿੱਚੋ"
    },
    "auto_compress": {
        "en": "Auto-compress",
        "mr": "स्वयंचलित कॉम्प्रेस",
        "hi": "स्वतः संपीड़न",
        "pa": "ਆਟੋ-ਕੰਪ੍ਰੈਸ"
    },
    "analyzing_visual": {
        "en": "Analyzing scrap visual features...",
        "mr": "भंगाराच्या दृश्य वैशिष्ट्यांचे विश्लेषण सुरू आहे...",
        "hi": "कबाड़ की दृश्य विशेषताओं का विश्लेषण हो रहा है...",
        "pa": "ਕਬਾੜ ਦੀਆਂ ਵਿਜ਼ੂਅਲ ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਹੋ ਰਿਹਾ ਹੈ..."
    },
    "confidence_label": {
        "en": "Confidence",
        "mr": "खात्री",
        "hi": "विश्वास",
        "pa": "ਭਰੋਸਾ"
    },
    "btn_accept_suggestion": {
        "en": "Accept",
        "mr": "स्वीकारा",
        "hi": "स्वीकारें",
        "pa": "ਮਨਜ਼ੂਰ ਕਰੋ"
    },
    "btn_accepted_suggestion": {
        "en": "Accepted",
        "mr": "स्वीकारले",
        "hi": "स्वीकृत",
        "pa": "ਮਨਜ਼ੂਰ ਕੀਤਾ"
    },
    "btn_change_category": {
        "en": "Change",
        "mr": "बदला",
        "hi": "बदलें",
        "pa": "ਬਦਲੋ"
    },
    "btn_skip_next": {
        "en": "Skip / Next",
        "mr": "वगळा / पुढे जा",
        "hi": "छोड़ें / आगे बढ़ें",
        "pa": "ਛੱਡੋ / ਅੱਗੇ ਵਧੋ"
    },
    "btn_next_weight": {
        "en": "Next: Enter Weight",
        "mr": "पुढे: वजन टाका",
        "hi": "आगे: वजन दर्ज करें",
        "pa": "ਅੱਗੇ: ਵਜ਼ਨ ਦਰਜ ਕਰੋ"
    },
    "step3_desc": {
        "en": "Enter approximate weight in kilograms (weigh-in verified later)",
        "mr": "अंदाजे वजन किलोमध्ये टाका (हस्तांतरणाच्या वेळी प्रत्यक्ष डिजिटल तपासणी होईल)",
        "hi": "अनुमानित वजन किलोग्राम में दर्ज करें (हैंडओवर पर डिजिटल जांच होगी)",
        "pa": "ਅੰਦਾਜ਼ਨ ਵਜ਼ਨ ਕਿੱਲੋ ਵਿੱਚ ਦਰਜ ਕਰੋ (ਹੈਂਡਓਵਰ ਵੇਲੇ ਡਿਜੀਟਲ ਜਾਂਚ ਹੋਵੇਗੀ)"
    },
    "item_condition_label": {
        "en": "Item Condition",
        "mr": "वस्तूची स्थिती",
        "hi": "वस्तु की स्थिति",
        "pa": "ਵਸਤੂ ਦੀ ਹਾਲਤ"
    },
    "btn_next_estimate": {
        "en": "Next: Instant Estimate",
        "mr": "पुढे: त्वरित मूल्य अंदाज",
        "hi": "आगे: तुरंत मूल्य अनुमान",
        "pa": "ਅੱਗੇ: ਤੁਰੰਤ ਮੁੱਲ ਅੰਦਾਜ਼ਾ"
    },
    "step4_desc": {
        "en": "Computed locally with verified pricing algorithms",
        "mr": "प्रमाणित किंमत अल्गोरिदमद्वारे स्थानिक पातळीवर मोजलेले",
        "hi": "सत्यापित मूल्य एल्गोरिदम द्वारा स्थानीय रूप से गणना की गई",
        "pa": "ਪ੍ਰਮਾਣਿਤ ਮੁੱਲ ਐਲਗੋਰਿਦਮ ਰਾਹੀਂ ਸਥਾਨਕ ਤੌਰ 'ਤੇ ਗਿਣਿਆ ਗਿਆ"
    },
    "instant_estimate_title": {
        "en": "Instant Value Estimate",
        "mr": "त्वरित मूल्य अंदाज",
        "hi": "तुरंत मूल्य अनुमान",
        "pa": "ਤੁਰੰਤ ਮੁੱਲ ਅੰਦਾਜ਼ਾ"
    },
    "offline_validated_badge": {
        "en": "Offline Validated",
        "mr": "ऑफलाइन प्रमाणित",
        "hi": "ऑफलाइन सत्यापित",
        "pa": "ਆਫਲਾਈਨ ਪ੍ਰਮਾਣਿਤ"
    },
    "minerals_recoverable_est": {
        "en": "Critical Minerals Recoverable (Est.)",
        "mr": "अंदाजे पुनर्प्राप्त होणारी धोरणात्मक खनिजे",
        "hi": "अनुमानित पुनर्प्राप्त होने वाले महत्वपूर्ण खनिज",
        "pa": "ਅੰਦਾਜ਼ਨ ਰਿਕਵਰ ਹੋਣ ਵਾਲੇ ਅਹਿਮ ਖਣਿਜ"
    },
    "zero_compliance_burden": {
        "en": "Paperwork and CPCB handover certificates auto-generated. Zero compliance burden.",
        "mr": "कागदपत्रे आणि CPCB हस्तांतरण प्रमाणपत्रे आपोआप तयार होतात. कोणताही अतिरिक्त ताण नाही.",
        "hi": "कागजी कार्रवाई और सीपीसीबी हैंडओवर प्रमाणपत्र स्वतः तैयार होते हैं। कोई अनुपालन बोझ नहीं।",
        "pa": "ਕਾਗਜ਼ੀ ਕਾਰਵਾਈ ਅਤੇ ਸੀਪੀਸੀਬੀ ਹੈਂਡਓਵਰ ਸਰਟੀਫਿਕੇਟ ਆਪਣੇ ਆਪ ਬਣਦੇ ਹਨ। ਕੋਈ ਵਾਧੂ ਬੋਝ ਨਹੀਂ।"
    },

    # Payment Success
    "payment_ready_transfer": {
        "en": "Payment Ready for Transfer",
        "mr": "रक्कम वर्ग करण्यासाठी तयार",
        "hi": "भुगतान हस्तांतरण के लिए तैयार",
        "pa": "ਭੁਗਤਾਨ ਟਰਾਂਸਫਰ ਲਈ ਤਿਆਰ"
    },
    "epr_compliant_settled": {
        "en": "EPR Compliant E-Waste Handover Settled",
        "mr": "EPR प्रमाणित ई-कचरा हस्तांतरण पूर्ण झाले",
        "hi": "ईपीआर अनुपालन ई-कचरा हैंडओवर संपन्न हुआ",
        "pa": "ਈਪੀਆਰ ਨਿਯਮਾਂ ਅਨੁਸਾਰ ਈ-ਕੂੜਾ ਹੈਂਡਓਵਰ ਮੁਕੰਮਲ ਹੋਇਆ"
    },
    "total_net_payout": {
        "en": "Total Net Payout",
        "mr": "एकूण निव्वळ रक्कम",
        "hi": "कुल शुद्ध भुगतान",
        "pa": "ਕੁੱਲ ਨਕਦ ਭੁਗਤਾਨ"
    },
    "platform_fee_zero": {
        "en": "Platform Fee: ₹0.00 (No fee for you)",
        "mr": "प्लॅटफॉर्म शुल्क: ₹०.०० (आपल्यासाठी पूर्णपणे मोफत)",
        "hi": "प्लेटफ़ॉर्म शुल्क: ₹0.00 (आपके लिए बिल्कुल मुफ्त)",
        "pa": "ਪਲੇਟਫਾਰਮ ਫੀਸ: ₹0.00 (ਤੁਹਾਡੇ ਲਈ ਬਿਲਕੁਲ ਮੁਫ਼ਤ)"
    },
    "payment_reference": {
        "en": "Payment Reference",
        "mr": "पेमेंट संदर्भ",
        "hi": "भुगतान संदर्भ",
        "pa": "ਭੁਗਤਾਨ ਹਵਾਲਾ"
    },
    "receipt_number": {
        "en": "Receipt Number",
        "mr": "पावती क्रमांक",
        "hi": "रसीद संख्या",
        "pa": "ਰਸੀਦ ਨੰਬਰ"
    },
    "authorized_buyer_label": {
        "en": "Authorized Buyer",
        "mr": "अधिकृत खरेदीदार",
        "hi": "अधिकृत खरीदार",
        "pa": "ਅਧਿਕਾਰਤ ਖਰੀਦਦਾਰ"
    },
    "btn_instant_upi": {
        "en": "Instant Simulated UPI Payout",
        "mr": "त्वरित UPI वर्ग",
        "hi": "तुरंत यूपीआई भुगतान",
        "pa": "ਤੁਰੰਤ ਯੂਪੀਆਈ ਭੁਗਤਾਨ"
    },
    "btn_collect_cash": {
        "en": "Collect Physical Cash on Handover",
        "mr": "हस्तांतरणावर प्रत्यक्ष रोख रक्कम स्वीकारा",
        "hi": "हैंडओवर पर प्रत्यक्ष नकद प्राप्त करें",
        "pa": "ਹੈਂਡਓਵਰ 'ਤੇ ਨਕਦ ਰਕਮ ਪ੍ਰਾਪਤ ਕਰੋ"
    },
    "btn_go_wallet": {
        "en": "Go to My Wallet",
        "mr": "माझ्या नोंदवहीकडे जा",
        "hi": "मेरे बहीखाते पर जाएं",
        "pa": "ਮੇਰੇ ਬਹੀਖਾਤੇ 'ਤੇ ਜਾਓ"
    },

    # Offline Bar
    "offline_local_saved": {
        "en": "Offline — Data saved locally",
        "mr": "ऑफलाइन — माहिती सुरक्षित सेव्ह झाली",
        "hi": "ऑफलाइन — डेटा सुरक्षित सहेजा गया",
        "pa": "ਆਫਲਾਈਨ — ਡਾਟਾ ਸੁਰੱਖਿਅਤ ਸੇਵ ਹੋਇਆ"
    },
    "simulated_offline_active": {
        "en": "Simulated Offline Mode Active",
        "mr": "सिम्युलेटेड ऑफलाइन मोड सक्रिय",
        "hi": "सिम्युलेटेड ऑफलाइन मोड सक्रिय",
        "pa": "ਸਿਮੂਲੇਟਿਡ ਆਫਲਾਈਨ ਮੋਡ ਚਾਲੂ"
    },
    "syncing_server": {
        "en": "Syncing with Server...",
        "mr": "सर्व्हरशी सिंक होत आहे...",
        "hi": "सर्वर से सिंक हो रहा है...",
        "pa": "ਸਰਵਰ ਨਾਲ ਸਿੰਕ ਹੋ ਰਿਹਾ ਹੈ..."
    },
    "items_waiting_sync": {
        "en": "{count} item(s) waiting to sync",
        "mr": "{count} वस्तू सिंक होण्याच्या प्रतीक्षेत",
        "hi": "{count} वस्तुएं सिंक की प्रतीक्षा में",
        "pa": "{count} ਵਸਤੂਆਂ ਸਿੰਕ ਹੋਣ ਦੀ ਉਡੀਕ ਵਿੱਚ"
    },
    "handover_in_progress": {
        "en": "Handover in Progress",
        "mr": "हस्तांतरण प्रक्रियेत आहे",
        "hi": "हैंडओवर प्रगति पर है",
        "pa": "ਹੈਂਡਓਵਰ ਜਾਰੀ ਹੈ"
    },
    "handover_complete": {
        "en": "Handover Complete",
        "mr": "हस्तांतरण पूर्ण झाले",
        "hi": "हैंडओवर पूर्ण हुआ",
        "pa": "ਹੈਂਡਓਵਰ ਮੁਕੰਮਲ ਹੋਇਆ"
    },
    "btn_track_agent": {
        "en": "Track Agent",
        "mr": "एजंटचा मागोवा घ्या",
        "hi": "एजेंट को ट्रैक करें",
        "pa": "ਏਜੰਟ ਨੂੰ ਟਰੈਕ ਕਰੋ"
    },
    "btn_view_handover": {
        "en": "View Handover",
        "mr": "हस्तांतरण पहा",
        "hi": "हैंडओवर देखें",
        "pa": "ਹੈਂਡਓਵਰ ਵੇਖੋ"
    }
}

i18n_dir = "d:/PROJECTS/kabadiwala/web/src/i18n"
languages = ['en', 'hi', 'mr', 'pa']

for lang in languages:
    filepath = os.path.join(i18n_dir, f"{lang}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    # Insert new keys before categories and ai
    categories = content.pop("categories", {})
    ai = content.pop("ai", {})
    
    for key, val_dict in new_keys.items():
        content[key] = val_dict[lang]
        
    content["categories"] = categories
    content["ai"] = ai
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
        f.write("\n")

print(f"Successfully updated all {len(languages)} translation files with {len(new_keys)} new keys.")
