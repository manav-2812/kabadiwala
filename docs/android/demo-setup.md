# Android Demo Setup & Connectivity Guide (SIH 2026, PS SIH26229)

This guide details three reliable demonstration configurations for the **Kabadiwala Connect** Android application during the live SIH 2026 evaluation.

---

## Method 1: USB Tethered Demo (Recommended for Predictability)

Running the backend on your laptop while tethering your phone via USB guarantees zero dependency on venue Wi-Fi interference.

### Prerequisites
- Presenter laptop running the FastAPI backend (`uvicorn app.main:app --port 8000`)
- Android phone with USB debugging enabled connected via USB cable
- `adb` installed on presenter laptop

### Step-by-Step Instructions
1. **Start the backend and seed data:**
   ```bash
   make demo
   # Runs backend at http://localhost:8000 and seeds realistic scenario
   ```

2. **Establish ADB reverse port forwarding:**
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
   *What this does:* When the Android phone connects to `http://localhost:8000`, the connection is forwarded directly through the USB cable to port 8000 on your laptop!

3. **Install the `demoLan` flavor APK:**
   ```bash
   adb install -r web/android/app/build/outputs/apk/demoLan/debug/app-demoLan-debug.apk
   ```

4. **Launch the app:**
   The app connects cleanly to `http://localhost:8000` via the forwarded port, completely isolated from venue network issues.

---

## Method 2: Same Wi-Fi Local Network Demo

If a wireless demo is required where the collector walks around with the phone:

1. **Find your laptop's local IP address:**
   - **Windows:** `ipconfig` (look for *IPv4 Address*, e.g., `192.168.1.45`)
   - **macOS/Linux:** `ifconfig` or `ip a`

2. **Start the backend listening on all interfaces:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Ensure laptop firewall allows port 8000 inbound:**
   ```powershell
   # Windows PowerShell (Run as Administrator if needed):
   New-NetFirewallRule -DisplayName "Kabadiwala Demo 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

4. **Configure the app:**
   In the `demoLan` debug build, the API endpoint defaults to the configured LAN host. You can also specify `VITE_API_URL=http://<YOUR_LAPTOP_IP>:8000` before running `make android-sync`.

---

## Method 3: Standalone Zero-Internet Demo (100% Offline)

If Wi-Fi fails completely or is blocked by institutional captive portals:

1. **Install the Standalone APK:**
   ```bash
   adb install -r web/android/app/build/outputs/apk/demoStandalone/release/app-demoStandalone-universal-release-unsigned.apk
   ```

2. **Enable Airplane Mode on the phone:**
   Toggle phone Airplane Mode to demonstrate to the jury that **zero network connectivity is required**.

3. **Open Kabadiwala Connect:**
   - Notice the discreet *"Standalone demo"* badge in the header.
   - Login using demo personas with default OTP `123456`.
   - Add items to the scrap basket, calculate estimates, receive simulated buyer quotes, and complete cash handover.
   - All transactions persist locally in IndexedDB!

---

## Hosted Cloud Backend Pre-Demo Warm-Up

If demonstrating against a cloud backend hosted on free or low-cost serverless tiers (Render, Railway, Fly.io, HuggingFace):

Run the warm-up script 5 minutes before your time slot:
```bash
bash scripts/android/warmup.sh https://api.kabadiwalaconnect.in
```

This pings the health check, wakes the container from cold sleep, and pre-caches material rate data.
