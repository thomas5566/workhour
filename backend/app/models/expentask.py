from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base


class ExpenTask(IdMixin, Base, TimestampMixin):
  
    __tablename__ = "expentask"

    expentask_name = Column(String(255), index=True)

    expens = relationship("Expenditure", back_populates="expentask")