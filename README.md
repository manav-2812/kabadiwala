# ♻️ Kabadiwala Connect

> **Smart India Hackathon 2026** — Problem Statement **SIH26229**  
> **Nodal Ministry**: Ministry of Mines & JNARDDC (Jawaharlal Nehru Aluminium Research Development and Design Centre)  
> **Theme**: Software, Clean & Green Technology  
> **Category**: E-Waste Formalisation, Critical Mineral Independence & Informal Collector Uplift

---

## 🌟 Executive Summary

**Kabadiwala Connect** is a full-stack, vernacular, low-literacy, offline-resilient e-waste formalisation marketplace. It bridges millions of informal scrap collectors (*kabadiwalas*) directly with Central Pollution Control Board (CPCB) authorized recyclers.

By introducing **statutory Minimum Support Price (MSP) floors**, **cryptographic SHA-256 chain-of-custody audit trails**, and **JNARDDC critical minerals recovery intelligence**, Kabadiwala Connect eliminates exploitative middlemen, prevents toxic backyard acid-leaching, and creates a domestic strategic stockpile of high-tech materials (Lithium, Neodymium, Cobalt, Copper, Gold, and Silver).

---

## 🚀 Key Innovations & Features

1. **Low-Literacy Vernacular Interface (4 Languages)**:
   - Native multilingual support (**Marathi**, **Hindi**, **Punjabi**, **English**) with Web Speech API text-to-speech voice prompts and subsetted WOFF2 fonts (Devanagari & Gurmukhi) preventing missing glyphs on Android 8+.
   - High-contrast visual cards, weight steppers, and large touch targets (≥ 56px / 7:1 contrast ratio) tailored for outdoor field use.
   - **Sunlight High-Contrast Mode**: 7:1+ contrast theme with deep black borders and text designed for collectors working under direct Indian sunlight.

2. **Native Installable Android App (Capacitor 8)**:
   - Works on entry-level Android devices (minSdk 26 Android 8.0 Oreo, targetSdk 34 Android 14) with 1–2 GB RAM.
   - **Zero-Network First Launch**: Assets bundled directly into the APK (`assets/public/`).
   - **Process-Death Draft Resilience**: Survives OS memory kills when Camera activity opens on low-RAM phones; resumes seamlessly.
   - **Product Flavors**: `prod` (HTTPS only), `demoLan` (local Wi-Fi/USB), and `demoStandalone` (zero-backend, zero-internet offline mode).
   - **Hardware Back & Safe-Area Insets**: Gesture navigation support, Android 15+ edge-to-edge safe area handling, and bilingual exit confirmation modal.

3. **Facility Weighbridge Handover Desk**:
   - Mobile-first console (`/handover-desk`) for weighbridge staff on mobile Chrome (responsive from 360px).
   - Real-time scale weight discrepancy alerts, scale photo evidence, cash handover settlement, and dual OTP confirmation.

4. **Fair Pricing Engine & Statutory MSP Floor**:
   - Protects informal collectors from price dumping. Recyclers can bid upward but cannot undercut statutory floor rates mandated by the Ministry of Mines.
   - Quality multipliers for condition (`broken`, `intact`, `stripped`).

5. **Cryptographic SHA-256 Audit Chain**:

*Documentation in progress during sprint...*
