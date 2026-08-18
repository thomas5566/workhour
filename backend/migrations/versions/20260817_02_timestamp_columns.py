"""Convert audit date columns to timezone-aware timestamps.

Revision ID: 20260817_02
Revises: 20260817_01
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260817_02"
down_revision: str | None = "20260817_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUDITED_TABLES = (
    "department",
    "task",
    "user",
    "expentask",
    "workhour",
    "expenditure",
    "daysoff",
)
AUDIT_COLUMNS = ("created_at", "updated_at")


def _column_types(table_name: str) -> dict[str, sa.types.TypeEngine]:
    inspector = sa.inspect(op.get_bind())
    return {
        column["name"]: column["type"]
        for column in inspector.get_columns(table_name)
    }


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    for table_name in AUDITED_TABLES:
        column_types = _column_types(table_name)
        for column_name in AUDIT_COLUMNS:
            current_type = column_types.get(column_name)
            if current_type is None or isinstance(current_type, sa.DateTime):
                continue
            if dialect == "sqlite":
                with op.batch_alter_table(table_name) as batch_op:
                    batch_op.alter_column(
                        column_name,
                        existing_type=sa.Date(),
                        type_=sa.DateTime(timezone=True),
                    )
            else:
                op.alter_column(
                    table_name,
                    column_name,
                    existing_type=sa.Date(),
                    type_=sa.DateTime(timezone=True),
                    postgresql_using=f"{column_name}::timestamp with time zone",
                )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    for table_name in AUDITED_TABLES:
        column_types = _column_types(table_name)
        for column_name in AUDIT_COLUMNS:
            current_type = column_types.get(column_name)
            if current_type is None or not isinstance(current_type, sa.DateTime):
                continue
            if dialect == "sqlite":
                with op.batch_alter_table(table_name) as batch_op:
                    batch_op.alter_column(
                        column_name,
                        existing_type=sa.DateTime(timezone=True),
                        type_=sa.Date(),
                    )
            else:
                op.alter_column(
                    table_name,
                    column_name,
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.Date(),
                    postgresql_using=f"{column_name}::date",
                )
