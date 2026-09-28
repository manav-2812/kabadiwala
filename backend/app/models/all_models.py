import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def gen_uuid() -> str:
    return str(uuid.uuid4())

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="collector", nullable=False)  # collector, aggregator, recycler, admin
    language: Mapped[str] = mapped_column(String(5), default="mr", nullable=False)     # mr, hi, pa, en (Marathi default per PS)
    otp_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True) # Deprecated / minimized
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    display_name_local: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    collector_profile: Mapped[Optional["Collector"]] = relationship("Collector", back_populates="user", uselist=False)
    aggregator_profile: Mapped[Optional["Aggregator"]] = relationship("Aggregator", back_populates="user", uselist=False)
    recycler_profile: Mapped[Optional["Recycler"]] = relationship("Recycler", back_populates="user", uselist=False)

class Collector(Base, TimestampMixin):
    __tablename__ = "collectors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    collector_code: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Delhi NCR", nullable=False)
    state: Mapped[str] = mapped_column(String(100), default="Delhi", nullable=False)
    operating_area_name: Mapped[str] = mapped_column(String(100), default="Hadapsar", nullable=False)
    operating_area_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)
    lat: Mapped[float] = mapped_column(Numeric(10, 6), default=28.6139, nullable=False) # Coarse operating center
    lng: Mapped[float] = mapped_column(Numeric(10, 6), default=77.2090, nullable=False) # Coarse operating center
    upi_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    kyc_status: Mapped[str] = mapped_column(String(20), default="minimized", nullable=False)  # minimized (data minimization)
    gps_consent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    wallet_balance_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_earned_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    lots_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=5.0, nullable=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=85, nullable=False)
    aggregator_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("aggregators.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="collector_profile")
    lots: Mapped[list["Lot"]] = relationship("Lot", back_populates="collector")

class Aggregator(Base, TimestampMixin):
    __tablename__ = "aggregators"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    business_name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(10, 6), default=28.6139, nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(10, 6), default=77.2090, nullable=False)
    commission_bps: Mapped[int] = mapped_column(Integer, default=500, nullable=False) # 5%
    verification_status: Mapped[str] = mapped_column(String(20), default="verified", nullable=False)
    service_radius_km: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    service_area_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="aggregator_profile")

class Recycler(Base, TimestampMixin):
    __tablename__ = "recyclers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(10, 6), default=28.6139, nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(10, 6), default=77.2090, nullable=False)
    cpcb_license_no: Mapped[str] = mapped_column(String(100), nullable=False)
    spcb_authorization_no: Mapped[str] = mapped_column(String(100), nullable=False)
    license_valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    license_valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    authorization_status: Mapped[str] = mapped_column(String(20), default="verified", nullable=False)
    accepted_material_codes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    capacity_kg_per_month: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)
    pickup_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pickup_radius_km: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    service_area_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=4.8, nullable=False)
    reliability_score: Mapped[int] = mapped_column(Integer, default=95, nullable=False)
    epr_registered: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="recycler_profile")
    agents: Mapped[list["PickupAgent"]] = relationship("PickupAgent", back_populates="recycler")
    rates: Mapped[list["RecyclerRate"]] = relationship("RecyclerRate", back_populates="recycler")

class Material(Base, TimestampMixin):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    name_mr: Mapped[str] = mapped_column(String(100), default="", nullable=False) # Marathi PS requirement
    name_pa: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_key: Mapped[str] = mapped_column(String(50), nullable=False)
    base_price_paise_per_kg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_floor_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_ceiling_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_hazardous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hazard_level: Mapped[str] = mapped_column(String(20), default="low", nullable=False)
    hazard_note_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    hazard_note_hi: Mapped[str] = mapped_column(Text, default="", nullable=False)
    hazard_note_mr: Mapped[str] = mapped_column(Text, default="", nullable=False)
    hazard_note_pa: Mapped[str] = mapped_column(Text, default="", nullable=False)
    safety_tip_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    safety_tip_hi: Mapped[str] = mapped_column(Text, default="", nullable=False)
    safety_tip_mr: Mapped[str] = mapped_column(Text, default="", nullable=False)
    safety_tip_pa: Mapped[str] = mapped_column(Text, default="", nullable=False)
    strategic_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="JNARDDC", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    compositions: Mapped[list["MaterialComposition"]] = relationship("MaterialComposition", back_populates="material")
    price_history: Mapped[list["PriceHistory"]] = relationship("PriceHistory", back_populates="material")
    subcategories: Mapped[list["MaterialSubcategory"]] = relationship("MaterialSubcategory", back_populates="material")

class MaterialSubcategory(Base, TimestampMixin):
    __tablename__ = "material_subcategories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    name_mr: Mapped[str] = mapped_column(String(100), nullable=False)
    name_pa: Mapped[str] = mapped_column(String(100), nullable=False)

    material: Mapped["Material"] = relationship("Material", back_populates="subcategories")

class MaterialComposition(Base, TimestampMixin):
    __tablename__ = "material_composition"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    element: Mapped[str] = mapped_column(String(10), nullable=False)  # cu, au, ag, pd, co, li, nd, sn, pb, al, fe
    grams_per_kg: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    source_note: Mapped[str] = mapped_column(String(255), default="JNARDDC illustrative baseline", nullable=False)

    material: Mapped["Material"] = relationship("Material", back_populates="compositions")

class PriceHistory(Base, TimestampMixin):
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    sub_category_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    price_paise_per_kg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    min_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    max_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    buying_price_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quoted_price_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    recycler_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    aggregator_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="synthetic", nullable=False) # field, platform, recycler_submitted, admin_import, synthetic
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    material: Mapped["Material"] = relationship("Material", back_populates="price_history")

    __table_args__ = (
        Index("idx_price_history_mat_date", "material_id", "date"),
    )

class RecyclerRate(Base, TimestampMixin):
    __tablename__ = "recycler_rates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    recycler_id: Mapped[str] = mapped_column(String(36), ForeignKey("recyclers.id"), nullable=False)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    sub_category_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rate_paise_per_kg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="recycler_submitted", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    recycler: Mapped["Recycler"] = relationship("Recycler", back_populates="rates")
    material: Mapped["Material"] = relationship("Material")

class Lot(Base, TimestampMixin):
    __tablename__ = "lots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    collector_id: Mapped[str] = mapped_column(String(36), ForeignKey("collectors.id"), nullable=False)
    aggregator_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("aggregators.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True, nullable=False)
    est_total_min_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    est_total_max_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    est_total_weight_g: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    actual_total_weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_amount_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    pickup_lat: Mapped[float] = mapped_column(Numeric(10, 6), default=28.6139, nullable=False)
    pickup_lng: Mapped[float] = mapped_column(Numeric(10, 6), default=77.2090, nullable=False)
    pickup_address: Mapped[str] = mapped_column(String(255), default="Local Scrap Yard, Delhi", nullable=False)
    is_hazardous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    safety_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    offline_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    client_uuid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    parent_lot_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lots.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="field", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    seed_batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    collector: Mapped["Collector"] = relationship("Collector", back_populates="lots")
    items: Mapped[list["LotItem"]] = relationship("LotItem", back_populates="lot", cascade="all, delete-orphan")
    quotes: Mapped[list["Quote"]] = relationship("Quote", back_populates="lot")
    transaction: Mapped[Optional["Transaction"]] = relationship("Transaction", back_populates="lot", uselist=False)
    trace_events: Mapped[list["TraceabilityEvent"]] = relationship("TraceabilityEvent", back_populates="lot")

    __table_args__ = (
        Index("idx_lots_status_created", "status", "created_at"),
        Index("idx_lots_collector", "collector_id"),
    )

class LotItem(Base, TimestampMixin):
    __tablename__ = "lot_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    sub_category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("material_subcategories.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), default="unknown", nullable=False) # household, shop, office, industrial, unknown
    est_weight_g: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    condition: Mapped[str] = mapped_column(String(20), default="broken", nullable=False)
    est_value_min_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    est_value_max_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    final_value_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ai_suggested_material_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    user_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="items")
    material: Mapped["Material"] = relationship("Material")
    subcategory: Mapped[Optional["MaterialSubcategory"]] = relationship("MaterialSubcategory")
    photos: Mapped[list["LotPhoto"]] = relationship("LotPhoto", back_populates="lot_item", cascade="all, delete-orphan")

class LotPhoto(Base, TimestampMixin):
    __tablename__ = "lot_photos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("lot_items.id"), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumb_url: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=150000, nullable=False)
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    phash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(4, 3), default=1.0, nullable=True)
    is_placeholder: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # AI data collection columns
    training_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    lighting: Mapped[str | None] = mapped_column(String(20), nullable=True)  # indoor, outdoor, dim

    lot_item: Mapped["LotItem"] = relationship("LotItem", back_populates="photos")

class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    recycler_id: Mapped[str] = mapped_column(String(36), ForeignKey("recyclers.id"), nullable=False)
    price_paise_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_breakdown_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    pickup_mode: Mapped[str] = mapped_column(String(20), default="pickup", nullable=False)
    pickup_eta_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="sent", nullable=False)
    note: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="quotes")
    recycler: Mapped["Recycler"] = relationship("Recycler")

    __table_args__ = (
        Index("idx_quotes_lot_status", "lot_id", "status"),
    )

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), unique=True, nullable=False)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id"), nullable=False)
    collector_id: Mapped[str] = mapped_column(String(36), ForeignKey("collectors.id"), nullable=False)
    buyer_type: Mapped[str] = mapped_column(String(20), default="recycler", nullable=False)
    buyer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    agreed_amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    final_amount_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    weight_variance_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(20), default="cash", nullable=False) # cash (default), upi, bank
    payment_status: Mapped[str] = mapped_column(String(30), default="unpaid", nullable=False) # unpaid, partial, paid, cash_pending_confirm, failed
    handover_ref: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"KC-HO-{uuid.uuid4().hex[:6].upper()}", nullable=False)
    collection_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    collection_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    handover_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    handover_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    handover_otp_hash: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    handover_qr_token: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    collector_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    buyer_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recycler_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recycler_confirmed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    cash_confirmed_by_collector: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cash_confirmed_collector_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collector_confirm_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    collector_confirm_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    cash_confirmed_by_buyer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cash_confirmed_buyer_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    buyer_confirm_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    buyer_confirm_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    advance_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    balance_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    balance_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_status: Mapped[str] = mapped_column(String(20), default="none", nullable=False) # none, pending, overdue, settled
    status: Mapped[str] = mapped_column(String(30), default="scheduled", nullable=False)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    receipt_no: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    pickup_mode: Mapped[str] = mapped_column(String(20), default="pickup", nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("pickup_agents.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="platform", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    seed_batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="transaction")
    quote: Mapped["Quote"] = relationship("Quote")
    collector: Mapped["Collector"] = relationship("Collector")
    agent: Mapped[Optional["PickupAgent"]] = relationship("PickupAgent")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="transaction")
    adjustments: Mapped[list["PaymentAdjustment"]] = relationship("PaymentAdjustment", back_populates="transaction")

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str] = mapped_column(String(20), default="cash", nullable=False) # cash (default), upi, bank_transfer
    status: Mapped[str] = mapped_column(String(20), default="initiated", nullable=False)
    gateway_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upi_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    seed_batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="payments")

class TraceabilityEvent(Base):
    __tablename__ = "traceability_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    geo_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    geo_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="trace_events")

    __table_args__ = (
        UniqueConstraint("lot_id", "seq", name="uq_lot_seq"),
        Index("idx_trace_lot_seq", "lot_id", "seq"),
    )

class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=False)
    from_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    tags: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)

class SafetyAcknowledgement(Base, TimestampMixin):
    __tablename__ = "safety_acknowledgements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    collector_id: Mapped[str] = mapped_column(String(36), ForeignKey("collectors.id"), nullable=False)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    title_hi: Mapped[str] = mapped_column(String(200), nullable=False)
    title_mr: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    title_pa: Mapped[str] = mapped_column(String(200), nullable=False)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_hi: Mapped[str] = mapped_column(Text, nullable=False)
    body_mr: Mapped[str] = mapped_column(Text, default="", nullable=False)
    body_pa: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    channel: Mapped[str] = mapped_column(String(20), default="in_app", nullable=False)

class SyncQueueLog(Base, TimestampMixin):
    __tablename__ = "sync_queue_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    client_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    result_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

class PickupSchedule(Base, TimestampMixin):
    __tablename__ = "pickup_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    slot_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slot_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="proposed", nullable=False)
    reason: Mapped[str] = mapped_column(String(255), default="", nullable=False)

class PickupAgent(Base, TimestampMixin):
    __tablename__ = "pickup_agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    recycler_id: Mapped[str] = mapped_column(String(36), ForeignKey("recyclers.id"), nullable=False)
    hub_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("aggregators.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    vehicle_no: Mapped[str] = mapped_column(String(50), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    recycler: Mapped["Recycler"] = relationship("Recycler", back_populates="agents")
    hub: Mapped[Optional["Aggregator"]] = relationship("Aggregator")

class PickupTracking(Base):
    __tablename__ = "pickup_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("pickup_agents.id"), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Numeric(5, 2), default=25.0, nullable=False)
    eta_min: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_tracking_tx_time", "transaction_id", "recorded_at"),
    )

class Cancellation(Base, TimestampMixin):
    __tablename__ = "cancellations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("lots.id"), nullable=False)
    by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    by_role: Mapped[str] = mapped_column(String(30), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)

class PaymentAdjustment(Base, TimestampMixin):
    __tablename__ = "payment_adjustments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="adjustments")

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    lot_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    ticket_no: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    lot_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="mr", nullable=False)
    assignee_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    first_response_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolution_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    csat_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    messages: Mapped[list["TicketMessage"]] = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base, TimestampMixin):
    __tablename__ = "ticket_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("support_tickets.id"), nullable=False)
    sender_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    sender_type: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attachment_type: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    duration_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="messages")

class FAQ(Base, TimestampMixin):
    __tablename__ = "faqs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    question_en: Mapped[str] = mapped_column(String(255), nullable=False)
    question_hi: Mapped[str] = mapped_column(String(255), nullable=False)
    question_mr: Mapped[str] = mapped_column(String(255), default="", nullable=False) # Marathi PS requirement
    question_pa: Mapped[str] = mapped_column(String(255), nullable=False)
    answer_en: Mapped[str] = mapped_column(Text, nullable=False)
    answer_hi: Mapped[str] = mapped_column(Text, nullable=False)
    answer_mr: Mapped[str] = mapped_column(Text, default="", nullable=False) # Marathi PS requirement
    answer_pa: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class NotificationTemplate(Base, TimestampMixin):
    __tablename__ = "notification_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    title_hi: Mapped[str] = mapped_column(String(200), nullable=False)
    title_mr: Mapped[str] = mapped_column(String(200), default="", nullable=False) # Marathi PS requirement
    title_pa: Mapped[str] = mapped_column(String(200), nullable=False)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_hi: Mapped[str] = mapped_column(Text, nullable=False)
    body_mr: Mapped[str] = mapped_column(Text, default="", nullable=False) # Marathi PS requirement
    body_pa: Mapped[str] = mapped_column(Text, nullable=False)
    sms_en: Mapped[str] = mapped_column(Text, nullable=False)
    sms_hi: Mapped[str] = mapped_column(Text, nullable=False)
    sms_mr: Mapped[str] = mapped_column(Text, default="", nullable=False) # Marathi PS requirement
    sms_pa: Mapped[str] = mapped_column(Text, nullable=False)

class PriceAlert(Base, TimestampMixin):
    __tablename__ = "price_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    collector_id: Mapped[str] = mapped_column(String(36), ForeignKey("collectors.id"), nullable=False)
    material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), default="above", nullable=False)
    threshold_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# -------------------------------------------------------------
# Living Data Pipeline & AI/ML Layer Tables (Sections 5 & 6)
# -------------------------------------------------------------

class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(String(100), default="Ministry of Mines / JNARDDC", nullable=False)

    versions: Mapped[list["DatasetVersion"]] = relationship("DatasetVersion", back_populates="dataset")

class DatasetVersion(Base, TimestampMixin):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(30), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    synthetic_share: Mapped[float] = mapped_column(Numeric(4, 3), default=1.000, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    exported_anonymized: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions")

class IngestQuarantine(Base, TimestampMixin):
    __tablename__ = "ingest_quarantine"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    dataset_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=True)
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(50), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class TrainingLabel(Base, TimestampMixin):
    __tablename__ = "training_labels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    label_material_id: Mapped[str] = mapped_column(String(36), ForeignKey("materials.id"), nullable=False)
    sub_class: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. phone_pcb, laptop_pcb
    source: Mapped[str] = mapped_column(String(50), default="field", nullable=False)  # field, user_correction, admin, public, prelabel_proposed
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    training_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # must be True to use in training export
    labeller_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

class MLModel(Base, TimestampMixin):
    __tablename__ = "ml_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    task: Mapped[str] = mapped_column(String(30), nullable=False)  # classify, valuation, anomaly, forecast
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(30), nullable=False)
    framework: Mapped[str] = mapped_column(String(50), default="onnx", nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trained_on_version: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metrics_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    demo_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    artifact_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)  # calibration temperature
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

class MLPrediction(Base, TimestampMixin):
    __tablename__ = "ml_predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    model_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ml_models.id"), nullable=True)  # nullable for rules path
    task: Mapped[str] = mapped_column(String(30), nullable=False)  # classify, valuation, anomaly, forecast, matching
    path: Mapped[str] = mapped_column(String(20), default="rules", nullable=False)  # device, server, rules
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    output_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.000, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    final_value_json: Mapped[str | None] = mapped_column(Text, nullable=True)

class AnomalyFlag(Base, TimestampMixin):
    __tablename__ = "anomaly_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=False)
    # code = structured rule code (WEIGHT_VARIANCE, PRICE_BELOW_BAND, etc.)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    # type kept for backward-compat with earlier migration
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score: Mapped[float] = mapped_column(Numeric(6, 3), default=0.0, nullable=False)
    reasons_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, reviewed_ok, confirmed
    reviewed_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    seed_batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction")

class MatchingWeight(Base, TimestampMixin):
    __tablename__ = "matching_weights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    weights_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class DriftSnapshot(Base, TimestampMixin):
    """Nightly drift monitoring snapshot (PSI, override rate, not-sure rate)."""
    __tablename__ = "drift_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    task: Mapped[str] = mapped_column(String(30), nullable=False)  # classify, valuation, anomaly, forecast
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)  # psi_class_dist, override_rate, not_sure_rate, price_psi
    value: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="ok", nullable=False)  # ok, warn, alert
