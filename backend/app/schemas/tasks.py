import datetime

from pydantic import ConfigDict, Field

from .base import BaseModel
from .cstshop import CstShop
from .users import User


class WorkhourTaskFull(BaseModel):
    user_id: int | None = None
    task_id: int | None = None
    # Preserve the Vue response key while reading the corrected ORM column.
    date: datetime.date = Field(validation_alias="start_date")
    hour: float | None = None
    description: str | None = None
    is_overtime: bool = False
    overtime_hour: float | None = None
    user: User | None = None


class TaskWrite(BaseModel):
    # Reject the retired cstshops input instead of silently discarding it.
    model_config = ConfigDict(extra="forbid")

    taskname: str = Field(min_length=1, max_length=255)
    fullname: str = Field(max_length=255)
    organization: str = Field(max_length=255)


class TaskCreate(TaskWrite):
    pass


class TaskUpdate(TaskWrite):
    pass


class Task(BaseModel):
    id: int
    taskname: str | None = None
    fullname: str | None = None
    organization: str | None = None
    cstshops: list[CstShop] = Field(default_factory=list)


class TaskGYBase(BaseModel):
    id: int
    taskname: str | None = None
    workhours: list[WorkhourTaskFull] = Field(default_factory=list)
