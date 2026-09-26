# [SIH-2026-PS-SIH26229] Iteration 77 polish
# Real-Device QA Checklist (30 Items)
## Kabadiwala Connect — SIH 2026 (PS SIH26229)

> **Tester Instructions:** Perform this test suite on a physical 1 GB to 2 GB RAM Android phone running Android 8.0 to Android 14. Document Pass/Fail status, tester initials, and timestamps.

- **Device Under Test (DUT):** _______________________________________
- **Android OS Version:** _______________________________________
- **RAM / Internal Storage:** _______________________________________
- **Tester Name & Role:** _______________________________________
- **Date Tested:** _______________________________________

---

| # | Test Item | Verification Steps | Expected Result | Pass / Fail | Notes |
|---|---|---|---|---|---|
| **1** | **Fresh Clean Install** | Sideload release APK via ADB or file manager. Launch immediately. | Installs without manifest parsing errors; launches to language selection screen. | [ ] PASS [ ] FAIL | |
| **2** | **Zero-Network First Launch** | Turn on Airplane Mode before opening the app for the very first time. | App shell loads from bundled assets; offline warning banner appears gracefully; no blank white screen. | [ ] PASS [ ] FAIL | |
| **3** | **Standalone Demo Operation** | Launch `demoStandalone` build with Wi-Fi and Cellular off. Complete a full scrap sale. | Full flow succeeds: item entry, weight, buyer quotes, cash dual handover, receipt generation. | [ ] PASS [ ] FAIL | |
| **4** | **Marathi (मराठी) Glyph Integrity** | Switch app language to Marathi. Check Home, Lot Builder, and Safety Hub. | All Devanagari conjuncts render cleanly; no tofu (□) or missing glyphs; font weights crisp. | [ ] PASS [ ] FAIL | |
| **5** | **Hindi (हिंदी) Glyph Integrity** | Switch app language to Hindi. Check Price Board, Wallet, and Ledger. | Proper Devanagari typography, correct grammar, no fallback text clipping. | [ ] PASS [ ] FAIL | |
| **6** | **Punjabi (ਪੰਜਾਬੀ) Glyph Integrity** | Switch app language to Punjabi. Inspect navigation tabs and dialogs. | Bundled Gurmukhi font renders correctly; vowel signs (matras) align properly without boxes. | [ ] PASS [ ] FAIL | |
| **7** | **English UI Consistency** | Switch app language to English. Check all sub-screens. | Clean Latin font rendering; numerals formatted in Indian grouping (`₹1,24,500`). | [ ] PASS [ ] FAIL | |
| **8** | **Camera Permission: Allowed** | Tap Camera in Lot Builder. Grant camera permission when prompted. | Native camera opens; photo snaps cleanly; compressed image &le; 150 KB; thumbnail preview shows. | [ ] PASS [ ] FAIL | |
| **9** | **Camera Permission: Denied** | Deny camera permission on prompt. | Non-blocking fallback: spoken alert explains why photo helps; allows proceeding with manual entry. | [ ] PASS [ ] FAIL | |
| **10** | **GPS Permission: Allowed** | At lot creation, grant location access when prompted. | Single location fix acquired (&le; 8s); displays operating area / ward name; no persistent background watcher. | [ ] PASS [ ] FAIL | |
| **11** | **GPS Permission: Denied** | Deny location permission on prompt. | Graceful fallback: uses default operating area or allows manual dropdown; sale is NOT blocked. | [ ] PASS [ ] FAIL | |
| **12** | **Storage Quota Warning (85%+)** | Simulate low storage or fill sandbox directory to 85% capacity. | Amber banner warns "Storage almost full"; auto-prunes oldest synced lot photos; preserves unsynced outbox. | [ ] PASS [ ] FAIL | |
| **13** | **Android Battery Saver Mode** | Turn on OS Battery Saver mode. Navigate through app. | All animations gracefully degrade; touch responsiveness remains smooth; no background thread leaks. | [ ] PASS [ ] FAIL | |
| **14** | **Portrait Orientation Lock** | Rotate physical phone 90° and 180° into landscape. | App remains firmly locked in portrait orientation; no layout breakage or UI reflow glitch. | [ ] PASS [ ] FAIL | |
| **15** | **Hardware Back: Flow Step-Back** | Open Lot Builder Step 3 -> Press hardware back gesture or button. | Returns to Step 2 cleanly; does not exit app; preserves all entered weights and photos. | [ ] PASS [ ] FAIL | |
| **16** | **Hardware Back: Exit Confirm** | On Home screen, press hardware back button. | Prominent exit confirmation dialog pops up with Big Yes/No buttons and optional spoken prompt. | [ ] PASS [ ] FAIL | |
| **17** | **TalkBack Screen Reader** | Enable Android TalkBack in Accessibility Settings. Navigate Home tabs. | Buttons have descriptive spoken content descriptions in current language; no secret tokens read aloud. | [ ] PASS [ ] FAIL | |
| **18** | **Sunlight / Outdoor High-Contrast Mode** | Tap the Sunlight mode icon in header. | UI transforms into high-contrast theme: 7:1+ contrast, deep black on white, bold borders, visible under bright sun. | [ ] PASS [ ] FAIL | |
| **19** | **System Font Scaling (130%)** | Set phone font size to "Largest" (130%) in OS Settings. | Buttons, cards, and numeric rate displays wrap cleanly without overlapping text or broken layouts. | [ ] PASS [ ] FAIL | |
| **20** | **Touch Targets (&ge; 56px)** | Measure primary touch targets (Add Scrap, Confirm, NumPad keys). | All primary action touch targets measure &ge; 56px (&ge; 48dp), easily clickable with gloved or wet hands. | [ ] PASS [ ] FAIL | |
| **21** | **Spoken Price Audio & TTS Fallback** | Tap Speaker icon next to Copper/Brass on Price Board. | Audio plays clearly; if pre-recorded pack not present, Web Speech / Android TTS speaks rate accurately. | [ ] PASS [ ] FAIL | |
| **22** | **Audio Language Pack Download** | Navigate to Settings -> Download Audio Pack (Hindi/Marathi). | Shows download progress bar and file size (&le; 2.5 MB); caches locally for zero-latency offline playback. | [ ] PASS [ ] FAIL | |
| **23** | **Voice Note Support Recording** | Open Support -> Hold microphone icon -> Record 15-second voice query. | Audio records via Opus/AAC; plays back preview; saves to offline outbox if offline. | [ ] PASS [ ] FAIL | |
| **24** | **Local Notifications & Quiet Hours** | Schedule notification or receive quote response past 9:00 PM. | Notification obeys quiet hours (suppressed or delayed until 7:00 AM) unless high priority. | [ ] PASS [ ] FAIL | |
| **25** | **Share Receipt via Share Sheet** | Tap "Share Receipt" after completed transaction. | Opens native Android Share Sheet with WhatsApp, Bluetooth, and Print options. | [ ] PASS [ ] FAIL | |
| **26** | **WhatsApp Verify Link Sharing** | Tap WhatsApp share icon on public verification certificate. | Pre-fills message with verification URL (`https://.../verify/<doc>`) and summary. | [ ] PASS [ ] FAIL | |
| **27** | **Phone Call Intent (`ACTION_DIAL`)** | Tap helpline or buyer contact icon. | Opens Android phone dialer with number pre-filled; does NOT dial automatically without user confirmation. | [ ] PASS [ ] FAIL | |
| **28** | **Process Death Test (`am kill`)** | Start building a lot (Step 2) -> Run `adb shell am kill in.kabadiwalaconnect.collector` -> Relaunch. | App restores exact draft state from IndexedDB; entered scrap items and photos remain intact. | [ ] PASS [ ] FAIL | |
| **29** | **Offline Handover & Sync on Reconnect** | Complete sale in Airplane Mode -> Reconnect Wi-Fi -> Tap Sync. | Outbox flushes automatically; server assigns official lot code; zero duplicate transactions created. | [ ] PASS [ ] FAIL | |
| **30** | **Uninstall & Privacy Data Purge** | Tap "Delete My Data" in Settings or uninstall app. | All local storage, drafts, cached photos, and tokens purged cleanly from device. | [ ] PASS [ ] FAIL | |

---

### Sign-off & Overall Result
- **Total Tests Passed:** _____ / 30
- **Jury Demo Readiness Assessment:** [ ] READY FOR LIVE DEMO [ ] BLOCKED
- **Lead QA Signature:** _______________________________________
