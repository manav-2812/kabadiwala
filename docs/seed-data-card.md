# Dataset Card: Kabadiwala Connect Realistic Seed Data (Layer A)

**System:** Kabadiwala Connect — Informal E-Waste Regularization Platform  
**Smart India Hackathon (SIH 2026):** Problem Statement PS SIH26229  
**Proponent:** Ministry of Mines & JNARDDC (Jawaharlal Nehru Aluminium Research Development and Design Centre)  
**Dataset Version:** `1.0.0-synthetic-layer-a`  
**Generator Engine:** [`seed/generate_realistic.py`](file:///d:/PROJECTS/kabadiwala/seed/generate_realistic.py)  
**Deterministic Seed:** `42`  
**Synthetic Share:** `100.0%` (Layer A Fictional Composite Baseline)  

---

> [!CAUTION]
> ### Data Minimization & Privacy Disclaimer
> **All seeded users, companies, facilities, and records in this dataset are fictional composites.**  
> - **Zero Real Entities:** No real individuals, real kabadiwalas, actual corporate entities, CPCB licence numbers, GSTINs, or real home addresses are represented.
> - **Zero Human Photos:** No photos, avatars, or facial imagery of people are stored. Profile avatars are rendered procedurally using CSS/SVG initials avatars (`InitialsAvatar.tsx`). Scrap item photos are procedural SVGs with `"DEMO PLACEHOLDER"` watermarks.
> - **Zero PII / KYC Storage:** No Aadhaar numbers, PAN cards, voter IDs, or banking credentials are collected or stored.
> - **Safe Test Phones:** Seeded phone numbers are isolated to non-dialable test ranges (`98000100XX`, `9876543XXX`, `9999999999`).
> - **SMS Mocking Guard:** The platform asserts `DEMO_MODE=True` on startup. Outgoing SMS and telephonic calls (`tel:`) are blocked and simulated in-app.

---

## 1. Dataset Dimensions & Volume Summary

| Entity Layer | Count | Empirical Benchmark / Requirement | Status |
|---|---|---|---|
| **User Accounts** | 49 | 49 total (34 collectors, 4 hubs, 8 recyclers, 3 staff) | ✅ Exact Match |
| **Collector Profiles** | 34 | Multi-city, 3-tier informal roster (Low, Mid, High) | ✅ Exact Match |
| **Aggregator Hubs** | 4 | Regional hubs (Pune, Delhi, Ludhiana, Bengaluru) | ✅ Exact Match |
| **Authorized Recyclers** | 8 | 6 verified, 1 pending, 1 expired CPCB status | ✅ Exact Match |
| **Pickup Specialists** | 8 | Authorized logistics specialists tied to hubs | ✅ Exact Match |
| **Price History Observations** | 7,280 | 90 days × 10 materials × 8 primary cities | ✅ Verified Grid |
| **Lots Created** | 474 | Baseline requirement: ≥ 320 lots | ✅ Exceeds Target |
| **Transactions Completed** | 454 | Baseline requirement: ≥ 230 transactions | ✅ Exceeds Target |
| **Buyer Competitive Quotes** | 1,224 | Baseline requirement: ≥ 700 quotes | ✅ Exceeds Target |
| **Payments Settled** | 454 | Double-entry reconciled: 85.2% cash, 14.8% UPI | ✅ Verified |
| **Traceability Events** | 2,270 | SHA-256 tamper-evident hash chains | ✅ 100% Valid |
| **Support Tickets** | 32 | Multilingual tickets (mr, hi, pa, en) with SLA & CSAT | ✅ Verified |
| **Deliberate Anomalies** | 8 | Exact cases matching `seed/expected_flags.json` | ✅ 8/8 Present |

---

## 2. Demographic & Geographic Distribution

The 34 seeded collectors represent the demographic and linguistic realities of e-waste collection across India's primary industrial and scrap trading corridors:

| State / Cluster | Primary Cities | Language(s) | Collector Personas | Hub |
|---|---|---|---|---|
| **Maharashtra** | Pune, Nashik, Chhatrapati Sambhajinagar, Thane, Nagpur | Marathi (`mr`), Hindi (`hi`) | 11 Personas (#1 to #11) | Sahyadri Scrap Hub (Bhosari MIDC) |
| **North Central** | Delhi NCR, Ghaziabad, Lucknow, Jaipur | Hindi (`hi`) | 10 Personas (#12 to #21) | Yamuna Vihar Aggregators (Loni Industrial) |
| **Punjab & Tricity** | Ludhiana, Amritsar, Mohali, Jalandhar, Patiala, Chandigarh | Punjabi (`pa`) | 10 Personas (#22 to #31) | Malwa Collection Point (Focal Point) |
| **South & Tech** | Bengaluru, Chandigarh | English (`en`) | 3 Personas (#32 to #34) | Peenya Metals Aggregation (Peenya) |

---

## 3. Physical & Economic Fidelity Parameters

1. **Scale Weight Distribution:**
   - Log-normal continuous distribution in grams (`actual_weight_g`, `est_weight_g`).
   - Digit preference test: **0.39%** of scale weights end in round `.0` or `.5` kg (against `< 25.0%` benchmark), mimicking authentic digital scale jitter.
2. **Trading Hours & Temporal Clustering:**
   - Peak trading hours: **94.1%** of handovers occur in empirical trading windows (10:00–13:00 and 16:00–19:00).
   - Sunday volume discount: Sunday accounts for only **6.2%** of weekly handovers (benchmark `< 14.0%`), reflecting formal aggregator closures.
3. **Payment Realism:**
   - Cash dominance: **85.2%** cash settlement, accurately modeling the informal recycling economy.
   - UPI adoption: **14.8%** settled via UPI, concentrated in modern tech hub personas (#16 Rajesh Chauhan, #33 Lakshmi Narayanan).
4. **Price Volatility & Seasonal Macro Drift:**
   - Base prices set in alignment with JNARDDC circular recovery values (Cu, Au, Ag, Pd, Nd, Li).
   - Macro shock scenario: Days 30–45 simulate an international refined copper supply disruption (+18% to +24% price spike) followed by mean reversion.

---

## 4. Deliberate Anomaly Suite

The database contains exactly 8 deliberate anomaly cases mapped to specific transaction records in `anomaly_flags`:

| Case | Anomaly Code | Severity | Target Persona | Anomaly Details |
|---|---|---|---|---|
| 1 | `WEIGHT_VARIANCE` | High | Jaswant Singh (#26) | 27% difference between collector's visual estimate and recycler scale weigh-in |
| 2 | `PRICE_BELOW_BAND` | High | Mangal Kamble (#6) | Recycler offer settled at 0.45x below the market floor band rate |
| 3 | `UNIT_ERROR_SUSPECT` | High | Imran Qureshi (#17) | 10x unit confusion (rate entered as Rs 45 instead of Rs 450/kg) |
| 4 | `DUPLICATE_PHOTO` | High | Amandeep Singh (#29) | Identical lot photo SHA-256 reused across two separate lots |
| 5 | `GPS_MISMATCH` | Medium | Rahul Thorat (#11) | Handover geolocation logged 6.0 km outside authorized buyer facility bounds |
| 6 | `PAYMENT_BEFORE_WEIGH` | High | Deepak Mishra (#21) | Cash receipt timestamped 15 minutes prior to scale weigh-in |
| 7 | `REPEATED_WEIGHT` | Medium | Santosh Gaikwad (#4) | Exact repeated weight (14,250g) across 4 successive lots within 7 days |
| 8 | `QUOTE_FAR_BELOW_MARKET` | High | Mohammad Irfan Ansari (#12) | Recycler quote submitted at 55% of prevailing benchmark market floor |

---

## 5. Provenance & Audit Verification

- **Audit Command:** `make verify-seed` or `python scripts/realism_audit.py`
- **Audit Verification Report:** [`docs/seed-realism-report.md`](file:///d:/PROJECTS/kabadiwala/docs/seed-realism-report.md)
- **Public Document Verification:** First transaction receipt is fixed to `KC-RCT-2026-00001` with hash verification live at `/verify/KC-RCT-2026-00001`.
- **Reproducibility:** Running `make reseed-fresh` re-anchors relative dates to the current execution day while maintaining 100% deterministic entity relationships.
