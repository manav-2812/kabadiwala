# Capacitor Plugins — Kabadiwala Connect
**Smart India Hackathon 2026 — PS SIH26229**

## Plugin Registry

Only add plugins with documented justification. Prefer official `@capacitor/*` plugins.

| Plugin | Version | Justification | Maintenance | Size Impact |
|--------|---------|---------------|-------------|-------------|
| `@capacitor/core` | ^7.x | Core runtime | Official, active | ~60 KB (APK) |
| `@capacitor/android` | ^7.x | Android platform | Official, active | ~2 MB (native runtime) |
| `@capacitor/app` | ^7.x | App lifecycle, back button, state change | Official, active | Minimal |
| `@capacitor/camera` | ^7.x | Native camera for photo capture (better than `<input>`) | Official, active | ~100 KB |
| `@capacitor/geolocation` | ^7.x | GPS fix for collection/handover locations | Official, active | Minimal |
| `@capacitor/network` | ^7.x | Network status detection for sync triggers | Official, active | Minimal |
| `@capacitor/preferences` | ^7.x | Key-value storage (settings, non-sensitive data) | Official, active | Minimal |
| `@capacitor/share` | ^7.x | Android share sheet for receipts/links | Official, active | Minimal |
| `@capacitor/filesystem` | ^7.x | App-private file storage for receipts | Official, active | Minimal |
| `@capacitor/local-notifications` | ^7.x | Local notifications (quotes, reminders) | Official, active | ~50 KB |
| `@capacitor/haptics` | ^7.x | Tactile feedback on actions | Official, active | Minimal |
| `@capacitor/keyboard` | ^7.x | Keyboard resize behavior | Official, active | Minimal |
| `@capacitor/splash-screen` | ^7.x | Native splash screen | Official, active | Minimal |
| `@capacitor/status-bar` | ^7.x | Status bar styling | Official, active | Minimal |

## Rejected Plugins (with reasoning)

| Plugin | Reason |
|--------|--------|
| `@capacitor/push-notifications` | Adds Firebase dependency (~1.5 MB). FCM is optional behind feature flag. |
| `@capacitor/browser` | Not needed — all navigation is in-app |
| `@capacitor/dialog` | Using web-based dialogs instead |
| `@capacitor-community/barcode-scanner` | Adds ML Kit (~4 MB). Using `html5-qrcode` JS scanner instead + typed alternative |
| `@capacitor/google-maps` | Not needed — using `geo:` intent for "Open in Maps" |
| `capacitor-secure-storage-plugin` | Investigating for token storage; currently using Preferences |

## Rules

1. **No plugin without a row in this table**
2. Community plugins need stronger justification than official ones
3. Any plugin adding >500 KB to APK size must have a documented alternative considered
4. Run `measure-size.sh` before and after adding a plugin
