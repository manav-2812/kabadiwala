import re

cols_to_remove = [
    'service_area_geojson', 'question_mr', 'answer_mr', 'sub_category_id', 'source_type',
    'phash', 'quality_score', 'name_mr', 'hazard_note_mr', 'safety_tip_mr',
    'title_mr', 'body_mr', 'sms_mr', 'gateway_ref', 'bank_ref', 'retry_count', 'completed_at',
    'buying_price_paise', 'quoted_price_paise', 'recycler_id', 'aggregator_id', 'is_synthetic',
    'payment_method', 'payment_status', 'handover_ref', 'collection_lat', 'collection_lng',
    'handover_lat', 'handover_lng', 'recycler_confirmed_at', 'recycler_confirmed_by',
    'cash_confirmed_by_collector', 'collector_confirm_lat', 'collector_confirm_lng',
    'cash_confirmed_by_buyer', 'buyer_confirm_lat', 'buyer_confirm_lng', 'due_status',
    'source'
]

with open("alembic/versions/0001_baseline.py", "r", encoding="utf-8") as f:
    content = f.read()

# For each column in cols_to_remove, if it appears in a column definition, remove it
for col in cols_to_remove:
    # Match patterns like:
    # col TYPE ..., or , col TYPE
    # e.g., \s*col\s+[A-Z0-9_()]+(\s+NOT\s+NULL)?,?
    pattern = rf',?\s*\b{col}\b\s+[A-Za-z0-9_()]+(\s+NOT\s+NULL)?(\s+DEFAULT\s+[^\s,)]+)?,?'
    # Be careful not to remove FOREIGN KEY or PRIMARY KEY or column in another table where it is legitimate baseline
    # Only in CREATE TABLE aggregators, transactions, etc.
    content = re.sub(rf',\s*{col}\s+[A-Z0-9_()]+', '', content, flags=re.IGNORECASE)
    content = re.sub(rf'\b{col}\s+[A-Z0-9_()]+,\s*', '', content, flags=re.IGNORECASE)

# Clean up any leftover syntax errors like ",\s*\)"
content = re.sub(r',\s*\)', '\n)', content)

with open("alembic/versions/0001_baseline.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Cleaned 0001_baseline.py")
