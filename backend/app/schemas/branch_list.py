from .base import BaseModel


class BranchList(BaseModel):
    id: int
    branch_name: str | None = None
    branch_title: str | None = None
