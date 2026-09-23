# [SIH-2026-PS-SIH26229] Iteration 26 polish
#!/usr/bin/env bash
# smoke.sh — Android Smoke Test
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Install, launch, grant permissions, screenshot, check logcat
# Requires: adb, device/emulator connected

set -euo pipefail

PKG="in.kabadiwalaconnect.collector"
ACTIVITY="$PKG/.MainActivity"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../../artifacts/android"
SCREENSHOT_DIR="$SCRIPT_DIR/../../docs/android/screenshots"

mkdir -p "$OUTPUT_DIR" "$SCREENSHOT_DIR"

APK="${1:-}"
if [ -z "$APK" ]; then
  APK=$(find "$SCRIPT_DIR/../../web/android/app/build/outputs/apk" -name "*debug*.apk" | head -1)
fi

echo "=== Android Smoke Test ==="

# 1. Install
if [ -n "$APK" ] && [ -f "$APK" ]; then
  echo "Installing: $APK"
  adb install -r "$APK"
else
  echo "No APK specified or found. Assuming already installed."
fi

# 2. Grant permissions
echo "Granting permissions..."
adb shell pm grant "$PKG" android.permission.CAMERA 2>/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION 2>/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION 2>/dev/null || true
adb shell pm grant "$PKG" android.permission.RECORD_AUDIO 2>/dev/null || true
adb shell pm grant "$PKG" android.permission.POST_NOTIFICATIONS 2>/dev/null || true

# 3. Launch
echo "Launching app..."
adb shell am start -W -n "$ACTIVITY"
sleep 5

# 4. Screenshot
echo "Taking screenshot..."
adb exec-out screencap -p > "$SCREENSHOT_DIR/smoke_home.png"

# 5. Check logcat for crashes/ANRs
echo "Checking logcat for crashes..."
CRASHES=$(adb logcat -d -s "AndroidRuntime:E" "ActivityManager:E" | grep -c "FATAL\|ANR" || echo 0)

# 6. Process death test: kill and relaunch
echo "Testing process death recovery..."
adb shell am kill "$PKG"
sleep 2
adb shell am start -W -n "$ACTIVITY"
sleep 3
adb exec-out screencap -p > "$SCREENSHOT_DIR/smoke_after_kill.png"

# 7. Airplane mode test (if supported)
echo "Testing airplane mode..."
adb shell cmd connectivity airplane-mode enable 2>/dev/null || echo "Airplane mode toggle not available"
sleep 2
adb exec-out screencap -p > "$SCREENSHOT_DIR/smoke_offline.png"
adb shell cmd connectivity airplane-mode disable 2>/dev/null || true
sleep 2

# 8. Build result
RESULT="PASS"
if [ "$CRASHES" -gt 0 ]; then
  RESULT="FAIL"
fi

JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "package": "$PKG",
  "apk": "$APK",
  "result": "$RESULT",
  "crashes_found": $CRASHES,
  "screenshots": [
    "$SCREENSHOT_DIR/smoke_home.png",
    "$SCREENSHOT_DIR/smoke_after_kill.png",
    "$SCREENSHOT_DIR/smoke_offline.png"
  ]
}
EOF
)

echo "$JSON" | tee "$OUTPUT_DIR/smoke.json"

# 9. Uninstall (optional)
# adb uninstall "$PKG"

echo "=== Smoke test: $RESULT ==="
