# Seed Data Realism & Statistical Audit Report
**Project:** Kabadiwala Connect — Informal E-Waste Regularization  
**SIH Problem Statement:** SIH26229 (Ministry of Mines & JNARDDC)  
**Audit Timestamp:** 2026-09-26 19:48:39 UTC  
**Auditor Engine:** `scripts/realism_audit.py`  
**Overall Verdict:** **PASS (10/10 CRITERIA MET)**

---

## Executive Summary
This report presents the deterministic statistical audit of the **Layer A Fictional Composite Seed Data** generated for the Kabadiwala Connect platform. All 49 user accounts, 486 lots, 464 transactions, and 1,237 buyer quotes were analyzed against empirical informal recycling benchmarks, data minimization protocols, and deliberate anomaly injection rules.

---

## Audit Criteria Scorecard

| # | Criterion | Benchmark / Rule | Result | Status |
|---|-----------|------------------|--------|--------|
| 1 | **Account Roster** | 49 total (34 collectors, 4 hubs, 8 recyclers, 3 staff) | Total Seeded Users: 49 (Req >=49), Collectors: 34 (Req 34), Hubs: 4 (Req 4), Recyclers: 8 (Req 8), Staff: 3 (Req 3) | ✅ PASS |
| 2 | **Linguistic Diversity** | Vernacular distribution (mr, hi, pa, en) | Marathi: 17, Hindi: 13, Punjabi: 15, English: 4 | ✅ PASS |
| 3 | **Data Minimization** | Zero placeholder tokens (`test`, `dummy`, `user\d+`) | Violations found: 0 | ✅ PASS |
| 4 | **Digit Preference** | Natural weighing (< 25% weights ending in .0 or .5 kg) | Round weights (.0 or .5 kg): 0.39% (3/772). Benchmark: < 25.0% | ✅ PASS |
| 5 | **Temporal Realism** | Peak trading (10-13 & 16-19 >= 50%); Sunday <= 14% | Transactions in peak hours (10-13 & 16-19): 94.1% (Benchmark >= 50%). Sunday share: 6.2% (Benchmark <= 14%) | ✅ PASS |
| 6 | **Payment Realism** | Cash dominance: 82% ± 6% share | Cash Share: 85.2% (387/454), UPI: 14.8% (67/454). Benchmark: 82% ± 6% | ✅ PASS |
| 7 | **Deliberate Anomalies** | Exactly 8 planned cases in `anomaly_flags` | Present: 8/8 cases. Missing: None | ✅ PASS |
| 8 | **Ledger Consistency** | Double-entry balance: lot value == payments + dues | Transactions Checked: 454, Inconsistencies: 0 | ✅ PASS |
| 9 | **Traceability Chain** | 100% completed lots have valid 64-char SHA-256 hash | Trace Events: 2270, Valid 64-char Hashes: 2270/2270 | ✅ PASS |
| 10 | **Support & Grievances** | >= 30 tickets, multilingual, SLA breach, CSAT scores | Tickets: 32 (Req >=30), SLA Breached: 11 (Req >=1), CSAT Rated: 21 (Req >=2) | ✅ PASS |
| 11 | **Public Document Verification** | Receipt `KC-RCT-2026-00001` present & accessible | Receipt KC-RCT-2026-00001 status: Found & Linked | ✅ PASS |

---

## Detailed Findings

### 1. Zero Placeholder & Privacy Verification
- All user accounts, operating areas, lots, and support tickets were scanned using regular expressions for placeholder tokens (`test`, `lorem`, `foo`, `bar`, `dummy`, `asdf`, `user\d+`).
- **Result:** Zero violations found. All entities use realistic composite names and locations without referencing real individuals or copyrighted entities.

### 2. Physical & Economic Fidelity
- **Scale Weigh-In Distribution:** Real scale readings exhibit jitter. Round weights (`.0` and `.5` kg) account for only **0.39%** of items, far below the 25% threshold that characterizes artificial demo seeds.
- **Cash Share:** The cash payment proportion settled at **85.2%**, reflecting the real-world informal sector preference while accurately demonstrating UPI adoption in remaining transactions.

### 3. Deliberate Anomaly Suite
All 8 deliberate anomaly cases specified in `seed/expected_flags.json` are properly seeded:
1. `WEIGHT_VARIANCE` (Jaswant Singh, Ludhiana) — 27% variance between estimate and digital scale.
2. `PRICE_BELOW_BAND` (Mangal Kamble, Pune) — Payout 0.45x below market price band floor.
3. `UNIT_ERROR_SUSPECT` (Imran Qureshi, Delhi) — 10x unit confusion (paise/rupee).
4. `DUPLICATE_PHOTO` (Amandeep Singh, Mohali) — Identical photo hash reused on separate lots.
5. `GPS_MISMATCH` (Rahul Thorat, Pune) — Handover logged 6 km from registered facility.
6. `PAYMENT_BEFORE_WEIGH` (Deepak Mishra, Ghaziabad) — Payment logged 15 mins prior to weigh-in.
7. `REPEATED_WEIGHT` (Santosh Gaikwad, Nashik) — Identical weight (14,250g) across 4 lots.
8. `QUOTE_FAR_BELOW_MARKET` (Mohammad Irfan Ansari, Delhi) — Buyer quote at 55% of floor rate.

---

## Conclusion
The Kabadiwala Connect realistic seed database (Layer A) satisfies all SIH 2026 PS SIH26229 realism, privacy, and integrity benchmarks.
