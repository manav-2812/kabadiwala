# ♻️ Kabadiwala Connect

> **Smart India Hackathon 2026** — Problem Statement **SIH26229**  
> **Nodal Ministry**: Ministry of Mines & JNARDDC (Jawaharlal Nehru Aluminium Research Development and Design Centre)  
> **Theme**: Software, Clean & Green Technology  
> **Category**: E-Waste Formalisation, Critical Mineral Independence & Informal Collector Uplift

---

## 🌟 Executive Summary

**Kabadiwala Connect** is a full-stack, vernacular, low-literacy, offline-resilient e-waste formalisation marketplace. It bridges millions of informal scrap collectors (*kabadiwalas*) directly with Central Pollution Control Board (CPCB) authorized recyclers.

By introducing **statutory Minimum Support Price (MSP) floors**, **cryptographic SHA-256 chain-of-custody audit trails**, and **JNARDDC critical minerals recovery intelligence**, Kabadiwala Connect eliminates exploitative middlemen, prevents toxic backyard acid-leaching, and creates a domestic strategic stockpile of high-tech materials (Lithium, Neodymium, Cobalt, Copper, Gold, and Silver).

---

## 🚀 Key Innovations & Features

1. **Low-Literacy Vernacular Interface (4 Languages)**:
   - Native multilingual support (**Marathi**, **Hindi**, **Punjabi**, **English**) with Web Speech API text-to-speech voice prompts and subsetted WOFF2 fonts (Devanagari & Gurmukhi) preventing missing glyphs on Android 8+.
   - High-contrast visual cards, weight steppers, and large touch targets (≥ 56px / 7:1 contrast ratio) tailored for outdoor field use.
   - **Sunlight High-Contrast Mode**: 7:1+ contrast theme with deep black borders and text designed for collectors working under direct Indian sunlight.

2. **Native Installable Android App (Capacitor 8)**:
   - Works on entry-level Android devices (minSdk 26 Android 8.0 Oreo, targetSdk 34 Android 14) with 1–2 GB RAM.
   - **Zero-Network First Launch**: Assets bundled directly into the APK (`assets/public/`).
   - **Process-Death Draft Resilience**: Survives OS memory kills when Camera activity opens on low-RAM phones; resumes seamlessly.
   - **Product Flavors**: `prod` (HTTPS only), `demoLan` (local Wi-Fi/USB), and `demoStandalone` (zero-backend, zero-internet offline mode).
   - **Hardware Back & Safe-Area Insets**: Gesture navigation support, Android 15+ edge-to-edge safe area handling, and bilingual exit confirmation modal.

3. **Facility Weighbridge Handover Desk**:
   - Mobile-first console (`/handover-desk`) for weighbridge staff on mobile Chrome (responsive from 360px).
   - Real-time scale weight discrepancy alerts, scale photo evidence, cash handover settlement, and dual OTP confirmation.

4. **Fair Pricing Engine & Statutory MSP Floor**:
   - Protects informal collectors from price dumping. Recyclers can bid upward but cannot undercut statutory floor rates mandated by the Ministry of Mines.
   - Quality multipliers for condition (`broken`, `intact`, `stripped`).

5. **Cryptographic SHA-256 Audit Chain**:
   - Every handover event (`lot_created` $\to$ `quote_accepted` $\to$ `agent_arrived` $\to$ `weighed` $\to$ `payment_released`) is cryptographically sealed into a sequential Merkle hash chain.
   - Built-in **Judge Tampering & Repair Tools**: Simulate unauthorized ledger alterations in real time and observe instantaneous audit failure detection and cryptographic repair.

6. **JNARDDC Critical Mineral Recovery Intelligence**:
   - Stoichiometric yields derived from JNARDDC scientific characterization data for printed circuit boards, lithium batteries, rare-earth magnets, and copper cables.
   - Translates collected e-waste volume directly into kilograms of strategic raw materials and national import substitution percentages.

7. **Dual Weigh-In & Anti-Fraud Dispute Arbitration**:
   - Dual tare scale verification. If scale variance exceeds 10%, a **Dispute Hold** is triggered with voice note capture and a 2-hour SLA auto-responder.

8. **Statutory Form 6 Manifest & ReportLab PDF Generation**:
   - Generates official CPCB Form 6 manifests with tamper-evident SHA-256 checksums and printable PDFs.
   - Public verification URL (`/verify/:docNumber`) enables customs, police, and CPCB inspectors to verify shipment integrity via QR code without exposing personal data.

9. **Offline-Tolerant IndexedDB Outbox**:
   - Field operations continue seamlessly even in zero-reception junkyards. Actions are queued in IndexedDB and replayed atomically upon reconnection.

10. **Live 3-Second Logistics Tracking**:
    - Real-time WebSocket connection (`/ws/tracking/{id}`) streaming GPS coordinates, ETA, and route animation on interactive Leaflet maps.

11. **Judge Demo Role Switcher**:
    - Floating persistent toolbar allowing judges to seamlessly switch personas:
      - **Collector**: Ramesh Kumar / Sunita Shinde (Marathi / Hindi / Punjabi)
      - **Recycler**: Sahyadri Urban Metals (CPCB Verified Hub)
      - **Admin**: Ministry of Mines & JNARDDC (National Oversight)
      - **Aggregator**: Pradeep Sharma (Micro-Hub Aggregator)

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy 2.0 (Async) + SQLite (`kabadiwala.db`) + ReportLab PDF Generator.
- **Frontend / PWA**: React 19 + TypeScript + Vite + Tailwind CSS v4 + Zustand + TanStack Query + React Router 7 + Framer Motion + i18next + Leaflet + Recharts + Lucide Icons + idb.
- **Mobile Native**: Capacitor 8 + Android SDK (API 34/35) + ABI Splits (`armeabi-v7a`, `arm64-v8a`) + R8 Minify + Resource Shrinking.
- **Testing**: Pytest + pytest-asyncio + Starlette TestClient (31/31 unit & integration test pass rate) + Bundle budget checks (PWA precache &le; 3 MB, initial JS gzip &le; 250 KB).

---

## ⚡ Quick Start & Running Locally

### Prerequisites
- **Python**: 3.11+ (Python 3.13 fully supported)
- **Node.js**: v18+ (Node v20+ recommended)

### One-Click Launch (Recommended)
```bash
python rundev.py
```
*Automatically checks prerequisites, seeds the SQLite database (if needed), starts FastAPI on `http://localhost:8000`, starts Vite on `http://localhost:5173`, and opens your web browser.*

**Options:**
- `python rundev.py --seed`: Force re-seed database with fresh mock lots & anomalies.
- `python rundev.py --no-browser`: Start without auto-opening the browser.

### Windows PowerShell Alternative
```powershell
.\run-demo.ps1
```

### Manual Setup (2 Terminals)

#### Terminal 1: Backend
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --port 8000 --reload
```
*Backend runs on `http://localhost:8000`. Interactive OpenAPI documentation at `http://localhost:8000/docs`.*

#### Terminal 2: Web Frontend
```bash
cd web
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## 🧪 Automated Testing

Run the test suite from the `backend/` directory:
```bash
cd backend
pytest -v
```
All **28 test suites pass in ~1.18s**:
- `test_price_engine.py`: Tests pricing formulas, MSP floor limits, and condition multipliers.
- `test_lot_state.py`: Tests state machine transitions and rejects invalid jumps with HTTP 409.
- `test_hash_chain.py`: Tests SHA-256 sequential hashing, tamper detection, and Merkle repair.
- `test_minerals.py`: Tests JNARDDC stoichiometric element calculations.
- `test_migrations.py`: Tests Alembic database migration upgrade and downgrade cycles.
- `test_ml_and_admin.py`: Tests vision classification, valuation, anomaly flags, and anonymized CSV export.
- `test_api_endpoints.py`: Tests FastAPI REST routes and public verification.

Run the frontend verification suites from the `web/` directory:
```bash
cd web
npm run test:i18n       # Verify 100% key parity across EN, HI, MR, PA
npm run measure:bundle  # Audit PWA collector chunk (<= 250KB gz) & precache (<= 3MB)
```

---

## 📂 Repository Structure

```
kabadiwala/
├── backend/
│   ├── app/
│   │   ├── core/           # Security, config, i18n exceptions, state machine
│   │   ├── db/             # SQLAlchemy async session, deterministic seed script
│   │   ├── models/         # 24+ SQLAlchemy models (Users, Lots, Trace, Minerals, etc.)
│   │   ├── schemas/        # Pydantic v2 schemas
│   │   ├── services/       # Price engine, trace, receipt PDF, minerals, payments
│   │   ├── routers/        # FastAPI endpoints (auth, lots, trace, dashboard, demo)
│   │   ├── ws/             # WebSocket tracking manager (3s live GPS broadcast)
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # 21 comprehensive automated tests
│   └── requirements.txt
├── web/
│   ├── src/
│   │   ├── app/            # Router, Providers, Root App
│   │   ├── design/         # Tokens, UI components (Voice, Weight, Map, RoleSwitcher)
│   │   ├── features/
│   │   │   ├── auth/       # Vernacular Login, Demo Switcher store
│   │   │   ├── collector/  # Home, Basket, LotBuilder, Tracking, Handover, Wallet
│   │   │   ├── recycler/   # Overview, Marketplace, Handovers, Inventory, Compliance
│   │   │   ├── admin/      # Ministry KPIs, Critical Minerals, Trace Explorer, Support
│   │   │   ├── aggregator/ # Micro-hub aggregator dashboard
│   │   │   └── verify/     # Public document verification
│   │   ├── i18n/           # Vernacular translations (en, hi, pa)
│   │   ├── lib/            # API client with offline interception, formatters, voice

*PWA offline sync & vernacular voice support active...*
