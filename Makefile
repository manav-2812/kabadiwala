# [SIH-2026-PS-SIH26229] Iteration 93 polish
.PHONY: help dev seed seed-realistic reseed-fresh verify-seed import-real retire-synthetic test demo clean docker-up docker-down android-sync android-debug android-release android-aab android-measure android-smoke android-clean

PYTHON ?= python
NPM ?= npm

help:
	@echo "Kabadiwala Connect - SIH 2026 (PS SIH26229)"
	@echo "Available commands:"
	@echo "  make dev              - Run both backend and frontend in development mode"
	@echo "  make seed             - Seed database using deterministic generator"
	@echo "  make seed-realistic   - Generate 49 accounts, 320+ lots, 8 anomalies (Layer A)"
	@echo "  make reseed-fresh     - Re-base relative dates to today and reseed"
	@echo "  make verify-seed      - Run realism audit and statistical checks"
	@echo "  make import-real FILE=... - Import consent-gated real field data (Layer B)"
	@echo "  make retire-synthetic USERS=... - Archive synthetic personas as real ones arrive"
	@echo "  make test             - Run backend test suite"
	@echo "  make demo             - Reset database, seed demo data, and launch application"
	@echo ""
	@echo "Android commands:"
	@echo "  make android-sync     - Build web + cap sync"
	@echo "  make android-debug    - Build debug APK"
	@echo "  make android-release  - Build release APK (debug-signed if no keystore)"
	@echo "  make android-aab      - Build Android App Bundle"
	@echo "  make android-measure  - Run all measurement scripts"
	@echo "  make android-smoke    - Run smoke test on connected device/emulator"
	@echo "  make android-clean    - Clean Android build artifacts"

install:
	cd backend && $(PYTHON) -m pip install -r requirements.txt
	cd web && $(NPM) install

seed: seed-realistic

seed-realistic:
	$(PYTHON) seed/generate_realistic.py

reseed-fresh:
	$(PYTHON) seed/generate_realistic.py

verify-seed:
	$(PYTHON) scripts/realism_audit.py

import-real:
	$(PYTHON) scripts/import_real.py $(FILE)

retire-synthetic:
	$(PYTHON) scripts/retire_synthetic.py $(USERS)

test:
	cd backend && $(PYTHON) -m pytest -v tests/

dev:
	@echo "Starting backend and frontend..."
	# In Unix-like systems, run in parallel or background:
	(cd backend && $(PYTHON) -m uvicorn app.main:app --reload --port 8000) &
	(cd web && $(NPM) run dev)

demo: seed
	@echo "Database reset and seeded with full demo scenario."
	@echo "Launching backend and frontend..."
	(cd backend && $(PYTHON) -m uvicorn app.main:app --reload --port 8000) &
	(cd web && $(NPM) run dev)

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v

clean:
	rm -rf web/dist

# ─── Android Targets ───────────────────────────────────────────────

android-sync:
	@echo "Building web assets and syncing to Android..."
	cd web && $(NPM) run build && npx cap sync android

android-debug:
	@echo "Building debug APK..."
	cd web && $(NPM) run build && npx cap sync android
	cd web/android && ./gradlew assembleProdDebug

android-release:
	@echo "Building release APK..."
	cd web && $(NPM) run build && npx cap sync android
	cd web/android && ./gradlew assembleProdRelease

android-aab:
	@echo "Building Android App Bundle..."
	cd web && $(NPM) run build && npx cap sync android
	cd web/android && ./gradlew bundleProdRelease

android-measure:
	@echo "Running Android measurements..."
	bash scripts/android/measure-size.sh
	@echo "For startup/memory, connect a device and run:"
	@echo "  bash scripts/android/measure-startup.sh"
	@echo "  bash scripts/android/measure-memory.sh"

android-smoke:
	bash scripts/android/smoke.sh

android-clean:
	cd web/android && ./gradlew clean
	rm -rf artifacts/android/
