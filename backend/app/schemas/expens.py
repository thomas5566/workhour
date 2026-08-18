import datetime

from pydantic import Field

from .base import BaseModel


class ExpenditureWrite(BaseModel):
    expentask_id: int = Field(gt=0)
    date: datetime.date
    price: int = Field(ge=0)
    description: str | None = Field(default=None, max_length=255)


class ExpenditureCreate(ExpenditureWrite):
    # Ownership is derived from the authenticated token, never request JSON.
    pass


class ExpenditureUpdate(ExpenditureWrite):
    pass


class Expenditure(BaseModel):
    id: int
    user_id: int | None = None
    expentask_id: int | None = None
    date: datetime.date | None = None
    price: int | None = None
    description: str | None = None


class ExpenTotal(BaseModel):
    year_month: str
    total_pric: int
