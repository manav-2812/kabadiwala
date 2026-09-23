# [SIH-2026-PS-SIH26229] Iteration 14 polish
# Android Troubleshooting & Diagnostics Guide
## Kabadiwala Connect — SIH 2026 (PS SIH26229)

This guide covers common edge cases and solutions when deploying and testing the **Kabadiwala Connect** Android application on entry-level Android devices.

---

## 1. Issue: "Android System WebView Too Old"

### Symptoms
- Upon launching the app on an Android 8.0 to Android 10 phone, a full-screen prompt appears:
  *"कृपया Android System WebView अपडेट करें / Please update Android System WebView"*
- WebAssembly SIMD or modern CSS features may fail to initialize.

### Cause
Entry-level devices that have not been updated via Google Play may run Android System WebView versions earlier than Chrome 69 (which lacks standard WebAssembly, BigInt, or AbortController support).

### Resolution
1. **Option A (Connected to Internet):**
   - Tap the large green **"Update WebView ▶"** button on screen.
   - It opens the Google Play Store directly to the `com.google.android.webview` package.
   - Tap **Update**.
2. **Option B (Offline Testing):**
   - Tap the **"Continue anyway"** button below the update prompt.
   - The app continues in degraded fallback mode (using server-side ML inference and manual material selection rather than on-device WASM).

---

## 2. Issue: Camera Permission Denied

### Symptoms
- In Lot Builder or Handover Desk, tapping the camera icon does not open the native camera viewfinder.

### Cause
- The user tapped "Deny" or "Don't ask again" on the OS permission modal.

### Resolution
1. **Graceful App Fallback:**
   - The app detects permission denial and plays an informative voice prompt in the active vernacular language.
   - Taking a photo is **non-mandatory**; the collector can proceed by simply typing the estimated weight and material type.
2. **Re-enabling Permission in Android Settings:**
   - Go to phone **Settings -> Apps & Notifications -> App permissions -> Camera**.
   - Find **Kabadiwala Connect** and set to **Allow**.
   - Or via ADB:
     ```bash
     adb shell pm grant in.kabadiwalaconnect.collector android.permission.CAMERA
     ```

---

## 3. Issue: Storage Almost Full (&ge; 85% Quota)

### Symptoms
- Amber warning banner appears at top of screen: *"Device storage is almost full"*.

### Cause
- Low-end phones with 16 GB or 32 GB eMMC storage may run low on disk space due to cached offline assets or camera photos.

### Resolution
1. **Automated Pruning:**
   - The app's storage manager automatically identifies photos of **already-synced** completed lots and purges their local binary blobs.
   - Unsynced draft lots in the outbox are **never purged**.
2. **Manual Cache Clear:**
   - Go to app **Settings -> Storage** and tap **"Prune Synced Photos"**.
   - To completely reset the app sandbox:
     ```bash
     adb shell pm clear in.kabadiwalaconnect.collector
     ```

---

## 4. Issue: Backend Cold-Start Latency (Cloud Free Tier)

### Symptoms
- On first login or quote fetch, spinner loads for 15 to 30 seconds before receiving data.

### Cause
- Cloud backends hosted on serverless tiers (Render, Railway, Fly.io) spin down containers after 15 minutes of inactivity.

### Resolution
1. **Pre-Warm the Server Before Demos:**
   - Run the automated warm-up script 5 minutes before presenting:
     ```bash
     bash scripts/android/warmup.sh https://api.kabadiwalaconnect.in
     ```
2. **Zero-Latency Fallback (Standalone Demo Flavor):**
   - If the cloud network is uncooperative, switch immediately to the `demoStandalone` flavor:
     ```bash
     adb install -r web/android/app/build/outputs/apk/demoStandalone/release/app-demoStandalone-universal-release-unsigned.apk
     ```
   - Operates with 0ms network latency directly from bundled IndexedDB seed data!

---

## 5. Issue: ADB Reverse Port Forwarding Disconnects

### Symptoms
- USB demo stops loading data from `http://localhost:8000`.

### Cause
- Disconnecting the USB cable or phone entering deep doze drops the ADB socket tunnel.

### Resolution
- Re-run the port forwarding command:
  ```bash
  adb reverse tcp:8000 tcp:8000
  ```
- Verify active tunnels:
  ```bash
  adb reverse --list
  ```
