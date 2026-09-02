"""seed_realism_fields_and_consent

Revision ID: 0004_seed_realism_fields
Revises: 0003_ai_ml_tables
Create Date: 2026-09-19

Adds:
- users.display_name_local, users.is_synthetic
- collectors.collector_code, collectors.operating_area_name, collectors.gps_consent, collectors.is_synthetic
- lot_photos.is_placeholder
- lots.seed_batch_id, lots.is_synthetic
- transactions.seed_batch_id, transactions.is_synthetic
- payments.seed_batch_id, payments.is_synthetic
- anomaly_flags.seed_batch_id, anomaly_flags.is_synthetic
- pickup_agents.hub_id, pickup_agents.is_synthetic
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0004_seed_realism_fields"
down_revision: Union[str, None] = "0003_ai_ml_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    def add_col_if_missing(table_name: str, column: sa.Column):
        existing_cols = [c["name"] for c in insp.get_columns(table_name)]
        if column.name not in existing_cols:
            with op.batch_alter_table(table_name, recreate="never") as batch_op:
                batch_op.add_column(column)

    add_col_if_missing("users", sa.Column("display_name_local", sa.String(100), nullable=True))
    add_col_if_missing("users", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("collectors", sa.Column("collector_code", sa.String(20), nullable=True))
    add_col_if_missing("collectors", sa.Column("operating_area_name", sa.String(100), nullable=True, server_default="Hadapsar"))
    add_col_if_missing("collectors", sa.Column("gps_consent", sa.Boolean(), nullable=False, server_default=sa.true()))
    add_col_if_missing("collectors", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("lot_photos", sa.Column("is_placeholder", sa.Boolean(), nullable=False, server_default=sa.false()))

    add_col_if_missing("lots", sa.Column("seed_batch_id", sa.String(36), nullable=True))
    add_col_if_missing("lots", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("transactions", sa.Column("seed_batch_id", sa.String(36), nullable=True))
    add_col_if_missing("transactions", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("payments", sa.Column("seed_batch_id", sa.String(36), nullable=True))
    add_col_if_missing("payments", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("anomaly_flags", sa.Column("seed_batch_id", sa.String(36), nullable=True))
    add_col_if_missing("anomaly_flags", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))

    add_col_if_missing("pickup_agents", sa.Column("hub_id", sa.String(36), nullable=True))
    add_col_if_missing("pickup_agents", sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    def drop_col_if_present(table_name: str, col_name: str):
        existing_cols = [c["name"] for c in insp.get_columns(table_name)]
        if col_name in existing_cols:
            with op.batch_alter_table(table_name, recreate="never") as batch_op:
                batch_op.drop_column(col_name)

    drop_col_if_present("pickup_agents", "is_synthetic")
    drop_col_if_present("pickup_agents", "hub_id")

    drop_col_if_present("anomaly_flags", "is_synthetic")
    drop_col_if_present("anomaly_flags", "seed_batch_id")

    drop_col_if_present("payments", "is_synthetic")
    drop_col_if_present("payments", "seed_batch_id")

    drop_col_if_present("transactions", "seed_batch_id")

    drop_col_if_present("lots", "seed_batch_id")

    drop_col_if_present("lot_photos", "is_placeholder")

    drop_col_if_present("collectors", "is_synthetic")
    drop_col_if_present("collectors", "gps_consent")
    drop_col_if_present("collectors", "operating_area_name")
    drop_col_if_present("collectors", "collector_code")

    drop_col_if_present("users", "is_synthetic")
    drop_col_if_present("users", "display_name_local")
