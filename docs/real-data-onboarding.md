# Real Data Onboarding & Ingestion Protocol (Layer B)

**Project:** Kabadiwala Connect — Informal E-Waste Regularization  
**SIH Problem Statement:** PS SIH26229 (Ministry of Mines & JNARDDC)  
**Governance Level:** Human-in-the-Loop Consent-Gated Anonymization Framework  

---

## 1. Overview & Ethical Foundations

Kabadiwala Connect operates under a strict two-layer data architecture:
- **Layer A (Demo Baseline):** 100% synthetic fictional composite records with zero real-world PII.
- **Layer B (Field Ingestion):** Consent-gated, privacy-preserving ingestion of authentic ground-truth data from pilot scrap collection yards, aggregator centers, and authorized recyclers.

> [!IMPORTANT]
> **Data Minimization Guarantee:** Under no circumstances will Aadhaar numbers, PAN cards, bank passwords, voter credentials, home addresses, or facial photographs of individuals be accepted, stored, or processed by Kabadiwala Connect.

---

## 2. Multilingual Voluntary Informed Consent Scripts

Before any real collector, scrap aggregator, or facility operator data is recorded, the field enumerator must verbally recite the following script in the participant's preferred vernacular language and obtain unambiguous affirmative consent.

### 2.1 English Consent Script
> *"Namaste. We are conducting a pilot study on informal e-waste collection under the Ministry of Mines initiative (Kabadiwala Connect). We would like to record your operational scrap trades (such as material types, weights, and selling prices) to help you get better market prices and formal recycling incentives.  
> Your participation is completely voluntary. We will NOT ask for or store your Aadhaar number, PAN card, or personal home address. Your name and phone number will be encrypted and masked. You may request to remove your data at any time without any penalty.  
> Do you agree to participate?"*

### 2.2 Hindi (हिंदी) Consent Script
> *"नमस्ते। हम खान मंत्रालय की पहल (कबाड़ीवाला कनेक्ट) के तहत ई-कचरा संग्रहण पर एक प्रायोगिक अध्ययन कर रहे हैं। हम आपके दैनिक स्क्रैप व्यापार (जैसे सामग्री का प्रकार, वजन और बिक्री मूल्य) का विवरण दर्ज करना चाहते हैं ताकि आपको बेहतर बाजार भाव और सरकारी प्रोत्साहन मिल सके।  
> इसमें आपकी भागीदारी पूरी तरह से स्वैच्छिक है। हम आपका आधार नंबर, पैन कार्ड या घर का पता कभी नहीं मांगेंगे। आपका नाम और फोन नंबर पूरी तरह सुरक्षित और गुप्त रखा जाएगा। आप किसी भी समय अपना विवरण हटाने का अनुरोध कर सकते हैं।  
> क्या आप इसमें भाग लेने के लिए सहमत हैं?"*

### 2.3 Marathi (मराठी) Consent Script
> *"नमस्कार. आम्ही खाण मंत्रालयाच्या उपक्रमांतर्गत (कबाडीवाला कनेक्ट) ई-कचरा गोळा करणाऱ्या बांधवांसाठी प्रायोगिक अभ्यास करत आहोत. आपल्याला बाजारात चांगला भाव आणि पुनर्वापर प्रोत्साहन मिळावे यासाठी आम्ही आपल्या भंगार व्यवहारांची (उदा. मालाचा प्रकार, वजन आणि मिळालेला दर) नोंद घेऊ इच्छितो.  
> यातील तुमचा सहभाग पूर्णपणे ऐच्छिक आहे. आम्ही तुमचा आधार क्रमांक, पॅन कार्ड किंवा घराचा पत्ता कधीही मागणार नाही. तुमचे नाव आणि संपर्क क्रमांक सुरक्षित आणि गोपनीय ठेवला जाईल. आपण कोणत्याही क्षणी आपली माहिती काढून घेण्याची विनंती करू शकता.  
> या उपक्रमात सहभागी होण्यासाठी आपली संमती आहे का?"*

### 2.4 Punjabi (ਪੰਜਾਬੀ) Consent Script
> *"ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ। ਅਸੀਂ ਖਾਣ ਮੰਤਰਾਲੇ ਦੀ ਪਹਿਲਕਦਮੀ (ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ) ਤਹਿਤ ਈ-ਵੇਸਟ ਇਕੱਠਾ ਕਰਨ 'ਤੇ ਇੱਕ ਪਾਇਲਟ ਅਧਿਐਨ ਕਰ ਰਹੇ ਹਾਂ। ਅਸੀਂ ਤੁਹਾਡੇ ਸਕ੍ਰੈਪ ਦੇ ਲੈਣ-ਦੇਣ (ਜਿਵੇਂ ਕਿ ਸਮਾਨ ਦੀ ਕਿਸਮ, ਵਜ਼ਨ ਅਤੇ ਵਿਕਰੀ ਮੁੱਲ) ਨੂੰ ਦਰਜ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹਾਂ ਤਾਂ ਜੋ ਤੁਹਾਨੂੰ ਬਿਹਤਰ ਬਾਜ਼ਾਰ ਮੁੱਲ ਮਿਲ ਸਕੇ।  
> ਤੁਹਾਡੀ ਭਾਗੀਦਾਰੀ ਪੂਰੀ ਤਰ੍ਹਾਂ ਮਰਜ਼ੀ ਅਨੁਸਾਰ ਹੈ। ਅਸੀਂ ਤੁਹਾਡਾ ਆਧਾਰ ਨੰਬਰ, ਪੈਨ ਕਾਰਡ ਜਾਂ ਘਰ ਦਾ ਪਤਾ ਕਦੇ ਨਹੀਂ ਪੁੱਛਾਂਗੇ। ਤੁਹਾਡਾ ਨਾਮ ਅਤੇ ਫ਼ੋਨ ਨੰਬਰ ਸੁਰੱਖਿਅਤ ਅਤੇ ਗੁਪਤ ਰੱਖਿਆ ਜਾਵੇਗਾ। ਤੁਸੀਂ ਕਿਸੇ ਵੀ ਸਮੇਂ ਆਪਣਾ ਡੇਟਾ ਹਟਾਉਣ ਲਈ ਕਹਿ ਸਕਦੇ ਹੋ।  
> ਕੀ ਤੁਸੀਂ ਇਸ ਵਿੱਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਸਹਿਮਤ ਹੋ?"*

---

## 3. Data Field Specifications

### 3.1 Allowed & Mandatory Fields
- `consent_confirmed` (Boolean): Must be explicitly set to `TRUE`. If `FALSE`, ingestion fails immediately.
- `consent_language` (String): `en`, `hi`, `mr`, or `pa`.
- `display_name` (String): Preferred pseudonym or first name.
- `city` and `operating_area_name` (String): e.g. "Pune", "Hadapsar".
- `coarse_lat` / `coarse_lng` (Float): City/area centroid coordinates (jittered to ±500m; no precise rooftop coordinates).
- `material_code` (String): Valid system code (e.g. `PCB`, `BATTERY_LI`, `CABLES`, `MOTORS`).
- `weight_kg` (Float): Actual scale weight.
- `rate_inr_per_kg` (Float): Transaction rate per kilogram.
- `payment_mode` (String): `cash` or `upi`.

### 3.2 Strictly Forbidden Fields (Ingestion Blocker)
Any CSV containing the following column names or data patterns is automatically rejected by the quarantine validator:
- `aadhaar`, `aadhaar_number`, `uid`
- `pan`, `pan_number`
- `voter_id`, `epic`
- `home_address`, `residential_address`, `street_number`
- `bank_account`, `ifsc`, `cvv`, `card_number`

---

## 4. Importer CLI & Admin Endpoint Usage

### 4.1 CLI Ingestion Command
To import a verified, consent-backed real CSV into Layer B:
```bash
# Using Makefile
make import-real FILE=data/real/collectors_batch_01.csv

# Or direct Python invocation
python scripts/import_real.py data/real/collectors_batch_01.csv --dataset-name "Pune-Pilot-Phase1"
```

### 4.2 Administrative REST Endpoint
Authorized administrators can upload CSVs via the Admin Console or API:
```http
POST /admin/import-real
Authorization: Bearer <ADMIN_TOKEN>
Content-Type: multipart/form-data

file: <binary CSV>
dataset_name: "Delhi-Seelampur-Batch-1"
consent_confirmed: true
```

### 4.3 Validation & Quarantine Pipeline
1. **Schema Check:** Header validation against standard templates in [`templates/`](file:///d:/PROJECTS/kabadiwala/templates/).
2. **Consent Guard:** Asserts `consent_confirmed == True` on every row.
3. **Denylist Check:** Scans company names against [`seed/denylist_real_entities.txt`](file:///d:/PROJECTS/kabadiwala/seed/denylist_real_entities.txt) to prevent unauthorized usage of real corporate trademarks.
4. **Quarantine Table (`ingest_quarantine`):** If a batch contains invalid rows, clean rows are processed while erroneous rows are quarantined for manual admin review.
5. **Layer Tagging:** Every imported record is tagged with `is_synthetic = False` and associated with a unique `dataset_version_id`.

---

## 5. Synthetic Persona Retirement Protocol

As genuine collectors and recyclers join the platform from field pilots, synthetic personas can be retired or merged without breaking historical foreign keys or ledger totals.

### 5.1 Retirement Command
```bash
# Using Makefile
make retire-synthetic USERS="9800010001,9800010002"

# Or direct Python invocation
python scripts/retire_synthetic.py 9800010001 9800010002 --reason "Replaced by onboarded pilot collectors in Pune"
```

### 5.2 Retirement Endpoint
```http
POST /admin/retire-synthetic
Authorization: Bearer <ADMIN_TOKEN>
Content-Type: application/json

{
  "user_phones": ["9800010001", "9800010002"],
  "reason": "Onboarding authentic Hadapsar collectors"
}
```
**Effects of Retirement:**
- `is_active` set to `False`.
- Login via OTP disabled for retired synthetic accounts.
- Profile flagged with `is_retired: True`.
- Historical lots, transactions, and blockchain trace events preserved for audit and ML benchmark consistency.
