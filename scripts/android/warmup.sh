#!/usr/bin/env bash
# warmup.sh — Hosted Backend Pre-Demo Warm-Up
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Free cloud tiers (Render, Railway, Fly.io, etc.) spin down on inactivity.
# Run this script 5 minutes before jury presentation to ensure the API
# is warm and responds with sub-second latency.

set -euo pipefail

API_URL="${1:-http://localhost:8000}"
MAX_RETRIES=10
RETRY_DELAY=3

echo "=========================================================="
echo "  Kabadiwala Connect — Backend Warm-Up & Health Check"
echo "  Target URL: $API_URL"
echo "=========================================================="

ATTEMPT=1
while [ $ATTEMPT -le $MAX_RETRIES ]; do
  echo -n "[Attempt $ATTEMPT/$MAX_RETRIES] Pinging health endpoint... "
  START_TIME=$(date +%s%N 2>/dev/null || date +%s)
  
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" || echo "000")
  
  if [ "$HTTP_STATUS" = "200" ]; then
    END_TIME=$(date +%s%N 2>/dev/null || date +%s)
    echo "SUCCESS (HTTP 200)"
    echo "  Backend is awake and ready for live Android demo."
    
    # Pre-warm essential collector endpoints
    echo "  Pre-fetching materials and price cache..."
    curl -s "$API_URL/api/materials" > /dev/null || true
    curl -s "$API_URL/api/prices/summary" > /dev/null || true
    echo "  Cache warmed! Ready for demonstration."
    exit 0
  else
    echo "WAITING (HTTP $HTTP_STATUS)"
    echo "  Server might be waking up from sleep. Retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
    ATTEMPT=$((ATTEMPT + 1))
  fi
done

echo ""
echo "⚠️  WARNING: Backend did not respond with 200 within $((MAX_RETRIES * RETRY_DELAY)) seconds."
echo "If network is unavailable, use the 'demoStandalone' flavor which works 100% offline!"
exit 1
