# Audio Recording & Vernacular Voice Asset Guide
**Smart India Hackathon 2026 — PS SIH26229**  
**Ministry of Mines & JNARDDC | Kabadiwala Connect**

---

## 1. Purpose & Target Persona

Informal waste collectors (*kabadiwalas*) in India operate in noisy, outdoor scrapyard environments where daylight glare and low textual literacy present severe usability barriers. 

To ensure **zero literacy dependency**, Kabadiwala Connect features a **Spoken Vernacular Price Board & Action Audio Layer**. When a collector taps any material card or transaction state, the platform speaks the live price, CPCB formal premium, and cash confirmation status in their chosen native language.

Supported Languages:
1. **मराठी (`mr-IN`)** — Marathi (Western India / Maharashtra e-waste hub)
2. **हिन्दी (`hi-IN`)** — Hindi (Northern & Central India)
3. **ਪੰਜਾਬੀ (`pa-IN`)** — Punjabi (Northern agricultural & industrial hub)
4. **English (`en-IN`)** — Indian English (Administrative / Compliance mode)

---

## 2. Technical Audio Specifications

| Parameter | Specification | Rationale |
|---|---|---|
| **Format** | MP3 (MPEG-1 Audio Layer III) / AAC | 100% universal Android WebView & Safari compatibility |
| **Channels** | Mono (1 Channel) | Eliminates stereo phase issues, halves file size |
| **Sample Rate** | 24,000 Hz (or 44,100 Hz downsampled) | Clear speech band (covers up to 12kHz frequencies) |
| **Bitrate** | 48 kbps – 64 kbps CBR | Ultra-low bandwidth (< 15 KB per short prompt) |
| **Target Loudness** | -16.0 LUFS (±1.0 LUFS) | Audible above noisy 75dB scrapyard and traffic ambiance |
| **Noise Floor** | < -55 dBFS | Clean voice without room echo or HVAC hum |
| **Silence Padding** | 30ms – 50ms pre/post | Prevents click/pop on mobile DAC startup and shutdown |

---

## 3. Directory Layout & File Naming

Audio files are hosted statically under `web/public/audio/{lang}/` and mapped via `web/public/audio/manifest.json`:

```
web/public/audio/
├── manifest.json
├── mr/
│   ├── materials/
│   │   ├── battery.mp3
│   │   ├── pcb_high.mp3
│   │   ├── pcb_low.mp3
│   │   ├── copper_wire.mp3
│   │   ├── aluminum_heat.mp3
│   │   ├── crt_glass.mp3
│   │   ├── compressor.mp3
│   │   ├── plastic_abs.mp3
│   │   ├── mixed_motor.mp3
│   │   └── solar_cell.mp3
│   ├── prompts/
│   │   ├── rupees_per_kg.mp3
│   │   ├── current_rate.mp3
│   │   ├── formal_premium.mp3
│   │   └── cash_payment_verified.mp3
│   └── numbers/
│       ├── 0.mp3 ... 10.mp3, 50.mp3, 100.mp3, 500.mp3
├── hi/ ...
├── pa/ ...
└── en/ ...
```

---

## 4. Voice Script & Pronunciation Guide

### 4.1 Marathi (`mr-IN`)
- **Battery:** "बॅटरी — ७२ रुपये प्रति किलो" (*Battery — bahattar rupaye prati kilo*)
- **High-grade PCB:** "उच्च दर्जाचे पीसीबी — ४५० रुपये प्रति किलो" (*Uchha darjache PCB — char-she-panchas rupaye prati kilo*)
- **Copper Wire:** "तांब्याची वायर — ६४० रुपये प्रति किलो" (*Tambyachi wire — sa-she-chalis rupaye prati kilo*)
- **Formal Premium:** "अधिकृत पुनर्वापरकर्ता २० टक्के अधिक भाव देईल" (*Adhikrut punarvapar karta vis takke adhik bhav deyil*)
- **Cash Handover:** "रोख रक्कम मिळाली आणि मोजली" (*Rokh rakkam milali aani mojli*)

### 4.2 Hindi (`hi-IN`)
- **Battery:** "बैटरी — ७२ रुपये प्रति किलो" (*Battery — bahattar rupaye prati kilo*)
- **High-grade PCB:** "हाई-ग्रेड मदरबोर्ड — ४५० रुपये प्रति किलो" (*High-grade motherboard — char sau pachas rupaye prati kilo*)
- **Copper Wire:** "तांबे का तार — ६४० रुपये प्रति किलो" (*Tambe ka taar — chhe sau chalis rupaye prati kilo*)
- **Formal Premium:** "सीपीसीबी अधिकृत खरीदार से बीस प्रतिशत अतिरिक्त मुनाफा" (*CPCB adhikrut kharidar se bees pratishat atirikt munafa*)
- **Cash Handover:** "नकद भुगतान प्राप्त हुआ और गिना गया" (*Nakad bhugtan prapt hua aur gina gaya*)

### 4.3 Punjabi (`pa-IN`)
- **Battery:** "ਬੈਟਰੀ — ੭੨ ਰੁਪਏ ਪ੍ਰਤੀ ਕਿਲੋ" (*Battery — bahattar rupaye prati kilo*)
- **Copper Wire:** "ਤਾਂਬੇ ਦੀ ਤਾਰ — ੬੪੦ ਰੁਪਏ ਪ੍ਰਤੀ ਕਿਲੋ" (*Tambe di taar — chhe sau chalis rupaye prati kilo*)
- **Cash Handover:** "ਨਕਦ ਭੁਗਤਾਨ ਪ੍ਰਾਪਤ ਹੋਇਆ" (*Nakad bhugtan prapt hoya*)

### 4.4 English (`en-IN`)
- **Battery:** "Battery — seventy-two rupees per kilogram"
- **High-grade PCB:** "High grade circuit board — four hundred and fifty rupees per kilogram"
- **Cash Handover:** "Cash payment received and verified on-site"

---

## 5. Fallback Architecture (Graceful Offline Degradation)

If an audio clip file has not yet been recorded or fails to load over a poor mobile connection, the frontend player (`web/src/lib/spokenPriceBoard.ts`) automatically falls back to:
1. **Native Web Speech Synthesis (`SpeechSynthesisUtterance`)** using standard BCP-47 language tags (`mr-IN`, `hi-IN`, `pa-IN`, `en-IN`).
2. **Visual High-Contrast Badge** displaying the price in large bold numerals (e.g., `₹640 / kg`).
