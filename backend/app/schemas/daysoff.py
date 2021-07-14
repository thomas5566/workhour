from pydantic import BaseModel
from typing import Optional
import datetime


class DaysoffBase(BaseModel):
    user_id: Optional[int] = None
    daysoff_name: str
    daysoff_date: datetime.date
    daysoff_hour: float


class Daysoff(DaysoffBase):
    id: int

    class Config:
        orm_mode = True


class DaysoffCreate(DaysoffBase):
    pass


class DaysoffUpdate(DaysoffBase):
    pass
