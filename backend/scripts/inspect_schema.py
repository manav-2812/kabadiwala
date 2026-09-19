import sqlite3

conn = sqlite3.connect("kabadiwala.db")
cur = conn.cursor()
new_tables = {
    'datasets', 'matching_weights', 'ml_models', 'dataset_versions',
    'ingest_quarantine', 'material_subcategories', 'ml_predictions',
    'training_labels', 'recycler_rates', 'anomaly_flags', 'alembic_version'
}

tables = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
for name, sql in tables:
    if name not in new_tables and not name.startswith("sqlite_"):
        print(f"# Table: {name}")
