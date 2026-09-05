# ML Pipeline Makefile
# Kabadiwala Connect -- SIH 2026 (PS SIH26229)
#
# Usage (from repo root):
#   make -f ml/Makefile ml-data     # validate manifest, check image counts
#   make -f ml/Makefile ml-train    # train classifier (needs data gate)
#   make -f ml/Makefile ml-eval     # evaluate on frozen test set
#   make -f ml/Makefile ml-export   # export to ONNX INT8
#   make -f ml/Makefile ml-parity   # golden vector parity test
#   make -f ml/Makefile ml-anomaly  # fit + eval anomaly detector
#   make -f ml/Makefile ml-all      # run full pipeline

PYTHON     := python
ML_DIR     := ml
ARTIFACTS  := ml/artifacts
METRICS    := ml/artifacts/metrics
MODELS     := ml/artifacts/models

.PHONY: ml-data ml-train ml-eval ml-export ml-parity ml-anomaly ml-forecast ml-all clean-metrics

$(METRICS) $(MODELS):
	mkdir -p $@

ml-data: $(METRICS)
	@echo "=== Validating image manifest ==="
	$(PYTHON) $(ML_DIR)/classify/train.py --check-data-only
	@echo "=== Image manifest OK ==="

ml-train: $(MODELS)
	@echo "=== Training MobileNetV3-Small classifier ==="
	$(PYTHON) $(ML_DIR)/classify/train.py --config $(ML_DIR)/configs/classify.yaml
	@echo "=== Training complete. Run ml-eval next. ==="

ml-eval: $(METRICS)
	@echo "=== Evaluating classifier on frozen test set ==="
	$(PYTHON) $(ML_DIR)/eval.py
	@echo "=== Evaluation complete. See $(METRICS)/classify.json ==="

ml-export: $(MODELS)
	@echo "=== Exporting to ONNX INT8 (budget: 4 MB) ==="
	$(PYTHON) $(ML_DIR)/classify/export.py
	@echo "=== Model size check ==="
	$(PYTHON) -c "import os; sz=os.path.getsize('$(MODELS)/classify.onnx')/1e6; \
	    print(f'  classify.onnx: {sz:.2f} MB'); \
	    assert sz <= 4.0, f'FAIL: {sz:.2f} MB > 4.0 MB budget'; print('  PASS')"

ml-parity:
	@echo "=== Golden vector parity test (Python vs ONNX) ==="
	$(PYTHON) $(ML_DIR)/classify/parity_test.py
	@echo "=== Parity test complete ==="

ml-anomaly: $(METRICS)
	@echo "=== Fitting anomaly detector ==="
	$(PYTHON) $(ML_DIR)/anomaly/fit.py
	@echo "=== Evaluating anomaly detector on injected truth ==="
	$(PYTHON) $(ML_DIR)/anomaly/eval_injected.py
	@echo "=== Anomaly metrics: $(METRICS)/anomaly.json ==="

ml-forecast: $(METRICS)
	@echo "=== Fitting price forecast model ==="
	$(PYTHON) $(ML_DIR)/forecast/fit.py
	$(PYTHON) $(ML_DIR)/forecast/backtest.py
	@echo "=== Forecast metrics: $(METRICS)/forecast.json ==="

ml-all: ml-data ml-train ml-eval ml-export ml-parity ml-anomaly
	@echo "=== Full ML pipeline complete ==="

clean-metrics:
	@echo "Removing metrics (keeps models)"
	rm -f $(METRICS)/*.json
