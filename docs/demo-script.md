# 3-Minute Hackathon Judging Demo Script

**Project**: Kabadiwala Connect  
**Problem Statement**: SIH26229 (Ministry of Mines, JNARDDC, Clean & Green Technology)

---

## ⏱ Minute 0:00 – 0:45: The Problem & Informal Collector Uplift

1. **Context & Persona**:
   - Open `http://localhost:5173`.
   - Point out the floating **Demo Role Switcher** at the bottom-right corner.
   - Click **"Collector (Ramesh Kumar - Delhi)"**.
   - Switch language to **हिन्दी (Hindi)** or **ਪੰਜਾਬੀ (Punjabi)**. Click the **Voice Button** (Speaker icon) next to Namaste Ramesh — observe natural Indian vernacular text-to-speech.

2. **Fair Price Guarantee & Basket**:
   - Tap the big **"+ Add Scrap"** button.
   - Select **"Printed Circuit Boards (PCB)"**.
   - Show how the **Minimum Support Price (MSP)** floor protects Ramesh from middlemen: regardless of who buys, he is guaranteed statutory floor pricing.
   - Use the **Weight Stepper** to set `5.0 kg`.
   - Click **"Add to Scrap Basket"**.
   - Tap the **Basket Bag** in the top header. Click **"Review & Create Lot"**. Tap **"Submit & Find Authorized Buyers"**.

---

## ⏱ Minute 0:45 – 1:30: Recycler Matching, Logistics & 3-Second Live GPS

1. **Recycler Portal**:
   - Open Demo Switcher and select **"Recycler (EcoBirba Circular Recyclers)"**.
   - Navigate to `/recycler/marketplace`.
   - Show the newly published Lot appearing with GPS coordinates in Okhla, Delhi.
   - Click **"Submit Competitive Bid"** (₹2,100).

2. **Acceptance & Live Logistics**:
   - Switch back to Collector. Lot now shows **"Quotes Available"**.
   - Click **"Accept EcoBirba Offer"**.
   - Click **"Track Pickup Agent"**.
   - Observe the **Live 3-second WebSocket GPS updates**: the delivery van moves on the Leaflet map towards the scrap location, updating distance and ETA in real time.

---

## ⏱ Minute 1:30 – 2:15: Dual Weigh-In, Dispute Resolution & Instant UPI Settlement

1. **Weigh-In at Handover**:
   - Navigate to `/lots/lot-1/handover` (or click "Start Handover Weigh-In").
   - Test the **Tare Scale**: Enter `5.2 kg` (measured weight).
   - Point out the variance indicator. If variance exceeds 10%, the system flags a **Dispute Hold** with voice recording capture.
   - Confirm handover. Instant UPI settlement executes with reference `KCUPI9918237412`.

2. **CPCB Form 6 Manifest & Public Verification**:
   - Click **"Download Official Receipt & EPR Certificate (PDF)"**.
   - A complete ReportLab PDF opens inline with statutory CPCB watermarks, dual signatures, and QR code.
   - Click the QR code / URL `/verify/KC-RCPT-2024-001`.
   - Show how anyone, customs officer or inspector can publicly verify document validity without exposing collector personal phone numbers.

---

## ⏱ Minute 2:15 – 3:00: Ministry of Mines & JNARDDC National Intelligence

1. **Admin Portal**:
   - Open Demo Switcher and click **"Admin (Ministry of Mines & JNARDDC)"**.
   - View the 6 National Headline KPIs:
     - 14.28 Tonnes formalised e-waste.
     - +21.4% collector income uplift over exploitative informal middlemen.
     - 84.6 kg strategic critical minerals recovered.

2. **JNARDDC Critical Mineral Recovery Stack**:
   - Show the interactive **Critical Minerals Recovery Chart**:
     - 48.2 kg Copper (Cu) — +12.8% import offset.
     - 14.5 kg Lithium (Li) — +14.2% import offset.
     - 4.2 kg Neodymium (Nd) — +22.0% import offset!
   - Highlight: *"This is the first system that translates scrap weight directly into national raw material sovereignty."*

3. **Judge Interactive Cryptographic Test**:
   - Click **"Traceability Explorer"** in the top navigation.
   - Show the 5-event SHA-256 hash chain: status is green **"Chain Verified"**.
   - **Click "Simulate Tampering"**: sequence #2's hash is intentionally altered in the ledger.
   - Immediately observe the red alert banner: **"SECURITY ALERT: Audit Chain Compromised! Broken at Seq #2"**.
   - **Click "Repair Chain"**: the cryptographic engine recalculates the Merkle sequence and restores green **"Chain Verified"**.

4. **Closing Pitch**:
   - *"Kabadiwala Connect dignifies informal green warriors with guaranteed MSP income, eliminates toxic backyard acid-leaching, and creates a traceable domestic supply chain for critical technology minerals."*
