from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Auth schemas
class OTPRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    otp: str

class SignupRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    name: str
    role: str = "collector"  # validated at handler level against _ALLOWED_SIGNUP_ROLES
    language: str = "hi"
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None
    cpcb_license_no: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    phone: str
    name: str
    role: str
    language: str
    avatar_url: Optional[str] = None
    is_active: bool
    profile: Optional[Dict[str, Any]] = None

class MeUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None
    upi_id: Optional[str] = None

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
    name_mr: Optional[str] = None
    name_pa: str
    icon_key: str
    base_price_paise_per_kg: int
    price_floor_paise: int
    price_ceiling_paise: int
    is_hazardous: bool
    hazard_level: str
    hazard_note_en: str
    hazard_note_hi: str
    hazard_note_mr: Optional[str] = None
    hazard_note_pa: str
    safety_tip_en: str
    safety_tip_hi: str
    safety_tip_mr: Optional[str] = None
    safety_tip_pa: str
    strategic_flag: bool
    compositions: List[MaterialCompositionResponse] = []

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
    name_mr: Optional[str] = None
    name_pa: str
    current_price_paise_per_kg: int
    change_pct_14d: float
    trend_reason_en: str
    trend_reason_hi: str
    trend_reason_mr: Optional[str] = None
    trend_reason_pa: str
    sparkline: List[int]
    is_hazardous: bool

# Lot & Basket schemas
class LotItemCreate(BaseModel):
    material_id: str
    est_weight_g: int
    condition: str = "broken" # working, broken, burnt, unknown
    photo_urls: List[str] = []
    ai_suggested_material_id: Optional[str] = None
    ai_confidence: Optional[float] = None
    user_override: bool = False

class LotItemResponse(BaseModel):
    id: str
    material_id: str
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    est_weight_g: int
    actual_weight_g: Optional[int] = None
    condition: str
    est_value_min_paise: int
    est_value_max_paise: int
    final_value_paise: Optional[int] = None
    photo_urls: List[str] = []

class LotCreate(BaseModel):
    items: List[LotItemCreate]
    pickup_lat: Optional[float] = 28.6139
    pickup_lng: Optional[float] = 77.2090
    pickup_address: Optional[str] = "Main Market, Sector 12"
    client_uuid: Optional[str] = None
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
    city: Optional[str] = None

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
    items: List[EstimateItemResponse]
    total_min_paise: int
    total_max_paise: int
    total_min_inr: float
    total_max_inr: float
    total_weight_kg: float
    recoverable_minerals: List[MineralChip]
    is_hazardous: bool
    explanation: str

class LotResponse(BaseModel):
    id: str
    lot_code: str
    collector_id: str
    collector_name: Optional[str] = None
    status: str
    est_total_min_paise: int
    est_total_max_paise: int
    est_total_weight_g: int
    actual_total_weight_g: Optional[int] = None
    final_amount_paise: Optional[int] = None
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    is_hazardous: bool
    created_at: datetime
    items: List[LotItemResponse] = []
    quote_count: int = 0
    active_quote: Optional[Dict[str, Any]] = None
    transaction: Optional[Dict[str, Any]] = None

class BasketItemRequest(BaseModel):
    material_id: str
    est_weight_g: int
    condition: str = "broken"
    photo_urls: List[str] = []

class BasketResponse(BaseModel):
    items: List[LotItemResponse]
    total_items: int
    est_total_min_paise: int
    est_total_max_paise: int
    est_total_weight_g: int
    recoverable_minerals: List[MineralChip]
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
    actual_weights: Dict[str, int] # item_id -> grams
    recycler_notes: Optional[str] = None
    rejected_item_ids: Optional[List[str]] = []

class HandoverConfirmRequest(BaseModel):
    otp_or_qr: str

class CashHandoverConfirmRequest(BaseModel):
    role: str = "collector" # collector or buyer
    cash_amount_paise: Optional[int] = None
    is_partial: bool = False
    advance_paise: Optional[int] = None
    balance_paise: Optional[int] = None
    due_days: Optional[int] = 7
    lat: Optional[float] = 28.6139
    lng: Optional[float] = 77.2090

class DisputeRequest(BaseModel):
    reason: str

# Payment schemas
class PaymentInitiateRequest(BaseModel):
    transaction_id: str
    method: str = "upi" # upi, cash, wallet
    upi_id: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    transaction_id: str
    amount_paise: int
    method: str
    upi_ref: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    platform_fee_paise: int = 0

# Traceability schemas
class TraceEventResponse(BaseModel):
    id: str
    lot_id: str
    seq: int
    event_type: str
    actor_user_id: str
    actor_role: str
    payload: Dict[str, Any]
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    occurred_at: datetime
    prev_hash: str
    event_hash: str

class TraceVerifyResponse(BaseModel):
    lot_id: str
    valid: bool
    total_events: int
    broken_at_seq: Optional[int] = None
    last_hash: str

# Support schemas
class TicketCreate(BaseModel):
    category: str
    lot_id: Optional[str] = None
    transaction_id: Optional[str] = None
    message: str
    language: str = "hi"
    attachment_url: Optional[str] = None
    attachment_type: str = "none" # none, image, voice
    duration_s: Optional[int] = None

class MessageCreate(BaseModel):
    body: str
    attachment_url: Optional[str] = None
    attachment_type: str = "none"
    duration_s: Optional[int] = None

class TicketMessageResponse(BaseModel):
    id: str
    sender_type: str
    sender_name: Optional[str] = None
    body: str
    attachment_url: Optional[str] = None
    attachment_type: str
    duration_s: Optional[int] = None
    created_at: datetime

class SupportTicketResponse(BaseModel):
    id: str
    ticket_no: str
    category: str
    priority: str
    status: str
    lot_id: Optional[str] = None
    lot_code: Optional[str] = None
    language: str
    first_response_due_at: datetime
    resolution_due_at: datetime
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_sla_breached: bool = False
    messages: List[TicketMessageResponse] = []

class FAQResponse(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    audio_url: Optional[str] = None

# Notification schemas
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    body: str
    sms_preview: str
    payload: Dict[str, Any]
    read_at: Optional[datetime] = None
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
