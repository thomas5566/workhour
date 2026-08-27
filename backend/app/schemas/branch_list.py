from pydantic import Field

from .base import BaseModel


class BranchList(BaseModel):
    id: int
    branch_name: str | None = None
    branch_title: str | None = None


class BranchListWrite(BaseModel):
    branch_name: str = Field(min_length=1, max_length=255)
    branch_title: str = Field(min_length=1, max_length=255)
