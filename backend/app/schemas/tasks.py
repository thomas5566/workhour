from typing import List
from pydantic import BaseModel



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


