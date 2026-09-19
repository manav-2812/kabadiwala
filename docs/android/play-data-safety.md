# Google Play Data Safety Form Questionnaire Draft
## Kabadiwala Connect — SIH 2026 (PS SIH26229)

> **Status:** Draft for developer reference and Play Console preparation.  
> **Notice:** This document answers Google Play's Data Safety questionnaire **truthfully** based strictly on the current code implementation of Kabadiwala Connect. No submission has been performed yet.

---

## 1. Overview Questions

| Question | Answer | Details |
|---|---|---|
| Does your app collect or share any user data? | **Yes** | Phone number (authentication), scrap photos (verification), approximate location (collection ward). |
| Is all of the user data collected by your app encrypted in transit? | **Yes** | All network communications use TLS 1.3 / HTTPS. Cleartext HTTP is disabled in production. |
| Do you provide a way for users to request that their data be deleted? | **Yes** | Users can tap "Delete My Data" in Settings or submit a deletion ticket via Support. |

---

## 2. Data Types Collected & Shared

### A. Location
- **Data type:** Approximate location & Precise location (single fix).
- **Collected:** Yes (single GPS fix acquired at time of scrap pickup or handover).
- **Shared:** No (never shared with third-party advertising or analytics networks).
- **Purpose:** App functionality (determining which local recycling hubs and kabadiwalas can service the pickup).
- **Optional or required?** **Optional.** Collectors can deny GPS permission and manually pick their ward or proceed with approximate area.

### B. Personal Information
- **Phone number:**
  - **Collected:** Yes. Used solely for OTP SMS login and account custody verification.
  - **Shared:** No.
  - **Purpose:** Account management, transaction receipts.
  - **Optional or required?** Required for collector account association.
- **Name / Identity:**
  - **Collected:** Optional display name (e.g. "Ramesh Kumar" or vernacular alias).
  - **Aadhaar / Government ID:** **NEVER COLLECTED.** Explicitly forbidden by PS SIH26229 data minimization mandate.

### C. Photos and Videos
- **Data type:** Photos of recyclable scrap lots and weighbridge scale readings.
- **Collected:** Yes (client-side compressed to &le; 150 KB, EXIF stripped).
- **Shared:** Only shared with the matched authorized recycler/hub for weight and material dispute resolution.
- **Purpose:** Transaction verification and fraud prevention.
- **Training Consent:** Each photo upload defaults to **Opt-Out** for AI training. Only used for AI retraining if collector explicitly checks the consent box.

### D. Audio Files
- **Data type:** Voice notes for customer support queries.
- **Collected:** Optional (only when collector holds the microphone button to dictate a support ticket).
- **Shared:** No.
- **Purpose:** Low-literacy grievance redressal.

### E. Financial Information
- **Data type:** Cash transaction amounts and voluntary UPI VPA handle for formal direct-to-bank settlement.
- **Collected:** Yes.
- **Credit Card / Bank Account numbers:** Not collected directly (handled via NPCI UPI intents).

### F. Device or Other Identifiers
- **Advertising ID (AAID):** **NOT COLLECTED.**
- **FCM Push Token:** Collected only if push notifications are enabled, solely for transaction status alerts.

---

## 3. Security and Privacy Practices

1. **Data Minimization:** No biometric data, no contact book scraping, no continuous location tracking, no call log access.
2. **On-Device Storage:** Tokens stored in Android Keystore / Encrypted Preferences.
3. **EXIF Stripping:** GPS metadata and camera serial numbers are stripped client-side in the WebView before transmission.
4. **Data Retention:** Unsynced drafts persist in IndexedDB. Synced photos are pruned when local storage reaches 85% capacity.
