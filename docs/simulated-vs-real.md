# Simulated vs. Production-Ready Capabilities

**Project**: Kabadiwala Connect  
**SIH 2026 Problem Statement**: SIH26229 (Ministry of Mines & JNARDDC)

To ensure zero external API dependencies, zero cost during judging, and 100% offline-runnable capability, certain external government and banking gateways are cleanly abstracted and simulated behind production-ready interfaces.

---

## Architecture Matrix

| Subsystem | Status in Prototype | How it is Implemented | Production Upgrade Path |
|---|---|---|---|
| **Cryptographic Traceability** | **100% Real & Production-Ready** | Real SHA-256 hash chaining using HMAC with secret salt, canonical JSON serialization, and sequence verification. Real tamper detection and repair. | Can anchor periodic Merkle roots to Hyperledger Fabric or Polygon public blockchain. |
| **Cash-First Physical Settlement** | **100% Real & Production-Ready** | Default payment method. Dual confirmation (collector + buyer) with coarse GPS geostamp and timestamps. Partial advance with pending dues tracking. | Direct operational protocol on-site. |
| **Computer Vision Classifier** | **Quantized & Honesty-Gated** | MobileNetV3-Small INT8 TFLite model (3.18 MB, passing <= 4.0 MB budget). Transparently labeled `demo_only: true` until verified field training data gate is reached (>= 200 verified images/class). Quality gate checks brightness & blur with spoken vernacular feedback before upload. | Retrain with active-learning reviewed images from `training_labels` via PyTorch export to ONNX/TFLite. |
| **Quantile Valuation Engine** | **Layer 1 Deterministic Rules** | Layer 1 rule engine active: P10-P90 bands with condition multipliers (working: 1.10x, broken: 1.00x, burnt: 0.70x, unknown: 0.95x) and verified trade medians. Layer 2 ML (LightGBM) gated until >= 200 completed transactions/material and holdout MAE improves by >= 10%. | Automatically promote Layer 2 model via admin evaluation gate when transaction volume targets are reached. |
| **Tabular Anomaly Detection** | **100% Real & Evaluated** | 9 deterministic rules (weight variance, price under/over-band, unit error, pHash duplicate photo, GPS jump, pre-weigh payment, repeated weight, quote below market) + robust MAD z-score. Evaluated against synthetic injected ground truth with 100% recall on tested rules and 0% false positive rate (<3% target). | Unsupervised Isolation Forest activates when transaction rows exceed `ML_MIN_ROWS_ANOMALY`. |
| **Explainable Matching** | **100% Real & Admin-Tunable** | 6-factor explainable scoring: Payout (0.30), Proximity (0.25), Rate (0.20), Pickup (0.10), Reliability (0.10), Response (0.05). Hard gates enforce verified CPCB authorization and active license validity. DB versioned with interactive admin weights slider editor. | Tune weights via feedback loop telemetry from completed handovers. |
| **Living Data Pipeline & Privacy** | **100% Real & DPDPA Compliant** | Living datasets with semantic versioning, synthetic vs real tracking, quarantine queue, and HMAC-SHA256 anonymized CSV export. | Feed directly into National Critical Mineral Registry. |
| **Lot State Machine** | **100% Real & Production-Ready** | Enforces valid transitions (`draft` $\to$ `listed` $\to$ `quoted` $\to$ ... $\to$ `completed`). Rejects invalid transitions with HTTP 409 Conflict. | Direct deploy as core state engine. |
| **Pricing Engine & MSP** | **100% Real & Production-Ready** | Formulaic pricing engine enforcing statutory Minimum Support Price floors, quality multipliers, and regional index benchmarks. | Feed live LME (London Metal Exchange) and MCX commodity price feeds. |
| **Critical Mineral Yields** | **100% Real & Production-Ready** | Stoichiometric yields for Cu, Au, Ag, Co, Li, Nd, Sn, Pd derived from JNARDDC scientific publications. | Integrate laboratory spectroscopic XRF assay upload. |
| **ReportLab PDF Generation** | **100% Real & Production-Ready** | Generates real, binary, printable PDF receipts with CPCB Form 6 watermarks, tabular line items, and QR codes. | Direct print & email automation. |
| **Offline Sync Outbox** | **100% Real & Production-Ready** | Browser IndexedDB queue catches offline actions; synchronizes in atomic batch when connection is restored. | Add background web workers and Push API. |
| **Vernacular TTS / Voice** | **100% Real (Self-Hosted Audio + TTS)** | Pre-recorded audio manifest and clip player with graceful Web Speech API fallback in Marathi (`mr`), Hindi (`hi`), Punjabi (`pa`), and English (`en`). Audio prompts guide photo quality, confidence levels, and price movements. | Integrate Bhashini AI / Google Cloud Speech for regional dialects. |
| **Live GPS Tracking** | **Hybrid Simulation** | Live WebSocket connection broadcasting GPS lat/lng coordinate updates every 3 seconds to live telemetry card. | Hook directly into logistics driver mobile app GPS sensors. |
| **SMS OTP Verification** | **Simulated for Demo** | Phone + fixed demo OTP `123456`. Immediate authentication without cellular gateway dependency. | Swap for Fast2SMS, Twilio, or MSG91 REST API. |
| **Digital UPI Withdrawal** | **Simulated & Opt-In** | Explicitly placed behind 'Enable Digital Payments' toggle (OFF by default). Simulates instant settlement reference (`KCWTH...`). | Connect Razorpay Route, Cashfree, or NPCI UPI 2.0 P2P AutoPay API. |
| **CPCB Portal Authorization** | **Realistic Local Database** | Recycler licenses (`DL/2023/042`) and Form 6 manifests stored locally in SQLite with real regulatory schemas. | Integrate National CPCB EPR Portal REST API v2 OAuth when public APIs are released. |

---

## 2. Safety Disclaimers & Operational Boundaries

> [!CAUTION]
> **Prototype Safety & Hazardous Material Notice:**  
> Kabadiwala Connect is an educational, research-oriented demonstration prototype built for the Smart India Hackathon 2026.  
> 1. **Hazardous Dismantling Warning:** Physical dismantling of cathode ray tubes (CRT), leaking lead-acid batteries, or swollen lithium-ion cells presents severe chemical and explosion hazards. All physical processing must occur strictly inside CPCB-authorized facilities equipped with acid fume scrubbers, HEPA filters, and certified personal protective equipment (PPE).  
> 2. **Regulatory Compliance:** Generating Form 6 manifests within this prototype simulates statutory filings under the E-Waste (Management) Rules, 2022. It does not replace formal electronic filing on the CPCB EPR portal.  
> 3. **Financial Escrow Disclaimer:** All wallet transactions, balances, and digital payouts in this build are simulated demonstration ledger entries; zero real Indian Rupees are held or transferred.

---

## 3. Clean Abstraction Interfaces
All services implement cleanly defined Python interfaces in `backend/app/services/`:
- `payments.py`: Contains cash and UPI payment handlers.
- `matching.py`: Contains geospatial ranking for licensed buyers.
- `trace.py`: Cryptographic hash chain verification engine.
- `price_engine.py`: Mineral yields and statutory price calculations.
- `receipt.py`: ReportLab PDF compiler.
- `importer.py`: Consent-gated real CSV importer and synthetic retirement engine.

No mock monkey-patching is used; the system runs standard business logic end-to-end.

---

## 4. Layer A (Synthetic Composite) vs Layer B (Real Field Ingestion)

| Attribute | Layer A (Fictional Composite Baseline) | Layer B (Real Field Ingestion) |
|---|---|---|
| **Origin** | Generated deterministically by `seed/generate_realistic.py` (seed 42) | Imported via `scripts/import_real.py` from verified pilot collection drives |
| **Identities** | 100% fictional composite personas, facilities, and entities | Real participants with masked PII and explicit affirmative consent |
| **Data Minimization** | Zero Aadhaar/PAN/KYC/home addresses; test phones only | Strictly no Aadhaar/PAN/KYC; coarse area centroids only (±500m jitter) |
| **Avatars & Photos** | Procedural CSS/SVG initials avatars; procedural scrap SVGs with watermarks | Clean scrap item photos only (strictly no facial imagery or human photos) |
| **Safety Guards** | `DEMO_MODE=True` blocks outgoing SMS gateways; `tel:` links disabled | Verified CPCB licensing checks; automated denylist check on entity names |
| **Flagging & Tagging** | `is_synthetic = True` on all records | `is_synthetic = False` with audit lineage tied to `dataset_versions` |
| **Audit Verification** | Validated via `scripts/realism_audit.py` (`make verify-seed`) | Validated via schema conformity and `ingest_quarantine` pipeline |
| **Retirement Protocol** | Archived via `make retire-synthetic` as authentic users arrive | Permanent audit log retained with active status |
