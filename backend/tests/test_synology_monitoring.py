from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings
from app.schemas.monitoring import MonitoringProblem
from app.services import monitoring


def test_synology_nas_hosts_are_discovered_by_group_and_include_alerts(monkeypatch) -> None:
    settings = Settings(
        DATABASE_URL="sqlite://",
        SECRET_KEY="test-secret-key-that-is-at-least-32-characters",
        ZABBIX_URL="https://zabbix.example/api_jsonrpc.php",
        ZABBIX_TOKEN="private-token",
        _env_file=None,
    )
    now = int(datetime.now(UTC).timestamp())
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_call(_: Settings, method: str, params: dict[str, Any]) -> tuple[Any, int]:
        calls.append((method, params))
        if method == "host.get":
            return [
                {
                    "hostid": "201", "host": "nas-b", "name": "NAS-B", "status": "0",
                    "hostgroups": [{"name": "Synology NAS"}],
                    "interfaces": [{"ip": "192.0.2.201", "type": "2", "available": "1"}],
                },
                {
                    "hostid": "200", "host": "nas-a", "name": "NAS-A", "status": "0",
                    "hostgroups": [{"name": "synology nas"}],
                    "interfaces": [{"ip": "192.0.2.200", "type": "2", "available": "1"}],
                },
                {
                    "hostid": "999", "host": "other", "name": "Other", "status": "0",
                    "hostgroups": [{"name": "Network devices"}], "interfaces": [],
                },
            ], 1
        return [
            {"hostid": "200", "lastclock": str(now), "status": "0", "state": "0"},
            {"hostid": "200", "lastclock": str(now), "status": "0", "state": "1"},
            {"hostid": "201", "lastclock": str(now), "status": "0", "state": "0"},
        ], 1

    problem = MonitoringProblem(
        event_id="7001", host_name="NAS-B", host_ids=["201"],
        severity=4, severity_label="High", occurred_at=datetime.now(UTC),
        acknowledged=False, message="Storage pool is degraded",
    )
    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)

    result = monitoring.get_synology_nas_health(settings, [problem])

    assert [device.name for device in result] == ["NAS-A", "NAS-B"]
    assert result[0].status == "ok"
    assert result[0].metrics == {
        "monitored_items": 1, "unsupported_items": 1, "active_alerts": 0,
    }
    assert result[1].status == "degraded"
    assert result[1].metrics["active_alerts"] == 1
    assert result[1].ip_address == "192.0.2.201"
    host_params = next(params for method, params in calls if method == "host.get")
    assert host_params["selectHostGroups"] == ["name"]
    item_params = next(params for method, params in calls if method == "item.get")
    assert item_params["hostids"] == ["201", "200"]
    assert "lastvalue" not in item_params["output"]


def test_synology_hosts_are_not_duplicated_in_vm_server_list() -> None:
    host = {"hostgroups": [{"name": "Synology NAS"}]}
    assert monitoring._is_synology_nas_host(host)
    assert not monitoring._is_synology_nas_host({
        "hostgroups": [{"name": "Network devices"}],
    })
