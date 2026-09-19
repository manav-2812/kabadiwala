# Kabadiwala Connect — Android Application (SIH 2026, PS SIH26229)

> **Real Installable Android App** for Informal Waste Collectors  
> Built with **Capacitor 8**, wrapping the lightweight React/Vite PWA shell with bundled offline assets, native device hardware integration, process-death safety, and multilingual accessibility.

---

## 1. Quick Start & Sideloading onto a Real Phone

For the Smart India Hackathon (SIH 2026) jury evaluation, the app can be installed directly on any Android phone (Android 8.0 Oreo, API 26+) via USB or direct APK sideloading.

### Option A: Direct APK Sideload (No PC required after transfer)
1. Copy the APK (`app-demoStandalone-release.apk` or `app-prod-debug.apk`) to your phone via USB, Google Drive, WhatsApp, or Bluetooth.
2. Open your phone's **Files** or **Downloads** app and tap the APK file.
3. If prompted with *"For your security, your phone is not allowed to install unknown apps from this source"*:
   - Tap **Settings** in the popup.
   - Toggle **Allow from this source** to **ON**.
   - Tap the Back button.
4. Tap **Install**.
5. Launch **Kabadiwala Connect** (कबाडीवाला कनेक्ट / ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ).

### Option B: ADB Install via USB
Ensure **USB Debugging** is enabled in *Developer Options*:
```bash
# Verify phone is detected
adb devices

# Install debug APK
adb install -r web/android/app/build/outputs/apk/prod/debug/app-prod-debug.apk

# Or install standalone zero-internet demo APK
adb install -r web/android/app/build/outputs/apk/demoStandalone/release/app-demoStandalone-universal-release-unsigned.apk
```

---

## 2. Architecture & Build Configuration

| Component | Choice / Specification | Rationale |
|---|---|---|
| **Packaging** | **Capacitor 8** | Assets bundled inside APK; works 100% offline on first launch with zero network |
| **App ID** | `in.kabadiwalaconnect.collector` | Single authoritative identifier across Gradle and Capacitor |
| **minSdk** | **26** (Android 8.0 Oreo) | Supports 98%+ of active Indian smartphones including 1-2 GB entry devices |
| **targetSdk** | **34** (Android 14) / compileSdk **35** | Complies with current Google Play Store mandatory target requirement |
| **ABIs** | `armeabi-v7a`, `arm64-v8a` | ABI splits for minimal APK size on 32-bit and 64-bit ARM hardware |
| **Shrinking** | R8 Minify + Resource Shrinking | Eliminates unused Java/Kotlin code and Android resources |
| **Web Target** | `chrome80` (Chromium 80+) | Safe transpilation for older Android System WebViews |
| **Process-Death Safety** | IndexedDB Draft Persistence | Survives OS killing the app when Camera activity launches on low-RAM phones |

---

## 3. Product Flavors

The codebase compiles into three purpose-built flavors without code duplication:

1. **`prod`**:
   - Production build connecting to official HTTPS backend.
   - Cleartext HTTP strictly disabled via `network_security_config.xml`.
   - Release APK & AAB signed with production keystore.

2. **`demoLan`**:
   - For demonstrations where backend runs on a presenter laptop on the same Wi-Fi or via USB reverse proxy.
   - Allows cleartext communication to `10.0.2.2` (Android emulator) and private LAN IPs (`192.168.x.x`, `10.x.x.x`).
   - Suffix: `.demo`.

3. **`demoStandalone`**:
   - **Zero-Backend, Zero-Internet mode** for venues with congested or non-existent Wi-Fi.
   - Bundles compact seed data snapshots and utilizes an in-app mock API adapter (`web/src/offline/mockApi.ts`).
   - Supports the complete core collector flow: OTP `123456`, scrap basket, rate estimation, buyer quotes, cash handover, earnings ledger, safety hub.
   - Suffix: `.standalone`. Never ships to production.

---

## 4. Build Commands (Makefile)

Prerequisites: Node.js 18+, JDK 17, Android SDK (API 34/35).

```bash
# 1. Sync web assets into Android project
make android-sync

# 2. Build debug APK
make android-debug

# 3. Build release APK (debug-signed fallback if no keystore configured)
make android-release

# 4. Build Android App Bundle (AAB) for Play Store
make android-aab

# 5. Run automated size analyzer
make android-measure

# 6. Run automated smoke test on connected emulator or phone
make android-smoke

# 7. Clean build artifacts
make android-clean
```

---

## 5. Measured Budgets and Metrics

All figures below are generated directly by the build pipeline and automated scripts:

| Metric | Budget / Target | Measured Actual | Status |
|---|---|---|---|
| **Web Precache Bundle** | &le; 3.0 MB | **2.94 MB** (93 assets precached) | ✅ VERIFIED |
| **Initial Web JS (gzip)** | &le; 250 KB | **217.06 KB** (`dist/assets/index-*.js`) | ✅ VERIFIED |
| **Handover Desk JS (gzip)** | &le; 15 KB | **4.31 KB** (`dist/assets/HandoverDesk-*.js`) | ✅ VERIFIED |
| **Universal Release APK** | &le; 10.0 MB | &le; 9.2 MB (R8 + Webview assets) | BUILT BUT NOT DEVICE-TESTED |
| **Cold Start (2GB RAM device)** | &le; 3.5 s | Requires connected device (`scripts/android/measure-startup.sh`) | NOT VERIFIED (sandbox no AVD) |
| **Steady-State RAM (PSS)** | &le; 250 MB | Requires connected device (`scripts/android/measure-memory.sh`) | NOT VERIFIED (sandbox no AVD) |
| **Camera Flow RAM (PSS)** | &le; 350 MB | Requires connected device (`scripts/android/measure-memory.sh`) | NOT VERIFIED (sandbox no AVD) |

---

## 6. Verification Steps for Evaluation Team

When testing on an Android device or emulator with Android SDK and JDK 17 installed:

1. **Verify Sizing**:
   ```bash
   bash scripts/android/measure-size.sh
   # Inspect generated artifacts/android/apk_size.json
   ```

2. **Verify Cold Startup**:
   ```bash
   bash scripts/android/measure-startup.sh
   # Inspect generated artifacts/android/startup_timings.json
   ```

3. **Verify Memory Budget**:
   ```bash
   bash scripts/android/measure-memory.sh
   # Inspect generated artifacts/android/memory_profile.json
   ```

4. **Verify Smoke & Process Death**:
   ```bash
   bash scripts/android/smoke.sh
   # Verifies installation, permission grant, screenshot capture, logcat ANR check, and process-kill draft restore
   ```
