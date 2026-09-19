import sqlite3

conn = sqlite3.connect("kabadiwala.db")
cur = conn.cursor()

new_tables = {
    'datasets', 'matching_weights', 'ml_models', 'dataset_versions',
    'ingest_quarantine', 'material_subcategories', 'ml_predictions',
    'training_labels', 'recycler_rates', 'anomaly_flags', 'alembic_version'
}

tables = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()

with open("alembic/versions/0001_baseline.py", "w", encoding="utf-8") as f:
    f.write('"""baseline schema\n\nRevision ID: 0001_baseline\nRevises: \nCreate Date: 2026-09-19 14:00:00\n"""\n')
    f.write('from alembic import op\nimport sqlalchemy as sa\n\n')
    f.write("revision = '0001_baseline'\ndown_revision = None\nbranch_labels = None\ndepends_on = None\n\n")
    f.write("def upgrade() -> None:\n")
    
    # We execute table creation using op.execute with the sqlite schema
    table_sqls = []
    table_names = []
    for name, sql in tables:
        if name not in new_tables and not name.startswith("sqlite_") and sql:
            table_sqls.append((name, sql))
            table_names.append(name)
    
    for name, sql in table_sqls:
        # Clean sql to ensure safe string literal
        cleaned_sql = sql.replace('"', '\\"')
        f.write(f'    op.execute("""{sql}""")\n')
    
    f.write("\ndef downgrade() -> None:\n")
    for name in reversed(table_names):
        f.write(f'    op.drop_table("{name}")\n')

print(f"Generated 0001_baseline.py with {len(table_sqls)} tables")
