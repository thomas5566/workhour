from typing import List, Optional
from pydantic import BaseModel
import datetime

class WorkhourBase(BaseModel):
    user_id: Optional[int] = None
    task_id: int
    date: datetime.date
    hour: float
    description: Optional[str] = None
    is_overtime: Optional[bool] = False

class WorkhourUpdate(WorkhourBase):
    pass

class WorkhourCreate(WorkhourBase):
    pass

class Workhour(WorkhourBase):
    id: int
    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    taskname: str
    fullname: str
    organization: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    fullname: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserToken(User):
    token: Optional[str] = None
    expiration: Optional[datetime.datetime] = None

class WorkhourFull(Workhour):
    user: Optional[User]
    task: Optional[Task]

class UserFull(User):
    workhours: List[WorkhourFull] = []

class TaskFull(Task):
    workhours: List[WorkhourFull] = []


