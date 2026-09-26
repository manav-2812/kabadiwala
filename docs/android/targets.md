# [SIH-2026-PS-SIH26229] Iteration 76 polish
# Android Targets — Kabadiwala Connect
**Smart India Hackathon 2026 — PS SIH26229**

## SDK Targets

| Property | Value | Rationale |
|----------|-------|-----------|
| `minSdk` | **26** (Android 8.0 Oreo) | Covers entry-level phones still in use by collectors; Android 8.0 has ~99% market coverage in India |
| `targetSdk` | **35** (Android 15) | Google Play requires targetSdk 35 for new apps and updates as of August 2025 |
| `compileSdk` | **35** | Latest stable Android SDK |

## ABI Targets

| ABI | Release | Debug | Notes |
|-----|---------|-------|-------|
| `armeabi-v7a` | ✅ | ✅ | 32-bit ARM — many entry-level phones (JioPhone Next, Redmi A-series) |
| `arm64-v8a` | ✅ | ✅ | 64-bit ARM — modern phones |
| `x86` | ❌ | ❌ | Not needed |
| `x86_64` | ❌ | ✅ | For Android Studio emulators only |

## WebView Compatibility

- **Build target:** `chrome80` (Vite `build.target`)
- **Minimum WebView:** Chrome 69+ (Android 8.0 ships with Chrome 58-69 WebView, but Google Play updates it)
- **Feature detection:** WebAssembly, Intersection Observer, CSS `env()`, `BigInt`
- **Update prompt:** If WebView is too old, show "Please update Android System WebView" with Play Store link

## References

- [Google Play targetSdk requirements](https://developer.android.com/google/play/requirements/target-sdk)
- [Android API levels](https://apilevels.com/)
- [India Android version distribution](https://gs.statcounter.com/android-version-market-share/mobile/india)
