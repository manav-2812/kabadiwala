# Android Permissions — Kabadiwala Connect
**Smart India Hackathon 2026 — PS SIH26229**

## Permission Policy

1. **Minimal permissions** — only what's needed for core functionality
2. **Request in context** — never at launch, only when the feature is used
3. **Plain rationale** — in the user's language (4 languages), with icon + voice
4. **Graceful denial** — every denied permission still allows completing a sale

## Requested Permissions

| Permission | When Requested | Rationale (shown to user) | If Denied |
|------------|---------------|---------------------------|-----------|
| `CAMERA` | User taps "Take Photo" in Lot Builder | "We need camera access to photograph your scrap items" | Photo optional — spoken reminder, manual material selection works |
| `ACCESS_FINE_LOCATION` | User opts into GPS stamping at collection/handover | "Your location helps verify the pickup point and find nearby buyers" | "Approximate location skipped" — sale continues without GPS |
| `ACCESS_COARSE_LOCATION` | Fallback if fine location denied | Same as above | Same as above |
| `RECORD_AUDIO` | User taps mic button for voice note | "Voice recording lets you describe the items" | Voice note unavailable — text alternative shown |
| `POST_NOTIFICATIONS` (Android 13+) | After first quote received, not at launch | "Get notified when buyers respond to your lot" | In-app notification inbox still works |
| `INTERNET` | Always (manifest only) | N/A | N/A |
| `ACCESS_NETWORK_STATE` | Always (manifest only) | N/A | N/A |

## Never Requested

| Permission | Reason |
|------------|--------|
| `READ_EXTERNAL_STORAGE` / `READ_MEDIA_*` | Use app-private storage + system share sheet |
| `READ_CONTACTS` | Not needed |
| `READ_PHONE_STATE` | Not needed |
| `SEND_SMS` | Not needed |
| `CALL_PHONE` | Use `ACTION_DIAL` intent (no permission needed) |
| `ACCESS_BACKGROUND_LOCATION` | Never — no continuous GPS |
| `SYSTEM_ALERT_WINDOW` | Not needed |
| `REQUEST_INSTALL_PACKAGES` | Not needed |
| `WRITE_EXTERNAL_STORAGE` | Use FileProvider for sharing |

## Denied-Permission Paths

Every core flow (basket → lot → quote → handover → payment) must complete
even if ALL optional permissions are denied:

1. **Camera denied:** Skip photo, show spoken reminder "Photo helps get better price",
   continue with manual material selection
2. **Location denied:** Show "Approximate location skipped", sale completes without GPS stamp
3. **Audio denied:** Disable voice note button, show text alternative
4. **Notifications denied:** All notifications appear in the in-app inbox instead
