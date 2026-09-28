from datetime import datetime
from typing import Any

from pydantic import BaseModel


# Auth schemas
class OTPRequest(BaseModel):
    phone: str | None = None
    email: str | None = None

class OTPVerifyRequest(BaseModel):
    phone: str | None = None
    email: str | None = None
    otp: str

class SignupRequest(BaseModel):
    phone: str | None = None
    email: str | None = None
    name: str
    role: str = "collector"  # validated at handler level against _ALLOWED_SIGNUP_ROLES
    language: str = "hi"
    city: str | None = None
    state: str | None = None
    address: str | None = None
    company_name: str | None = None
    cpcb_license_no: str | None = None
    spcb_authorization_no: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]

class UserResponse(BaseModel):
    id: str
    phone: str
    name: str
    role: str
    language: str
    avatar_url: str | None = None
    is_active: bool
    profile: dict[str, Any] | None = None

class MeUpdate(BaseModel):
    name: str | None = None
    language: str | None = None
    avatar_url: str | None = None
    upi_id: str | None = None

# Material & Mineral schemas
class MaterialCompositionResponse(BaseModel):
    element: str
    grams_per_kg: float
    source_note: str

class MaterialResponse(BaseModel):
    id: str
    code: str
    name_en: str
    name_hi: str
    name_mr: str | None = None
    name_pa: str
    icon_key: str
    base_price_paise_per_kg: int
    price_floor_paise: int
    price_ceiling_paise: int
    is_hazardous: bool
    hazard_level: str
    hazard_note_en: str
    hazard_note_hi: str
    hazard_note_mr: str | None = None
    hazard_note_pa: str
    safety_tip_en: str
    safety_tip_hi: str
    safety_tip_mr: str | None = None
    safety_tip_pa: str
    strategic_flag: bool
    compositions: list[MaterialCompositionResponse] = []

# Price schemas
class PriceHistoryItem(BaseModel):
    date: str
    price_paise_per_kg: int
    min_paise: int
    max_paise: int

class PriceSummaryItem(BaseModel):
    material_id: str
    material_code: str
    name_en: str
    name_hi: str
    name_mr: str | None = None
    name_pa: str
    current_price_paise_per_kg: int
    change_pct_14d: float
    trend_reason_en: str
    trend_reason_hi: str
    trend_reason_mr: str | None = None
    trend_reason_pa: str
    sparkline: list[int]
    is_hazardous: bool

# Lot & Basket schemas
class LotItemCreate(BaseModel):
    material_id: str
    est_weight_g: int
    condition: str = "broken" # working, broken, burnt, unknown
    photo_urls: list[str] = []
    ai_suggested_material_id: str | None = None
    ai_confidence: float | None = None
    user_override: bool = False

class LotItemResponse(BaseModel):
    id: str
    material_id: str
    material_code: str | None = None
    material_name: str | None = None
    est_weight_g: int
    actual_weight_g: int | None = None
    condition: str
    est_value_min_paise: int
    est_value_max_paise: int
    final_value_paise: int | None = None
    photo_urls: list[str] = []

class LotCreate(BaseModel):
    items: list[LotItemCreate]
    pickup_lat: float | None = 28.6139
    pickup_lng: float | None = 77.2090
    pickup_address: str | None = "Main Market, Sector 12"
    client_uuid: str | None = None
    offline_created: bool = False

class MineralChip(BaseModel):
    element: str
    name: str
    grams: float
    is_strategic: bool

class EstimateItemRequest(BaseModel):
    material_code: str
    weight_kg: float
    condition: str = "broken"
    city: str | None = None

class EstimateItemResponse(BaseModel):
    material_code: str
    weight_kg: float
    min_paise: int
    max_paise: int
    min_inr: float
    max_inr: float
    condition_factor: float
    base_price_paise_per_kg: int

class LotEstimateResponse(BaseModel):
    items: list[EstimateItemResponse]
    total_min_paise: int
    total_max_paise: int
    total_min_inr: float
    total_max_inr: float
    total_weight_kg: float
    recoverable_minerals: list[MineralChip]
    is_hazardous: bool
    explanation: str

class LotResponse(BaseModel):
    id: str
    lot_code: str
    collector_id: str
    collector_name: str | None = None
    status: str
    est_total_min_paise: int
    est_total_max_paise: int
    est_total_weight_g: int
    actual_total_weight_g: int | None = None
    final_amount_paise: int | None = None
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    is_hazardous: bool
    created_at: datetime
    items: list[LotItemResponse] = []
    quote_count: int = 0
    active_quote: dict[str, Any] | None = None
    transaction: dict[str, Any] | None = None

class BasketItemRequest(BaseModel):
    material_id: str
    est_weight_g: int
    condition: str = "broken"
    photo_urls: list[str] = []

class BasketResponse(BaseModel):
    items: list[LotItemResponse]
    total_items: int
    est_total_min_paise: int
    est_total_max_paise: int
    est_total_weight_g: int
    recoverable_minerals: list[MineralChip]
    is_hazardous: bool

# Quote schemas
class QuoteCreate(BaseModel):
    lot_id: str
    price_paise_total: int
    pickup_mode: str = "pickup" # pickup, dropoff
    pickup_eta_hours: int = 2
    note: str = ""

class QuoteResponse(BaseModel):
    id: str
    lot_id: str
    recycler_id: str
    recycler_name: str
    recycler_cpcb_license: str
    recycler_rating: float
    price_paise_total: int
    pickup_mode: str
    pickup_eta_at: datetime
    valid_until: datetime
    status: str
    note: str
    is_best_price: bool = False
    is_nearest: bool = False

# Recycler Match schemas
class RecyclerMatchItem(BaseModel):
    id: str
    company_name: str
    contact_person: str
    address: str
    city: str
    lat: float
    lng: float
    distance_km: float
    cpcb_license_no: str
    spcb_authorization_no: str
    license_valid_to: datetime
    authorization_status: str
    rating_avg: float
    reliability_score: int
    pickup_available: bool
    estimated_payout_paise: int
    ranking_score: float
    ranking_reason: str

# Transaction & Handover schemas
class WeighInRequest(BaseModel):
    actual_weights: dict[str, int] # item_id -> grams
    recycler_notes: str | None = None
    rejected_item_ids: list[str] | None = []

class HandoverConfirmRequest(BaseModel):
    otp_or_qr: str

class CashHandoverConfirmRequest(BaseModel):
    role: str = "collector" # collector or buyer
    cash_amount_paise: int | None = None
    is_partial: bool = False
    advance_paise: int | None = None
    balance_paise: int | None = None
    due_days: int | None = 7
    lat: float | None = 28.6139
    lng: float | None = 77.2090

class DisputeRequest(BaseModel):
    reason: str

# Payment schemas
class PaymentInitiateRequest(BaseModel):
    transaction_id: str
    method: str = "upi" # upi, cash, wallet
    upi_id: str | None = None

class PaymentResponse(BaseModel):
    id: str
    transaction_id: str
    amount_paise: int
    method: str
    upi_ref: str | None = None
    status: str
    paid_at: datetime | None = None
    failure_reason: str | None = None
    platform_fee_paise: int = 0

# Traceability schemas
class TraceEventResponse(BaseModel):
    id: str
    lot_id: str
    seq: int
    event_type: str
    actor_user_id: str
    actor_role: str
    payload: dict[str, Any]
    geo_lat: float | None = None
    geo_lng: float | None = None
    occurred_at: datetime
    prev_hash: str
    event_hash: str

class TraceVerifyResponse(BaseModel):
    lot_id: str
    valid: bool
    total_events: int
    broken_at_seq: int | None = None
    last_hash: str

# Support schemas
class TicketCreate(BaseModel):
    category: str
    lot_id: str | None = None
    transaction_id: str | None = None
    message: str
    language: str = "hi"
    attachment_url: str | None = None
    attachment_type: str = "none" # none, image, voice
    duration_s: int | None = None

class MessageCreate(BaseModel):
    body: str
    attachment_url: str | None = None
    attachment_type: str = "none"
    duration_s: int | None = None

class TicketMessageResponse(BaseModel):
    id: str
    sender_type: str
    sender_name: str | None = None
    body: str
    attachment_url: str | None = None
    attachment_type: str
    duration_s: int | None = None
    created_at: datetime

class SupportTicketResponse(BaseModel):
    id: str
    ticket_no: str
    category: str
    priority: str
    status: str
    lot_id: str | None = None
    lot_code: str | None = None
    language: str
    first_response_due_at: datetime
    resolution_due_at: datetime
    first_responded_at: datetime | None = None
    resolved_at: datetime | None = None
    is_sla_breached: bool = False
    messages: list[TicketMessageResponse] = []

class FAQResponse(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    audio_url: str | None = None

# Notification schemas
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    body: str
    sms_preview: str
    payload: dict[str, Any]
    read_at: datetime | None = None
    created_at: datetime

# Live Tracking schemas
class TrackingPoint(BaseModel):
    transaction_id: str
    agent_name: str
    agent_phone: str
    agent_vehicle: str
    lat: float
    lng: float
    speed_kmh: float
    eta_min: int
    is_arrived: bool

# Dashboard KPIs
class AdminKPIs(BaseModel):
    formalised_tonnes: float
    active_collectors: int
    authorized_recyclers: int
    total_payouts_inr: float
    avg_collector_premium_pct: float
    critical_minerals_recovered_kg: float

class MineralRecoveryStat(BaseModel):
    element: str
    name: str
    total_kg: float
    import_offset_pct: float
    color_hex: str
