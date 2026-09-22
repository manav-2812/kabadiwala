# [SIH-2026-PS-SIH26229] Iteration 2 polish
import pytest
from app.core.lot_state import validate_transition, LotStatus, get_allowed_next_states
from app.core.i18n import KabadiwalaAPIException

def test_valid_forward_transitions():
    assert validate_transition(LotStatus.DRAFT, LotStatus.LISTED) is True
    assert validate_transition(LotStatus.LISTED, LotStatus.QUOTED) is True
    assert validate_transition(LotStatus.QUOTED, LotStatus.ACCEPTED) is True
    assert validate_transition(LotStatus.ACCEPTED, LotStatus.PICKUP_SCHEDULED) is True
    assert validate_transition(LotStatus.PICKUP_SCHEDULED, LotStatus.ARRIVED) is True
    assert validate_transition(LotStatus.ARRIVED, LotStatus.WEIGHED) is True
    assert validate_transition(LotStatus.WEIGHED, LotStatus.PAYMENT_PENDING) is True
    assert validate_transition(LotStatus.PAYMENT_PENDING, LotStatus.COMPLETED) is True

def test_valid_side_exit_dispute():
    assert validate_transition(LotStatus.WEIGHED, LotStatus.DISPUTED) is True
    assert validate_transition(LotStatus.DISPUTED, LotStatus.RESOLVED_ACCEPTED) is True
    assert validate_transition(LotStatus.RESOLVED_ACCEPTED, LotStatus.PAYMENT_PENDING) is True

def test_valid_cancellation():
    assert validate_transition(LotStatus.DRAFT, LotStatus.CANCELLED) is True
    assert validate_transition(LotStatus.LISTED, LotStatus.CANCELLED) is True
    assert validate_transition(LotStatus.QUOTED, LotStatus.CANCELLED) is True

def test_illegal_transition_raises_409():
    with pytest.raises(KabadiwalaAPIException) as exc_info:
        validate_transition(LotStatus.DRAFT, LotStatus.COMPLETED)
    assert exc_info.value.status_code == 409
    assert isinstance(exc_info.value.detail, dict)
    assert exc_info.value.detail["code"] == "ILLEGAL_TRANSITION"

def test_completed_cannot_revert_to_draft():
    with pytest.raises(KabadiwalaAPIException) as exc_info:
        validate_transition(LotStatus.COMPLETED, LotStatus.DRAFT)
    assert exc_info.value.status_code == 409

def test_allowed_next_states():
    next_states = get_allowed_next_states(LotStatus.DRAFT)
    assert "listed" in next_states
    assert "cancelled" in next_states
    assert "completed" not in next_states
