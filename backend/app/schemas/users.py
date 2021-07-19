from typing import List, Optional
from pydantic import BaseModel
import datetime

from .departments import Department


class TaskList(BaseModel):
    taskname: str

    class Config:
        orm_mode = True


class WorkList(BaseModel):
    user_id: Optional[int] = None
    task_id: int
    date: datetime.date
    hour: float
    description: Optional[str] = None
    is_overtime: Optional[bool] = False
    overtime_hour: float
    task: Optional[TaskList]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    fullname: Optional[str] = None
    password: str
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
    username: str
    department_id: int
    department: Optional[Department]
    workhours: List[WorkList] = []

    class Config:
        orm_mode = True
