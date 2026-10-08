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
        common = {"lastclock": str(now), "status": "0", "state": "0", "units": ""}
        return [
            {**common, "hostid": "200", "name": "Model serial number",
             "key_": "synoSystem.serialNumber", "lastvalue": "SERIAL-200"},
            {**common, "hostid": "200", "name": "Version",
             "key_": "synoSystem.version", "lastvalue": "DSM 7.2.2"},
            {**common, "hostid": "200", "name": "System Status",
             "key_": "synoSystem.systemStatus", "lastvalue": "1"},
            {**common, "hostid": "200", "name": "Power Status",
             "key_": "synoSystem.powerStatus", "lastvalue": "2"},
            {**common, "hostid": "200", "name": "System Uptime",
             "key_": "synoSystem.sysUpTime", "lastvalue": "900000"},
            {**common, "hostid": "200", "name": "Storage Used on /volume1 (%)",
             "key_": "host.hrStorage.hrStorageTable.hrStorageEntry.hrStorageUsed[40,pct]",
             "lastvalue": "42", "units": "%"},
            {**common, "hostid": "200", "name": "Drive 1 Status",
             "key_": "synoDisk.diskTable.diskEntry.diskStatus.[0]", "lastvalue": "4"},
            {**common, "hostid": "200", "name": "CPU Fan Status",
             "key_": "synoSystem.cpuFanStatus", "lastvalue": "1"},
            {**common, "hostid": "200", "name": "System Fan Status",
             "key_": "synoSystem.systemFanStatus", "lastvalue": "2"},
            {**common, "hostid": "200", "name": "Drive 1 Temperature",
             "key_": "synoDisk.diskTable.diskEntry.diskTemperature.[0]",
             "lastvalue": "55", "units": "C"},
            {**common, "hostid": "200", "name": "Drive 1 Bad sectors count",
             "key_": "synoDisk.diskTable.diskEntry.diskBadSector.[0]", "lastvalue": "2"},
            {**common, "hostid": "200", "name": "Volume 1 RAID Status",
             "key_": "synoRaid.raidTable.raidEntry.raidStatus.[0]", "lastvalue": "11"},
            {**common, "hostid": "200", "name": "Ignored secret-like item",
             "key_": "vendor.private.value", "lastvalue": "must-not-leak"},
            {**common, "hostid": "200", "name": "Unsupported",
             "key_": "unsupported", "lastvalue": "", "state": "1"},
            {**common, "hostid": "201", "name": "Version",
             "key_": "synoSystem.version", "lastvalue": "DSM 6.2"},
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
        "serial_number": "SERIAL-200",
        "dsm_version": "DSM 7.2.2",
        "system_status": "Normal",
        "power_status": "Failed",
        "uptime_seconds": 900000,
        "volume_usage:/volume1": 42,
        "disk_status:Drive 1": "System Partition Failed",
        "cpu_fan_status": "Normal",
        "system_fan_status": "Failed",
        "disk_temperature:Drive 1": 55,
        "disk_bad_sectors:Drive 1": 2,
        "raid_status:Volume 1 RAID": "Degraded",
        "monitored_items": 13,
        "unsupported_items": 1,
        "active_alerts": 0,
    }
    assert "must-not-leak" not in result[0].metrics.values()
    assert set(result[0].metric_sampled_at) == {
        "serial_number", "dsm_version", "system_status", "power_status",
        "uptime_seconds", "volume_usage:/volume1", "disk_status:Drive 1",
        "cpu_fan_status", "system_fan_status", "disk_temperature:Drive 1",
        "disk_bad_sectors:Drive 1", "raid_status:Volume 1 RAID",
    }
    assert result[1].status == "degraded"
    assert result[1].metrics["active_alerts"] == 1
    assert result[1].ip_address == "192.0.2.201"
    host_params = next(params for method, params in calls if method == "host.get")
    assert host_params["selectHostGroups"] == ["name"]
    item_params = next(params for method, params in calls if method == "item.get")
    assert item_params["hostids"] == ["201", "200"]
    assert "lastvalue" in item_params["output"]
    assert item_params["selectValueMap"] == ["name", "mappings"]

    problems = monitoring.apply_synology_nas_rules([], [result[0]])
    assert [(row.severity, row.event_id) for row in problems] == [
        (4, "synology-metric:200:system_fan_status"),
        (2, "synology-metric:200:disk_temperature:Drive 1"),
        (4, "synology-metric:200:disk_bad_sectors:Drive 1"),
        (4, "synology-metric:200:raid_status:Volume 1 RAID"),
    ]
    assert result[0].status == "degraded"
    assert result[0].metrics["active_alerts"] == 4


def test_synology_native_problem_prevents_duplicate_local_alert() -> None:
    sampled_at = datetime.now(UTC)
    item_key = "synoRaid.raidTable.raidEntry.raidStatus.[0]"
    device = monitoring.NetworkDeviceHealth(
        host_id="200", name="NAS-A", status="ok", message="current",
        metrics={"raid_status:Volume 1 RAID": "Degraded"},
        metric_sampled_at={"raid_status:Volume 1 RAID": sampled_at},
        metric_item_keys={"raid_status:Volume 1 RAID": [item_key]},
    )
    native = MonitoringProblem(
        event_id="7002", host_name="NAS-A", host_ids=["200"], item_keys=[item_key],
        severity=4, severity_label="High", occurred_at=sampled_at,
        acknowledged=False, message="RAID degraded",
    )

    result = monitoring.apply_synology_nas_rules([native], [device])

    assert result == [native]
    assert device.metrics["active_alerts"] == 1


def test_synology_hosts_are_not_duplicated_in_vm_server_list() -> None:
    host = {"hostgroups": [{"name": "Synology NAS"}]}
    assert monitoring._is_synology_nas_host(host)
    assert not monitoring._is_synology_nas_host({
        "hostgroups": [{"name": "Network devices"}],
    })


def test_synology_ignores_internal_subvolume_usage() -> None:
    assert monitoring._synology_metric_name(
        "Storage Used on /volume1/@docker/btrfs (%)",
        "host.hrStorage.hrStorageTable.hrStorageEntry.hrStorageUsed[99,pct]",
    ) is None
    assert monitoring._synology_metric_name(
        "Storage Used on /volume2 (%)",
        "host.hrStorage.hrStorageTable.hrStorageEntry.hrStorageUsed[41,pct]",
    ) == "volume_usage:/volume2"
