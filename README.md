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


*MSP pricing & audit chain in active development...*
