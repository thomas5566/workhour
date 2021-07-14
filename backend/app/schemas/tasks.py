from typing import List, Optional
from pydantic import BaseModel
import datetime
from .users import User


class WorkhourTaskFull(BaseModel):
    user_id: Optional[int] = None
    task_id: Optional[int] = None
    date: datetime.date
    hour: float
    description: Optional[str] = None
    is_overtime: Optional[bool] = False
    overtime_hour: float
    user: Optional[User]

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


class TaskGYBase(BaseModel):
    id: str
    taskname: str
    workhours: List[WorkhourTaskFull] = []
    # task_name: str
    # user_name: str
    # user_id: int
    # worklist_task_id: int
    # worklist_date: datetime.date
    # worklist_hour: str
    # worklist_overtime: str
    # worklist_overtime_hour: str
    # worklist_description: str

    class Config:
        orm_mode = True
