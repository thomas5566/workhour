from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import DatabaseSession, PageLimit, PageOffset
from app.auth import ManagerUser
from app.core.config import settings
from app.repository.alert_log_crud import get_alert_logs
from app.schemas.alert_logs import AlertLog, AlertLogPage
from app.schemas.monitoring import MonitoringSummary
from app.services.monitoring import build_monitoring_summary

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/summary", response_model=MonitoringSummary)
def get_monitoring_summary(_: ManagerUser) -> MonitoringSummary:
    """Return a sanitized, read-only infrastructure health snapshot."""
    return build_monitoring_summary(settings)


@router.get("/alert-logs", response_model=AlertLogPage)
def list_alert_logs(
    _: ManagerUser,
    db: DatabaseSession,
    date_from: Annotated[datetime | None, Query(alias="from")] = None,
    date_to: Annotated[datetime | None, Query(alias="to")] = None,
    message: Annotated[str | None, Query(max_length=500)] = None,
    offset: PageOffset = 0,
    limit: PageLimit = 100,
) -> AlertLogPage:
    """Search durable High-or-Disaster events by time and message text."""
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Start time must not be later than end time",
        )
    records, total = get_alert_logs(
        db,
        date_from=date_from,
        date_to=date_to,
        message=message,
        offset=offset,
        limit=limit,
    )
    return AlertLogPage(
        items=[AlertLog.model_validate(record) for record in records],
        total=total,
        limit=limit,
        offset=offset,
    )
