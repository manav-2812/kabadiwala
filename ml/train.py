#!/usr/bin/env python3
"""
Kabadiwala Connect -- ML Training Launcher
SIH 2026 (PS SIH26229)

This script trains the MobileNetV3-Small classifier on the verified image dataset.
It will NOT run (and honestly says so) until the real PyTorch training pipeline
in ml/classify/train.py is available and the data gates are met.

Data gate (Section 3.1): >= 60 verified images per class AND macro-F1 >= 0.80
on the frozen test set AND no class recall < 0.60 => demo_only = False.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REAL_TRAINER = os.path.join(os.path.dirname(__file__), "classify", "train.py")


def main():
    if os.path.exists(REAL_TRAINER):
        # Delegate to the real training pipeline
        import subprocess
        result = subprocess.run(
            [sys.executable, REAL_TRAINER] + sys.argv[1:],
            cwd=os.path.dirname(__file__)
        )
        sys.exit(result.returncode)
    else:
        print("=" * 65)
        print("[KABADIWALA CONNECT] ML TRAINING")
        print("=" * 65)
        print("")
        print("[WARNING] Real training pipeline not yet available.")
        print("  Expected: ml/classify/train.py")
        print("")
        print("  Until that file exists AND the data gates are met,")
        print("  the classifier runs in demo_only=true mode.")
        print("")
        print("  Data gate requirements (Section 3.1):")
        print("    - >= 60 verified images per class in ml/data/images/<class>/")
        print("    - Frozen-test macro-F1 >= 0.80")
        print("    - No class recall < 0.60")
        print("")
        print("  To contribute images: enable Data Collection Mode")
        print("  (long-press app version in Settings).")
        print("=" * 65)
        sys.exit(0)


if __name__ == "__main__":
    main()
