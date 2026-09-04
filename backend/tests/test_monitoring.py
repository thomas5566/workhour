from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings
from app.services import monitoring

BASE_SETTINGS = {
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "SECRET_KEY": "test-secret-key-that-is-at-least-32-characters",
}


def test_unconfigured_monitoring_is_explicit_and_safe() -> None:
    summary = monitoring.build_monitoring_summary(
        Settings(**BASE_SETTINGS, _env_file=None)
    )

    assert summary.status == "unconfigured"
    assert {integration.status for integration in summary.integrations} == {
        "unconfigured"
    }
    assert all(not integration.configured for integration in summary.integrations)


def test_zabbix_summary_contains_only_sanitized_metrics(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )

    captured_problem_params: dict[str, Any] = {}

    def fake_call(_: Settings, method: str, params: dict[str, Any]) -> tuple[Any, int]:
        if method == "problem.get":
            captured_problem_params.update(params)
        responses = {
            "apiinfo.version": "7.0.0",
            "host.get": [
                {
                    "hostid": "1",
                    "status": "0",
                    "interfaces": [{"available": "1"}],
                },
                {"hostid": "2", "status": "0", "interfaces": []},
            ],
            "problem.get": [{"eventid": "9"}],
        }
        return responses[method], 4

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.check_zabbix(settings)
    serialized = result.model_dump_json()

    assert result.status == "ok"
    assert result.metrics["hosts"] == 2
    assert result.metrics["active_problems"] == 1
    assert captured_problem_params["severities"] == [2, 3, 4, 5]
    assert "private-zabbix-token" not in serialized


def test_zabbix_call_sends_api_token_as_bearer_header(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )
    captured: dict[str, Any] = {}

    def fake_request(*_: Any, **kwargs: Any) -> tuple[Any, int]:
        captured.update(kwargs)
        return {"jsonrpc": "2.0", "result": [], "id": 1}, 3

    monkeypatch.setattr(monitoring, "_request_json", fake_request)
    monitoring._zabbix_call(settings, "host.get", {"output": ["hostid"]})

    assert captured["token"] == "private-zabbix-token"
    assert "auth" not in captured["payload"]


def test_fortigate_health_uses_only_supported_zabbix_items(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )

    def fake_call(_: Settings, method: str, __: dict[str, Any]) -> tuple[Any, int]:
        if method == "host.get":
            return [
                {
                    "hostid": "7",
                    "host": "FortiGate-Branch",
                    "name": "FortiGate Branch",
                    "status": "0",
                    "interfaces": [
                        {"ip": "192.0.2.1", "type": "2", "available": "1"}
                    ],
                }
            ], 2
        return [
            {
                "hostid": "7", "key_": "system.name", "lastvalue": "branch-fw",
                "units": "", "status": "0", "state": "0",
            },
            {
                "hostid": "7", "key_": "vm.memory.util[x]", "lastvalue": "49",
                "lastclock": str(int(datetime.now(UTC).timestamp())),
                "units": "%", "status": "0", "state": "0",
            },
            {
                "hostid": "7", "key_": "system.uptime[x]", "lastvalue": "3600",
                "lastclock": str(int(datetime.now(UTC).timestamp())),
                "units": "uptime", "status": "0", "state": "0",
            },
            {
                "hostid": "7", "key_": "wc.mem.usage[x]", "lastvalue": "99",
                "units": "%", "status": "0", "state": "1",
            },
        ], 3

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.get_fortigate_health(settings)

    assert len(result) == 1
    assert result[0].status == "ok"
    assert result[0].metrics == {
        "hostname": "branch-fw",
        "memory": 49,
        "uptime_seconds": 3600,
    }
    assert "private-zabbix-token" not in result[0].model_dump_json()


def test_server_health_uses_fresh_supported_agent_items(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )
    current_clock = str(int(datetime.now(UTC).timestamp()))

    def fake_call(_: Settings, method: str, __: dict[str, Any]) -> tuple[Any, int]:
        if method == "host.get":
            return [
                {
                    "hostid": "8", "host": "vm-01", "name": "VM 01", "status": "0",
                    "hostgroups": [{"name": "Windows servers"}], "parentTemplates": [],
                    "discoveryRule": [],
                    "interfaces": [{"ip": "192.0.2.8", "type": "1", "available": "1"}],
                },
                {
                    "hostid": "31", "host": "uuid", "name": "ESXi-166", "status": "0",
                    "hostgroups": [{"name": "Applications"}], "parentTemplates": [],
                    "discoveryRule": {"key_": "nutanix.host.discovery"},
                    "interfaces": [],
                },
            ], 2
        return [
            {
                "hostid": "8", "key_": "system.cpu.util", "lastvalue": "12.5",
                "units": "%", "status": "0", "state": "0", "lastclock": current_clock,
            },
            {
                "hostid": "8", "key_": "system.uptime", "lastvalue": "7200",
                "units": "uptime", "status": "0", "state": "0", "lastclock": current_clock,
            },
            {
                "hostid": "8", "key_": "vfs.fs.dependent.size[C:,pused]",
                "lastvalue": "72.4", "units": "%", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "8", "key_": "vfs.fs.dependent.size[D:,pused]",
                "lastvalue": "91.2", "units": "%", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "8", "key_": "vfs.fs.dependent.size[E:,total]",
                "lastvalue": "100", "units": "GB", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
        ], 2

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.get_server_health(settings)

    assert len(result) == 1
    assert result[0].status == "ok"
    assert result[0].metrics == {
        "cpu": 12.5,
        "uptime_seconds": 7200,
        "disk_usage:C:": 72.4,
        "disk_usage:D:": 91.2,
    }


def test_nutanix_health_uses_host_group_and_fresh_items(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )
    current_clock = str(int(datetime.now(UTC).timestamp()))

    def fake_call(_: Settings, method: str, __: dict[str, Any]) -> tuple[Any, int]:
        if method == "host.get":
            return [
                {
                    "hostid": "30", "host": "cluster-01", "name": "Cluster 01",
                    "status": "0", "hostgroups": [{"name": "Nutanix"}],
                    "parentTemplates": [], "interfaces": [],
                    "macros": [{
                        "macro": "{$NUTANIX.PRISM.ELEMENT.IP}", "value": "192.0.2.30",
                    }],
                },
                {
                    "hostid": "31", "host": "esxi-166", "name": "ESXi-166",
                    "status": "0", "hostgroups": [{"name": "Hypervisors"}],
                    "parentTemplates": [],
                    "discoveryRule": {"key_": "nutanix.host.discovery"},
                    "interfaces": [], "macros": [{
                        "macro": "{$NUTANIX.PRISM.ELEMENT.IP}", "value": "192.0.2.30",
                    }],
                },
            ], 2
        return [
            {
                "hostid": "30", "name": "Hypervisor: CPU usage, %",
                "key_": "nutanix.cluster.hypervisor.cpu.usage.percent",
                "lastvalue": "18.5", "units": "%", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "30", "name": "Old item", "key_": "nutanix.old",
                "lastvalue": "", "units": "", "status": "0", "state": "1",
                "lastclock": current_clock,
            },
            {
                "hostid": "30", "name": "Container: Total",
                "key_": 'nutanix.storage.container.capacity.bytes["one"]',
                "lastvalue": "1000", "units": "B", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "30", "name": "Container: Free",
                "key_": 'nutanix.storage.container.free.bytes["one"]',
                "lastvalue": "600", "units": "B", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "30", "name": "Container: Used",
                "key_": 'nutanix.storage.container.usage.bytes["one"]',
                "lastvalue": "400", "units": "B", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "31", "name": "Hypervisor: CPU usage, %",
                "key_": "nutanix.host.hypervisor.cpu.usage.percent",
                "lastvalue": "27.5", "units": "%", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
            {
                "hostid": "31", "name": "Hypervisor: Memory usage, %",
                "key_": "nutanix.host.hypervisor.memory.usage.percent",
                "lastvalue": "61.2", "units": "%", "status": "0", "state": "0",
                "lastclock": current_clock,
            },
        ], 2

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.get_nutanix_health(settings)

    assert len(result) == 2
    assert result[0].name == "Cluster 01"
    assert result[0].ip_address == "192.0.2.30"
    assert result[0].status == "ok"
    assert result[0].last_updated_at is not None
    assert result[0].unsupported_item_details == ["Old item"]
    assert result[0].metrics == {
        "cpu": 18.5,
        "storage_containers": 1,
        "storage_capacity_bytes": 1000,
        "storage_used_bytes": 400,
        "storage_free_bytes": 600,
        "storage_utilization": 40.0,
        "supported_items": 4,
        "unsupported_items": 1,
    }
    assert result[1].name == "ESXi-166"
    assert result[1].ip_address == "192.0.2.166"
    assert result[1].status == "ok"
    assert result[1].metrics == {
        "cpu": 27.5,
        "memory": 61.2,
        "supported_items": 2,
        "unsupported_items": 0,
    }


def test_warning_problems_include_source_host(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )

    def fake_call(_: Settings, method: str, __: dict[str, Any]) -> tuple[Any, int]:
        if method == "problem.get":
            return [{
                "eventid": "99", "objectid": "55", "name": "Service stopped",
                "severity": "3", "clock": "1700000000", "acknowledged": "0",
            }], 2
        return [{
            "triggerid": "55", "hosts": [{"hostid": "8", "name": "VM 01"}],
        }], 2

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.get_warning_problems(settings)

    assert len(result) == 1
    assert result[0].host_name == "VM 01"
    assert result[0].severity_label == "Average"
    assert result[0].acknowledged is False


def test_peplink_health_includes_missing_and_monitored_hosts(monkeypatch) -> None:
    settings = Settings(
        **BASE_SETTINGS,
        ZABBIX_URL="https://zabbix.example.com/api_jsonrpc.php",
        ZABBIX_TOKEN="private-zabbix-token",
        _env_file=None,
    )

    def fake_call(_: Settings, method: str, __: dict[str, Any]) -> tuple[Any, int]:
        if method == "host.get":
            return [{
                "hostid": "20", "host": "Peplink-A1", "name": "Peplink-A1",
                "status": "0",
                "interfaces": [{"ip": "192.0.2.20", "type": "2", "available": "1"}],
            }], 2
        return [
            {
                "hostid": "20", "key_": "system.uptime", "lastvalue": "3600",
                "lastclock": str(int(datetime.now(UTC).timestamp())),
                "units": "uptime", "status": "0", "state": "0",
            },
            {
                "hostid": "20", "key_": "wanState[WAN 1]", "lastvalue": "3",
                "lastclock": str(int(datetime.now(UTC).timestamp())),
                "units": "", "status": "0", "state": "0",
                "valuemap": {"mappings": [
                    {"type": "0", "value": "3", "newvalue": "Connected"},
                ]},
            },
            {
                "hostid": "20", "key_": "pepVpnStatusConnectionState[Branch]",
                "lastclock": str(int(datetime.now(UTC).timestamp())),
                "lastvalue": "4", "units": "", "status": "0", "state": "0",
                "valuemap": {"mappings": [
                    {"type": "0", "value": "4", "newvalue": "Connected"},
                ]},
            },
        ], 2

    monkeypatch.setattr(monitoring, "_zabbix_call", fake_call)
    result = monitoring.get_peplink_health(settings)

    assert len(result) == 6
    assert result[0].name == "Peplink-A1"
    assert result[0].status == "ok"
    assert result[0].metrics == {
        "uptime_seconds": 3600,
        "WAN 1 狀態": "Connected",
        "SpeedFusion 總數": 1,
        "SpeedFusion 已連線": 1,
        "SpeedFusion 異常": 0,
    }
    assert result[-1].name == "Peplink-StoreHose"
    assert result[-1].status == "unconfigured"
