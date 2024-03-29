from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Time, Float, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class IdMixin(object):
    id = Column(Integer, primary_key=True, index=True)


class TimestampMixin(object):
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())


class Department(IdMixin, Base, TimestampMixin):

    __tablename__ = "department"

    department_name = Column(String(255), index=True)
    user = relationship("User", back_populates="department", uselist=False)


class Task(IdMixin, Base, TimestampMixin):

    __tablename__ = "task"

    taskname = Column(String(255), index=True)
    fullname = Column(String(255))
    organization = Column(String(255))
    is_active = Column(Boolean(), default=True)

    workhours = relationship("Workhour", back_populates="task")
    cstshops = relationship("CstShop", back_populates="task")


class User(IdMixin, Base, TimestampMixin):

    __tablename__ = "user"

    username = Column(String(100), unique=True, index=True)
    fullname = Column(String(255), default="")
    password = Column(String(255))
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    checklistAll_permission = Column(Integer, default=0)  # 0: user, 1: manager
    # worklistAll_permission = Column(Integer, default=0)  # 0: user, 1: manager

    workhours = relationship("Workhour", back_populates="user")
    expenditures = relationship("Expenditure", back_populates="user")
    daysoff = relationship("DaysOff", back_populates="user")
    department_id = Column(Integer, ForeignKey("department.id"))
    department = relationship(
        "Department", back_populates="user", uselist=False)


class ExpenTask(IdMixin, Base, TimestampMixin):

    __tablename__ = "expentask"

    expentask_name = Column(String(255), index=True)

    expens = relationship("Expenditure", back_populates="expentask")


class Workhour(IdMixin, Base, TimestampMixin):

    __tablename__ = "workhour"

    user_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    shop_id = Column(Integer, ForeignKey("cst_shop.id"))
    start_date = Column(Date)
    hour = Column(Numeric(4, 2))
    case_close = Column(Boolean, default=False)
    overtime_hour = Column(Numeric(4, 2))
    description = Column(String(255), index=True)
    active = Column(Boolean, default=True)
    end_date = Column(Date)
    todo = Column(String(255), index=True)
    cause_issue = Column(String(255), index=True)
    processing_method = Column(String(255), index=True)

    user = relationship("User", back_populates="workhours", uselist=False)
    task = relationship("Task", back_populates="workhours", uselist=False)
    shop = relationship("CstShop", back_populates="workhours", uselist=False)


class Expenditure(IdMixin, Base, TimestampMixin):

    __tablename__ = "expenditure"

    user_id = Column(Integer, ForeignKey("user.id"))
    expentask_id = Column(Integer, ForeignKey("expentask.id"))
    date = Column(Date)
    price = Column(Integer)
    description = Column(String(255), index=True)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="expenditures", uselist=False)
    expentask = relationship(
        "ExpenTask", back_populates="expens", uselist=False)


class DaysOff(IdMixin, Base, TimestampMixin):

    __tablename__ = "daysoff"

    daysoff_name = Column(String(255), index=True)
    daysoff_date = Column(Date)
    daysoff_hour = Column(Numeric(4, 2))
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="daysoff")

class CstShop(IdMixin, Base):

    __tablename__ = "cst_shop"

    main_department_id = Column(Integer, ForeignKey("task.id"))    
    shop_name = Column(String(255))
    shop_number = Column(String(255))

    task = relationship("Task", back_populates="cstshops")
    workhours = relationship("Workhour", back_populates="shop")


class BranchList(IdMixin, Base):

    __tablename__ = "branch_list"

    branch_name = Column(String(255))
    branch_title = Column(String(255))


class ServerList(IdMixin, Base):

    __tablename__ = "serverlist"

    branch_id = Column(Integer)
    server_name = Column(String(255))
    server_ip = Column(String(255))
    server_location = Column(String(255))
    server_acc = Column(String(255))
    server_pass = Column(String(255))
    server_remark = Column(String(255))

