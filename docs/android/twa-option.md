# Trusted Web Activity (TWA) Option & Trade-off Analysis
## Kabadiwala Connect — SIH 2026 (PS SIH26229)

> **Document Purpose:** Evaluate Trusted Web Activity (TWA) via Google Bubblewrap as a secondary packaging approach for Google Play Store distribution, and document why **Capacitor 8 is the primary fixed choice** for informal waste collectors.

---

## 1. Executive Summary

A **Trusted Web Activity (TWA)** is an Android wrapper that opens a full-screen Chrome or Chromium browser tab without any browser address bar or UI chrome. It is built using the Android Custom Tabs protocol and requires a verified two-way cryptographic association called **Digital Asset Links** (`assetlinks.json`).

While TWA produces an ultra-small wrapper APK (~1.5 MB), it has **severe limitations** for entry-level informal waste collectors in India who frequently work in cellular dead zones or zero-connectivity scrap yards.

---

## 2. Comparison Matrix: Capacitor vs. Trusted Web Activity

| Evaluation Criteria | Capacitor 8 (Selected Primary) | Trusted Web Activity (TWA) |
|---|---|---|
| **First Launch with Zero Network** | **WORKS 100% OFFLINE**<br>HTML/JS/CSS/fonts/icons are bundled directly inside the APK assets directory. | **FAILS / BLANK SCREEN**<br>Requires initial network connection to download the web app from a hosted HTTPS domain. |
| **Hosted Domain Dependency** | **Zero dependency**<br>Runs directly off `https://localhost` within native WebView. | **Strict dependency**<br>Must own a live domain with valid SSL and hosted `.well-known/assetlinks.json`. |
| **Hardware Access (Camera, Geolocation)** | **Native Capacitor Plugins**<br>Accesses camera, GPS, vibration, and filesystem directly with native permission prompts. | **Browser Web APIs only**<br>Relies on Chrome's HTML5 permissions; camera relies on `<input type="file" capture>`. |
| **Process-Death Draft Recovery** | **Robust**<br>Native bridge handles Android OS activity recreation events and restores IndexedDB draft. | **Fragile**<br>Chrome tab can be purged by OS low-memory killer, losing unsaved state. |
| **Android System WebView Support** | **Targeted Transpilation**<br>Vite target set to `chrome80` with polyfills; bundles fonts to prevent missing glyphs on Android 8-10. | **Dependent on installed Chrome version**<br>If phone has outdated Chrome or no Google Play Services, behavior is unpredictable. |
| **Standalone Demo Mode (`demoStandalone`)** | **Fully supported**<br>Bundles seed data inside APK for zero-internet hackathon jury demos. | **Impossible without hosted mock**<br>Cannot bundle local mock responses inside TWA wrapper. |
| **APK File Size** | ~8 MB to 9.5 MB (universal) | ~1.5 MB (thin wrapper) |

---

## 3. How to Build a TWA (If Required in Future for Play Store Lite)

If the team decides to publish a lightweight TWA companion to the Play Store for urban users with stable 4G/5G connections:

### Step 1: Install Bubblewrap CLI
```bash
npm install -g @bubblewrap/cli
```

### Step 2: Initialize TWA Project
```bash
bubblewrap init --manifest=https://app.kabadiwalaconnect.in/manifest.webmanifest
```

### Step 3: Configure Digital Asset Links
Generate the SHA-256 fingerprint from your release keystore:
```bash
keytool -list -v -keystore release.keystore -alias kabadiwala
```

Add the fingerprint to `https://app.kabadiwalaconnect.in/.well-known/assetlinks.json`:
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "in.kabadiwalaconnect.collector.twa",
    "sha256_cert_fingerprints": [
      "YOUR_HEX_SHA256_FINGERPRINT_HERE"
    ]
  }
}]
```

### Step 4: Build APK / AAB
```bash
bubblewrap build
```

---

## 4. Conclusion & Recommendation

For **PS SIH26229**, where target users are informal waste collectors with entry-level Android devices working in low-connectivity scrap markets, **Capacitor 8 is unequivocally the superior and necessary choice**. It guarantees that an illiterate or low-literacy collector can open their phone and record scrap even in basements, recycling godowns, and rural collection centers with zero network coverage.
