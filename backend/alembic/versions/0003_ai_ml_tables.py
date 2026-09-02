"""ai_ml_columns_and_drift_snapshots

Revision ID: 0003_ai_ml_tables
Revises: b55a21309efa
Create Date: 2026-09-19

Adds:
- lot_items.user_override
- lot_photos.training_consent, session_id, lighting
- ml_models.artifact_url, sha256, temperature, created_by
- ml_predictions.task, path  (model_id made nullable)
- training_labels.sub_class, training_consent
- anomaly_flags.code  (type kept as alias)
- drift_snapshots table (new)
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0003_ai_ml_tables"
down_revision: Union[str, None] = "b55a21309efa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # lot_items — add user_override
    # ---------------------------------------------------------------
    with op.batch_alter_table("lot_items") as batch_op:
        batch_op.add_column(
            sa.Column("user_override", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    # ---------------------------------------------------------------
    # lot_photos — add AI data collection columns
    # ---------------------------------------------------------------
    with op.batch_alter_table("lot_photos") as batch_op:
        batch_op.add_column(
            sa.Column("training_consent", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column("session_id", sa.String(36), nullable=True)
        )
        batch_op.add_column(
            sa.Column("lighting", sa.String(20), nullable=True)
        )

    # ---------------------------------------------------------------
    # ml_models — add artifact tracking columns
    # ---------------------------------------------------------------
    with op.batch_alter_table("ml_models") as batch_op:
        batch_op.add_column(
            sa.Column("artifact_url", sa.String(500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sha256", sa.String(64), nullable=True)
        )
        batch_op.add_column(
            sa.Column("temperature", sa.Numeric(6, 4), nullable=True)
        )
        batch_op.add_column(
            sa.Column("created_by", sa.String(36), nullable=True)
        )

    # ---------------------------------------------------------------
    # ml_predictions — add task, path; make model_id nullable
    # ---------------------------------------------------------------
    with op.batch_alter_table("ml_predictions") as batch_op:
        batch_op.add_column(
            sa.Column("task", sa.String(30), nullable=False, server_default="classify")
        )
        batch_op.add_column(
            sa.Column("path", sa.String(20), nullable=False, server_default="rules")
        )
        # SQLite batch_alter supports alter_column for nullable
        batch_op.alter_column("model_id", existing_type=sa.String(36), nullable=True)

    # ---------------------------------------------------------------
    # training_labels — add sub_class, training_consent
    # ---------------------------------------------------------------
    with op.batch_alter_table("training_labels") as batch_op:
        batch_op.add_column(
            sa.Column("sub_class", sa.String(50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("training_consent", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    # ---------------------------------------------------------------
    # anomaly_flags — add code column (type kept for compat)
    # ---------------------------------------------------------------
    with op.batch_alter_table("anomaly_flags") as batch_op:
        batch_op.add_column(
            # Backfill code from type using server_default; type stays as alias
            sa.Column("code", sa.String(50), nullable=False, server_default="UNKNOWN")
        )
        batch_op.alter_column("type", existing_type=sa.String(50), nullable=True)

    # ---------------------------------------------------------------
    # drift_snapshots — new table
    # ---------------------------------------------------------------
    op.create_table(
        "drift_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task", sa.String(30), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric_name", sa.String(50), nullable=False),
        sa.Column("value", sa.Numeric(8, 5), nullable=False),
        sa.Column("threshold", sa.Numeric(8, 5), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="ok"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Drop drift_snapshots
    op.drop_table("drift_snapshots")

    # Revert anomaly_flags
    with op.batch_alter_table("anomaly_flags") as batch_op:
        batch_op.drop_column("code")
        batch_op.alter_column("type", existing_type=sa.String(50), nullable=False)

    # Revert training_labels
    with op.batch_alter_table("training_labels") as batch_op:
        batch_op.drop_column("training_consent")
        batch_op.drop_column("sub_class")

    # Revert ml_predictions
    with op.batch_alter_table("ml_predictions") as batch_op:
        batch_op.drop_column("path")
        batch_op.drop_column("task")
        batch_op.alter_column("model_id", existing_type=sa.String(36), nullable=False)

    # Revert ml_models
    with op.batch_alter_table("ml_models") as batch_op:
        batch_op.drop_column("created_by")
        batch_op.drop_column("temperature")
        batch_op.drop_column("sha256")
        batch_op.drop_column("artifact_url")

    # Revert lot_photos
    with op.batch_alter_table("lot_photos") as batch_op:
        batch_op.drop_column("lighting")
        batch_op.drop_column("session_id")
        batch_op.drop_column("training_consent")

    # Revert lot_items
    with op.batch_alter_table("lot_items") as batch_op:
        batch_op.drop_column("user_override")
