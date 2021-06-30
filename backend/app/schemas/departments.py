from pydantic import BaseModel


class DepartmentBase(BaseModel):
    department_name: str


class Department(DepartmentBase):
    id: int

    class Config:
        orm_mode = True