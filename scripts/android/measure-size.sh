# [SIH-2026-PS-SIH26229] Iteration 88 polish
#!/usr/bin/env bash
# measure-size.sh — APK/AAB Size Measurement
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Outputs JSON to stdout and artifacts/android/apk_size.json
# Requires: Android SDK (apkanalyzer or bundletool)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../../web/android"
OUTPUT_DIR="$SCRIPT_DIR/../../artifacts/android"

mkdir -p "$OUTPUT_DIR"

echo "=== APK Size Measurement ==="

# Find release APKs
UNIVERSAL_APK=$(find "$PROJECT_DIR/app/build/outputs/apk" -name "*universal*release*.apk" 2>/dev/null | head -1)
ARM64_APK=$(find "$PROJECT_DIR/app/build/outputs/apk" -name "*arm64*release*.apk" 2>/dev/null | head -1)
ARMV7_APK=$(find "$PROJECT_DIR/app/build/outputs/apk" -name "*armeabi*release*.apk" 2>/dev/null | head -1)
AAB=$(find "$PROJECT_DIR/app/build/outputs/bundle" -name "*.aab" 2>/dev/null | head -1)

get_size_mb() {
  if [ -f "$1" ]; then
    local bytes=$(stat -f%z "$1" 2>/dev/null || stat --printf="%s" "$1" 2>/dev/null || echo 0)
    echo "scale=2; $bytes / 1048576" | bc
  else
    echo "0"
  fi
}

UNIVERSAL_SIZE=$(get_size_mb "$UNIVERSAL_APK")
ARM64_SIZE=$(get_size_mb "$ARM64_APK")
ARMV7_SIZE=$(get_size_mb "$ARMV7_APK")
AAB_SIZE=$(get_size_mb "$AAB")

# Try apkanalyzer for top contributors
CONTRIBUTORS="[]"
if command -v apkanalyzer &>/dev/null && [ -f "$UNIVERSAL_APK" ]; then
  CONTRIBUTORS=$(apkanalyzer apk file-size "$UNIVERSAL_APK" 2>/dev/null | head -15 | jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo "[]")
fi

# Build JSON output
JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "universal_apk_mb": $UNIVERSAL_SIZE,
  "arm64_apk_mb": $ARM64_SIZE,
  "armv7_apk_mb": $ARMV7_SIZE,
  "aab_mb": $AAB_SIZE,
  "budget_mb": 10,
  "within_budget": $(echo "$UNIVERSAL_SIZE <= 10" | bc),
  "apk_paths": {
    "universal": "$UNIVERSAL_APK",
    "arm64": "$ARM64_APK",
    "armv7": "$ARMV7_APK",
    "aab": "$AAB"
  },
  "top_contributors": $CONTRIBUTORS
}
EOF
)

echo "$JSON" | tee "$OUTPUT_DIR/apk_size.json"

# Check budget
if (( $(echo "$UNIVERSAL_SIZE > 10" | bc -l) )); then
  echo "⚠️  OVER BUDGET: Universal APK is ${UNIVERSAL_SIZE} MB (budget: 10 MB)"
  exit 1
else
  echo "✅ Within budget: Universal APK is ${UNIVERSAL_SIZE} MB"
fi
