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


def test_collector_excludes_only_page_derived_cpu_and_memory(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    occurred_at = datetime(2026, 10, 2, 2, 0, tzinfo=UTC)

    def problem(
        event_id: str,
        message: str,
        *,
        source: str,
        item_keys: list[str],
    ) -> MonitoringProblem:
        return MonitoringProblem(
            event_id=event_id,
            host_name="Peplink-01",
            severity=4,
            severity_label="High",
            occurred_at=occurred_at,
            acknowledged=False,
            message=message,
            source=source,
            item_keys=item_keys,
        )

    local_cpu = problem(
        "branch-metric:101:cpu",
        "CPU 使用率 98.0%（本頁規則；目前取樣）",
        source="workhour",
        item_keys=["system.cpu.util", "system.cpu.util[,idle]"],
    )
    local_memory = problem(
        "branch-metric:101:memory",
        "Memory 使用率 90.11%（本頁規則；目前取樣）",
        source="workhour",
        item_keys=["vm.memory.util"],
    )
    local_wan = problem(
        "branch-metric:101:WAN 狀態",
        "WAN 狀態: Disconnect（本頁規則；目前取樣）",
        source="workhour",
        item_keys=["wanState[WAN]"],
    )
    zabbix_cpu = problem(
        "9002",
        "CPU utilization is high",
        source="zabbix",
        item_keys=["system.cpu.util"],
    )

    monkeypatch.setattr(alert_logging.settings, "ZABBIX_URL", "https://zabbix.test")
    monkeypatch.setattr(alert_logging.settings, "ZABBIX_TOKEN", "test-token")
    monkeypatch.setattr(alert_logging, "SessionLocal", session_factory)
    monkeypatch.setattr(
        alert_logging.monitoring, "get_branch_peplink_health", lambda _: []
    )
    monkeypatch.setattr(
        alert_logging.monitoring, "get_high_problems", lambda _: [zabbix_cpu]
    )
    monkeypatch.setattr(
        alert_logging.monitoring,
        "apply_branch_wan_rules",
        lambda problems, _: [*problems, local_cpu, local_memory, local_wan],
    )

    assert alert_logging.collect_alert_logs_once() == 2
    with Session(engine) as db:
        records = list(db.scalars(select(MonitoringAlertLog)))
        assert {record.event_id for record in records} == {
            "9002",
            "branch-metric:101:WAN 狀態",
        }

    engine.dispose()
