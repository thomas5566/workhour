from pydantic import BaseModel


class BranchListBase(BaseModel):
    id: int
    branch_name: str
    branch_title: str


class BranchList(BranchListBase):
    id: int

    class Config:
        orm_mode = True

