import sqlite3
import re
import os

new_tables = {
    'datasets', 'matching_weights', 'ml_models', 'dataset_versions',
    'ingest_quarantine', 'material_subcategories', 'ml_predictions',
    'training_labels', 'recycler_rates', 'anomaly_flags', 'alembic_version'
}

cols_to_remove = {
    'aggregators': {'service_area_geojson'},
    'faqs': {'question_mr', 'answer_mr'},
    'lot_items': {'sub_category_id', 'source_type'},
    'lot_photos': {'phash', 'quality_score'},
    'lots': {'source', 'is_synthetic'},
    'materials': {'name_mr', 'hazard_note_mr', 'safety_tip_mr', 'source', 'is_synthetic'},
    'notification_templates': {'title_mr', 'body_mr', 'sms_mr'},
    'notifications': {'title_mr', 'body_mr'},
    'payments': {'gateway_ref', 'bank_ref', 'retry_count', 'completed_at'},
    'price_history': {'sub_category_id', 'unit', 'buying_price_paise', 'quoted_price_paise', 'recycler_id', 'aggregator_id', 'is_synthetic'},
    'recyclers': {'service_area_geojson'},
    'transactions': {
        'payment_method', 'payment_status', 'handover_ref', 'collection_lat', 'collection_lng',
        'handover_lat', 'handover_lng', 'recycler_confirmed_at', 'recycler_confirmed_by',
        'cash_confirmed_by_collector', 'collector_confirm_lat', 'collector_confirm_lng',
        'cash_confirmed_by_buyer', 'buyer_confirm_lat', 'buyer_confirm_lng', 'due_status',
        'source', 'is_synthetic'
    }
}

conn = sqlite3.connect("kabadiwala.db")
cur = conn.cursor()

tables = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()

baseline_sqls = []
baseline_table_names = []

for name, sql in tables:
    if name in new_tables or name.startswith("sqlite_") or not sql:
        continue
    
    # If this table has added columns, strip them from the CREATE TABLE statement
    if name in cols_to_remove:
        remove_set = cols_to_remove[name]
        lines = sql.split('\n')
        kept_lines = []
        for line in lines:
            # Check if line defines one of the columns
            stripped = line.strip().strip(',')
            parts = stripped.split()
            if parts and parts[0] in remove_set:
                continue
            # Also remove unique constraints on added columns if any
            if any(f'UNIQUE ({col})' in line for col in remove_set):
                continue
            kept_lines.append(line)
        # Fix trailing comma on second to last line if needed
        clean_lines = []
        for i, l in enumerate(kept_lines):
            clean_lines.append(l)
        # Clean up any syntax error like comma before closing parenthesis
        cleaned_sql = '\n'.join(clean_lines)
        cleaned_sql = re.sub(r',\s*\)', '\n)', cleaned_sql)
        baseline_sqls.append((name, cleaned_sql))
    else:
        baseline_sqls.append((name, sql))
    
    baseline_table_names.append(name)

# Write 0001_baseline.py
with open("alembic/versions/0001_baseline.py", "w", encoding="utf-8") as f:
    f.write('"""baseline schema\n\nRevision ID: 0001_baseline\nRevises: \nCreate Date: 2026-09-19 14:00:00\n"""\n')
    f.write('from alembic import op\nimport sqlalchemy as sa\n\n')
    f.write("revision = '0001_baseline'\ndown_revision = None\nbranch_labels = None\ndepends_on = None\n\n")
    f.write("def upgrade() -> None:\n")
    for name, sql in baseline_sqls:
        # Use raw string or escaped string
        f.write(f'    op.execute("""{sql}""")\n')
    f.write("\ndef downgrade() -> None:\n")
    for name in reversed(baseline_table_names):
        f.write(f'    op.drop_table("{name}")\n')

print(f"Wrote 0001_baseline.py with {len(baseline_sqls)} tables")
