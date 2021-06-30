from typing import Optional
from pydantic import BaseModel
import datetime

from .users import User
from .expentasks import ExpenTask


class ExpenditureBase(BaseModel):
    user_id: Optional[int] = None
    expentask_id: int
    date: datetime.date
    price: int
    description: Optional[str] = None


class ExpenditureUpdate(ExpenditureBase):
    user_id: int
    expentask_id: int
    date: datetime.date
    price: int
    description: str

    class Config:
        orm_mode = True


class ExpenditureCreate(ExpenditureBase):
    pass


class Expenditure(ExpenditureBase):
    id: int

    class Config:
        orm_mode = True


class ExpenTotal(BaseModel):
    year_month: str
    total_pric: int

    class Config:
        orm_mode = True
