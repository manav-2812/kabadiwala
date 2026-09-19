# AI Integration Gap Report — Kabadiwala Connect (SIH 2026, PS SIH26229)
Generated: 2026-09-19

---

## How to Read This Report

Status codes:
- **EXISTS** — fully implemented per spec
- **PARTIAL** — some parts exist, others missing or non-compliant
- **MISSING** — not present in the codebase at all

---

## C1: Material Classification (Photo → Category)

| Requirement | Status | Evidence / Gap |
|---|---|---|
| MobileNetV3-Small backbone with 10-class head | PARTIAL | `ml/train.py` exists but only **simulates** training (fake epoch loop, no PyTorch). No real model training pipeline. |
| INT8 ONNX export ≤ 4 MB | PARTIAL | `ml/export.py` exists; `ml/model.tflite` (3.2 MB) exists but is TFLite not ONNX; no ONNX file present |
| Temperature scaling / calibration | MISSING | No `ml/classify/calibrate.py` |
| Parity test (PyTorch vs ONNX; browser WASM) | MISSING | No `ml/classify/parity_test.py`, no golden JSONs |
| On-device worker (`classifier.worker.ts`) | MISSING | `web/src/features/collector/` has no AI worker files |
| Server endpoint `POST /ml/classify` | PARTIAL | `backend/app/routers/ml.py#L124` exists but returns **random/hardcoded** mock values, not real model inference |
| Confidence threshold 0.60 / "Not sure" fallback | PARTIAL | Threshold logic exists in mock (L152) but is never real |
| `ai_suggested_material_id`, `ai_confidence`, `user_override` stored on LotItem | MISSING | `LotItem` model has no such columns |
| Demo model tag in UI | MISSING | No `demo_only` flag surfaced to the collector UI |
| Data Collection Mode (hidden long-press) | MISSING | Not present in collector app |
| Admin Label Review Queue | MISSING | No admin UI for reviewing/verifying training photos |
| Manifest tooling (`make ml-data`) | MISSING | No `ml/data/manifests/images_manifest.csv`, no manifest validator |
| Promotion gate / rollback endpoints | MISSING | No `POST /admin/ml/models/{id}/activate` or rollback |
| `metrics/classify.json` with confusion matrix, ECE, coverage | PARTIAL | `ml/metrics.json` has fake hardcoded numbers, not real eval output |
| Latency measured on throttled profile | PARTIAL | `ml/metrics.json` has fake latency values |
| Safety card shown automatically for BATTERY_LI, CRT, LCD | PARTIAL | `SafetyHub.tsx` exists; auto-trigger in Lot Builder missing |

---

## C2: Approximate Valuation

| Requirement | Status | Evidence / Gap |
|---|---|---|
| Layer 1 rules (client + server, identical formula) | PARTIAL | Server rules in `ml.py#L190`; no TS twin in `web/src/` |
| Shared golden vectors (Python vs TS) | MISSING | No `ml/golden/valuation_golden.json` |
| Layer 2 quantile GBM (gated at ≥ 200 real rows) | PARTIAL | `ml.py` has a single regressor-style endpoint but no gate check, no real GBM |
| `basis` object with layer, n_recent_sales, scope | PARTIAL | `basis_line` string exists but uses `random.randint()` for sample count |
| `POST /ml/valuate` with items array + lat/lng | PARTIAL | Endpoint exists but takes single item, not array |
| Price-of-the-day clamp [0.5x, 2x] | MISSING | Not implemented |
| `metrics/valuation.json` with MAE vs baseline | MISSING | No valuation metrics file |

---

## C3: Recycler Matching & Ranking

| Requirement | Status | Evidence / Gap |
|---|---|---|
| Hard filters (verified, valid licence, area) | EXISTS | `backend/app/services/matching.py#L33-37` |
| Weighted score formula w1–w6 | PARTIAL | `matching.py#L77-82` has 4 weights (payout 0.50, proximity 0.25, rating 0.15, pickup 0.10), not the 6-weight spec |
| Reason codes (NEAREST, HIGHEST_PAYOUT, etc.) | PARTIAL | One reason per recycler (L88); only 3 possible values |
| Weights admin-editable and versioned | PARTIAL | `MatchingWeight` table exists in DB; no admin UI to edit weights or apply them dynamically to the matching formula |
| `weights_version` in API response | MISSING | Not in response |
| Offline TS twin with shared golden tests | MISSING | No `web/src/features/collector/matching.ts` |
| Impression logging to `ml_predictions` | MISSING | `rank_recyclers_for_lot()` never writes to DB |

---

## C4: Abnormal Transaction Detection

| Requirement | Status | Evidence / Gap |
|---|---|---|
| `anomaly_flags` DB table | EXISTS | `all_models.py#L679` |
| Rules: WEIGHT_VARIANCE, PRICE_BELOW_BAND, PRICE_ABOVE_BAND | PARTIAL | `admin.py` lists anomalies from DB; seeded entries exist but the rule engine that *creates* flags during weigh-in is missing from `transactions.py` |
| Rules: UNIT_ERROR_SUSPECT, DUPLICATE_PHOTO, GPS_MISMATCH, PAYMENT_BEFORE_WEIGH, REPEATED_WEIGHT, QUOTE_FAR_BELOW_MARKET | MISSING | Not implemented in any service |
| Statistical z-score (MAD-based) | MISSING | |
| Isolation Forest (gated ≥ 300 rows) | MISSING | |
| Injected-truth eval with recall/precision per type | MISSING | No `ml/anomaly/eval_injected.py` |
| Seeded anomalous transactions for demo | PARTIAL | Some anomaly records seeded in migration, but rule engine doesn't auto-create them on weigh-in |
| Review workflow (open → reviewed_ok / confirmed) | EXISTS | `admin.py#L43` list and PATCH |
| Auto support-ticket on high severity | MISSING | |
| `code` field on AnomalyFlag (e.g. "WEIGHT_VARIANCE") | PARTIAL | `type` column exists, different naming from spec |
| pHash duplicate detection server-side | MISSING | `LotPhoto.phash` column exists; comparison logic missing |
| `phash.ts` client-side dHash | MISSING | No file in web/src |
| Quality gate (`quality.ts`) blur/brightness check | MISSING | |

---

## C5: Price Trends & Forecast

| Requirement | Status | Evidence / Gap |
|---|---|---|
| 7/14/30-day moving averages | PARTIAL | `prices.py` computes 14-day sparkline; no explicit MA7/MA30 or slope computation |
| Slope %/week and arrow (Rising/Falling/Steady) | PARTIAL | `pct_change_14d` computed; no weekly slope rule, no arrow enum |
| `GET /prices/trends?material=&city=` endpoint | MISSING | Endpoint doesn't exist; only `/prices/summary` and `/prices` |
| Forecast (Holt-Winters / linear, gated) | MISSING | |
| `is_demo` tag on synthetic-derived forecasts | MISSING | |
| Spoken sentences composed from audio clips | MISSING | |
| Inline SVG sparklines in collector app (no chart lib) | PARTIAL | `PricesView.tsx` exists; uses data from backend |

---

## C6: Duplicate / Low-Quality Photo Detection

| Requirement | Status | Evidence / Gap |
|---|---|---|
| `phash` column on `lot_photos` | EXISTS | `all_models.py#L266` |
| `phash.ts` dHash (9×8 grayscale) in browser | MISSING | |
| `quality.ts` blur/brightness gate | MISSING | |
| Server-side pHash Hamming distance comparison | MISSING | |
| Spoken quality feedback in 4 languages | MISSING | |
| `training_consent` column on photos | MISSING | `LotPhoto` has no `training_consent`, `session_id`, or `lighting` columns |

---

## C7: Feedback Loop & Registry

| Requirement | Status | Evidence / Gap |
|---|---|---|
| `ml_models` table | EXISTS | `all_models.py#L651` — partial fields (missing `artifact_url`, `sha256`, `temperature`, `created_by`) |
| `ml_predictions` table | EXISTS | `all_models.py#L665` — partial fields (missing `task` ENUM, `path` ENUM, `input_hash`, `latency_ms`) |
| `training_labels` table | EXISTS | `all_models.py#L641` — partial fields (missing `sub_class`, `training_consent`, `prelabel` source) |
| `anomaly_flags` table | EXISTS | `all_models.py#L679` — missing `code` field (has `type`), missing `reasons_json` with i18n |
| `matching_weights` table | EXISTS | `all_models.py#L694` |
| `dataset_versions` table | EXISTS | `all_models.py#L617` |
| `ingest_quarantine` table | EXISTS | `all_models.py#L632` |
| `drift_snapshots` table | MISSING | Not in `all_models.py` |
| Prediction logging on every ML call | MISSING | `ml.py` classify/valuate endpoints don't write to `ml_predictions` |
| Override writes `user_override=true` to DB | MISSING | |
| Retrain candidate (no auto-activate) | MISSING | No `POST /admin/ml/retrain` |
| Promotion gate (beats active model on frozen test) | MISSING | |
| Rollback endpoint | MISSING | No `POST /admin/ml/models/{id}/rollback` |
| Drift nightly job (PSI, override rate, not-sure rate) | MISSING | |
| Retrain suggestion banner (labels grew ≥20%) | MISSING | |

---

## C8: Spoken Output (Pre-recorded Clips)

| Requirement | Status | Evidence / Gap |
|---|---|---|
| `audio.ts` clip composer | MISSING | No file |
| `scripts/generate-audio-manifest.ts` | MISSING | No file |
| `docs/audio-recording-guide.md` | EXISTS | `docs/audio-recording-guide.md` (5.7 KB) |
| Silent/beep placeholders per clip per language | MISSING | No `/public/audio/` directory |
| Web Speech TTS fallback | MISSING | |

---

## Database / Migration Gaps

| Gap | Details |
|---|---|
| `drift_snapshots` table | Missing from models and migrations |
| `LotPhoto` missing columns | `training_consent`, `session_id`, `lighting` columns absent |
| `LotItem` missing columns | `ai_suggested_material_id`, `ai_confidence`, `user_override` absent |
| `MLModel` missing columns | `artifact_url`, `sha256`, `temperature`, `created_by` absent |
| `MLPrediction` missing columns | `task` ENUM, `path` ENUM device/server/rules absent; `model_id` is non-nullable (should be nullable for rules path) |
| `TrainingLabel` missing columns | `sub_class`, `training_consent`, `prelabel_proposed` source ENUM value |
| `AnomalyFlag` column naming | `type` should be `code` per spec |

---

## Config Flags (Section 2)

| Flag | Status |
|---|---|
| `ML_ENABLED` | MISSING from `config.py` |
| `ML_CLASSIFY_MODE` | MISSING |
| `ML_CLASSIFY_MIN_CONF` | MISSING |
| `ML_MIN_ROWS_PER_MATERIAL` | MISSING |
| `ML_MIN_ROWS_ANOMALY` | MISSING |
| `ML_FORECAST_MIN_DAYS` | MISSING |
| `ML_PRELABEL_PROVIDER` | MISSING |
| `ML_LOG_PREDICTIONS` | MISSING |

---

## Admin AI Console Pages (Section 12)

| Page | Status |
|---|---|
| 1. AI Overview (active models, gate status) | MISSING |
| 2. Classifier (confusion matrix, per-class table, retrain) | MISSING |
| 3. Label Review Queue | MISSING |
| 4. Predictions Log | MISSING |
| 5. Valuation metrics | MISSING |
| 6. Matching weights editor | MISSING |
| 7. Anomalies queue (already exists in AdminCompliance.tsx) | PARTIAL |
| 8. Data Health | EXISTS — `DataHealthPanel.tsx` (16 KB) |
| 9. Drift charts | MISSING |

---

## Collector App AI Touchpoints (Section 13)

| Touchpoint | Status |
|---|---|
| Photo quality gate → classifier suggestion → confirm/override | MISSING in UI |
| Basis line shown in estimate step | PARTIAL (LotBuilder has estimate step, no basis line) |
| Ranked buyer list with reason icons (offline twin) | PARTIAL (FindBuyers.tsx exists; no reason icons or offline twin) |
| Prices: trend arrow, spoken line, sparkline | PARTIAL (PricesView exists; no arrow or spoken) |
| Safety card auto-show for BATTERY_LI / CRT / LCD | MISSING |
| Handover: friendly message on anomaly check | MISSING |

---

## ML/ Folder Structure Gaps

| Needed | Status |
|---|---|
| `ml/configs/classify.yaml` | MISSING |
| `ml/configs/valuation.yaml` | MISSING |
| `ml/configs/anomaly.yaml` | MISSING |
| `ml/configs/forecast.yaml` | MISSING |
| `ml/classify/` (train, eval, export, calibrate, parity_test) | MISSING (only flat `ml/train.py`, `ml/eval.py`, `ml/export.py`) |
| `ml/valuation/` (train, eval, backtest) | MISSING |
| `ml/anomaly/` (fit, eval_injected) | MISSING |
| `ml/forecast/` (fit, backtest) | MISSING |
| `ml/data/manifests/images_manifest.csv` | MISSING |
| `ml/data/synthetic/price_generator.py` | MISSING |
| `ml/golden/valuation_golden.json` | MISSING |
| `ml/golden/classify_golden.json` | MISSING |
| `ml/artifacts/metrics/*.json` | PARTIAL (only `ml/metrics.json` with fake values) |
| `ml/Makefile` (ml-data, ml-train, ml-eval, ml-export, ml-parity) | MISSING |
| `ml/requirements.txt` (pinned) | MISSING |
| `MODEL_CARDS/classify.md` | MISSING |
| `ml/DATASET_CARD.md` | EXISTS (3.5 KB) |

---

## Honesty / Anti-pattern Checks

| Check | Status |
|---|---|
| `random.randint()` used for `n_recent_sales` in valuate response | **VIOLATION** — `ml.py#L238` |
| Hardcoded fake accuracy in `ml/eval.py` (not from real model) | **VIOLATION** — `eval.py#L34-45` |
| Fake epoch loop in `ml/train.py` (simulated, no PyTorch) | **VIOLATION** — `train.py#L47-63` |
| Hardcoded latency in `ml/metrics.json` | **VIOLATION** |
| `demo_only = true` gate respected in UI | MISSING |
| No "AI-powered" badges found | PASS |
| No sparkle/brain icons found | PASS |

---

## Summary Counts

| Status | Count |
|---|---|
| EXISTS (fully compliant) | 8 |
| PARTIAL | 26 |
| MISSING | 47 |
| HONESTY VIOLATIONS (fix first) | 4 |

---

## Execution Priority (per Section 18)

Given SIH demo constraints, priority order:

1. **Fix honesty violations** — remove fake numbers from `eval.py`, `train.py`, `ml.py`
2. **Config flags** — add all 8 ML flags to `config.py` and `.env`
3. **DB migration** — add missing columns + `drift_snapshots` table
4. **Shared golden vectors** — valuation + matching (Python + TS parity)
5. **C2 rules + basis line** — Layer 1 real rules in Python + TS twin
6. **C3 matching** — 6-weight formula, reasons, weights from DB, impression logging
7. **C4 anomaly rules** — rule engine wired into `transactions.py` weigh-in
8. **C5 trend arrows + `/prices/trends` endpoint**
9. **C6 quality gate + pHash** — TS worker + server duplicate check
10. **C1 real training pipeline** — proper PyTorch/ONNX pipeline (or explicit `demo_only=true` with honest placeholder)
11. **C7 feedback loop** — prediction logging, retrain candidate flow
12. **Admin AI Console pages** — Overview, Classifier, Labels, Weights editor, Drift
13. **C8 audio** — manifest + placeholder clips + composer
