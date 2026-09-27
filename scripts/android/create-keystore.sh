# [SIH-2026-PS-SIH26229] Iteration 91 polish
#!/usr/bin/env bash
# create-keystore.sh — Release Keystore Generator
# Kabadiwala Connect — SIH 2026 (PS SIH26229)
#
# Interactive script to create a release signing keystore.
# Output is git-ignored. BACK UP THIS FILE — losing it blocks updates!

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PATH="$SCRIPT_DIR/../../release.keystore"

echo "=== Kabadiwala Connect — Release Keystore Generator ==="
echo ""
echo "⚠️  IMPORTANT: Back up this keystore! Losing it means you cannot"
echo "    publish updates to the same app listing on Google Play."
echo ""

read -p "Keystore output path [$DEFAULT_PATH]: " KS_PATH
KS_PATH="${KS_PATH:-$DEFAULT_PATH}"

read -p "Key alias [kabadiwala]: " KS_ALIAS
KS_ALIAS="${KS_ALIAS:-kabadiwala}"

read -p "Validity (years) [25]: " KS_VALIDITY
KS_VALIDITY="${KS_VALIDITY:-25}"

echo ""
echo "You will be prompted for passwords and certificate details."
echo ""

keytool -genkeypair \
  -v \
  -keystore "$KS_PATH" \
  -alias "$KS_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity $((KS_VALIDITY * 365)) \
  -storetype JKS

echo ""
echo "✅ Keystore created: $KS_PATH"
echo ""
echo "To use in builds, set these environment variables:"
echo "  export KC_KEYSTORE_FILE=$KS_PATH"
echo "  export KC_KEYSTORE_PASSWORD=<your-store-password>"
echo "  export KC_KEY_ALIAS=$KS_ALIAS"
echo "  export KC_KEY_PASSWORD=<your-key-password>"
echo ""
echo "For CI, add these as GitHub Actions secrets."
echo ""
echo "⚠️  DO NOT commit this file to git!"
