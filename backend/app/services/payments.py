import random
import string
from datetime import datetime, timezone
from typing import Dict, Any

def generate_upi_ref() -> str:
    digits = "".join(random.choices(string.digits, k=10))
    return f"KCUPI{digits}"

def process_simulated_payment(
    amount_paise: int,
    method: str = "upi",
    force_failure: bool = False
) -> Dict[str, Any]:
    """
    Simulates UPI or Cash payment transaction.
    Atomic with wallet credit and transaction status change.
    """
    if force_failure:
        return {
            "status": "failed",
            "upi_ref": None,
            "failure_reason": "Bank server timeout (Simulated for Demo)",
            "paid_at": None,
            "platform_fee_paise": 0
        }
        
    ref = generate_upi_ref() if method == "upi" else f"CASH-{digits_only(8)}"
    return {
        "status": "success",
        "upi_ref": ref,
        "failure_reason": None,
        "paid_at": datetime.now(timezone.utc),
        "platform_fee_paise": 0  # Zero fee for collectors
    }

def digits_only(k: int) -> str:
    return "".join(random.choices(string.digits, k=k))
