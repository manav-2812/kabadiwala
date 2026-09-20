# Seed Data & Realism Gap Report
**Project**: Kabadiwala Connect  
**SIH 2026 Problem Statement**: PS SIH26229 (Ministry of Mines & JNARDDC)  
**Date**: September 2026  
**Auditor**: Autonomous Coding Agent (Antigravity)

---

## 1. Executive Summary

An audit was conducted on the existing database seeding scripts (`backend/app/db/seed.py`), models (`backend/app/models/all_models.py`), data generators, and frontend collector views. The existing seed data was an initial minimal bootstrap that falls significantly short of the realistic, culturally nuanced, statistically plausible 90-day dataset required for production-like demonstration, ML gating verification, and SIH 2026 evaluation.

| Dimension | Target (Prompt Spec) | Existing Baseline | Gap Status |
|---|---|---|---|
| **Collector Accounts** | **34** (exact roster, 11 MR, 10 HI, 10 PA, 3 EN) | 10 generic collectors (no native script) | **MISSING (24 collectors)** |
| **Aggregator Hubs** | **4** (fictional business names, defined radii) | 5 generic hubs | **PARTIAL (names & linkages non-compliant)** |
| **Recyclers** | **8** (6 verified, 1 pending, 1 expired) | 7 recyclers (all active/authorized) | **PARTIAL (missing expired & pending roles)** |
| **Pickup Agents** | **8** linked to specific recyclers/hubs | 7 unlinked generic agents | **PARTIAL** |
| **Admin & Support Staff** | **3** (1 admin, 2 multilingual support agents) | 1 generic admin (`9999999999`) | **MISSING (2 support agents)** |
| **Total User Accounts** | **49** accounts (all OTP `123456` enabled) | 23 accounts | **MISSING (26 accounts)** |
| **Lots Volume** | **320+** across past 90 days with Poisson timing | ~40 lots | **THIN (~12% of target)** |
| **Transactions & Receipts**| **230+** with exact ledger reconciliation | ~30 transactions | **THIN** |
| **Quotes Volume** | **700+** (1 to 4 per lot, 3-12% spread around market) | ~50 quotes | **THIN** |
| **Deliberate Anomalies** | **8** distinct cases with `seed/expected_flags.json` | 6 hardcoded anomaly flags | **PARTIAL (missing specific 8 cases)** |
| **Data Minimization** | No avatars, no real CPCB/GSTIN formats, internal plates | External dicebear avatars, realistic CPCB IDs | **NON-COMPLIANT (Honesty / Privacy)** |
| **Multilingual Script** | `display_name_local` (Devanagari & Gurmukhi) | Only Latin names in DB | **MISSING** |
| **Real-Data Importer** | Consent-gated importer tool + templates | None | **MISSING** |
| **Collector 360 Admin Page**| Detailed 360 view for every collector | None | **MISSING** |

---

## 2. Detailed Gap Analysis by Capability

### 2.1 Entity Rosters & Data Minimization (Sections 2, 3, 8)
- **Gap 1.1 (Collector Roster)**: The current database has only 10 arbitrary collectors. The prompt specifies 34 specific fictional personas with assigned operating localities (e.g. Pune Hadapsar, Nashik Satpur, Delhi Seelampur, Ludhiana Focal Point, Bengaluru Peenya), specific scrap focuses, and tier assignments (Light, Medium, Heavy).
- **Gap 1.2 (Native Script Names)**: Users only have `name` (Latin). `display_name_local` does not exist on `users` or `collectors`. In the Marathi, Hindi, and Punjabi interfaces, collectors should see their native script names (e.g. *सुनीता जाधव*, *ਗੁਰਪ੍ਰੀਤ ਸਿੰਘ*).
- **Gap 1.3 (Privacy & Avatar Policy)**: Current seed sets `avatar_url="https://api.dicebear.com/..."`. The PS rules enforce strict data minimization: zero personal avatars or people photos. UI must generate CSS/SVG initials avatars locally.
- **Gap 1.4 (Fictional ID Compliance)**: Current seed used `CPCB-REG-DL-2023-019` which resembles official registration numbering. The spec requires an explicitly fictional internal pattern: `KC-DEMO-AUTH-<STATE>-<4 digits>` with a disclaimer.
- **Gap 1.5 (Fictional Plates)**: Real-looking vehicle plates (e.g. `DL 1L AA 4012`) must be replaced with fictional internal patterns: `DEMO-MH-14-XX-####`.

### 2.2 Temporal & Statistical Behavior Model (Section 4)
- **Gap 2.1 (Relative Temporal Anchoring)**: Current lots use static timestamps or arbitrary intervals. The spec requires relative dates (`days_ago`) re-basable via `make reseed-fresh` so the app is always "live" on the day of judging.
- **Gap 2.2 (Lognormal Weight & Digit Bias)**: Existing weights are often round multiples of 1000g or 5000g. Spec strictly limits round-number bias ($\le 25\%$ ending in .0 or .5 kg) and mandates lognormal distributions tailored per material class.
- **Gap 2.3 (Status & Payment Mix)**: Cash share must be calibrated to ~82% $\pm$ 6%, with dual confirmation timestamps (1 to 20 minutes apart). Outstanding pending dues must exist for 6 to 8 collectors.
- **Gap 2.4 (Offline & Traceability)**: Offline-created lots (`offline_created=true`, `client_uuid`) must exist for designated offline-heavy personas (#9 Dattatray Kale, #11 Rahul Thorat, #31 Rajwinder Kaur). Valid SHA-256 hash chains must link every lot event, reserving exactly one lot for tamper demonstration.

### 2.3 Deliberate Anomaly Ground Truth (Section 6.2)
- **Gap 3.1 (8 Expected Anomaly Cases)**:
  1. `WEIGHT_VARIANCE` (27% actual vs estimated)
  2. `PRICE_BELOW_BAND` (0.45x market low)
  3. `UNIT_ERROR_SUSPECT` (10x price multiplier)
  4. `DUPLICATE_PHOTO` (same pHash on persona #29 Amandeep Singh across two lots)
  5. `GPS_MISMATCH` (handover location 6 km from recycler)
  6. `PAYMENT_BEFORE_WEIGH` (payment logged before digital weigh-in)
  7. `REPEATED_WEIGHT` (same exact weight on 4 lots in 7 days)
  8. `QUOTE_FAR_BELOW_MARKET` (quote at 55% of market median)
- Need `seed/expected_flags.json` mapping each anomaly lot/transaction to the expected flag code and severity.

### 2.4 Real-Data Importer & Tooling (Section 7)
- **Gap 4.1 (Importer Path)**: No automated CSV validation and ingestion pipeline exists for real field research data.
- **Gap 4.2 (Templates)**: Missing `templates/collectors.csv`, `templates/transactions.csv`, `templates/recyclers.csv`, and `templates/price_observations.csv`.
- **Gap 4.3 (Consent Gate & Anonymization)**: Importer must reject rows where `consent_confirmed` is not `TRUE`, quarantine invalid rows with error codes, anonymize sensitive attributes via HMAC-SHA256, and flag rows as `is_synthetic = false`, `source = 'field'`.

### 2.5 UI & Safety Guards (Sections 5, 8, 11)
- **Gap 5.1 (Collector 360 Admin Page)**: Admin console lacks a dedicated `Collector360.tsx` page showing detailed profile, area, join date, language, lots timeline, earnings chart, trust score, tickets, ratings, and anomaly flags.
- **Gap 5.2 (Demo Calling Safety Guard)**: `tel:` links and call buttons must be disabled in demo mode with a tooltip: *"Calling is disabled in demo mode"*.
- **Gap 5.3 (Startup Safety Check)**: Backend startup check must verify `DEMO_MODE=true` if synthetic records exist, preventing any outbound cellular SMS/calls.

---

## 3. Implementation Roadmap

1. **Phase 1: DB Schema Migration (`0004_seed_realism_fields.py`)**
   - Add `display_name_local` to `users` and `collectors`.
   - Add `seed_batch_id` (varchar 36) to `lots`, `transactions`, `payments`, `anomaly_flags`.
   - Add `is_placeholder` (boolean) to `lot_photos`.
   - Add `gps_consent` (boolean) to `collectors`.
   - Ensure `is_synthetic` is uniformly tracked across all entity models.

2. **Phase 2: Configuration & Roster Manifest**
   - Create `seed/persona_config.yaml` with assumptions, distributions, and city centers.
   - Create `seed/denylist_real_entities.txt` to guard against real company names.
   - Create `seed/expected_flags.json` documenting the 8 deliberate anomaly cases.

3. **Phase 3: Deterministic Data Generator (`seed/generate_realistic.py`)**
   - Implement deterministic seeded generation (RNG seed = 42).
   - Generate all 49 user accounts (34 collectors, 4 hubs, 8 recyclers, 8 agents, 3 staff).
   - Generate 90-day price history across 10 materials and 8 cities.
   - Generate 320+ lots with realistic lognormal weights, Poisson arrival timing, and status transitions.
   - Generate 230+ transactions with exact ledger reconciliation (`lot_items == transaction == payments + dues`).
   - Generate valid cryptographic SHA-256 hash chains for all lots.
   - Generate realistic multilingual support tickets and notification streams.

4. **Phase 4: Safety Guards & Placeholder Photos**
   - Create procedural SVG/Canvas neutral placeholder scrap images with class watermarks.
   - Implement calling disabled guard in demo mode.
   - Add startup safety check in FastAPI lifespan.

5. **Phase 5: Real-Data Import Pipeline & Templates**
   - Build `backend/app/services/importer.py` with validation, quarantine, consent gating, and anonymization.
   - Create CSV templates in `templates/`.
   - Add admin UI / CLI trigger for importing real data.

6. **Phase 6: Frontend Enhancements**
   - Create `web/src/features/admin/Collector360.tsx` and register route `/admin/collectors/:id`.
   - Add discreet "Demo data" chips and presentation mode toggle.
   - Ensure native-script rendering and initials avatars.

7. **Phase 7: Realism Audit, Playwright Tests & Documentation**
   - Create `scripts/realism_audit.py` producing `docs/seed-realism-report.md`.
   - Create `docs/seed-data-card.md`, `docs/real-data-onboarding.md`, and `docs/demo-cast.md`.
   - Run verification test suite (`pytest`, `realism_audit`, bundle measure, Playwright E2E).
