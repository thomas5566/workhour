"""Add persistent High-or-higher monitoring alert history.

Revision ID: 20261002_05
Revises: 20260908_04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261002_05"
down_revision: str | None = "20260908_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "monitoring_alert_log",
        sa.Column("event_key", sa.String(512), nullable=False),
        sa.Column("event_id", sa.String(255), nullable=False),
        sa.Column("host_name", sa.String(255), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("severity_label", sa.String(32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    for column in (
        "id", "event_key", "event_id", "host_name", "severity",
        "occurred_at", "resolved_at", "source",
    ):
        op.create_index(
            f"ix_monitoring_alert_log_{column}", "monitoring_alert_log", [column]
        )


def downgrade() -> None:
    op.drop_table("monitoring_alert_log")
