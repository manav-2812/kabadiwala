from enum import Enum

from app.core.i18n import KabadiwalaAPIException


class LotStatus(str, Enum):
    DRAFT = "draft"
    LISTED = "listed"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    PICKUP_SCHEDULED = "pickup_scheduled"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    WEIGHED = "weighed"
    AWAITING_CONFIRM = "awaiting_confirm"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_FAILED = "payment_failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    BUYER_NO_SHOW = "buyer_no_show"
    DISPUTED = "disputed"
    RESOLVED_ACCEPTED = "resolved_accepted"
    RESOLVED_REVISED = "resolved_revised"
    RESOLVED_CANCELLED = "resolved_cancelled"
    REFUND_REVIEW = "refund_review"

# Allowed forward transitions and side exits
TRANSITIONS: dict[LotStatus, set[LotStatus]] = {
    LotStatus.DRAFT: {LotStatus.LISTED, LotStatus.CANCELLED},
    LotStatus.LISTED: {LotStatus.QUOTED, LotStatus.CANCELLED},
    LotStatus.QUOTED: {LotStatus.ACCEPTED, LotStatus.LISTED, LotStatus.CANCELLED},
    LotStatus.ACCEPTED: {
        LotStatus.PICKUP_SCHEDULED,
        LotStatus.IN_TRANSIT,
        LotStatus.ARRIVED,
        LotStatus.RESCHEDULED,
        LotStatus.BUYER_NO_SHOW,
        LotStatus.CANCELLED
    },
    LotStatus.PICKUP_SCHEDULED: {
        LotStatus.IN_TRANSIT,
        LotStatus.ARRIVED,
        LotStatus.RESCHEDULED,
        LotStatus.BUYER_NO_SHOW,
        LotStatus.CANCELLED
    },
    LotStatus.IN_TRANSIT: {
        LotStatus.ARRIVED,
        LotStatus.BUYER_NO_SHOW,
        LotStatus.RESCHEDULED
    },
    LotStatus.ARRIVED: {LotStatus.WEIGHED, LotStatus.DISPUTED},
    LotStatus.WEIGHED: {LotStatus.AWAITING_CONFIRM, LotStatus.PAYMENT_PENDING, LotStatus.DISPUTED},
    LotStatus.AWAITING_CONFIRM: {
        LotStatus.PAYMENT_PENDING,
        LotStatus.DISPUTED
    },
    LotStatus.PAYMENT_PENDING: {
        LotStatus.COMPLETED,
        LotStatus.PAYMENT_FAILED
    },
    LotStatus.PAYMENT_FAILED: {
        LotStatus.PAYMENT_PENDING,  # Retry
        LotStatus.COMPLETED         # Manual cash fallback
    },
    LotStatus.RESCHEDULED: {LotStatus.PICKUP_SCHEDULED, LotStatus.CANCELLED},
    LotStatus.BUYER_NO_SHOW: {LotStatus.LISTED, LotStatus.CANCELLED},
    LotStatus.DISPUTED: {
        LotStatus.RESOLVED_ACCEPTED,
        LotStatus.RESOLVED_REVISED,
        LotStatus.RESOLVED_CANCELLED
    },
    LotStatus.RESOLVED_ACCEPTED: {LotStatus.PAYMENT_PENDING, LotStatus.COMPLETED},
    LotStatus.RESOLVED_REVISED: {LotStatus.PAYMENT_PENDING, LotStatus.COMPLETED},
    LotStatus.RESOLVED_CANCELLED: {LotStatus.CANCELLED},
    LotStatus.COMPLETED: {LotStatus.REFUND_REVIEW},
    LotStatus.CANCELLED: set(),
    LotStatus.REFUND_REVIEW: {LotStatus.COMPLETED}
}

def validate_transition(current: LotStatus | str, next_state: LotStatus | str) -> bool:
    curr_enum = LotStatus(current) if isinstance(current, str) else current
    next_enum = LotStatus(next_state) if isinstance(next_state, str) else next_state

    allowed = TRANSITIONS.get(curr_enum, set())
    if next_enum not in allowed:
        raise KabadiwalaAPIException(
            status_code=409,
            code="ILLEGAL_TRANSITION",
            message_key="invalid_state_transition",
            details={
                "current_status": curr_enum.value,
                "requested_status": next_enum.value,
                "allowed_transitions": [s.value for s in allowed]
            }
        )
    return True

def get_allowed_next_states(current: LotStatus | str) -> list[str]:
    curr_enum = LotStatus(current) if isinstance(current, str) else current
    return [s.value for s in TRANSITIONS.get(curr_enum, set())]
