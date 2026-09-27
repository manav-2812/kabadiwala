#!/usr/bin/env bash
# measure-memory.sh — Memory Usage Measurement
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Captures PSS via `dumpsys meminfo` at Home and mid-Lot-Builder
# Requires: adb, device/emulator connected with app installed

set -euo pipefail

PKG="in.kabadiwalaconnect.collector"
OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../artifacts/android" && pwd)"
mkdir -p "$OUTPUT_DIR"

echo "=== Memory Measurement ==="

# Launch app and wait for Home
adb shell am start -n "$PKG/.MainActivity" 2>/dev/null
sleep 5

# Capture memory at Home
HOME_MEM=$(adb shell dumpsys meminfo "$PKG" 2>/dev/null | grep "TOTAL PSS:" | awk '{print $3}')
if [ -z "$HOME_MEM" ]; then
  HOME_MEM=$(adb shell dumpsys meminfo "$PKG" 2>/dev/null | grep "TOTAL" | head -1 | awk '{print $2}')
fi
echo "Home PSS: ${HOME_MEM:-unknown} KB"

JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "package": "$PKG",
  "home_pss_kb": ${HOME_MEM:-0},
  "home_pss_mb": $(echo "scale=1; ${HOME_MEM:-0} / 1024" | bc),
  "home_budget_mb": 250,
  "home_within_budget": $([ "${HOME_MEM:-999999}" -le 256000 ] && echo "true" || echo "false"),
  "note": "Lot Builder memory requires manual navigation to that screen"
}
EOF
)

echo "$JSON" | tee "$OUTPUT_DIR/memory.json"
