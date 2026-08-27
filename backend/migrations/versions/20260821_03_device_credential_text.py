"""Expand encrypted device credential columns to text.

Revision ID: 20260821_03
Revises: 20260817_02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260821_03"
down_revision: str | None = "20260817_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CREDENTIAL_COLUMNS = (
    ("serverlist", "server_pass"),
    ("ipcamlist", "admin_pass"),
    ("ipcamlist", "user_pass"),
)


def _alter(table_name: str, column_name: str, target_type: sa.types.TypeEngine) -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column(
                column_name,
                existing_type=sa.String(length=255),
                type_=target_type,
            )
    else:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.String(length=255),
            type_=target_type,
        )


def upgrade() -> None:
    for table_name, column_name in CREDENTIAL_COLUMNS:
        _alter(table_name, column_name, sa.Text())


def downgrade() -> None:
    for table_name, column_name in CREDENTIAL_COLUMNS:
        _alter(table_name, column_name, sa.String(length=255))
