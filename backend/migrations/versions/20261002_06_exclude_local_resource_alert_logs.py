"""Remove page-derived CPU and memory samples from persistent alert history.

Revision ID: 20261002_06
Revises: 20261002_05
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261002_06"
down_revision: str | None = "20261002_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # These rows are transient page observations, not source-system incidents.
    # Event keys are used instead of translated message text so cleanup remains
    # deterministic across display wording changes.
    op.get_bind().execute(
        sa.text(
            """
            DELETE FROM monitoring_alert_log
            WHERE source = 'workhour'
              AND (event_key LIKE :cpu_pattern OR event_key LIKE :memory_pattern)
            """
        ),
        {
            "cpu_pattern": "workhour:branch-metric:%:cpu",
            "memory_pattern": "workhour:branch-metric:%:memory",
        },
    )


def downgrade() -> None:
    # Deleted transient observations cannot be reconstructed reliably.
    pass
