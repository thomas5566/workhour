from typing import Optional
from pydantic import BaseModel
import datetime


class WorkhourBase(BaseModel):
    user_id: Optional[int] = None
    task_id: int
    date: datetime.date
    hour: float
    description: Optional[str] = None
    is_overtime: Optional[bool] = False
    overtime_hour: float


class WorkhourUpdate(WorkhourBase):
    pass


class WorkhourCreate(WorkhourBase):
    pass


class WorkhourTotal(BaseModel):
    year_month: str
    total_hour: float
    total_overtime_hour: float

    class Config:
        orm_mode = True


class Workhour(WorkhourBase):
    id: int

    class Config:
        orm_mode = True


