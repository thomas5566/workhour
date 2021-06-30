from pydantic import BaseModel


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

