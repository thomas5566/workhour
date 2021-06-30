from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Date, Numeric
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base


class Workhour(IdMixin, Base, TimestampMixin):
  
    __tablename__ = "workhour"

    user_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    date = Column(Date)
    hour = Column(Numeric(4, 2))
    is_overtime = Column(Boolean, default=False)
    overtime_hour = Column(Numeric(4, 2))
    description = Column(String(255), index=True)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="workhours", uselist=False)
    task = relationship("Task", back_populates="workhours", uselist=False)