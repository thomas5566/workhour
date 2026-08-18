from .base import BaseModel


class Department(BaseModel):
    id: int
    department_name: str | None = None
