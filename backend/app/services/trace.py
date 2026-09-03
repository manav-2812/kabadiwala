import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Sequence

GENESIS_HASH = "0" * 64

def canonical_json(data: Any) -> str:
    """Returns deterministic, sorted, compact JSON string for cryptographic hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)

def compute_event_hash(
    prev_hash: str,
    seq: int,
    event_type: str,
    payload: Dict[str, Any],
    occurred_at: datetime | str
) -> str:
    iso_time = occurred_at.isoformat() if isinstance(occurred_at, datetime) else occurred_at
    payload_str = canonical_json(payload)
    raw = f"{prev_hash}{seq}{event_type}{payload_str}{iso_time}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_event_chain(events: Sequence[Any]) -> Dict[str, Any]:
    """
    Verifies the integrity of a list of TraceabilityEvent records ordered by seq.
    Returns:
      {
        "valid": bool,
        "total_events": int,
