from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base


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

    department_id = Column(Integer, ForeignKey("department.id"))
    department = relationship(
        "Department", back_populates="user", uselist=False)
