from typing import Optional, List
from pydantic import BaseModel
import datetime


class WorkhourBase(BaseModel):
    user_id: Optional[int] = None
    task_id: int
    shop_id: int
    start_date: datetime.date
    hour: float
    description: Optional[str] = None
    case_close: Optional[bool] = False
    overtime_hour: float
    end_date: datetime.date
    todo: Optional[str] = None
    cause_issue: Optional[str] = None
    processing_method: Optional[str] = None


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


class WorkhourByYearMonth(BaseModel):
    year_month: datetime.date
    total_events: int

    class Config:
        orm_mode = True

class WorkhourByUserId(BaseModel):
    user_id: int
    total_events: int
    username: str
    fullname: str

    class Config:
        orm_mode = True


class WorkhourByShopId(BaseModel):
    shop_id: int
    total_events: int
    shop_name: str

    class Config:
        orm_mode = True
        
