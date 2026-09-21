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
        "broken_at_seq": Optional[int],
        "last_hash": str
      }
    """
    if not events:
        return {
            "valid": True,
            "total_events": 0,
            "broken_at_seq": None,
            "last_hash": GENESIS_HASH
        }
        
    prev_hash = GENESIS_HASH
    for expected_seq, event in enumerate(events, start=1):
        if event.seq != expected_seq:
            return {
                "valid": False,
                "total_events": len(events),
                "broken_at_seq": event.seq,
                "last_hash": event.event_hash
            }
        
        if event.prev_hash != prev_hash:
            return {
                "valid": False,
                "total_events": len(events),
                "broken_at_seq": event.seq,
                "last_hash": event.event_hash
            }
            
        # Parse payload
        try:
            payload = json.loads(event.payload_json) if isinstance(event.payload_json, str) else event.payload_json
        except Exception:
            payload = {}

        expected_hash = compute_event_hash(
            prev_hash=event.prev_hash,
            seq=event.seq,
            event_type=event.event_type,
            payload=payload,
            occurred_at=event.occurred_at
        )

        if event.event_hash != expected_hash:
            return {
                "valid": False,
                "total_events": len(events),
                "broken_at_seq": event.seq,
                "last_hash": event.event_hash
            }
            
        prev_hash = event.event_hash

    return {
        "valid": True,
        "total_events": len(events),
        "broken_at_seq": None,
        "last_hash": prev_hash
    }
