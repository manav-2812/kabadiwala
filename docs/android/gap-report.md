# [SIH-2026-PS-SIH26229] Iteration 106 polish
# Android Gap Report — Kabadiwala Connect
**Smart India Hackathon 2026 — PS SIH26229**
**Audit Date:** 2026-09-27

---

## 1. Current PWA State

| Aspect | Status | Detail |
|--------|--------|--------|
| **Framework** | React 19 + Vite 6 + TypeScript 5.7 | Single codebase at `web/` |
| **PWA Plugin** | `vite-plugin-pwa@0.21.1` (Workbox) | `registerType: 'autoUpdate'` |
| **Precache** | Workbox glob `**/*.{js,css,html,svg,png,woff2}` | Runtime caching for `/api/materials` (StaleWhileRevalidate, 7d) and `/api/prices` (NetworkFirst, 1d) |
| **Manifest** | Inline in vite.config.ts — `name: 'Kabadiwala Connect'`, `display: standalone`, `orientation: portrait` | Icons: only `favicon.svg` (no rasterized PNGs for adaptive icon) |
| **Offline support** | IndexedDB via `idb` package — `outbox`, `basket`, `cache` stores | Mutations queued via `queueAction()` in outbox; GET requests fail with no fallback when offline + no cache |
| **Service Worker** | Workbox-generated + separate `firebase-messaging-sw.js` for FCM | FCM SW has env var injection hack via Vite dev server middleware |
| **Build output** | `web/dist/` — standard Vite build | Manual chunks: vendor-charts (recharts/d3), vendor-maps (leaflet), vendor-firebase |

### Gaps for Capacitor:
- **No Capacitor project at all** — no `capacitor.config.ts`, no `android/` folder
- PWA service worker approach won't be primary on Capacitor (assets bundled in APK)
- `createBrowserRouter` used — needs to work with Capacitor's `https://` scheme
- No `build.target` set in Vite — defaults to modern ESNext; needs conservative target for old WebView
- `firebase-messaging-sw.js` injected via server middleware — won't work in Capacitor (no Vite server)

---

## 2. Bundle Sizes (from existing code analysis)

| Item | Estimated | Budget |
|------|-----------|--------|
| **Collector JS chunk** | ~167 KB gzip (per `docs/apk.md`) | ≤ 250 KB gzip |
| **Total precache** | ~2.4 MB (per `docs/apk.md`) | ≤ 3 MB |
| **Fonts (WOFF2)** | 39 files, ~1.32 MB total (Inter 3 weights × 7 subsets + NotoDevangari 3×3 + NotoGurmukhi 3×3) | Within budget but many Inter subsets (Cyrillic, Greek, Vietnamese) are unnecessary |
| **Audio clips** | `manifest.json` only (16 KB), no actual `.webm`/`.mp3` clip files exist | Placeholder state — TTS fallback is the only working path |
| **ML model** | `ml/model.tflite` — 3.3 MB (TFLite format) | Needs ONNX conversion for WASM; should be downloadable pack, not in APK |
| **Images** | `web/public/photos/` exists (placeholder photos), `favicon.svg` only icon | No adaptive Android icon assets |

### Gaps:
- **Fonts are bloated** — Cyrillic, Greek, Vietnamese subsets of Inter are unnecessary for India deployment. Can save ~200 KB+
- **No actual audio clips** — only manifest placeholder; TTS fallback works
- **ML model is TFLite** — needs ONNX Web conversion or server-only path
- No bundle measurement scripts exist for Android-specific metrics

---

## 3. Offline Layer

| Component | Status | Gap |
|-----------|--------|-----|
| **IndexedDB stores** | `outbox`, `basket`, `cache` (via `idb@8`) | ✅ Exists |
| **Mutation queueing** | `queueAction()` — POST/PATCH/DELETE queued offline | ✅ Exists, returns optimistic response |
| **Sync triggers** | None implemented — outbox items are queued but never automatically synced | ❌ **Critical gap**: no sync-on-resume, no sync-on-reconnect, no manual "Sync now" |
| **Offline GET fallback** | API client returns nothing for offline GETs (no cached response fallback) | ❌ **Gap**: prices, materials, lots should fall back to IndexedDB cache |
| **Storage persistence** | No `navigator.storage.persist()` call | ❌ **Gap** |
| **Quota monitoring** | None | ❌ **Gap** |
| **Draft persistence** | LotBuilder state is React `useState` only — not persisted | ❌ **Critical gap**: process death kills all draft data |

---

## 4. Camera / GPS Code

| Feature | Status | Gap |
|---------|--------|-----|
| **Photo capture** | `<input type="file" accept="image/*" capture="environment">` in LotBuilder | ❌ Needs Capacitor Camera plugin for native quality |
| **Image compression** | Canvas-based resize exists in LotBuilder (1280px, quality 0.7) | Partially done; no explicit ≤150 KB enforcement |
| **EXIF stripping** | Not implemented | ❌ **Gap** |
| **Thumbnails** | Not implemented | ❌ **Gap** |
| **Photo quality gate** | `assessQuality()` in `quality.ts` — brightness + blur check | ✅ Exists |
| **Perceptual hash** | `computeDHash()` in `phash.ts` — 64-bit dHash | ✅ Exists |
| **GPS** | Hardcoded `{ lat: 28.6139, lng: 77.2090 }` in HandoverView | ❌ **Critical gap**: no real geolocation, no consent flow |
| **Process-death safety** | No draft persistence mechanism | ❌ **Critical gap** |

---

## 5. i18n (Internationalization)

| Aspect | Status | Gap |
|--------|--------|-----|
| **Languages** | `mr`, `hi`, `pa`, `en` — all four JSON files present | ✅ |
| **i18next** | Configured with `react-i18next`, `localStorage` persistence | ✅ |
| **Translation coverage** | 18 KB en, 32 KB hi, 33 KB mr, 31 KB pa | ✅ Good coverage |
| **Fonts** | Inter (Latin), Noto Sans Devanagari, Noto Sans Gurmukhi — all subsetted WOFF2 | ✅ Bundled |
| **Language switch** | `LanguageSwitch` component exists | ✅ |
| **Localized app label** | Not done (no Android `values-mr/strings.xml` etc.) | ❌ **Gap** |
| **`locales_config.xml`** | Not done (Android 13+ per-app language) | ❌ **Gap** |
| **Date/currency format** | `formatINR()` exists in `format.ts` with Indian grouping (₹1,24,500) | ✅ |
| **RTL** | Not applicable (all four languages are LTR) | N/A |
| **Tofu testing** | Not done — need screenshots on Android 8 emulator | ❌ **Gap** |

---

## 6. Audio System

| Component | Status | Gap |
|-----------|--------|-----|
| **Audio clip composer** | `audio.ts` — `playToken()`, `playPhrase()`, `cancelAudio()` | ✅ Architecture exists |
| **Pre-recorded clips** | `manifest.json` exists but `placeholder: true` — no actual audio files | ❌ Only TTS fallback works |
| **TTS fallback** | `speechFallback()` using Web Speech API | ✅ Works |
| **Spoken price board** | `spokenPriceBoard.ts` — `speakMaterialRate()` with clip → TTS chain | ✅ Works |
| **Voice input** | `voice.ts` — `startVoiceRecognition()` using Web Speech API | ✅ |
| **Volume check** | Not implemented — no "Volume is low" hint | ❌ **Gap** |
| **Audio focus** | Not handled — Android audio focus behavior not considered | ❌ **Gap** |
| **Downloadable packs** | Not implemented — no pack download UI/logic | ❌ **Gap** |

---

## 7. ML (Machine Learning)

| Component | Status | Gap |
|-----------|--------|-----|
| **Model** | `ml/model.tflite` (3.3 MB) — trained MobileNetV2 classifier | ✅ Trained |
| **Server inference** | Backend has ML endpoints (`/api/ml/classify`) | ✅ |
| **Client inference** | Not implemented — LotBuilder has AI suggestion state but no ONNX/WASM runtime | ❌ **Gap** |
| **ONNX Runtime** | Not installed | ❌ **Gap** |
| **SIMD detection** | Not implemented | ❌ **Gap** |
| **Memory guard** | Not implemented | ❌ **Gap** |
| **Model download** | No download mechanism — model is only in `ml/` directory | ❌ **Gap** |

---

## 8. Native Features Not Yet Implemented

| Feature | Status |
|---------|--------|
| **Capacitor project** | ❌ Not created |
| **Camera plugin** | ❌ Uses `<input>` tag |
| **Geolocation plugin** | ❌ Hardcoded coordinates |
| **Network detection plugin** | ❌ Basic `navigator.onLine` only |
| **Local notifications** | ❌ Not implemented (FCM push only via Firebase) |
| **Share/FileProvider** | ❌ Not implemented |
| **Deep links** | ❌ Not configured |
| **Back button handling** | ❌ Not implemented |
| **Safe area insets** | ❌ No `env(safe-area-inset-*)` usage |
| **Keyboard handling** | ❌ No Capacitor keyboard plugin |
| **Splash screen** | ❌ No native splash |
| **Status bar** | ❌ No StatusBar plugin |
| **Portrait lock** | ❌ Only in PWA manifest, not enforced natively |
| **Sunlight/high-contrast mode** | ❌ Not implemented |
| **Font scale handling** | ❌ Not tested |
| **TalkBack labels** | ❌ No `aria-label` on icon buttons |
| **Exit confirmation** | ❌ Not implemented |
| **Process-death recovery** | ❌ Not implemented |

---

## 9. Security

| Aspect | Status | Gap |
|--------|--------|-----|
| **Token storage** | `localStorage` | ❌ Should use secure storage (Android Keystore-backed) |
| **Network security config** | N/A (no Android project) | ❌ **Gap** |
| **CSP** | No Content-Security-Policy meta tag | ❌ **Gap** |
| **EXIF stripping** | Not done | ❌ **Gap** |
| **Cleartext traffic** | N/A | ❌ **Gap** |
| **WebView hardening** | N/A | ❌ **Gap** |
| **Keystore** | N/A | ❌ **Gap** |
| **Data safety form** | Not drafted | ❌ **Gap** |
| **Privacy policy** | Not drafted | ❌ **Gap** |

---

## 10. Build & CI

| Aspect | Status | Gap |
|--------|--------|-----|
| **Makefile targets** | `dev`, `seed`, `test`, `demo`, `docker-*` | ❌ No Android targets |
| **CI workflow** | None found in repo | ❌ **Gap** |
| **Bundle measurement** | `scripts/measure-bundle.mjs` exists | Partially — no Android-specific scripts |
| **APK doc** | `docs/apk.md` — documents Bubblewrap (TWA) + Capacitor approaches | ✅ Good reference but outdated (minSdk 23, old package IDs) |

---

## 11. Existing Docs

| Doc | Relevant Android Content |
|-----|--------------------------|
| `docs/apk.md` | TWA + Capacitor approaches documented; size estimates present |
| `docs/ai-gap-report.md` | ML model status, ONNX plan mentioned |
| `docs/architecture.md` | System architecture overview |
| `docs/audio-recording-guide.md` | Audio clip recording spec |
| `docs/demo-script.md` | Demo flow script |
| `docs/i18n-review.md` | i18n coverage review |

---

## 12. Summary: Critical Gaps to Close

### Must-Have (Blocking):
1. ❌ Create Capacitor project with Android platform
2. ❌ Configure `build.target` for old WebView (chrome80)
3. ❌ Draft persistence / process-death safety
4. ❌ Real GPS with consent
5. ❌ Sync engine (on-resume, on-reconnect, manual)
6. ❌ Native camera via Capacitor plugin
7. ❌ EXIF stripping
8. ❌ Back button / exit confirmation
9. ❌ Safe area insets
10. ❌ Secure token storage
11. ❌ Demo standalone flavor with mock API

### Important (High Priority):
12. ❌ Sunlight/high-contrast mode
13. ❌ Font scale testing
14. ❌ TalkBack labels
15. ❌ Network security config (HTTPS-only for prod)
16. ❌ ABI splits + R8 minification
17. ❌ Android measurement scripts
18. ❌ Localized app label + `locales_config.xml`
19. ❌ Handover Desk mobile route for recycler staff
20. ❌ Audio pack download mechanism

### Nice-to-Have:
21. ❌ ONNX Runtime Web integration
22. ❌ Maestro UI automation flows
23. ❌ TWA option documentation
24. ❌ Play Store data safety form
25. ❌ Privacy policy in 4 languages
