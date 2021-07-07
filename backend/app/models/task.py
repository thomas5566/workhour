from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base

class Task(IdMixin, Base, TimestampMixin):
  
    __tablename__ = "task"

    taskname = Column(String(255), index=True)
    fullname = Column(String(255))
    organization = Column(String(255))
    is_active = Column(Boolean(), default=True)
    workhours = relationship("Workhour", back_populates="task")