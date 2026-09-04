"""Branch discovery and health checks use fixtures, never live SNMP writes."""
from datetime import UTC, datetime

import pytest

from app.core.config import Settings
from app.services import monitoring


def settings():
    return Settings(DATABASE_URL="sqlite://", SECRET_KEY="test-secret-key-at-least-32-characters",
                    ZABBIX_URL="http://zabbix.example/api_jsonrpc.php", ZABBIX_TOKEN="test-token",
                    _env_file=None)


def host(name, identifier="1", visible=None, enabled=True):
    return {"hostid": identifier, "host": name, "name": visible or name,
            "status": "0" if enabled else "1",
            "interfaces": [{"ip": "192.0.2.1", "type": "2", "available": "1"}]}


def item(key, value, age=10, state="0", host_id="1"):
    return {"hostid": host_id, "key_": key, "lastvalue": value, "state": state,
            "lastclock": str(int(datetime.now(UTC).timestamp()) - age), "units": ""}


def mock_api(monkeypatch, hosts, items):
    calls = []

    def call(_, method, params):
        calls.append((method, params))
        return (hosts if method == "host.get" else items), 1

    monkeypatch.setattr(monitoring, "_zabbix_call", call)
    return calls


def test_exact_branch_range_and_technical_name(monkeypatch):
    calls = mock_api(monkeypatch, [host("Peplink-91", "91"), host("Peplink-A1", "100"),
                                  host("Peplink-01", visible="First shop"),
                                  host("Peplink-202", "202"), host("Peplink-00", "0")], [])
    result = monitoring.get_branch_peplink_health(settings())
    assert {row.host_name for row in result} == {"Peplink-01", "Peplink-91", "Peplink-202"}
    assert result[0].name == "First shop"
    assert len(calls) == 2
    assert set(calls[1][1]["hostids"]) == {"1", "91", "202"}


def test_maps_wan_and_resources_and_retains_missing(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("wanState[WAN 1]", "3"), item("wanHealthCheckState[WAN 1]", "1"),
        item("system.cpu.util", "25"), item("system.uptime", "123456"),
        item("secret.raw", "private-config"),
    ])
    result = monitoring.get_branch_peplink_health(settings())[0]
    assert result.metrics["WAN 1 狀態"] == "Connected"
    assert result.metrics["WAN 1 健康檢查"] == "Success"
    assert result.metrics["cpu"] == 25
    assert result.metrics["memory"] is None
    assert result.metric_states["memory"] == "missing"
    assert result.status == "degraded"
    assert "private-config" not in result.model_dump_json()


def test_stale_unsupported_invalid_never_become_zero(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("wanState[WAN 1]", "3", age=601),
        item("system.cpu.util", "NaN"), item("vm.memory.util", "25", state="1"),
        item("system.uptime", "0"),
    ])
    result = monitoring.get_branch_peplink_health(settings())[0]
    assert result.metric_states["WAN 1 狀態"] == "stale"
    assert result.metrics["WAN 1 狀態"] is None
    assert result.metric_states["cpu"] == "unknown"
    assert result.metric_states["memory"] == "unsupported"
    assert result.metrics["uptime_seconds"] == 0


def test_value_map_is_used_and_disabled_host_stays_degraded(monkeypatch):
    wan = item("wanState[WAN 1]", "3")
    wan["valuemap"] = {"mappings": [{"type": "0", "value": "3", "newvalue": "Connected"}]}
    mock_api(monkeypatch, [host("Peplink-01", enabled=False)], [
        wan, item("wanHealthCheckState[WAN 1]", "1"), item("system.cpu.util", "25"),
        item("vm.memory.util", "40"), item("system.uptime", "100"),
    ])
    result = monitoring.get_branch_peplink_health(settings())[0]
    assert result.metrics["WAN 1 狀態"] == "Connected"
    assert result.status == "degraded"


def test_empty_scope_never_fetches_all_items(monkeypatch):
    calls = mock_api(monkeypatch, [], [])
    assert monitoring.get_branch_peplink_health(settings()) == []
    assert len(calls) == 1


def test_original_tab_fetches_only_original_hosts(monkeypatch):
    calls = mock_api(monkeypatch, [host("Peplink-01"), host("Peplink-A1", "2")], [])
    result = monitoring.get_peplink_health(settings())
    assert len(result) == 6
    assert calls[1][1]["hostids"] == ["2"]
    assert not any(row.name == "Peplink-01" for row in result)


def test_new_host_group_members_are_discovered_each_refresh(monkeypatch):
    hosts = [host("Peplink-01")]
    mock_api(monkeypatch, hosts, [])
    assert len(monitoring.get_branch_peplink_health(settings())) == 1
    new_host = host("Store-New-Router", "203")
    new_host["hostgroups"] = [{"name": "Peplink"}]
    hosts.append(new_host)
    assert len(monitoring.get_branch_peplink_health(settings())) == 2
    assert not monitoring._is_branch_peplink({
        **host("Peplink-A1"), "hostgroups": [{"name": "Peplink"}],
    })


def test_hidden_wifi_items_are_not_exposed_or_counted(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("wanState[Wi-Fi WAN]", "2"),
        item("wanState[Wi-Fi WAN on 2.4 GHz]", "2"),
        item("wanHealthCheckState[Wi-Fi WAN on 5 GHz]", "0"),
        item("wanState[VLAN WAN]", "2"),
        item("wanHealthCheckState[VLAN WAN 2]", "0"),
        item("wanState[WAN]", "3"),
    ])
    result = monitoring.get_branch_peplink_health(settings())
    assert not any("Wi-Fi" in key for key in result[0].metrics)
    assert not any("VLAN" in key for key in result[0].metrics)
    assert monitoring.apply_branch_wan_rules([], result) == []
    assert monitoring.apply_branch_wan_rules([
        native_problem("wanState[VLAN WAN]"),
        native_problem("wanHealthCheckState[VLAN WAN 2]", "2"),
    ], result) == []


def native_problem(key, identifier="1", host_ids=None):
    return monitoring.MonitoringProblem(
        event_id=identifier, host_name="Peplink-01", severity=3,
        severity_label="Average", occurred_at=datetime.now(UTC), acknowledged=False,
        message="Generic message without interface names", host_ids=host_ids or ["1"],
        item_keys=[key],
    )


def test_disabled_backup_filter_is_scoped_and_never_hides_unrelated_incidents(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("wanState[FET]", "1"), item("wanState[Cellular]", "1"),
    ])
    devices = monitoring.get_branch_peplink_health(settings())
    problems = [native_problem("wanState[FET]", "1"),
                native_problem("wanHealthCheckState[Cellular]", "2"),
                native_problem("system.cpu.util", "3"),
                native_problem("wanState[FET]", "4", ["other"]),
                native_problem("wanState[FET]", "5", ["1", "other"])]
    result = monitoring.apply_branch_wan_rules(problems, devices)
    assert {p.event_id for p in result} == {"3", "4", "5"}
    devices[0].metric_states["FET 狀態"] = "stale"
    assert any(p.event_id == "1" for p in monitoring.apply_branch_wan_rules(problems, devices))


def test_wan_disconnect_fallback_deduplicates_and_recovers(monkeypatch):
    items = [item("wanState[WAN]", "2"), item("wanState[Cellular]", "8")]
    mock_api(monkeypatch, [host("Peplink-01")], items)
    devices = monitoring.get_branch_peplink_health(settings())
    local = monitoring.apply_branch_wan_rules([], devices)
    assert len(local) == 1 and local[0].source == "workhour"
    assert local[0].severity == 2 and "WAN" in local[0].message
    native = native_problem("wanState[WAN]")
    assert monitoring.apply_branch_wan_rules([native], devices) == [native]
    devices[0].enabled = False
    assert monitoring.apply_branch_wan_rules([], devices) == []
    devices[0].enabled = True
    devices[0].metric_states["WAN 狀態"] = "stale"
    assert monitoring.apply_branch_wan_rules([], devices) == []
    items[0]["lastvalue"] = "3"
    recovered = monitoring.get_branch_peplink_health(settings())
    assert monitoring.apply_branch_wan_rules([], recovered) == []


def test_native_problem_retains_exact_trigger_associations(monkeypatch):
    def call(_, method, params):
        if method == "problem.get":
            return [{"eventid": "1", "objectid": "10", "severity": "2", "clock": "1700000000"}], 0
        assert params["selectItems"] == ["key_"]
        return [{"triggerid": "10", "hosts": [{"hostid": "1", "name": "Peplink-01"}],
                 "items": [{"key_": "wanState[WAN]"}]}], 0
    monkeypatch.setattr(monitoring, "_zabbix_call", call)
    result = monitoring.get_warning_problems(settings())[0]
    assert result.host_ids == ["1"] and result.item_keys == ["wanState[WAN]"]


@pytest.mark.parametrize("seconds,count", [
    (30 * 86400 + 1, 0), (60 * 86400, 0), (90 * 86400, 0), (90 * 86400 + 1, 1),
])
def test_uptime_warning_boundary(monkeypatch, seconds, count):
    mock_api(monkeypatch, [host("Peplink-01")], [item("system.uptime", str(seconds))])
    devices = monitoring.get_branch_peplink_health(settings())
    problems = monitoring.apply_branch_wan_rules([], devices)
    assert len(problems) == count
    if count:
        assert problems[0].severity == 2
        assert "超過 90 天" in problems[0].message
        assert devices[0].metric_severities["uptime_seconds"] == 2
        assert devices[0].alert_severity == 2


@pytest.mark.parametrize("value,severity", [(79.99, 0), (80, 2), (89.99, 2), (90, 4)])
def test_resource_alerts_match_colors_and_recover(monkeypatch, value, severity):
    items = [item("system.cpu.util", str(value)), item("vm.memory.util", str(value))]
    mock_api(monkeypatch, [host("Peplink-01")], items)
    devices = monitoring.get_branch_peplink_health(settings())
    problems = monitoring.apply_branch_wan_rules([], devices)
    assert len(problems) == (2 if severity else 0)
    assert devices[0].alert_severity == severity
    assert all(p.severity == severity and p.source == "workhour" for p in problems)
    for row in items:
        row["lastvalue"] = "20"
    recovered = monitoring.get_branch_peplink_health(settings())
    assert monitoring.apply_branch_wan_rules([], recovered) == []
    assert recovered[0].alert_severity == 0


@pytest.mark.parametrize("state", ["1", "8"])
def test_backup_fail_excluded_only_with_fresh_disabled_or_standby(monkeypatch, state):
    items = [item("wanState[FET]", state), item("wanHealthCheckState[FET]", "0")]
    mock_api(monkeypatch, [host("Peplink-01")], items)
    devices = monitoring.get_branch_peplink_health(settings())
    assert monitoring.apply_branch_wan_rules([
        native_problem("wanHealthCheckState[FET]")], devices) == []
    items[0]["lastvalue"] = "3"
    devices = monitoring.get_branch_peplink_health(settings())
    assert len(monitoring.apply_branch_wan_rules([], devices)) == 1
    assert devices[0].alert_severity == 2
    items[0]["lastvalue"] = state
    items[0]["lastclock"] = "1"
    devices = monitoring.get_branch_peplink_health(settings())
    native = native_problem("wanHealthCheckState[FET]")
    assert monitoring.apply_branch_wan_rules([native], devices) == [native]


def test_resource_dedup_and_native_high_annotates_card(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [item("system.cpu.util", "95")])
    devices = monitoring.get_branch_peplink_health(settings())
    native = native_problem("system.cpu.util")
    native.severity = 5
    native.severity_label = "Disaster"
    assert monitoring.apply_branch_wan_rules([native], devices) == [native]
    assert devices[0].metric_severities["cpu"] == 5
    assert devices[0].alert_severity == 5


def test_invalid_stale_disabled_metrics_do_not_generate_alerts(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("system.cpu.util", "95", age=601), item("vm.memory.util", "99", state="1"),
        item("system.uptime", "NaN"),
    ])
    devices = monitoring.get_branch_peplink_health(settings())
    assert monitoring.apply_branch_wan_rules([], devices) == []
    mock_api(monkeypatch, [host("Peplink-01", enabled=False)], [
        item("system.cpu.util", "95"), item("system.uptime", "99999999"),
    ])
    devices = monitoring.get_branch_peplink_health(settings())
    assert monitoring.apply_branch_wan_rules([], devices) == []


def test_disconnect_and_failed_health_form_one_event(monkeypatch):
    mock_api(monkeypatch, [host("Peplink-01")], [
        item("wanState[WAN]", "2"), item("wanHealthCheckState[WAN]", "0"),
    ])
    devices = monitoring.get_branch_peplink_health(settings())
    assert len(monitoring.apply_branch_wan_rules([], devices)) == 1


@pytest.mark.parametrize("message", [
    "FET Link down", "Peplink-88 : FET Link down", "Peplink-08: FET Link down",
    "  Peplink-80： fet link DOWN  ",
])
def test_zabbix_fet_link_down_hidden_without_host_discovery(message):
    problem = native_problem("wanState[FET]")
    problem.message = message
    original = problem.model_dump()
    assert monitoring.apply_branch_wan_rules([problem], []) == []
    assert problem.model_dump() == original


@pytest.mark.parametrize("message,source", [
    ("Peplink-88 : FET Link down", "workhour"),
    ("Peplink-88 : WAN Link down", "zabbix"),
    ("Peplink-88 : Cellular Link down", "zabbix"),
    ("Peplink-88 : FET Link down and CPU high", "zabbix"),
    ("Memory usage high", "zabbix"),
])
def test_fet_name_filter_preserves_other_events(message, source):
    problem = native_problem("system.cpu.util")
    problem.message = message
    problem.source = source
    assert monitoring.apply_branch_wan_rules([problem], []) == [problem]


def test_hidden_fet_event_does_not_raise_card_severity_but_local_rules_remain(monkeypatch):
    items = [item("wanState[FET]", "3"), item("vm.memory.util", "85")]
    mock_api(monkeypatch, [host("Peplink-01")], items)
    problem = native_problem("wanState[FET]")
    problem.message = "Peplink-01 : FET Link down"
    problem.severity = 4
    problem.severity_label = "High"
    devices = monitoring.get_branch_peplink_health(settings())
    result = monitoring.apply_branch_wan_rules([problem], devices)
    assert len(result) == 1 and "Memory" in result[0].message
    assert devices[0].alert_severity == 2
    assert all(p.source == "workhour" for p in result)
    items[0]["lastvalue"] = "2"
    devices = monitoring.get_branch_peplink_health(settings())
    result = monitoring.apply_branch_wan_rules([problem], devices)
    assert len(result) == 2
    assert all(p.source == "workhour" and p.severity == 2 for p in result)
