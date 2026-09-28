from typing import Any

from fastapi import HTTPException

ERROR_MESSAGES = {
    "en": {
        "auth_invalid_otp": "Invalid or expired OTP. Please try again.",
        "auth_user_not_found": "User account not found.",
        "auth_unauthorized": "You do not have permission to access this resource.",
        "lot_not_found": "Scrap lot not found.",
        "invalid_state_transition": "Illegal order state transition.",
        "basket_empty": "Your scrap basket is empty.",
        "quote_not_found": "Quote not found or expired.",
        "transaction_not_found": "Transaction not found.",
        "weight_variance_high": "Weight variance exceeds 10%. Confirmation required.",
        "payment_failed": "Payment processing failed. Please retry or choose cash.",
        "chain_tampered": "Audit hash chain integrity violation detected.",
        "dispute_active": "An active dispute is blocking this action."
    },
    "hi": {
        "auth_invalid_otp": "अमान्य या समाप्त ओटीपी। कृपया पुन: प्रयास करें।",
        "auth_user_not_found": "उपयोगकर्ता खाता नहीं मिला।",
        "auth_unauthorized": "आपको इस संसाधन तक पहुंचने की अनुमति नहीं है।",
        "lot_not_found": "कबाड़ लॉट नहीं मिला।",
        "invalid_state_transition": "अमान्य लॉट स्थिति परिवर्तन।",
        "basket_empty": "आपकी कबाड़ टोकरी खाली है।",
        "quote_not_found": "कोटेशन नहीं मिला या समाप्त हो गया।",
        "transaction_not_found": "लेनदेन नहीं मिला।",
        "weight_variance_high": "वजन में 10% से अधिक अंतर है। पुष्टि आवश्यक है।",
        "payment_failed": "भुगतान विफल रहा। कृपया पुनः प्रयास करें या नकद चुनें।",
        "chain_tampered": "ऑडिट हैश सुरक्षा उल्लंघन का पता चला।",
        "dispute_active": "एक सक्रिय विवाद इस कार्रवाई को रोक रहा है।"
    },
    "pa": {
        "auth_invalid_otp": "ਅਵੈਧ ਜਾਂ ਮਿਆਦ ਪੁੱਗ ਚੁੱਕਾ ਓਟੀਪੀ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "auth_user_not_found": "ਉਪਭੋਗਤਾ ਖਾਤਾ ਨਹੀਂ ਲੱਭਿਆ।",
        "auth_unauthorized": "ਤੁਹਾਡੇ ਕੋਲ ਇਸ ਸਰੋਤ ਤੱਕ ਪਹੁੰਚਣ ਦੀ ਇਜਾਜ਼ਤ ਨਹੀਂ ਹੈ।",
        "lot_not_found": "ਕਬਾੜ ਲਾਟ ਨਹੀਂ ਲੱਭੀ।",
        "invalid_state_transition": "ਗੈਰ-ਕਾਨੂੰਨੀ ਆਰਡਰ ਸਥਿਤੀ ਤਬਦੀਲੀ।",
        "basket_empty": "ਤੁਹਾਡੀ ਕਬਾੜ ਟੋਕਰੀ ਖਾਲੀ ਹੈ।",
        "quote_not_found": "ਕੋਟੇਸ਼ਨ ਨਹੀਂ ਮਿਲੀ ਜਾਂ ਮਿਆਦ ਪੁੱਗ ਗਈ।",
        "transaction_not_found": "ਲੈਣ-ਦੇਣ ਨਹੀਂ ਮਿਲਿਆ।",
        "weight_variance_high": "ਭਾਰ ਵਿੱਚ 10% ਤੋਂ ਵੱਧ ਅੰਤਰ ਹੈ। ਪੁਸ਼ਟੀ ਦੀ ਲੋੜ ਹੈ।",
        "payment_failed": "ਭੁਗਤਾਨ ਅਸਫਲ ਰਿਹਾ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ ਜਾਂ ਨਕਦ ਚੁਣੋ।",
        "chain_tampered": "ਆਡਿਟ ਹੈਸ਼ ਸੁਰੱਖਿਆ ਉਲੰਘਣਾ ਦਾ ਪਤਾ ਲੱਗਾ।",
        "dispute_active": "ਇੱਕ ਕਿਰਿਆਸ਼ੀਲ ਵਿਵਾਦ ਇਸ ਕਾਰਵਾਈ ਨੂੰ ਰੋਕ ਰਿਹਾ ਹੈ।"
    }
}

class KabadiwalaAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message_key: str,
        details: dict[str, Any] | None = None,
        detail: Any | None = None
    ):
        info = details if details is not None else ({"info": detail} if isinstance(detail, str) else (detail or {}))
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message_key": message_key,
                "details": info
            }
        )
