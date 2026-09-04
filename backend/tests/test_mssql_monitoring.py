"""Exercise SQL monitoring without touching live SQL, Zabbix, or credentials."""
from datetime import UTC, datetime

import pytest

from app.core.config import Settings
from app.services import monitoring


@pytest.fixture
def settings():
    return Settings(
        DATABASE_URL="sqlite://", SECRET_KEY="test-secret-key-that-is-at-least-32-characters",
        ZABBIX_URL="https://zabbix.example/api_jsonrpc.php", ZABBIX_TOKEN="private-token",
        _env_file=None,
    )


def item(key, value, *, item_id="1", age=10, state="0"):
    return {
        "itemid": item_id, "hostid": "10881", "key_": key, "lastvalue": value,
        "lastclock": str(int(datetime.now(UTC).timestamp()) - age), "state": state,
        "status": "0", "hosts": [{"hostid": "10881", "host": "WIN-TEST", "name": "POS303"}],
    }


def mock_api(monkeypatch, items, problems=None, triggers=None):
    calls = []

    def call(_, method, params):
        calls.append((method, params))
        return {"item.get": items, "problem.get": problems or [],
                "trigger.get": triggers or []}[method], 1

    monkeypatch.setattr(monitoring, "_zabbix_call", call)
    return calls


def test_instances_and_databases_do_not_overwrite_each_other(monkeypatch, settings):
    rows = [item('mssql.pos3030.db.state["whmis"]', "0"),
            item('mssql.pos3030.db.state["other"]', "0", item_id="2"),
            item("mssql.other.service", "1", item_id="3"),
            item("mssql.pos3030.raw", "private-token", item_id="4")]
    mock_api(monkeypatch, rows)
    result = monitoring.get_mssql_health(settings)
    assert len(result) == 2
    assert len(result[1].metrics) == 2
    assert result[1].metrics[1].label.startswith("whmis")
    assert all(row.status == "ok" for row in result)
    assert "private-token" not in str(result)


@pytest.mark.parametrize(("value", "age", "state", "expected"), [
    ("1", 10, "0", "ok"), ("0", 10, "0", "critical"),
    ("1", 301, "0", "stale"), ("1", 10, "1", "unsupported"),
    ("nan", 10, "0", "unknown"), ("-1", 10, "0", "unknown"),
    ("collector error", 10, "0", "unknown"),
])
def test_service_status_and_invalid_samples(monkeypatch, settings, value, age, state, expected):
    mock_api(monkeypatch, [item("mssql.pos3030.service", value, age=age, state=state)])
    result = monitoring.get_mssql_health(settings)[0]
    assert result.metrics[0].status == expected
    assert result.status == ("ok" if expected == "ok" else "degraded")


def test_each_item_has_its_own_freshness(monkeypatch, settings):
    mock_api(monkeypatch, [item("mssql.pos3030.service", "1"),
                          item('mssql.pos3030.db.fullbackup.age["whmis"]', "2500",
                               item_id="2", age=901),
                          item("mssql.pos3030.version", "12.0.6024.0", item_id="3", age=3600)])
    result = monitoring.get_mssql_health(settings)[0]
    assert [m.status for m in result.metrics] == ["ok", "ok", "stale"]
    assert result.status == "degraded"


def test_problem_severity_matches_item_not_other_instance(monkeypatch, settings):
    problem = {"eventid": "90", "objectid": "10", "severity": "4", "clock": "1788316000",
               "name": "Log high", "acknowledged": "0"}
    calls = mock_api(monkeypatch, [
        item('mssql.pos3030.db.logused["whmis"]', "95"),
        item("mssql.other.service", "1", item_id="2"),
    ], [problem], [{"triggerid": "10", "functions": [{"itemid": "1"}]}])
    result = monitoring.get_mssql_health(settings)
    assert result[0].problems == []
    assert len(result[1].problems) == 1
    assert result[1].metrics[0].severity == 4
    assert result[1].metrics[0].status == "critical"
    params = next(params for method, params in calls if method == "problem.get")
    assert params["recent"] is False and params["suppressed"] is False


def test_api_failure_does_not_report_healthy_empty_result(monkeypatch, settings):
    for name in ["get_fortigate_health", "get_peplink_health", "get_server_health",
                 "get_nutanix_health", "get_warning_problems"]:
        monkeypatch.setattr(monitoring, name, lambda _: [])
    monkeypatch.setattr(monitoring, "check_zabbix", lambda _: monitoring.IntegrationHealth(
        name="zabbix", configured=True, status="ok", message="ok"))

    def fail(_):
        raise ValueError("private-token")

    monkeypatch.setattr(monitoring, "get_mssql_health", fail)
    result = monitoring.build_monitoring_summary(settings)
    assert result.status == "degraded"
    assert result.mssql_error
    assert "private-token" not in result.model_dump_json()


def test_no_matching_collectors_does_not_query_all_problems(monkeypatch, settings):
    calls = mock_api(monkeypatch, [])
    assert monitoring.get_mssql_health(settings) == []
    assert len(calls) == 1
