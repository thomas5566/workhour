from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import false, func

from .db.base import Base


class IdMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class TimestampMixin:
    # These remain nullable to match the deployed legacy schema exactly.
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Department(IdMixin, TimestampMixin, Base):
    __tablename__ = "department"

    department_name: Mapped[str | None] = mapped_column(String(255), index=True)
    # A department contains many users; a collection annotation prevents
    # SQLAlchemy from treating this one-to-many relationship as a scalar.
    users: Mapped[list[User]] = relationship(back_populates="department")


class Task(IdMixin, TimestampMixin, Base):
    __tablename__ = "task"

    taskname: Mapped[str | None] = mapped_column(String(255), index=True)
    fullname: Mapped[str | None] = mapped_column(String(255))
    organization: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool | None] = mapped_column(Boolean(), default=True)

    workhours: Mapped[list[Workhour]] = relationship(back_populates="task")
    cstshops: Mapped[list[CstShop]] = relationship(back_populates="task")


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "user"

    username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )
    fullname: Mapped[str | None] = mapped_column(String(255), default="")
    password: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool | None] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool | None] = mapped_column(Boolean(), default=False)
    checklistAll_permission: Mapped[int | None] = mapped_column(Integer, default=0)
    # Incremented whenever credentials or an explicit logout invalidates JWTs.
    auth_version: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workhours: Mapped[list[Workhour]] = relationship(back_populates="user")
    expenditures: Mapped[list[Expenditure]] = relationship(back_populates="user")
    department_id: Mapped[int | None] = mapped_column(ForeignKey("department.id"))
    department: Mapped[Department | None] = relationship(back_populates="users")


class ExpenTask(IdMixin, TimestampMixin, Base):
    __tablename__ = "expentask"

    expentask_name: Mapped[str | None] = mapped_column(String(255), index=True)
    expens: Mapped[list[Expenditure]] = relationship(back_populates="expentask")


class Workhour(IdMixin, TimestampMixin, Base):
    __tablename__ = "workhour"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("task.id"))
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("cst_shop.id"))
    start_date: Mapped[date | None] = mapped_column(Date)
    hour: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    case_close: Mapped[bool | None] = mapped_column(Boolean(), default=False)
    overtime_hour: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    description: Mapped[str | None] = mapped_column(String(255), index=True)
    active: Mapped[bool | None] = mapped_column(Boolean(), default=True)
    end_date: Mapped[date | None] = mapped_column(Date)
    todo: Mapped[str | None] = mapped_column(String(255), index=True)
    cause_issue: Mapped[str | None] = mapped_column(String(255), index=True)
    processing_method: Mapped[str | None] = mapped_column(String(255), index=True)

    user: Mapped[User | None] = relationship(back_populates="workhours")
    task: Mapped[Task | None] = relationship(back_populates="workhours")
    shop: Mapped[CstShop | None] = relationship(back_populates="workhours")


class Expenditure(IdMixin, TimestampMixin, Base):
    __tablename__ = "expenditure"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    expentask_id: Mapped[int | None] = mapped_column(ForeignKey("expentask.id"))
    date: Mapped[date | None] = mapped_column(Date)
    price: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(String(255), index=True)
    active: Mapped[bool | None] = mapped_column(Boolean(), default=True)

    user: Mapped[User | None] = relationship(back_populates="expenditures")
    expentask: Mapped[ExpenTask | None] = relationship(back_populates="expens")


class DaysOff(IdMixin, TimestampMixin, Base):
    # Keep the retired feature's table in Alembic metadata until a separately
    # approved data-retention migration decides whether existing rows may drop.
    __tablename__ = "daysoff"

    daysoff_name: Mapped[str | None] = mapped_column(String(255), index=True)
    daysoff_date: Mapped[date | None] = mapped_column(Date)
    daysoff_hour: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    active: Mapped[bool | None] = mapped_column(Boolean(), default=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))


class CstShop(IdMixin, Base):
    __tablename__ = "cst_shop"

    # Keep the legacy column name while mapping it to the Task relationship.
    main_department_id: Mapped[int | None] = mapped_column(ForeignKey("task.id"))
    shop_name: Mapped[str | None] = mapped_column(String(255))
    shop_number: Mapped[str | None] = mapped_column(String(255))

    task: Mapped[Task | None] = relationship(back_populates="cstshops")
    workhours: Mapped[list[Workhour]] = relationship(back_populates="shop")


class BranchList(IdMixin, Base):
    __tablename__ = "branch_list"

    branch_name: Mapped[str | None] = mapped_column(String(255))
    branch_title: Mapped[str | None] = mapped_column(String(255))


class ServerList(IdMixin, Base):
    __tablename__ = "serverlist"

    branch_id: Mapped[int | None] = mapped_column(Integer)
    server_name: Mapped[str | None] = mapped_column(String(255))
    server_ip: Mapped[str | None] = mapped_column(String(255))
    server_location: Mapped[str | None] = mapped_column(String(255))
    server_acc: Mapped[str | None] = mapped_column(String(255))
    server_pass: Mapped[str | None] = mapped_column(Text)
    server_remark: Mapped[str | None] = mapped_column(String(255))


class TransactionsList(IdMixin, Base):
    # This retired integration remains mapped only to preserve its legacy data.
    __tablename__ = "transactions"

    amount: Mapped[str | None] = mapped_column(String(255))
    sale_id: Mapped[str | None] = mapped_column(String(255))
    sale_amount: Mapped[str | None] = mapped_column(String(255))
    pos_id: Mapped[str | None] = mapped_column(String(255))
    canceled: Mapped[str | None] = mapped_column(String(255))
    transaction_id: Mapped[str | None] = mapped_column(String(255))
    service_amount: Mapped[str | None] = mapped_column(String(255))
    discount_amount: Mapped[str | None] = mapped_column(String(255))
    sale_deleted: Mapped[str | None] = mapped_column(String(255))
    employee_username: Mapped[str | None] = mapped_column(String(255))
    shipping_fee: Mapped[str | None] = mapped_column(String(255))
    shop_id: Mapped[int | None] = mapped_column(Integer)
    create_time: Mapped[date | None] = mapped_column(Date)
    update_time: Mapped[date | None] = mapped_column(Date)


class FetnetList(IdMixin, Base):
    __tablename__ = "fetnetlist"

    branch_id: Mapped[int | None] = mapped_column(Integer)
    shop_id: Mapped[int | None] = mapped_column(Integer)
    shop_name: Mapped[str | None] = mapped_column(String(255))
    shop_tax: Mapped[str | None] = mapped_column(String(255))
    shop_location: Mapped[str | None] = mapped_column(String(255))
    shop_phone_number: Mapped[str | None] = mapped_column(String(255))
    shop_phone_short_code: Mapped[str | None] = mapped_column(String(255))
    adsl_number: Mapped[str | None] = mapped_column(String(255))
    fetnet_phone_number: Mapped[str | None] = mapped_column(String(255))
    adsl_bank_number: Mapped[str | None] = mapped_column(String(255))
    fetnetlist_remark: Mapped[str | None] = mapped_column(String(255))


class IpCamList(IdMixin, Base):
    __tablename__ = "ipcamlist"

    shop_id: Mapped[int | None] = mapped_column(Integer)
    shop_name: Mapped[str | None] = mapped_column(String(255))
    ipcam_brand: Mapped[str | None] = mapped_column(String(255))
    ipcam_ip: Mapped[str | None] = mapped_column(String(255))
    admin_acc: Mapped[str | None] = mapped_column(String(255))
    admin_pass: Mapped[str | None] = mapped_column(Text)
    user_acc: Mapped[str | None] = mapped_column(String(255))
    user_pass: Mapped[str | None] = mapped_column(Text)
    phone_port: Mapped[str | None] = mapped_column(String(255))
    http_port: Mapped[str | None] = mapped_column(String(255))
    tcp_port: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(String(255))


class MonitoringAlertLog(IdMixin, TimestampMixin, Base):
    """Persist one row for each continuous High-or-higher alert incident."""

    __tablename__ = "monitoring_alert_log"

    event_key: Mapped[str] = mapped_column(String(512), index=True)
    event_id: Mapped[str] = mapped_column(String(255), index=True)
    host_name: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[int] = mapped_column(Integer, index=True)
    severity_label: Mapped[str] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    acknowledged: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )
    source: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str] = mapped_column(Text)
