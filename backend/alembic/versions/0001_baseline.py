"""baseline schema

Revision ID: 0001_baseline
Revises: 
Create Date: 2026-09-19 14:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_baseline'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36), 
	action VARCHAR(100) NOT NULL, 
	entity VARCHAR(50) NOT NULL, 
	entity_id VARCHAR(36) NOT NULL, 
	ip VARCHAR(50), 
	user_agent VARCHAR(255), 
	meta_json TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE documents (
	id VARCHAR(36) NOT NULL, 
	type VARCHAR(30) NOT NULL, 
	number VARCHAR(50) NOT NULL, 
	lot_id VARCHAR(36), 
	transaction_id VARCHAR(36), 
	user_id VARCHAR(36), 
	storage_url VARCHAR(500) NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	generated_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE faqs (
	id VARCHAR(36) NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	question_en VARCHAR(255) NOT NULL, 
	question_hi VARCHAR(255) NOT NULL, 
	question_pa VARCHAR(255) NOT NULL, 
	answer_en TEXT NOT NULL, 
	answer_hi TEXT NOT NULL, 
	answer_pa TEXT NOT NULL, 
	audio_url VARCHAR(500), 
	sort_order INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE materials (
	id VARCHAR(36) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	name_en VARCHAR(100) NOT NULL, 
	name_hi VARCHAR(100) NOT NULL, 
	name_pa VARCHAR(100) NOT NULL, 
	icon_key VARCHAR(50) NOT NULL, 
	base_price_paise_per_kg BIGINT NOT NULL, 
	price_floor_paise BIGINT NOT NULL, 
	price_ceiling_paise BIGINT NOT NULL, 
	is_hazardous BOOLEAN NOT NULL, 
	hazard_level VARCHAR(20) NOT NULL, 
	hazard_note_en TEXT NOT NULL, 
	hazard_note_hi TEXT NOT NULL, 
	hazard_note_pa TEXT NOT NULL, 
	safety_tip_en TEXT NOT NULL, 
	safety_tip_hi TEXT NOT NULL, 
	safety_tip_pa TEXT NOT NULL, 
	strategic_flag BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE notification_templates (
	id VARCHAR(36) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	title_en VARCHAR(200) NOT NULL, 
	title_hi VARCHAR(200) NOT NULL, 
	title_pa VARCHAR(200) NOT NULL, 
	body_en TEXT NOT NULL, 
	body_hi TEXT NOT NULL, 
	body_pa TEXT NOT NULL, 
	sms_en TEXT NOT NULL, 
	sms_hi TEXT NOT NULL, 
	sms_pa TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	language VARCHAR(5) NOT NULL, 
	otp_hash VARCHAR(255), 
	otp_expires_at DATETIME, 
	is_active BOOLEAN NOT NULL, 
	avatar_url VARCHAR(255), 
	last_login_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id)
)""")
    op.execute("""CREATE TABLE aggregators (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	business_name VARCHAR(150) NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	state VARCHAR(100) NOT NULL, 
	lat NUMERIC(10, 6) NOT NULL, 
	lng NUMERIC(10, 6) NOT NULL, 
	commission_bps INTEGER NOT NULL, 
	verification_status VARCHAR(20) NOT NULL, 
	service_radius_km INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (user_id)
)""")
    op.execute("""CREATE TABLE material_composition (
	id VARCHAR(36) NOT NULL, 
	material_id VARCHAR(36) NOT NULL, 
	element VARCHAR(10) NOT NULL, 
	grams_per_kg NUMERIC(10, 4) NOT NULL, 
	source_note VARCHAR(255) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id)
)""")
    op.execute("""CREATE TABLE notifications (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	title_en VARCHAR(200) NOT NULL, 
	title_hi VARCHAR(200) NOT NULL, 
	title_pa VARCHAR(200) NOT NULL, 
	body_en TEXT NOT NULL, 
	body_hi TEXT NOT NULL, 
	body_pa TEXT NOT NULL, 
	payload_json TEXT NOT NULL, 
	read_at DATETIME, 
	channel VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")
    op.execute("""CREATE TABLE price_history (
	id VARCHAR(36) NOT NULL, 
	material_id VARCHAR(36) NOT NULL, 
	city VARCHAR(100), 
	date VARCHAR(10) NOT NULL, 
	price_paise_per_kg BIGINT NOT NULL, 
	min_paise BIGINT NOT NULL, 
	max_paise BIGINT NOT NULL, 
	source VARCHAR(50) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id)
)""")
    op.execute("""CREATE TABLE recyclers (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	company_name VARCHAR(150) NOT NULL, 
	contact_person VARCHAR(100) NOT NULL, 
	address TEXT NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	state VARCHAR(100) NOT NULL, 
	lat NUMERIC(10, 6) NOT NULL, 
	lng NUMERIC(10, 6) NOT NULL, 
	cpcb_license_no VARCHAR(100) NOT NULL, 
	spcb_authorization_no VARCHAR(100) NOT NULL, 
	license_valid_from DATETIME NOT NULL, 
	license_valid_to DATETIME NOT NULL, 
	authorization_status VARCHAR(20) NOT NULL, 
	accepted_material_codes TEXT NOT NULL, 
	capacity_kg_per_month INTEGER NOT NULL, 
	pickup_available BOOLEAN NOT NULL, 
	pickup_radius_km INTEGER NOT NULL, 
	rating_avg NUMERIC(3, 2) NOT NULL, 
	reliability_score INTEGER NOT NULL, 
	epr_registered BOOLEAN NOT NULL, 
	gstin VARCHAR(20), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (user_id)
)""")
    op.execute("""CREATE TABLE support_tickets (
	id VARCHAR(36) NOT NULL, 
	ticket_no VARCHAR(30) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	category VARCHAR(30) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	lot_id VARCHAR(36), 
	transaction_id VARCHAR(36), 
	language VARCHAR(5) NOT NULL, 
	assignee_id VARCHAR(36), 
	first_response_due_at DATETIME NOT NULL, 
	resolution_due_at DATETIME NOT NULL, 
	first_responded_at DATETIME, 
	resolved_at DATETIME, 
	csat_score INTEGER, 
	source VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(assignee_id) REFERENCES users (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")
    op.execute("""CREATE TABLE sync_queue_log (
	id VARCHAR(36) NOT NULL, 
	client_uuid VARCHAR(64) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	action VARCHAR(50) NOT NULL, 
	applied_at DATETIME NOT NULL, 
	result_json TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (client_uuid), 
	UNIQUE (client_uuid)
)""")
    op.execute("""CREATE TABLE collectors (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	state VARCHAR(100) NOT NULL, 
	operating_area_geojson TEXT, 
	lat NUMERIC(10, 6) NOT NULL, 
	lng NUMERIC(10, 6) NOT NULL, 
	upi_id VARCHAR(100), 
	aadhaar_last4 VARCHAR(4), 
	kyc_status VARCHAR(20) NOT NULL, 
	wallet_balance_paise BIGINT NOT NULL, 
	total_earned_paise BIGINT NOT NULL, 
	lots_completed INTEGER NOT NULL, 
	rating_avg NUMERIC(3, 2) NOT NULL, 
	trust_score INTEGER NOT NULL, 
	aggregator_id VARCHAR(36), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(aggregator_id) REFERENCES aggregators (id), 
	UNIQUE (user_id), 
	UNIQUE (user_id)
)""")
    op.execute("""CREATE TABLE pickup_agents (
	id VARCHAR(36) NOT NULL, 
	recycler_id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	vehicle_no VARCHAR(50) NOT NULL, 
	photo_url VARCHAR(255) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(recycler_id) REFERENCES recyclers (id)
)""")
    op.execute("""CREATE TABLE ticket_messages (
	id VARCHAR(36) NOT NULL, 
	ticket_id VARCHAR(36) NOT NULL, 
	sender_user_id VARCHAR(36), 
	sender_type VARCHAR(20) NOT NULL, 
	body TEXT NOT NULL, 
	attachment_url VARCHAR(500), 
	attachment_type VARCHAR(20) NOT NULL, 
	duration_s INTEGER, 
	is_internal BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sender_user_id) REFERENCES users (id), 
	FOREIGN KEY(ticket_id) REFERENCES support_tickets (id)
)""")
    op.execute("""CREATE TABLE lots (
	id VARCHAR(36) NOT NULL, 
	lot_code VARCHAR(30) NOT NULL, 
	collector_id VARCHAR(36) NOT NULL, 
	aggregator_id VARCHAR(36), 
	status VARCHAR(30) NOT NULL, 
	est_total_min_paise BIGINT NOT NULL, 
	est_total_max_paise BIGINT NOT NULL, 
	est_total_weight_g INTEGER NOT NULL, 
	actual_total_weight_g INTEGER, 
	final_amount_paise BIGINT, 
	pickup_lat NUMERIC(10, 6) NOT NULL, 
	pickup_lng NUMERIC(10, 6) NOT NULL, 
	pickup_address VARCHAR(255) NOT NULL, 
	is_hazardous BOOLEAN NOT NULL, 
	safety_acknowledged_at DATETIME, 
	offline_created BOOLEAN NOT NULL, 
	client_uuid VARCHAR(64), 
	parent_lot_id VARCHAR(36), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_lot_id) REFERENCES lots (id), 
	FOREIGN KEY(collector_id) REFERENCES collectors (id), 
	FOREIGN KEY(aggregator_id) REFERENCES aggregators (id), 
	UNIQUE (client_uuid), 
	UNIQUE (client_uuid)
)""")
    op.execute("""CREATE TABLE price_alerts (
	id VARCHAR(36) NOT NULL, 
	collector_id VARCHAR(36) NOT NULL, 
	material_id VARCHAR(36) NOT NULL, 
	direction VARCHAR(10) NOT NULL, 
	threshold_paise BIGINT NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	last_fired_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id), 
	FOREIGN KEY(collector_id) REFERENCES collectors (id)
)""")
    op.execute("""CREATE TABLE cancellations (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	by_user_id VARCHAR(36) NOT NULL, 
	by_role VARCHAR(30) NOT NULL, 
	reason_code VARCHAR(50) NOT NULL, 
	note TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(by_user_id) REFERENCES users (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id)
)""")
    op.execute("""CREATE TABLE lot_items (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	material_id VARCHAR(36) NOT NULL, 
	est_weight_g INTEGER NOT NULL, 
	actual_weight_g INTEGER, 
	condition VARCHAR(20) NOT NULL, 
	est_value_min_paise BIGINT NOT NULL, 
	est_value_max_paise BIGINT NOT NULL, 
	final_value_paise BIGINT, 
	ai_suggested_material_id VARCHAR(36), 
	ai_confidence NUMERIC(4, 3), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id)
)""")
    op.execute("""CREATE TABLE pickup_schedules (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	requested_by VARCHAR(36) NOT NULL, 
	slot_start DATETIME NOT NULL, 
	slot_end DATETIME NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	reason VARCHAR(255) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(requested_by) REFERENCES users (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id)
)""")
    op.execute("""CREATE TABLE quotes (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	recycler_id VARCHAR(36) NOT NULL, 
	price_paise_total BIGINT NOT NULL, 
	price_breakdown_json TEXT NOT NULL, 
	pickup_mode VARCHAR(20) NOT NULL, 
	pickup_eta_at DATETIME NOT NULL, 
	valid_until DATETIME NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	note VARCHAR(255) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id), 
	FOREIGN KEY(recycler_id) REFERENCES recyclers (id)
)""")
    op.execute("""CREATE TABLE safety_acknowledgements (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	collector_id VARCHAR(36) NOT NULL, 
	material_id VARCHAR(36) NOT NULL, 
	acknowledged_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id), 
	FOREIGN KEY(collector_id) REFERENCES collectors (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id)
)""")
    op.execute("""CREATE TABLE traceability_events (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	seq INTEGER NOT NULL, 
	event_type VARCHAR(50) NOT NULL, 
	actor_user_id VARCHAR(36) NOT NULL, 
	actor_role VARCHAR(20) NOT NULL, 
	payload_json TEXT NOT NULL, 
	geo_lat NUMERIC(10, 6), 
	geo_lng NUMERIC(10, 6), 
	occurred_at DATETIME NOT NULL, 
	prev_hash VARCHAR(64) NOT NULL, 
	event_hash VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(actor_user_id) REFERENCES users (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id), 
	CONSTRAINT uq_lot_seq UNIQUE (lot_id, seq)
)""")
    op.execute("""CREATE TABLE lot_photos (
	id VARCHAR(36) NOT NULL, 
	lot_item_id VARCHAR(36) NOT NULL, 
	storage_url VARCHAR(500) NOT NULL, 
	thumb_url VARCHAR(500) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	taken_at DATETIME NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lot_item_id) REFERENCES lot_items (id)
)""")
    op.execute("""CREATE TABLE transactions (
	id VARCHAR(36) NOT NULL, 
	lot_id VARCHAR(36) NOT NULL, 
	quote_id VARCHAR(36) NOT NULL, 
	collector_id VARCHAR(36) NOT NULL, 
	buyer_type VARCHAR(20) NOT NULL, 
	buyer_id VARCHAR(36) NOT NULL, 
	agreed_amount_paise BIGINT NOT NULL, 
	final_amount_paise BIGINT, 
	weight_variance_pct NUMERIC(5, 2), 
	handover_otp_hash VARCHAR(255) NOT NULL, 
	handover_qr_token VARCHAR(100) NOT NULL, 
	collector_confirmed_at DATETIME, 
	buyer_confirmed_at DATETIME, 
	cash_confirmed_collector_at DATETIME, 
	cash_confirmed_buyer_at DATETIME, 
	advance_paise BIGINT NOT NULL, 
	balance_paise BIGINT NOT NULL, 
	balance_due_at DATETIME, 
	status VARCHAR(30) NOT NULL, 
	receipt_url VARCHAR(500), 
	receipt_no VARCHAR(50), 
	dispute_reason TEXT, 
	pickup_mode VARCHAR(20) NOT NULL, 
	agent_id VARCHAR(36), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agent_id) REFERENCES pickup_agents (id), 
	UNIQUE (receipt_no), 
	FOREIGN KEY(quote_id) REFERENCES quotes (id), 
	FOREIGN KEY(collector_id) REFERENCES collectors (id), 
	FOREIGN KEY(lot_id) REFERENCES lots (id), 
	UNIQUE (lot_id), 
	UNIQUE (lot_id), 
	UNIQUE (receipt_no)
)""")
    op.execute("""CREATE TABLE payment_adjustments (
	id VARCHAR(36) NOT NULL, 
	transaction_id VARCHAR(36) NOT NULL, 
	type VARCHAR(30) NOT NULL, 
	amount_paise BIGINT NOT NULL, 
	reason VARCHAR(255) NOT NULL, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id)
)""")
    op.execute("""CREATE TABLE payments (
	id VARCHAR(36) NOT NULL, 
	transaction_id VARCHAR(36) NOT NULL, 
	amount_paise BIGINT NOT NULL, 
	method VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	upi_ref VARCHAR(100), 
	failure_reason VARCHAR(255), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id)
)""")
    op.execute("""CREATE TABLE pickup_tracking (
	id INTEGER NOT NULL, 
	transaction_id VARCHAR(36) NOT NULL, 
	agent_id VARCHAR(36) NOT NULL, 
	lat NUMERIC(10, 6) NOT NULL, 
	lng NUMERIC(10, 6) NOT NULL, 
	speed_kmh NUMERIC(5, 2) NOT NULL, 
	eta_min INTEGER NOT NULL, 
	recorded_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agent_id) REFERENCES pickup_agents (id), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id)
)""")
    op.execute("""CREATE TABLE ratings (
	id VARCHAR(36) NOT NULL, 
	transaction_id VARCHAR(36) NOT NULL, 
	from_user_id VARCHAR(36) NOT NULL, 
	to_user_id VARCHAR(36) NOT NULL, 
	stars INTEGER NOT NULL, 
	tags VARCHAR(255) NOT NULL, 
	comment TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	deleted_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id), 
	FOREIGN KEY(to_user_id) REFERENCES users (id), 
	FOREIGN KEY(from_user_id) REFERENCES users (id)
)""")

def downgrade() -> None:
    op.drop_table("ratings")
    op.drop_table("pickup_tracking")
    op.drop_table("payments")
    op.drop_table("payment_adjustments")
    op.drop_table("transactions")
    op.drop_table("lot_photos")
    op.drop_table("traceability_events")
    op.drop_table("safety_acknowledgements")
    op.drop_table("quotes")
    op.drop_table("pickup_schedules")
    op.drop_table("lot_items")
    op.drop_table("cancellations")
    op.drop_table("price_alerts")
    op.drop_table("lots")
    op.drop_table("ticket_messages")
    op.drop_table("pickup_agents")
    op.drop_table("collectors")
    op.drop_table("sync_queue_log")
    op.drop_table("support_tickets")
    op.drop_table("recyclers")
    op.drop_table("price_history")
    op.drop_table("notifications")
    op.drop_table("material_composition")
    op.drop_table("aggregators")
    op.drop_table("users")
    op.drop_table("notification_templates")
    op.drop_table("materials")
    op.drop_table("faqs")
    op.drop_table("documents")
    op.drop_table("audit_logs")
