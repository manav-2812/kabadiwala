# [SIH-2026-PS-SIH26229] Iteration 57 polish
#!/usr/bin/env bash
# measure-startup.sh — Cold Start Measurement
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Runs `adb shell am start -W` 10 times, outputs median and p90
# Requires: adb, device/emulator connected

set -euo pipefail

PKG="in.kabadiwalaconnect.collector"
ACTIVITY="$PKG/.MainActivity"
OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../artifacts/android" && pwd)"
mkdir -p "$OUTPUT_DIR"

RUNS=10
TIMES=()

echo "=== Cold Start Measurement ($RUNS runs) ==="

for i in $(seq 1 $RUNS); do
  # Force stop to ensure cold start
  adb shell am force-stop "$PKG" 2>/dev/null || true
  sleep 1

  # Clear cached process
  adb shell am kill "$PKG" 2>/dev/null || true
  sleep 0.5

  # Measure cold start
  RESULT=$(adb shell am start -W -n "$ACTIVITY" 2>&1)
  TOTAL=$(echo "$RESULT" | grep "TotalTime:" | awk '{print $2}')

  if [ -n "$TOTAL" ]; then
    TIMES+=("$TOTAL")
    echo "Run $i: ${TOTAL}ms"
  else
    echo "Run $i: FAILED"
  fi
done

# Sort and compute stats
IFS=$'\n' SORTED=($(sort -n <<<"${TIMES[*]}")); unset IFS

COUNT=${#SORTED[@]}
if [ "$COUNT" -eq 0 ]; then
  echo "No successful measurements"
  exit 1
fi

MEDIAN=${SORTED[$((COUNT / 2))]}
P90_IDX=$(( (COUNT * 9 + 9) / 10 - 1 ))
P90=${SORTED[$P90_IDX]}

JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "package": "$PKG",
  "runs": $COUNT,
  "median_ms": $MEDIAN,
  "p90_ms": $P90,
  "budget_ms": 3500,
  "within_budget": $([ "$MEDIAN" -le 3500 ] && echo "true" || echo "false"),
  "all_times_ms": [$(IFS=,; echo "${SORTED[*]}")]
}
EOF
)

echo "$JSON" | tee "$OUTPUT_DIR/startup.json"
