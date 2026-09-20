# SIH 2026 Presentation Cast Sheet: Kabadiwala Connect

**Problem Statement:** PS SIH26229 — Ministry of Mines & JNARDDC  
**Universal Demo OTP:** `123456` (All seeded personas)  
**System Mode:** `DEMO_MODE=True` (Layer A Fictional Composite Baseline)  

Use this cast sheet during judge walkthroughs and evaluation sessions. Each persona is engineered to demonstrate a specific platform capability, linguistic adaptation, or fraud-prevention rule.

---

## 1. Key Collector Personas

| # | Persona & Code | City & Cluster | Native Language | Role & Story Focus | Phone | Quick Demo Path |
|---|---|---|---|---|---|---|
| **#2** | **Sunita Shinde**<br>`KC-C-0002` | Pune (Hadapsar) | Marathi (`mr`) | **Women Leadership & High Trust**<br>Top female informal collector in Pune corridor. Demonstrates high trust score (94), Marathi vernacular UI, and high formalization earnings. | `9800010002` | `/` (Home)<br>`/wallet` |
| **#6** | **Mangal Kamble**<br>`KC-C-0006` | Pune (Yerawada) | Marathi (`mr`) | **Anomaly #2: Price Below Band**<br>Demonstrates automated market price protection. A recycler tried to offer a rate 0.45x below the market floor band, triggering an admin compliance flag and dispute flow. | `9800010006` | `/admin/collectors` (Filter #6)<br>`/lots` |
| **#7** | **Prakash Sawant**<br>`KC-C-0007` | Pune (Kothrud) | Marathi (`mr`) | **New User First-Time Journey**<br>Joined 6 days ago. Has exactly 1 completed lot. Used to demonstrate the onboarding wizard, guided photo scrap identification, and first digital receipt. | `9800010007` | `/build-lot`<br>`/lots` |
| **#9** | **Anand Jadhav**<br>`KC-C-0009` | Chhatrapati Sambhajinagar | Marathi (`mr`) | **Top-3 Overall Earner**<br>High-volume PCB and critical mineral aggregator. Demonstrates large-scale formal premium earnings (> ₹40,000) and multi-material lots. | `9800010009` | `/wallet`<br>`/unit-economics` |
| **#11** | **Rahul Thorat**<br>`KC-C-0011` | Pune (Pimpri) | Marathi (`mr`) | **Anomaly #5: GPS Mismatch**<br>Logged handover location 6.0 km outside authorized buyer boundary. Also features buyer-no-show resolution and buffer cancellation. | `9800010011` | `/admin/collectors` (Filter #11)<br>`/admin/compliance` |
| **#12** | **Mohammad Irfan Ansari**<br>`KC-C-0012` | Delhi NCR (Seelampur) | Hindi (`hi`) | **Anomaly #8: Quote Far Below Market**<br>High-volume Delhi corridor collector. A buyer submitted an exploitative quote at 55% of floor rate, caught by the dynamic quote fairness engine. | `9800010012` | `/prices`<br>`/admin/ai/valuation` |
| **#16** | **Rajesh Chauhan**<br>`KC-C-0016` | Jaipur (Sanganer) | Hindi (`hi`) | **100% UPI Cashless Adopter**<br>Demonstrates digital UPI instant payout integration, UPI QR verification, and instant bank credit notification without physical cash handling. | `9800010016` | `/wallet`<br>`/notifications` |
| **#17** | **Imran Qureshi**<br>`KC-C-0017` | Delhi NCR (Nehru Place) | Hindi (`hi`) | **Anomaly #3: Unit Error Suspect (10x)**<br>Demonstrates ML outlier detection. Rate was mistakenly entered as ₹45/kg instead of ₹450/kg, flagged instantly before payout execution. | `9800010017` | `/admin/collectors` (Filter #17)<br>`/admin/ai/predictions` |
| **#19** | **Anil Verma**<br>`KC-C-0019` | Lucknow (Charbagh) | Hindi (`hi`) | **Inactive Churn Re-engagement**<br>No login for 40 days. Used to demonstrate proactive SMS reactivation alerts, local price surge notifications, and churn recovery incentives. | `9800010019` | `/support`<br>`/admin/data-health` |
| **#21** | **Deepak Mishra**<br>`KC-C-0021` | Delhi NCR (Okhla) | Hindi (`hi`) | **Anomaly #6: Payment Before Weigh-In**<br>Fraud detection test case: cash payment timestamp logged 15 minutes before actual digital scale tare, caught by temporal sequencer. | `9800010021` | `/admin/compliance`<br>`/admin/trace` |
| **#26** | **Jaswant Singh**<br>`KC-C-0026` | Jalandhar (Focal Point) | Punjabi (`pa`) | **Anomaly #1: Weight Variance Dispute**<br>Demonstrates scale dispute workflow. 27% difference between collector visual estimate (50kg) and buyer scale (36.5kg), triggering arbitration. | `9800010026` | `/support`<br>`/admin/support` |
| **#29** | **Amandeep Singh**<br>`KC-C-0029` | Mohali (Phase 9) | Punjabi (`pa`) | **Anomaly #4: Duplicate Photo Hash**<br>Demonstrates perceptual/SHA-256 image anti-fraud deduplication. Attempted to claim formal recycling premium on identical lot photo. | `9800010029` | `/admin/compliance`<br>`/admin/ai/classifier` |
| **#33** | **Lakshmi Narayanan**<br>`KC-C-0033` | Bengaluru (Yeshwanthpur) | English (`en`) | **Urban Tech Hub Collector**<br>Specialized in server motherboards and Li-ion power packs. Demonstrates English vernacular layout, critical mineral extraction breakdown, and UPI payout. | `9800010033` | `/`<br>`/wallet` |

---

## 2. Recycler & Buyer Personas

| # | Facility & Company | City | CPCB Authorization | Capability & Demo Feature | Phone | Path |
|---|---|---|---|---|---|---|
| **#1** | **Sahyadri Urban Metals Pvt Ltd** | Pune (Bhosari) | `verified` | **Authorized Critical Mineral Refiner**<br>Full critical mineral recovery capabilities (Cu, Au, Ag, Li). Issues Form 6 digital manifests and instant digital scale payouts. | `9876543401` | `/recycler`<br>`/recycler/marketplace` |
| **#5** | **Ganga Plains Recyclers Pvt Ltd** | Ghaziabad | `verified` | **North India E-Waste Hub**<br>Active bidder on Delhi NCR, Ghaziabad, and Lucknow aggregation lots with competitive automated price matching. | `9876543405` | `/recycler/inventory` |
| **#7** | **Chenab Circular Recyclers LLP** | Ludhiana | `pending` | **Pending CPCB Licence Gating**<br>Demonstrates compliance gating: filtered from hazardous Li-ion / battery lots until CPCB renewal is approved. | `9876543407` | `/recycler/compliance` |
| **#8** | **Malwa Materials Recovery Pvt Ltd** | Ludhiana | `expired` | **Expired Licence Hard Blocker**<br>Licence expired 40 days ago. Hard-blocked by the matching engine from placing quotes or accepting scrap handovers. | `9876543408` | `/admin/compliance`<br>`/recycler` |

---

## 3. Administrative & Public Verification Personas

| Role | Name | Title & Jurisdiction | Capabilities | Phone | Path |
|---|---|---|---|---|---|
| **Portal Administrator** | **Dr. V. Sharma** | Chief Mineral Intelligence Director, Ministry of Mines | Access to full **Collector 360** dossier, data health audit, unit economics, matching weight sliders, and anomaly adjudication queue. | `9999999999` | `/admin`<br>`/admin/collectors` |
| **Public Verifier** | *Any Citizen / Auditor* | Public Document Inspector | Verifies Form 6 manifests, transaction certificates, and cryptographic hash chains without requiring login. | *No Login* | `/verify/KC-RCT-2026-00001` |

---

## 4. Suggested 5-Minute Evaluation Walkthrough

1. **Step 1: Informal Collector Experience (2 mins)**
   - Log in as **Sunita Shinde** (`9800010002` / `123456`).
   - Observe Marathi vernacular layout: `"नमस्कार Sunita Shinde"`.
   - Check Voice Price Board (`/prices`) speaking current market rates for Copper and PCB.
   - View `/wallet` showing cash-in-hand and formal recycling premium earned.
2. **Step 2: Recycler Acceptance & Traceability (1.5 mins)**
   - Switch role to **Sahyadri Urban Metals** (`9876543401` / `123456`).
   - View marketplace bids, digital scale weigh-in simulator, and instant payment settlement.
   - Show cryptographic SHA-256 hash generation on lot handover.
3. **Step 3: National Admin & Collector 360 (1.5 mins)**
   - Switch to **Dr. V. Sharma** (`9999999999` / `123456`).
   - Navigate to `/admin/collectors`: search for **Jaswant Singh** (`#26`) or **Mangal Kamble** (`#6`).
   - Click to open the **Collector 360 Dossier**: explore complete lot history, double-entry ledger balance, deliberate anomaly audit flags, and vernacular tickets.
   - Point to the live verification link `/verify/KC-RCT-2026-00001` proving end-to-end auditability.
