from typing import List, Optional
from pydantic import BaseModel
import datetime

from .departments import Department


class UserBase(BaseModel):
    username: str
    fullname: Optional[str] = None
    # password: str
    is_superuser: Optional[bool] = None
    checklistAll_permission: Optional[int] = None
    department_id: int
    department: Optional[Department]


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserToken(User):
    token: Optional[str] = None
    expiration: Optional[datetime.datetime] = None


class DataTotal(BaseModel):
    year_month: str
    # department_name: str
    # user_name: str
    total_hour: float
    total_overtime_hour: float
    total_pric: Optional[int] = None
    total_pric2: Optional[int] = None

    class Config:
        orm_mode = True

