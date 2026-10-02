from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import MonitoringAlertLog
from ..schemas.monitoring import MonitoringProblem
from .transaction import commit_or_rollback

HIGH_SEVERITY = 4


def synchronize_alert_logs(
    db: Session,
    problems: list[MonitoringProblem],
    observed_at: datetime,
) -> int:
    """Record new incidents, refresh active ones, and close recovered incidents."""
    qualifying = {
        f"{problem.source}:{problem.event_id}": problem
        for problem in problems
        if problem.severity >= HIGH_SEVERITY
    }
    active = list(
        db.scalars(
            select(MonitoringAlertLog).where(MonitoringAlertLog.resolved_at.is_(None))
        )
    )
    active_by_key = {record.event_key: record for record in active}

    for event_key, record in active_by_key.items():
        if event_key not in qualifying:
            record.resolved_at = observed_at
            record.last_observed_at = observed_at

    created = 0
    for event_key, problem in qualifying.items():
        record = active_by_key.get(event_key)
        if record is None:
            db.add(
                MonitoringAlertLog(
                    event_key=event_key,
                    event_id=problem.event_id,
                    host_name=problem.host_name,
                    severity=problem.severity,
                    severity_label=problem.severity_label,
                    occurred_at=problem.occurred_at,
                    last_observed_at=observed_at,
                    acknowledged=problem.acknowledged,
                    source=problem.source,
                    message=problem.message,
                )
            )
            created += 1
            continue
        record.host_name = problem.host_name
        record.severity = problem.severity
        record.severity_label = problem.severity_label
        record.last_observed_at = observed_at
        record.acknowledged = problem.acknowledged
        record.message = problem.message

    commit_or_rollback(db)
    return created


def get_alert_logs(
    db: Session,
    *,
    date_from: datetime | None,
    date_to: datetime | None,
    message: str | None,
    offset: int,
    limit: int,
) -> tuple[list[MonitoringAlertLog], int]:
    filters = []
    if date_from is not None:
        filters.append(MonitoringAlertLog.occurred_at >= date_from)
    if date_to is not None:
        filters.append(MonitoringAlertLog.occurred_at <= date_to)
    if message:
        escaped = message.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        filters.append(MonitoringAlertLog.message.ilike(f"%{escaped}%", escape="\\"))

    total = db.scalar(
        select(func.count()).select_from(MonitoringAlertLog).where(*filters)
    ) or 0
    records = list(
        db.scalars(
            select(MonitoringAlertLog)
            .where(*filters)
            .order_by(MonitoringAlertLog.occurred_at.desc(), MonitoringAlertLog.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return records, total
