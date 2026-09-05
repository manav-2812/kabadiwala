"""
Evaluate Injected Anomaly Rules
Kabadiwala Connect -- SIH 2026 (PS SIH26229)

Evaluates rule detection precision, recall, and false positive rate against injected ground truth.
Outputs results to ml/artifacts/metrics/anomaly.json
"""
import os
import csv
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTH_DIR = os.path.join(BASE_DIR, "data", "synthetic")
METRICS_DIR = os.path.join(BASE_DIR, "artifacts", "metrics")
os.makedirs(METRICS_DIR, exist_ok=True)


def evaluate():
    tx_file = os.path.join(SYNTH_DIR, "synthetic_transactions.csv")
    truth_file = os.path.join(SYNTH_DIR, "injected_truth.csv")
    
    if not os.path.exists(tx_file) or not os.path.exists(truth_file):
        print("Synthetic files missing. Run price_generator.py first.")
        return

    # Load ground truth
    ground_truth = {}
    with open(truth_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ground_truth[row["transaction_id"]] = row["expected_rule"]

    # Evaluate rules on each transaction
    detected = defaultdict(list)
    total_clean = 0
    false_positives = 0

    with open(tx_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tx_id = row["transaction_id"]
            is_anomaly = tx_id in ground_truth
            if not is_anomaly:
                total_clean += 1

            est_wt = float(row["est_weight_g"])
            actual_wt = float(row["actual_weight_g"])
            price_per_kg = float(row["final_price_per_kg_paise"])
            quote_per_kg = float(row["quote_per_kg_paise"])
            dist_km = float(row["gps_distance_km"])

            flags = []

            # Rule 1: WEIGHT_VARIANCE (> 25% high)
            variance_pct = abs(actual_wt - est_wt) / max(est_wt, 1) * 100.0
            if variance_pct > 25.0:
                flags.append("WEIGHT_VARIANCE")

            # Rule 2: PRICE_BELOW_BAND (< 60% of quote / market)
            if quote_per_kg > 0 and (price_per_kg / quote_per_kg) < 0.60:
                flags.append("PRICE_BELOW_BAND")

            # Rule 3: UNIT_ERROR_SUSPECT (~10x multiplier)
            if quote_per_kg > 0:
                ratio = price_per_kg / quote_per_kg
                if ratio >= 8.0:
                    flags.append("UNIT_ERROR_SUSPECT")

            # Rule 4: GPS_MISMATCH (> 10 km)
            if dist_km > 10.0:
                flags.append("GPS_MISMATCH")

            for fl in flags:
                detected[fl].append(tx_id)

            if not is_anomaly and len(flags) > 0:
                false_positives += 1

    # Compute metrics per rule
    results = {}
    rules = ["WEIGHT_VARIANCE", "PRICE_BELOW_BAND", "UNIT_ERROR_SUSPECT", "GPS_MISMATCH"]
    
    for r in rules:
        expected_ids = [k for k, v in ground_truth.items() if v == r]
        detected_ids = detected[r]
        
        tp = len(set(detected_ids).intersection(set(expected_ids)))
        fn = len(expected_ids) - tp
        fp = len(detected_ids) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        
        results[r] = {
            "ground_truth_count": len(expected_ids),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
        }

    fpr = false_positives / total_clean if total_clean > 0 else 0.0
    
    summary = {
        "dataset": "synthetic_injected_truth",
        "total_transactions": total_clean + len(ground_truth),
        "clean_transactions": total_clean,
        "injected_anomalies": len(ground_truth),
        "false_positive_rate": round(fpr, 4),
        "fpr_target_met": fpr < 0.03,  # Target: < 3% FPR
        "rules": results
    }

    out_path = os.path.join(METRICS_DIR, "anomaly.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Anomaly evaluation completed:")
    print(f"  FPR on clean data: {fpr*100:.2f}% (Target: < 3%)")
    for r, m in results.items():
        print(f"  [{r}] Recall: {m['recall']*100:.1f}%, Precision: {m['precision']*100:.1f}%")
    print(f"Metrics written -> {out_path}")


if __name__ == "__main__":
    evaluate()
