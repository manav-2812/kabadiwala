# REST & WebSocket API Specification

**Base URL**: `http://localhost:8000/api`  
**WebSocket URL**: `ws://localhost:8000/ws/tracking/{transaction_id}`

All endpoints return JSON and accept standard bearer token authentication (`Authorization: Bearer <token>`). In the prototype, all demo roles have pre-seeded sessions.

---

## Authentication & Profiles

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/request-otp` | Sends SMS OTP to mobile (demo code `123456`) |
| `POST` | `/auth/verify-otp` | Validates OTP and returns JWT access token + profile |
| `GET` | `/auth/me` | Returns current authenticated user and linked role profile |
| `PATCH` | `/auth/me` | Updates user preferences (e.g. language `hi`, `en`, `pa`) |

---

## Materials & Pricing Engine

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/materials` | Lists all 10 e-waste material categories with Hindi/Punjabi names |
| `GET` | `/prices/summary` | Today's top moving material prices per kg |
| `GET` | `/prices/{material_code}/historical` | 90-day daily price trend for charts |
| `POST` | `/prices/calculator` | Fair price estimate with statutory MSP floor and quality multipliers |

---

## Scrap Basket & Lots

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/basket` | Current collector scrap basket items and estimated total |
| `POST` | `/basket/items` | Adds item to basket with weight and condition |
| `DELETE` | `/basket/items/{id}` | Removes item from basket |
| `POST` | `/lots` | Creates lot from basket items or direct submission |
| `GET` | `/lots` | Lists lots (filter by `status`, `collector_only`) |
| `GET` | `/lots/{id}` | Complete lot details with items, composition, quotes |
| `PATCH` | `/lots/{id}/status` | Enforces state machine transition (409 on invalid transition) |
| `POST` | `/lots/{id}/confirm-handover` | Dual tare scale weigh-in confirmation & payment release |

---

## Recyclers & Bidding Quotes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/recyclers/nearby` | Geospatially ranked licensed recyclers (lat/lng, capacity) |
| `GET` | `/quotes?lot_id={id}` | Bids submitted for a specific lot |
| `POST` | `/quotes` | Recycler submits competitive bid |
| `POST` | `/quotes/{id}/accept` | Collector accepts bid, schedules logistics |

---

## Transactions & Payments

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/transactions/{id}` | Handover settlement record and weight variance |
| `POST` | `/transactions/{id}/dispute` | Flags dispute when weight variance > 10% |
| `POST` | `/payments/{id}/retry` | Retries failed UPI payment or triggers cash voucher |
| `GET` | `/wallet` | Collector wallet balance, formal premium earned, ledger entries |

---

## Cryptographic Traceability

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/lots/{id}/trace` | Full sequence of SHA-256 chained events with payloads |
| `GET` | `/lots/{id}/trace/verify` | Verifies hash chain integrity; reports broken sequence |

---

## Documents & Public Verification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/documents` | List of receipts and certificates |
| `GET` | `/documents/{number}/pdf` | Generates / downloads ReportLab statutory PDF |
| `GET` | `/verify/{doc_number}` | Public verification endpoint (strips sensitive personal info) |

---

## National Admin & Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/admin/kpis` | National formalisation tonnes, payouts, minerals |
| `GET` | `/dashboard/admin/minerals` | JNARDDC stoichiometric critical minerals recovery stats |
| `GET` | `/dashboard/admin/geo` | City-level tonnage aggregation (9 cities) |
| `GET` | `/dashboard/admin/flow` | Material flow conversion funnel |
| `GET` | `/dashboard/admin/compliance` | Recycler compliance risk and dispute log |
| `GET` | `/dashboard/admin/export?format=csv` | Statutory CPCB Form 6 manifest CSV export |

---

## Judge Demo Simulation Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/demo/reset` | Deterministically resets database to clean seed state |
| `POST` | `/demo/tamper` | Corrupts hash at seq 2 of lot for judge audit testing |
| `POST` | `/demo/repair` | Recalculates Merkle event hashes and restores validity |
| `POST` | `/demo/simulate-payment-failure` | Next payment simulates bank gateway timeout |

---

## WebSocket Tracking Channel

Connect to: `ws://localhost:8000/ws/tracking/{transaction_id}`

### Message Payload (every 3 seconds):
```json
{
  "type": "agent_location",
  "transaction_id": "tx-1",
  "lat": 28.5355,
  "lng": 77.2620,
  "eta_minutes": 12,
  "speed_kmh": 24,
  "status": "in_transit"
}
```
