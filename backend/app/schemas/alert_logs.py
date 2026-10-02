from datetime import datetime

from pydantic import Field

from .base import BaseModel


class AlertLog(BaseModel):
    id: int
    event_id: str
    host_name: str
    severity: int = Field(ge=4, le=5)
    severity_label: str
    occurred_at: datetime
    last_observed_at: datetime
    resolved_at: datetime | None = None
    acknowledged: bool
    source: str
    message: str


class AlertLogPage(BaseModel):
    items: list[AlertLog]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
