from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base

class Department(IdMixin, Base, TimestampMixin):
  
    __tablename__ = "department"

    department_name = Column(String(255), index=True)
    user = relationship("User", back_populates="department", uselist=False)