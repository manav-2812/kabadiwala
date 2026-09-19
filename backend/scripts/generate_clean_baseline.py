import sys
from sqlalchemy import MetaData, Table, Column, PrimaryKeyConstraint
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite

from app.models.all_models import Base

new_tables = {
    'datasets', 'matching_weights', 'ml_models', 'dataset_versions',
    'ingest_quarantine', 'material_subcategories', 'ml_predictions',
    'training_labels', 'recycler_rates', 'anomaly_flags'
}

cols_added = {
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

baseline_meta = MetaData()
sqlite_dialect = sqlite.dialect()

for table in list(Base.metadata.sorted_tables):
    if table.name in new_tables:
        continue
    
    remove_for_this = cols_added.get(table.name, set())
    cols = []
    for col in table.columns:
        if col.name not in remove_for_this:
            cols.append(col._copy())
    
    constraints = []
    for c in list(table.constraints):
        if isinstance(c, PrimaryKeyConstraint):
            continue
        c_cols = {col.name for col in getattr(c, 'columns', [])}
        if not (c_cols & remove_for_this):
            keep_fk = True
            for fk in getattr(c, 'elements', []):
                target_table = fk.column.table.name if hasattr(fk, 'column') and hasattr(fk.column, 'table') else ''
                if target_table in new_tables:
                    keep_fk = False
            if keep_fk:
                try:
                    constraints.append(c._copy())
                except Exception:
                    pass
    
    Table(table.name, baseline_meta, *cols, *constraints)

with open("alembic/versions/0001_baseline.py", "w", encoding="utf-8") as f:
    f.write('"""baseline schema\n\nRevision ID: 0001_baseline\nRevises: \nCreate Date: 2026-09-19 14:00:00\n"""\n')
    f.write('from alembic import op\nimport sqlalchemy as sa\n\n')
    f.write("revision = '0001_baseline'\ndown_revision = None\nbranch_labels = None\ndepends_on = None\n\n")
    f.write("def upgrade() -> None:\n")
    
    for table in baseline_meta.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=sqlite_dialect)).strip()
        f.write(f'    op.execute("""{ddl}""")\n')
    
    f.write("\ndef downgrade() -> None:\n")
    for table in reversed(baseline_meta.sorted_tables):
        f.write(f'    op.drop_table("{table.name}")\n')

print(f"Generated clean 0001_baseline.py with {len(baseline_meta.sorted_tables)} tables")
