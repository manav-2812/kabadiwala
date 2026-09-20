# Internationalization (i18n) Review & Translation Audit

**Project**: Kabadiwala Connect (SIH 2026, PS SIH26229)  
**Supported Languages**:
1. **मराठी (mr)** - Marathi (Maharashtra & Western India e-waste hubs)
2. **हिन्दी (hi)** - Hindi (Delhi NCR, Rajasthan, UP, MP corridors)
3. **ਪੰਜਾਬੀ (pa)** - Punjabi (Ludhiana, Chandigarh, Amritsar industrial clusters)
4. **English (en)** - Technical reference & Administrative Console

---

## 1. Review Status & Disclaimer

> [!WARNING]
> **Native Linguistic Review Status**: `needs_native_review`  
> All translations in this prototype have been drafted with high attention to grammatical syntax and localized e-waste industry terminology. However, in strict compliance with hackathon guidelines, translations are designated as **drafts pending on-the-ground validation** by native waste-picker community representatives in Pune, Mumbai, Ludhiana, and Delhi NCR.

---

## 2. Translation Coverage Summary

| Language | Code | Total Keys | Coverage vs English | Review Status |
|---|---|---|---|---|
| English (Reference) | `en` | 83 | 100.0% | `authoritative` |
| Hindi | `hi` | 83 | 100.0% | `needs_native_review` |
| Marathi | `mr` | 83 | 100.0% | `needs_native_review` |
| Punjabi | `pa` | 83 | 100.0% | `needs_native_review` |

Automated verification is enforced via `scripts/check-i18n.ts` (`npm run test:i18n`), validating key existence, non-empty values, and placeholder consistency.

---

## 3. String Groups & Terminology Mapping

### Core Navigation & Actions
| Key | English (`en`) | Hindi (`hi`) | Marathi (`mr`) | Punjabi (`pa`) |
|---|---|---|---|---|
| `nav_home` | Home | होम | मुख्यपृष्ठ | ਮੁੱਖ ਪੰਨਾ |
| `nav_lots` | My Lots | मेरे लॉट | माझे लॉट्स | ਮੇਰੇ ਲਾਟ |
| `nav_prices` | Prices | बाजार भाव | बाजारभाव | ਬਾਜ਼ਾਰ ਭਾਅ |
| `nav_wallet` | Earnings Ledger | कमाई बहीखाता | कमाई नोंदवही | ਕਮਾਈ ਬਹੀਖਾਤਾ |
| `nav_basket` | Basket | कबाड़ टोकरी | भंगार टोपली | ਕਬਾੜ ਟੋਕਰੀ |
| `btn_add_scrap` | + Add Scrap | + कबाड़ जोड़ें | + भंगार जोडा | + ਕਬਾੜ ਜੋੜੋ |
| `btn_confirm_handover` | Confirm Handover (OTP/QR) | हैंडओवर पुष्टि (ओटीपी/क्यूआर) | हस्तांतरण खात्री (OTP/QR) | ਹੈਂਡਓਵਰ ਪੁਸ਼ਟੀ (ਓਟੀਪੀ/ਕਿਊਆਰ) |
| `btn_raise_dispute` | Raise Weight Dispute | वजन पर विवाद दर्ज करें | वजन तक्रार नोंदवा | ਵਜ਼ਨ 'ਤੇ ਵਿਵਾਦ ਦਰਜ ਕਰੋ |

### Cash-First & Statutory Verification
| Key | English (`en`) | Hindi (`hi`) | Marathi (`mr`) | Punjabi (`pa`) |
|---|---|---|---|---|
| `wallet_balance` | Ledger Balance | बहीखाता शेष | नोंदवही शिल्लक | ਬਹੀਖਾਤਾ ਬਾਕੀ |
| `pending_dues` | Pending Buyer Dues | खरीदार की बकाया राशि | खरेदीदाराकडून येणे बाकी रक्कम | ਖਰੀਦਦਾਰ ਦਾ ਬਕਾਇਆ |
| `cash_confirmed_collector` | I have counted and received full cash in hand | मैंने पूरी नकद राशि हाथ में गिनकर प्राप्त कर ली है | मी प्रत्यक्ष रोख रक्कम मोजून स्वीकारली आहे | ਮੈਂ ਪੂਰੀ ਨਕਦ ਰਾਸ਼ੀ ਹੱਥ ਵਿੱਚ ਗਿਣ ਕੇ ਲੈ ਲਈ ਹੈ |
| `cash_confirmed_buyer` | Buyer confirms cash payout handed over | खरीदार ने नकद भुगतान सौंपे जाने की पुष्टि की | खरेदीदाराने रोख रक्कम दिल्याची पुष्टी केली | ਖਰੀਦਦਾਰ ਨੇ ਨਕਦ ਭੁਗਤਾਨ ਦੇਣ ਦੀ ਪੁਸ਼ਟੀ ਕੀਤੀ |
| `dual_confirm_title` | Dual Cash Confirmation | दोहरी नकद पुष्टि | दुहेरी रोख रक्कम पडताळणी | ਦੋਹਰੀ ਨਕਦ ਪੁਸ਼ਟੀ |
| `digital_payments_toggle` | Enable Digital Payments | डिजिटल भुगतान सक्षम करें | डिजिटल पेमेंट्स सुरू करा | ਡਿਜੀਟਲ ਭੁਗਤਾਨ ਚਾਲੂ ਕਰੋ |

### E-Waste Material Categories
| Material Code | English | Hindi | Marathi | Punjabi |
|---|---|---|---|---|
| `PCB` | Circuit Boards | सर्किट बोर्ड | सर्किट बोर्ड (PCB) | ਸਰਕਟ ਬੋਰਡ (ਪੀਸੀਬੀ) |
| `BATTERY_LI` | Lithium Battery | लिथियम बैटरी | लिथियम बॅटरी | ਲਿਥੀਅਮ ਬੈਟਰੀ |
| `MAGNET` | Magnet Parts | चुंबक भाग | चुंबक भाग | ਚੁੰਬਕੀ ਹਿੱਸੇ |
| `CRT` | CRT Screen | सीआरटी स्क्रीन | सीआरटी स्क्रीन | ਸੀਆਰਟੀ ਸਕ੍ਰੀਨ |
| `LCD` | LCD Panel | एलसीडी डिस्प्ले | एलसीडी पॅनेल | ਐਲਸੀਡੀ ਪੈਨਲ |
| `CABLE` | Copper Cables | तांबे के तार | तांब्याची केबल | ਤਾਂਬੇ ਦੀਆਂ ਤਾਰਾਂ |
| `MOTOR` | Motors | मोटर | मोटर्स | ਮੋਟਰਾਂ |
| `PLASTIC_MIXED` | Mixed Plastic | मिश्रित प्लास्टिक | मिश्र प्लास्टिक | ਮਿਕਸਡ ਪਲਾਸਟਿਕ |
| `BATTERY_PB` | Lead-Acid Battery | लेड-एसिड बैटरी | लेड-अ‍ॅसिड बॅटरी | ਲੈੱਡ-ਐਸਿਡ ਬੈਟਰੀ |
| `OTHER` | Appliances | उपकरण | इतर उपकरणे | ਹੋਰ ਉਪਕਰਣ |

---

## 4. Dialect & Cultural Considerations

1. **Marathi Colloquialism vs Formal Marathi**:
   - In informal scrap yards in Mumbai (Dharavi/Kurla), scrap is universally called *"भंगार"* (Bhangar) rather than Sanskritized *"कचरा"* (Kachra).
   - "Earnings Ledger" is rendered as *"कमाई नोंदवही"* (Kamai Nondvahi), which is directly understood by self-help groups and cooperative workers in Maharashtra.
   - For Circuit Boards, *"सर्किट बोर्ड"* or *"मदरबोर्ड"* is retained in transliteration because English technical abbreviations are standard across informal electronic dismantlers.

2. **Hindi Transliteration vs Translation**:
   - Technical terms like OTP, QR, and CPCB are written phonetically in Devanagari (*ओटीपी, क्यूआर, सीपीसीबी*) to prevent confusing semi-literate collectors.
   - "Ledger" is translated as *"बहीखाता"* (Bahikhata), honoring traditional Indian informal accounting practices.

3. **Punjabi Nuances**:
   - In industrial centers like Ludhiana and Jalandhar, e-waste dismantling terms often blend Punjabi with technical Hindi/Urdu words (*ਕਬਾੜ, ਬਹੀਖਾਤਾ, ਪਰਤਾਵਾ*).
   - Gurmukhi orthography is strictly adhered to, with subsetted font self-hosting ensuring zero missing glyphs (tofu boxes).
