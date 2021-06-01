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

class ExpenTaskBase(BaseModel):
    expentask_name: str

class ExpenTaskCreate(ExpenTaskBase):
    pass

class ExpenTaskUpdate(ExpenTaskBase):
    pass

class ExpenTask(ExpenTaskBase):
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

class ExpenditureFull(Expenditure):
    user: Optional[User]
    expentask: Optional[ExpenTask]

class UserFull(User):
    workhours: List[WorkhourFull] = []

class TaskFull(Task):
    workhours: List[WorkhourFull] = []

class ExpenTaskFull(ExpenTask):
    expenditures: List[ExpenditureFull] = []

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
