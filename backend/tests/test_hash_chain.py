# [SIH-2026-PS-SIH26229] Iteration 116 polish
import pytest
from datetime import datetime, timezone
from app.services.trace import compute_event_hash, verify_event_chain, GENESIS_HASH

class MockEvent:
    def __init__(self, seq, event_type, payload, occurred_at, prev_hash, event_hash):
        self.seq = seq
        self.event_type = event_type
        self.payload_json = payload
        self.occurred_at = occurred_at
        self.prev_hash = prev_hash
        self.event_hash = event_hash

def test_hash_chain_valid_sequence():
    now = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    
    # Block 1
    p1 = {"action": "created", "lot": "KC-001"}
    h1 = compute_event_hash(GENESIS_HASH, 1, "lot_created", p1, now)
    e1 = MockEvent(1, "lot_created", p1, now, GENESIS_HASH, h1)

    # Block 2
    p2 = {"status": "listed"}
    h2 = compute_event_hash(h1, 2, "listed", p2, now)
    e2 = MockEvent(2, "listed", p2, now, h1, h2)

    # Block 3
    p3 = {"amount": 2500}
    h3 = compute_event_hash(h2, 3, "quoted", p3, now)
    e3 = MockEvent(3, "quoted", p3, now, h2, h3)

    res = verify_event_chain([e1, e2, e3])
    assert res["valid"] is True
    assert res["total_events"] == 3
    assert res["broken_at_seq"] is None
    assert res["last_hash"] == h3

def test_hash_chain_tampered_payload():
    now = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    
    p1 = {"action": "created"}
    h1 = compute_event_hash(GENESIS_HASH, 1, "lot_created", p1, now)
    e1 = MockEvent(1, "lot_created", p1, now, GENESIS_HASH, h1)

    p2 = {"status": "listed"}
    h2 = compute_event_hash(h1, 2, "listed", p2, now)
    # Tamper with block 2 hash
    tampered_h2 = "deadbeef" + h2[8:]
    e2 = MockEvent(2, "listed", p2, now, h1, tampered_h2)

    res = verify_event_chain([e1, e2])
    assert res["valid"] is False
    assert res["broken_at_seq"] == 2

def test_hash_chain_broken_prev_link():
    now = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    
    p1 = {"action": "created"}
    h1 = compute_event_hash(GENESIS_HASH, 1, "lot_created", p1, now)
    e1 = MockEvent(1, "lot_created", p1, now, GENESIS_HASH, h1)

    p2 = {"status": "listed"}
    # Prev hash points to wrong value
    wrong_prev = "1" * 64
    h2 = compute_event_hash(wrong_prev, 2, "listed", p2, now)
    e2 = MockEvent(2, "listed", p2, now, wrong_prev, h2)

    res = verify_event_chain([e1, e2])
    assert res["valid"] is False
    assert res["broken_at_seq"] == 2
