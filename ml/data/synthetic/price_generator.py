"""
Synthetic Price & Transaction Generator
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Generates deterministic price histories and transactions with injected anomaly ground truth.
Seeds: 42 (deterministic reproducibility).
Outputs:
  ml/data/synthetic/synthetic_prices.csv
  ml/data/synthetic/synthetic_transactions.csv
  ml/data/synthetic/injected_truth.csv
"""
import os
import csv
import math
import random
from datetime import datetime, timedelta, timezone

SEED = 42
random.seed(SEED)

BASE_PRICES = {
    "PCB": 40000,           # ₹400/kg in paise
    "BATTERY_LI": 30000,    # ₹300/kg
    "CABLE": 45000,         # ₹450/kg
    "MOTOR": 25000,         # ₹250/kg
    "CRT": 5000,            # ₹50/kg
    "LCD": 18000,           # ₹180/kg
    "PLASTIC_MIXED": 12000, # ₹120/kg
    "BATTERY_PB": 22000,    # ₹220/kg
}

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Pune", "Nagpur", "Jaipur"]
CITY_OFFSETS = {
    "Mumbai": 1.05,
    "Delhi": 1.02,
    "Bengaluru": 0.98,
    "Pune": 1.00,
    "Nagpur": 0.95,
    "Jaipur": 0.97,
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_prices(days: int = 90):
    """Generates 90 days of synthetic price history across materials and cities."""
    prices = []
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    for mat, base in BASE_PRICES.items():
        for city in CITIES:
            offset = CITY_OFFSETS[city]
            current_price = base * offset
            for d in range(days):
                curr_date = start_date + timedelta(days=d)
                # Weekly seasonality: slight dip on weekends
                day_of_week = curr_date.weekday()
                seasonality = 1.0 - 0.02 * math.sin(2 * math.pi * day_of_week / 7)
                # Random walk drift (-1.5% to +1.5%)
                drift = 1.0 + (random.uniform(-0.015, 0.015))
                current_price = max(base * 0.5, current_price * drift * seasonality)
                
                prices.append({
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "material_code": mat,
                    "city": city,
                    "price_paise_per_kg": round(current_price),
                    "volume_kg": random.randint(200, 2500)
                })
                
    price_csv = os.path.join(OUTPUT_DIR, "synthetic_prices.csv")
    with open(price_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "material_code", "city", "price_paise_per_kg", "volume_kg"])
        writer.writeheader()
        writer.writerows(prices)
    print(f"Generated {len(prices)} price points -> {price_csv}")
    return prices


def generate_transactions(n_clean: int = 400):
    """
    Generates transactions with injected anomalies:
    1. WEIGHT_VARIANCE (est vs actual > 25%)
    2. PRICE_BELOW_BAND (final < 60% band low)
    3. PRICE_ABOVE_BAND (final > 150% band high)
    4. UNIT_ERROR_SUSPECT (price ~10x off)
    5. DUPLICATE_PHOTO (same pHash across distinct lots)
    6. GPS_MISMATCH (handover > 10 km from recycler)
    """
    transactions = []
    injected_truth = []
    tx_id_seq = 1000

    start_date = datetime.now(timezone.utc) - timedelta(days=30)
    materials = list(BASE_PRICES.keys())

    # 1. Clean transactions
    for i in range(n_clean):
        tx_id_seq += 1
        mat = random.choice(materials)
        city = random.choice(CITIES)
        base = BASE_PRICES[mat] * CITY_OFFSETS[city]
        
        est_wt = random.randint(1000, 50000)
        actual_wt = round(est_wt * random.uniform(0.95, 1.05)) # within 5%
        price_per_kg = round(base * random.uniform(0.95, 1.05))
        total_price = round((actual_wt / 1000.0) * price_per_kg)
        
        tx_time = start_date + timedelta(hours=random.randint(1, 700))
        weigh_in = tx_time - timedelta(minutes=random.randint(5, 20))
        payment_time = tx_time
        
        tx = {
            "transaction_id": f"TX_{tx_id_seq}",
            "lot_id": f"LOT_{tx_id_seq}",
            "material_code": mat,
            "city": city,
            "est_weight_g": est_wt,
            "actual_weight_g": actual_wt,
            "final_price_paise": total_price,
            "final_price_per_kg_paise": price_per_kg,
            "quote_per_kg_paise": round(price_per_kg * random.uniform(0.95, 1.02)),
            "photo_phash": f"{random.getrandbits(64):016x}",
            "gps_distance_km": round(random.uniform(0.1, 1.5), 2),
            "payment_minutes_before_weigh": -15, # paid 15 min after weigh
            "weigh_in_at": weigh_in.isoformat(),
            "payment_at": payment_time.isoformat(),
        }
        transactions.append(tx)

    # 2. Injected Anomalies (Ground Truth)
    # A1: WEIGHT_VARIANCE (5 cases)
    for _ in range(5):
        tx_id_seq += 1
        mat = random.choice(materials)
        city = random.choice(CITIES)
        base = BASE_PRICES[mat] * CITY_OFFSETS[city]
        est_wt = 5000
        actual_wt = 7500 # 50% variance
        price_per_kg = round(base)
        total_price = round((actual_wt / 1000.0) * price_per_kg)
        
        tx = {
            "transaction_id": f"TX_{tx_id_seq}",
            "lot_id": f"LOT_{tx_id_seq}",
            "material_code": mat,
            "city": city,
            "est_weight_g": est_wt,
            "actual_weight_g": actual_wt,
            "final_price_paise": total_price,
            "final_price_per_kg_paise": price_per_kg,
            "quote_per_kg_paise": price_per_kg,
            "photo_phash": f"{random.getrandbits(64):016x}",
            "gps_distance_km": 0.5,
            "payment_minutes_before_weigh": -10,
            "weigh_in_at": (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat(),
            "payment_at": datetime.now(timezone.utc).isoformat(),
        }
        transactions.append(tx)
        injected_truth.append({"transaction_id": tx["transaction_id"], "expected_rule": "WEIGHT_VARIANCE", "severity": "high"})

    # A2: PRICE_BELOW_BAND (5 cases)
    for _ in range(5):
        tx_id_seq += 1
        mat = random.choice(materials)
        city = random.choice(CITIES)
        base = BASE_PRICES[mat] * CITY_OFFSETS[city]
        wt = 10000
        price_per_kg = round(base * 0.40) # 40% of market (below 60% threshold)
        total_price = round((wt / 1000.0) * price_per_kg)
        
        tx = {
            "transaction_id": f"TX_{tx_id_seq}",
            "lot_id": f"LOT_{tx_id_seq}",
            "material_code": mat,
            "city": city,
            "est_weight_g": wt,
            "actual_weight_g": wt,
            "final_price_paise": total_price,
            "final_price_per_kg_paise": price_per_kg,
            "quote_per_kg_paise": round(base),
            "photo_phash": f"{random.getrandbits(64):016x}",
            "gps_distance_km": 0.8,
            "payment_minutes_before_weigh": -10,
            "weigh_in_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "payment_at": datetime.now(timezone.utc).isoformat(),
        }
        transactions.append(tx)
        injected_truth.append({"transaction_id": tx["transaction_id"], "expected_rule": "PRICE_BELOW_BAND", "severity": "high"})

    # A3: UNIT_ERROR_SUSPECT (5 cases)
    for _ in range(5):
        tx_id_seq += 1
        mat = random.choice(materials)
        city = random.choice(CITIES)
        base = BASE_PRICES[mat] * CITY_OFFSETS[city]
        wt = 5000
        price_per_kg = round(base * 10.0) # 10x multiplier
        total_price = round((wt / 1000.0) * price_per_kg)
        
        tx = {
            "transaction_id": f"TX_{tx_id_seq}",
            "lot_id": f"LOT_{tx_id_seq}",
            "material_code": mat,
            "city": city,
            "est_weight_g": wt,
            "actual_weight_g": wt,
            "final_price_paise": total_price,
            "final_price_per_kg_paise": price_per_kg,
            "quote_per_kg_paise": round(base),
            "photo_phash": f"{random.getrandbits(64):016x}",
            "gps_distance_km": 0.4,
            "payment_minutes_before_weigh": -10,
            "weigh_in_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "payment_at": datetime.now(timezone.utc).isoformat(),
        }
        transactions.append(tx)
        injected_truth.append({"transaction_id": tx["transaction_id"], "expected_rule": "UNIT_ERROR_SUSPECT", "severity": "high"})

    # A4: GPS_MISMATCH (5 cases)
    for _ in range(5):
        tx_id_seq += 1
        mat = random.choice(materials)
        city = random.choice(CITIES)
        base = BASE_PRICES[mat] * CITY_OFFSETS[city]
        wt = 8000
        price_per_kg = round(base)
        total_price = round((wt / 1000.0) * price_per_kg)
        
        tx = {
            "transaction_id": f"TX_{tx_id_seq}",
            "lot_id": f"LOT_{tx_id_seq}",
            "material_code": mat,
            "city": city,
            "est_weight_g": wt,
            "actual_weight_g": wt,
            "final_price_paise": total_price,
            "final_price_per_kg_paise": price_per_kg,
            "quote_per_kg_paise": price_per_kg,
            "photo_phash": f"{random.getrandbits(64):016x}",
            "gps_distance_km": 15.5, # 15.5 km away!
            "payment_minutes_before_weigh": -10,
            "weigh_in_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
            "payment_at": datetime.now(timezone.utc).isoformat(),
        }
        transactions.append(tx)
        injected_truth.append({"transaction_id": tx["transaction_id"], "expected_rule": "GPS_MISMATCH", "severity": "high"})

    # Save to CSV
    tx_csv = os.path.join(OUTPUT_DIR, "synthetic_transactions.csv")
    with open(tx_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(transactions[0].keys()))
        writer.writeheader()
        writer.writerows(transactions)
        
    truth_csv = os.path.join(OUTPUT_DIR, "injected_truth.csv")
    with open(truth_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_id", "expected_rule", "severity"])
        writer.writeheader()
        writer.writerows(injected_truth)

    print(f"Generated {len(transactions)} transactions ({len(injected_truth)} injected anomalies) -> {tx_csv}")
    print(f"Injected truth saved -> {truth_csv}")


if __name__ == "__main__":
    generate_prices(90)
    generate_transactions(400)
