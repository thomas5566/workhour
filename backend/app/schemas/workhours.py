from datetime import date
from typing import Self

from pydantic import Field, model_validator

from .base import BaseModel


class WorkhourWrite(BaseModel):
    """Validated fields accepted when creating or replacing a workhour."""

    task_id: int = Field(gt=0)
    shop_id: int = Field(gt=0)
    start_date: date
    # Numeric(4, 2) stores at most 99.99; reject overflow before it reaches SQL.
    hour: float = Field(ge=0, lt=100)
    description: str | None = Field(default=None, max_length=255)
    case_close: bool = False
    overtime_hour: float = Field(ge=0, lt=100)
    end_date: date
    todo: str | None = Field(default=None, max_length=255)
    cause_issue: str | None = Field(default=None, max_length=255)
    processing_method: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        # Invalid ranges are client input errors, not repository/database errors.
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class WorkhourCreate(WorkhourWrite):
    # Ownership is derived from the authenticated token, never request JSON.
    pass


class WorkhourUpdate(WorkhourWrite):
    pass


class Workhour(BaseModel):
    """Read model tolerant of nullable columns in the deployed legacy schema."""

    id: int
    user_id: int | None = None
    task_id: int | None = None
    shop_id: int | None = None
    start_date: date | None = None
    hour: float | None = None
    description: str | None = None
    case_close: bool | None = None
    overtime_hour: float | None = None
    end_date: date | None = None
    todo: str | None = None
    cause_issue: str | None = None
    processing_method: str | None = None


class WorkhourTotal(BaseModel):
    year_month: str
    total_hour: float
    total_overtime_hour: float


class WorkhourByYearMonth(BaseModel):
    year_month: date
    total_events: int


class WorkhourByUserId(BaseModel):
    user_id: int
    total_events: int
    username: str | None = None
    fullname: str | None = None


class WorkhourByShopId(BaseModel):
    shop_id: int
    total_events: int
    shop_name: str | None = None
