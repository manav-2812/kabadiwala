# pyright: reportMissingImports=false
"""
CLI Utility to archive/retire synthetic users as real users are onboarded.
Usage:
    python scripts/retire_synthetic.py KC-C-0001 KC-C-0002 ...
Or:
    make retire-synthetic USERS="KC-C-0001,KC-C-0002"
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from app.services.importer import retire_synthetic_users  # type: ignore
except ImportError:
    from backend.app.services.importer import retire_synthetic_users  # type: ignore

async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/retire_synthetic.py <user_id_or_collector_code> ...")
        sys.exit(1)

    targets = []
    for arg in sys.argv[1:]:
        targets.extend([t.strip() for t in arg.split(",") if t.strip()])

    print(f"[INFO] Retiring synthetic users: {targets}...")
    res = await retire_synthetic_users(targets)
    print("=" * 60)
    print(f"Status: {res.get('status')}")
    print(f"Retired Users Count: {res.get('retired_count')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
