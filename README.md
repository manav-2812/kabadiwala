# ♻️ Kabadiwala Connect

> **Smart India Hackathon 2026** — Problem Statement **SIH26229**  
> **Nodal Ministry**: Ministry of Mines & JNARDDC (Jawaharlal Nehru Aluminium Research Development and Design Centre)  
> **Theme**: Software, Clean & Green Technology  
> **Category**: E-Waste Formalisation, Critical Mineral Independence & Informal Collector Uplift  
> **Target Repository**: [github.com/manav-2812/kabadiwala](https://github.com/manav-2812/kabadiwala)

---

[![Backend CI](https://github.com/manav-2812/kabadiwala/actions/workflows/backend.yml/badge.svg)](https://github.com/manav-2812/kabadiwala/actions/workflows/backend.yml)
[![Web CI](https://github.com/manav-2812/kabadiwala/actions/workflows/web.yml/badge.svg)](https://github.com/manav-2812/kabadiwala/actions/workflows/web.yml)
[![Security Scan](https://github.com/manav-2812/kabadiwala/actions/workflows/security.yml/badge.svg)](https://github.com/manav-2812/kabadiwala/actions/workflows/security.yml)
[![Python 3.11 | 3.13](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Node 20+](https://img.shields.io/badge/node-20%2B-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 🔗 Live Deployments & Verification Endpoints

- **Web Application & PWA**: [Live Web Application](http://localhost:5173) (Installable PWA on Android & Chrome)
- **Interactive OpenAPI Documentation**: [Backend Swagger UI](http://localhost:8000/docs) | [ReDoc Specification](http://localhost:8000/redoc)
- **Public Verification & Chain Audit**: `/verify/KC-RCT-2026-00001` (Tamper-evident, zero PII public verification)
- **Android APK**: Bundled native APK built via Capacitor 8 (`web/android/`) with offline-first local asset fallbacks.

---

## 🌟 Executive Summary

**Kabadiwala Connect** is an enterprise-grade, vernacular, low-literacy, offline-resilient circular economy marketplace designed for **SIH26229**. It transitions India's informal e-waste collectors (*kabadiwalas*) into the formal supply chain by connecting them directly with Central Pollution Control Board (CPCB) authorized recyclers.

By enforcing **statutory Minimum Support Price (MSP) floors**, **cryptographic SHA-256 chain-of-custody audit trails**, and **JNARDDC critical minerals recovery intelligence**, Kabadiwala Connect eliminates predatory intermediaries, curtails toxic backyard acid-leaching, and secures a domestic strategic supply of high-tech critical minerals (Lithium, Neodymium, Cobalt, Copper, Gold, and Silver).

---

## 🛡️ Security & Access Control Architecture

Kabadiwala Connect implements defense-in-depth security across every endpoint:

1. **Role-Based Access Control (RBAC §1.1)**:
   - Admin routes (`/api/admin/*`) are strictly protected with `require_role("admin")`.
   - Collector tokens attempting to query administrative anomalies, matching weights, or data health receive immediate **HTTP 403 Forbidden**.
   - Public self-signup (`POST /api/auth/signup`) explicitly forbids self-assigning the `admin` role (`HTTP 422 Unprocessable Entity`).
2. **Object-Level Authorization (IDOR Protection §1.8)**:
   - Collectors and counterparties can only view, edit, or cancel lots and resources they personally own.
   - Cross-account access attempts return **HTTP 404 Not Found** to prevent resource ID enumeration.
3. **Cryptographic Secrets & Production Invariants (§1.2, §1.3)**:
   - Default developmental secret keys are blocked in production via Pydantic model validators.
   - CORS configuration rejects wildcards (`*`) when `ENVIRONMENT=production`.
4. **Brute-Force & Abuse Mitigation (§1.6)**:
   - Rate limiting on OTP generation endpoints via `slowapi` (3 requests per 10 minutes per phone/IP).
   - Passwords and OTP hashes stored using industry-standard **bcrypt** KDF (`passlib[bcrypt]`).
   - Cryptographically secure RNG (`secrets` module) for UPI transaction references and cash receipt identifiers (§1.5).

---

## 🚀 Core Features

1. **Vernacular Low-Literacy Experience (4 Languages)**:
   - Full translation parity across **English**, **Hindi (हिंदी)**, **Marathi (मराठी)**, and **Punjabi (ਪੰਜਾਬੀ)**.
   - Web Speech API text-to-speech voice guidance and subsetted local WOFF2 fonts for offline rendering.
   - **Sunlight Mode**: 7:1+ contrast theme with reinforced borders for outdoor junkyard readability.
2. **Offline-Tolerant IndexedDB Outbox**:
   - Scrap lots created in zero-connectivity environments queue into IndexedDB and replay with guaranteed idempotency upon reconnection.
3. **Statutory Minimum Support Price (MSP) Floor**:
   - Transparent price engine prevents price dumping. Recyclers can compete upwards but cannot bid below Ministry-mandated floor rates.
4. **Cryptographic SHA-256 Chain of Custody**:
   - Sequential Merkle hash chain logs every lifecycle event (`lot_created` $\to$ `quote_accepted` $\to$ `weighed` $\to$ `payment_released`).
   - Interactive tampering simulator demonstrates real-time cryptographic audit failure and mathematical repair.
5. **JNARDDC Critical Mineral Recovery Intelligence**:
   - Stoichiometric yields derived from scientific characterization data for PCBs, Li-ion batteries, rare-earth magnets, and copper cables.
6. **Dual Weigh-In & Anti-Fraud Dispute Arbitration**:
   - Dual tare scale verification. Discrepancies exceeding 10.0% trigger an automatic **Dispute Hold** with voice note capture and 2-hour SLA.
7. **Statutory Form 6 Manifest & ReportLab PDF Generation**:
   - Generates official CPCB Form 6 manifests with tamper-evident digital signatures and printable PDFs.
   - Privacy-safe public verification URL (`/verify/:docNumber`) strips all personal data per DPDP Act 2023.
8. **CPCB Recycler Authorization Gatekeeper (§2.4)**:
   - Self-registered recyclers enter the system in `pending` status. Only authorized administrators can mark a recycler `verified` after checking official CPCB/SPCB records.
   - Expired licenses (e.g. *Malwa Materials Recovery*) are automatically excluded from collector matchmaking.

---

## 🧪 Testing & Quality Gates

The codebase is backed by rigorous automated test suites across every tier:

### 1. Backend Pytest Suite
```bash
cd backend && pytest -v
```
- **70 passing automated tests (100% pass rate, 0 warnings)**.
- `test_rbac.py`: 26 test cases asserting unauthenticated 401, collector 403, and admin 200 on all administrative endpoints.
- `test_idor.py`: 8 comprehensive test suites validating object-level ownership boundaries (HTTP 404).
- `test_matching_golden.py`: Golden vector regression test verifying exclusion of unverified and expired recyclers.
- `test_hash_chain.py`: Cryptographic Merkle chain integrity, genesis block validation, and tamper detection.
- `test_lot_state.py`: Finite state machine transition invariants and illegal state jump rejections (HTTP 409).
- `test_minerals.py`: JNARDDC stoichiometric element extraction yield calculations.
- `test_price_engine.py`: Dynamic pricing formulas, condition multipliers, and MSP floor enforcement.
- `test_api_endpoints.py`: Public verification, instant estimation, and pricing summaries.

### 2. Frontend Vitest Suite
```bash
cd web && npm test
```
- **20 passing component and unit tests (100% pass rate)**.
- `matching.test.ts`: Golden file vector validation and expired recycler exclusion.
- `valuation.test.ts`: Deterministic Layer-1 pricing calculations verified against `valuation_golden.json`.
- `components.test.tsx`: Accessible interaction, boundary handling, and audio narration triggers on `WeightStepper` and `VoiceButton`.
- `dispute.test.ts`: Boundary condition validation at the exact 10.0% variance threshold (9.9% passes, 10.1% triggers dispute).
- `authStore.test.ts`: Zustand store state transitions, language switching, and secure token clearance on logout.

### 3. Internationalization Parity Gate
```bash
cd web && npm run test:i18n
```
- **100% translation key parity across all 4 languages (362 keys each in EN, HI, MR, PA)**.

### 4. End-to-End Test Automation
- **Playwright Web E2E (`web/e2e/`)**:
  - `collector_happy_path.spec.ts`: End-to-end scrap sale journey.
  - `offline_resilience.spec.ts`: Outbox queueing and sync idempotency.
  - `expired_license_exclusion.spec.ts`: Marketplace filtering of expired recyclers.
  - `public_verify_privacy.spec.ts`: Verification page PII leak audit.
  - `rbac_enforcement.spec.ts`: Browser route guard and 403 API refusal.
  - `vernacular_completeness.spec.ts`: Real-time vernacular dynamic UI update.
- **Android Maestro Flows (`web/android/maestro/`)**:
  - `sale_flow_hi.yaml` (Hindi native flow)
  - `sale_flow_mr.yaml` (Marathi native flow)
  - `sale_flow_pa.yaml` (Punjabi native flow)
  - `sale_flow_en.yaml` (English native flow)

---

## 🔍 What's Real vs Simulated

To ensure complete transparency during hackathon evaluation and compliance audits:

| Subsystem | Real Implementation | Simulated for Demo / Evaluation | Production Path |
|---|---|---|---|
| **Cryptographic Hash Chain** | **100% Real**: SHA-256 sequential Merkle chain, deterministic genesis block, recalculation & verification algorithms. | Live tamper toggle provided in the UI so evaluators can inspect failure detection. | Direct database commit. |
| **State Machine** | **100% Real**: Strict transitions (`created` $\to$ `matched` $\to$ `weighed` $\to$ `settled`) enforced at ORM and service layers. | None. | Same. |
| **Pricing & MSP Floor** | **100% Real**: Mathematical model incorporating commodity market baselines and statutory floors. | Demo price boards with seeded historical trends. | Live MCX / metal exchange API feeds. |
| **Critical Mineral Stoichiometry**| **100% Real**: Element extraction factors based on JNARDDC published characterization benchmarks. | None. | Same. |
| **OTP Delivery** | **Hybrid / Dual**: Carrier integrations for Firebase Phone Auth, Fast2SMS, Twilio, and MSG91. | In local development, generated verification codes are logged to console and prefilled for 1-click evaluation. | Set carrier API credentials in `.env`. |
| **Logistics Tracking** | **Real WebSocket**: Live bidirectional `/ws/tracking/{id}` connection streaming coordinates. | GPS movement is simulated along a realistic corridor to enable instant evaluation without driving. | Connects to `@capacitor/geolocation` on mobile devices. |
| **Weighbridge Integration** | **100% Real**: Responsive weighbridge console (`/handover-desk`), scale photo capture, and dual OTP. | Digital scale input can be simulated via quick-buttons (`+0%`, `+12%`). | Connects to serial/Bluetooth digital weighing scales via Web Serial API. |

---

## 📊 SIH26229 Criteria Compliance Matrix

| SIH26229 Requirement | Implementation Evidence | Status |
|---|---|---|
| **Formalise Informal Transactions** | Lot lifecycle state machine (`lot_state.py`), matching engine (`matching.py`). | **Implemented & Verified** |
| **Statutory MSP Floor Protection** | Price engine rejects bids below statutory minimum (`price_engine.py`). | **Implemented & Verified** |
| **CPCB-Authorised Recycler Verification**| Recycler authorization gatekeeper; pending-by-default status; hard-filters expired licenses (`matching.py`). | **Implemented & Verified** |
| **Chain-of-Custody Audit Trail** | Cryptographic SHA-256 hash chain with tamper detection (`trace.py`). | **Implemented & Verified** |
| **Critical Mineral Intelligence** | Stoichiometric recovery yield math for Li, Co, Nd, Cu, Au, Ag (`minerals.py`). | **Implemented & Verified** |
| **Vernacular Low-Literacy Usability** | 4 languages (EN, HI, MR, PA), text-to-speech, 7:1 Sunlight contrast mode (`i18n.ts`). | **Implemented & Verified** |
| **Offline-First Field Resilience** | IndexedDB outbox queue with replay idempotency (`outbox.ts`, `syncEngine.ts`). | **Implemented & Verified** |
| **Statutory Manifest Compliance** | Official CPCB Form 6 manifest generator with QR code and ReportLab PDF output (`receipt.py`). | **Implemented & Verified** |
| **DPDP Act 2023 Data Minimization** | Zero PII in public verification; collector phone and bank identifiers stripped (`PublicVerifyView.tsx`). | **Implemented & Verified** |
| **Real-Time Logistics Visibility** | WebSocket GPS telemetry with ETA and Leaflet mapping (`tracking.py`). | **Implemented & Verified** |
| **Anti-Fraud Dispute Resolution** | Dual-weigh dispute arbitration holding payment upon >10.0% variance (`HandoverView.tsx`). | **Implemented & Verified** |

---

## ⚡ Quick Start & Running Locally

### One-Command Launch (Recommended)
```bash
python rundev.py
```
*Checks environment dependencies, initializes database schema, seeds deterministic demo data, starts FastAPI on `http://localhost:8000`, starts Vite on `http://localhost:5173`, and opens the default browser.*

### Manual Startup

#### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --port 8000 --reload
```

#### Terminal 2: Web Frontend
```bash
cd web
npm install
npm run dev
```

---

## 👥 Demo Personas & Credentials

All test accounts use the developmental universal OTP: **`123456`**.

| Persona | Role | Mobile | Cluster / Region | Focus Area |
|---|---|---|---|---|
| **Ram Lal** | Collector | `9876543210` | Delhi NCR | Hindi UI, High trust score, Photo scrap builder, Cash-first handover |
| **Surinder Kumar** | Collector | `9876543211` | Chandigarh | Punjabi UI, Offline outbox sync, Battery scrap lot |
| **Santosh Gaikwad** | Collector | `9876543213` | Mumbai | Marathi UI, Weighbridge dispute simulation (>10% variance) |
| **EcoBirba Recyclers** | Recycler | `9819810001` | Delhi NCR | CPCB Verified, Form 6 manifest generator, High reliability (95) |
| **Malwa Materials Recovery** | Recycler | `9876543408` | Ludhiana | **Expired License**: Demonstrates automated exclusion from matching |
| **Ministry Administrator** | Admin | `9999999999` | National Portal | Anomaly review queue, ML model drift, Critical mineral KPI dossier |

---

## 📜 Statutory Alignment & Environmental Standards

- **E-Waste (Management) Rules, 2022**: Digital Form 6 manifest compliance, EPR credit ledger synchronization, and TSDF intake confirmation.
- **Hazardous & Other Wastes (Management and Transboundary Movement) Rules, 2016**: Anti-burning safety directives, toxic chemical warnings, and safe handling guidelines.
- **Digital Personal Data Protection (DPDP) Act, 2023**: Explicit consent gates, purpose limitation, and strict data minimization across all public inspection routes.

---

*Developed for Smart India Hackathon 2026. Dedicated to uplifting India's grassroots circular economy workers and advancing national critical mineral independence.*
