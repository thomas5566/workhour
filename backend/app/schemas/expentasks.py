from pydantic import Field

from .base import BaseModel


class ExpenTaskWrite(BaseModel):
    expentask_name: str = Field(min_length=1, max_length=255)


class ExpenTaskCreate(ExpenTaskWrite):
    pass


class ExpenTaskUpdate(ExpenTaskWrite):
    pass


class ExpenTask(BaseModel):
    id: int
    expentask_name: str | None = None
