from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import MonitoringAlertLog
from app.schemas.monitoring import MonitoringProblem
from app.services import alert_logging


def test_collector_persists_a_complete_high_alert_snapshot(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    problem = MonitoringProblem(
        event_id="9001",
        host_name="Any Zabbix Host",
        severity=4,
        severity_label="High",
        occurred_at=datetime(2026, 10, 2, 1, 0, tzinfo=UTC),
        acknowledged=False,
        message="CPU utilization is high",
    )

    monkeypatch.setattr(alert_logging.settings, "ZABBIX_URL", "https://zabbix.test")
    monkeypatch.setattr(alert_logging.settings, "ZABBIX_TOKEN", "test-token")
    monkeypatch.setattr(alert_logging, "SessionLocal", session_factory)
    monkeypatch.setattr(
        alert_logging.monitoring, "get_branch_peplink_health", lambda _: []
    )
    monkeypatch.setattr(
        alert_logging.monitoring, "get_high_problems", lambda _: [problem]
    )
    monkeypatch.setattr(
        alert_logging.monitoring,
        "apply_branch_wan_rules",
        lambda problems, _: problems,
    )

    assert alert_logging.collect_alert_logs_once() == 1
    with Session(engine) as db:
        record = db.scalar(select(MonitoringAlertLog))
        assert record is not None
        assert record.event_id == "9001"
        assert record.host_name == "Any Zabbix Host"

    engine.dispose()
