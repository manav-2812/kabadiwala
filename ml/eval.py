#!/usr/bin/env python3
"""
Kabadiwala Connect -- ML Evaluation Reporter
SIH 2026 (PS SIH26229)

Reads real metrics from ml/artifacts/metrics/classify.json (written by
ml/classify/eval.py after a real model is trained).

If no real model exists, reports honestly that no real evaluation has been
run -- it does NOT invent numbers.
"""

import sys
import os
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

METRICS_FILE = os.path.join(
    os.path.dirname(__file__), "artifacts", "metrics", "classify.json"
)
REAL_EVAL = os.path.join(os.path.dirname(__file__), "classify", "eval.py")


def main():
    # If real eval pipeline exists, delegate to it
    if os.path.exists(REAL_EVAL):
        import subprocess
        result = subprocess.run(
            [sys.executable, REAL_EVAL] + sys.argv[1:],
            cwd=os.path.dirname(__file__)
        )
        sys.exit(result.returncode)

    # Otherwise, read from artifacts if they exist
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        demo_only = metrics.get("demo_only", True)
        print("=" * 65)
        print("[KABADIWALA CONNECT] CLASSIFIER EVALUATION RESULTS")
        if demo_only:
            print("[STATUS] demo_only=true -- metrics below are from demo/synthetic data")
            print("         These numbers are NOT from a real field-verified dataset.")
        else:
            print("[STATUS] demo_only=false -- trained on real verified data")
        print("=" * 65)
        print(f"  Model:        {metrics.get('model_name', 'unknown')}")
        print(f"  Dataset:      {metrics.get('dataset', 'unknown')}")
        print(f"  Eval date:    {metrics.get('eval_date', 'unknown')}")
        print(f"  Top-1 Acc:    {metrics.get('top1_accuracy', 0) * 100:.1f}%")
        print(f"  Macro F1:     {metrics.get('macro_f1', 0):.3f}")
        if "model_size" in metrics:
            sz = metrics["model_size"]
            print(f"  INT8 size:    {sz.get('int8_quantized_size_mb', '?')} MB "
                  f"(budget <= 4.0 MB: {'PASS' if sz.get('budget_compliance') else 'FAIL'})")
        print("=" * 65)
        return metrics

    # No metrics at all
    print("=" * 65)
    print("[KABADIWALA CONNECT] ML EVALUATION")
    print("=" * 65)
    print("")
    print("[INFO] No classifier metrics found.")
    print(f"  Expected: {METRICS_FILE}")
    print("")
    print("  No real model has been trained yet.")
    print("  The classifier runs in demo_only=true mode (rule-based fallback).")
    print("")
    print("  To generate real metrics:")
    print("    1. Collect >= 60 verified images per class in ml/data/images/<class>/")
    print("    2. Run: python ml/classify/train.py")
    print("    3. Run: python ml/classify/eval.py")
    print("=" * 65)
    return None


if __name__ == "__main__":
    main()
