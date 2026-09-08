"""Add JWT revocation and login throttling state to users.

Revision ID: 20260908_04
Revises: 20260821_03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260908_04"
down_revision: str | None = "20260821_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("auth_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "user",
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("user", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "locked_until")
    op.drop_column("user", "failed_login_attempts")
    op.drop_column("user", "auth_version")
