from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from .timestamp import IdMixin, TimestampMixin
from ..database import Base


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