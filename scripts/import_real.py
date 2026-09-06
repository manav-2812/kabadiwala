# pyright: reportMissingImports=false
"""
CLI Utility to import real field data into Kabadiwala Connect.
Usage:
    python scripts/import_real.py <path_to_csv_file> [dataset_type]
Or:
    make import-real FILE=templates/collectors.csv
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from app.services.importer import import_real_data  # type: ignore
except ImportError:
    from backend.app.services.importer import import_real_data  # type: ignore

async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_real.py <path_to_csv> [dataset_type]")
        sys.exit(1)

    file_path = sys.argv[1]
    dataset_type = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"[INFO] Importing real field data from {file_path}...")
    res = await import_real_data(file_path, dataset_type)
    print("=" * 60)
    print(f"Status: {res.get('status')}")
    print(f"Dataset: {res.get('dataset_type')}")
    print(f"Imported Rows: {res.get('imported_count')}")
    print(f"Quarantined Rows: {res.get('quarantined_count')}")
    if res.get('quarantine_reasons'):
        print("Quarantine Reasons:")
        for r in res.get('quarantine_reasons'):
            print(f"  - {r}")
    print(f"Current Synthetic Share: {res.get('current_synthetic_share')}")
    print(f"Version Tag: {res.get('version_tag')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
