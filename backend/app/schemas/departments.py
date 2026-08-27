from pydantic import Field

from .base import BaseModel


class Department(BaseModel):
    id: int
    department_name: str | None = None


class DepartmentWrite(BaseModel):
    department_name: str = Field(min_length=1, max_length=255)
