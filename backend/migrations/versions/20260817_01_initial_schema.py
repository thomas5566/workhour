"""Initial WorkHour schema baseline.

Revision ID: 20260817_01
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260817_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "branch_list",
        sa.Column("branch_name", sa.String(255)),
        sa.Column("branch_title", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_branch_list_id", "branch_list", ["id"])

    op.create_table(
        "department",
        sa.Column("department_name", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_department_department_name", "department", ["department_name"])
    op.create_index("ix_department_id", "department", ["id"])

    op.create_table(
        "expentask",
        sa.Column("expentask_name", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_expentask_expentask_name", "expentask", ["expentask_name"])
    op.create_index("ix_expentask_id", "expentask", ["id"])

    op.create_table(
        "fetnetlist",
        sa.Column("branch_id", sa.Integer()),
        sa.Column("shop_id", sa.Integer()),
        sa.Column("shop_name", sa.String(255)),
        sa.Column("shop_tax", sa.String(255)),
        sa.Column("shop_location", sa.String(255)),
        sa.Column("shop_phone_number", sa.String(255)),
        sa.Column("shop_phone_short_code", sa.String(255)),
        sa.Column("adsl_number", sa.String(255)),
        sa.Column("fetnet_phone_number", sa.String(255)),
        sa.Column("adsl_bank_number", sa.String(255)),
        sa.Column("fetnetlist_remark", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_fetnetlist_id", "fetnetlist", ["id"])

    op.create_table(
        "ipcamlist",
        sa.Column("shop_id", sa.Integer()),
        sa.Column("shop_name", sa.String(255)),
        sa.Column("ipcam_brand", sa.String(255)),
        sa.Column("ipcam_ip", sa.String(255)),
        sa.Column("admin_acc", sa.String(255)),
        sa.Column("admin_pass", sa.String(255)),
        sa.Column("user_acc", sa.String(255)),
        sa.Column("user_pass", sa.String(255)),
        sa.Column("phone_port", sa.String(255)),
        sa.Column("http_port", sa.String(255)),
        sa.Column("tcp_port", sa.String(255)),
        sa.Column("remark", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_ipcamlist_id", "ipcamlist", ["id"])

    op.create_table(
        "serverlist",
        sa.Column("branch_id", sa.Integer()),
        sa.Column("server_name", sa.String(255)),
        sa.Column("server_ip", sa.String(255)),
        sa.Column("server_location", sa.String(255)),
        sa.Column("server_acc", sa.String(255)),
        sa.Column("server_pass", sa.String(255)),
        sa.Column("server_remark", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_serverlist_id", "serverlist", ["id"])

    op.create_table(
        "task",
        sa.Column("taskname", sa.String(255)),
        sa.Column("fullname", sa.String(255)),
        sa.Column("organization", sa.String(255)),
        sa.Column("is_active", sa.Boolean()),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_task_id", "task", ["id"])
    op.create_index("ix_task_taskname", "task", ["taskname"])

    op.create_table(
        "transactions",
        sa.Column("amount", sa.String(255)),
        sa.Column("sale_id", sa.String(255)),
        sa.Column("sale_amount", sa.String(255)),
        sa.Column("pos_id", sa.String(255)),
        sa.Column("canceled", sa.String(255)),
        sa.Column("transaction_id", sa.String(255)),
        sa.Column("service_amount", sa.String(255)),
        sa.Column("discount_amount", sa.String(255)),
        sa.Column("sale_deleted", sa.String(255)),
        sa.Column("employee_username", sa.String(255)),
        sa.Column("shipping_fee", sa.String(255)),
        sa.Column("shop_id", sa.Integer()),
        sa.Column("create_time", sa.Date()),
        sa.Column("update_time", sa.Date()),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])

    op.create_table(
        "cst_shop",
        sa.Column("main_department_id", sa.Integer(), sa.ForeignKey("task.id")),
        sa.Column("shop_name", sa.String(255)),
        sa.Column("shop_number", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
    )
    op.create_index("ix_cst_shop_id", "cst_shop", ["id"])

    op.create_table(
        "user",
        sa.Column("username", sa.String(100)),
        sa.Column("fullname", sa.String(255)),
        sa.Column("password", sa.String(255)),
        sa.Column("is_active", sa.Boolean()),
        sa.Column("is_superuser", sa.Boolean()),
        sa.Column("checklistAll_permission", sa.Integer()),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("department.id")),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_user_id", "user", ["id"])
    op.create_index("ix_user_username", "user", ["username"], unique=True)

    op.create_table(
        "daysoff",
        sa.Column("daysoff_name", sa.String(255)),
        sa.Column("daysoff_date", sa.Date()),
        sa.Column("daysoff_hour", sa.Numeric(4, 2)),
        sa.Column("active", sa.Boolean()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_daysoff_daysoff_name", "daysoff", ["daysoff_name"])
    op.create_index("ix_daysoff_id", "daysoff", ["id"])

    op.create_table(
        "expenditure",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("expentask_id", sa.Integer(), sa.ForeignKey("expentask.id")),
        sa.Column("date", sa.Date()),
        sa.Column("price", sa.Integer()),
        sa.Column("description", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_expenditure_description", "expenditure", ["description"])
    op.create_index("ix_expenditure_id", "expenditure", ["id"])

    op.create_table(
        "workhour",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id")),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("cst_shop.id")),
        sa.Column("start_date", sa.Date()),
        sa.Column("hour", sa.Numeric(4, 2)),
        sa.Column("case_close", sa.Boolean()),
        sa.Column("overtime_hour", sa.Numeric(4, 2)),
        sa.Column("description", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("end_date", sa.Date()),
        sa.Column("todo", sa.String(255)),
        sa.Column("cause_issue", sa.String(255)),
        sa.Column("processing_method", sa.String(255)),
        sa.Column("id", sa.Integer(), primary_key=True),
        *_audit_columns(),
    )
    op.create_index("ix_workhour_cause_issue", "workhour", ["cause_issue"])
    op.create_index("ix_workhour_description", "workhour", ["description"])
    op.create_index("ix_workhour_id", "workhour", ["id"])
    op.create_index("ix_workhour_processing_method", "workhour", ["processing_method"])
    op.create_index("ix_workhour_todo", "workhour", ["todo"])


def downgrade() -> None:
    op.drop_table("workhour")
    op.drop_table("expenditure")
    op.drop_table("daysoff")
    op.drop_table("user")
    op.drop_table("cst_shop")
    op.drop_table("transactions")
    op.drop_table("task")
    op.drop_table("serverlist")
    op.drop_table("ipcamlist")
    op.drop_table("fetnetlist")
    op.drop_table("expentask")
    op.drop_table("department")
    op.drop_table("branch_list")
