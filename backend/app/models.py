from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Time, Float, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class IdMixin(object):
    id = Column(Integer, primary_key=True, index=True)

class TimestampMixin(object):
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(IdMixin, Base, TimestampMixin):

    __tablename__ = "user"

    username = Column(String(100), unique=True, index=True)
    fullname = Column(String(255))
    password = Column(String(255))

    workhours = relationship("Workhour", back_populates="user")

class Task(IdMixin, Base, TimestampMixin):

    __tablename__ = "task"

    taskname = Column(String(255), index=True)
    fullname = Column(String(255))
    organization = Column(String(255))
    workhours = relationship("Workhour", back_populates="task")

class Workhour(IdMixin, Base, TimestampMixin):

    __tablename__ = "workhour"

    user_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    date = Column(Date)
    hour = Column(Numeric(4,2))
    is_overtime = Column(Boolean, default=False)
    description = Column(String(255), index=True)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="workhours", uselist=False)
    task = relationship("Task", back_populates="workhours", uselist=False)
