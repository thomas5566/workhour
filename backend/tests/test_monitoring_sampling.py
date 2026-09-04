from datetime import UTC, datetime

import pytest

from app.core.config import Settings
from app.services import monitoring

TEST_SECRET = "x" * 32


@pytest.mark.parametrize("kind,name,keys", [
    ("fortigate", "FortiGate-A1", ["vm.memory.util[x]", "system.uptime[x]"]),
    ("server", "VM-01", ["system.cpu.util", "vm.memory.util"]),
    ("peplink", "Peplink-A1", ["wanState[WAN 1]", "system.uptime"]),
])
def test_device_sampling_refresh_and_stale_detection(monkeypatch, kind, name, keys):
    now = int(datetime.now(UTC).timestamp())
    rows = [{"hostid": "1", "key_": key, "lastvalue": "20", "units": "",
             "state": "0", "status": "0", "lastclock": str(now - 30)} for key in keys]
    calls = []

    def call(_, method, params):
        calls.append(method)
        if method == "host.get":
            return [{"hostid": "1", "host": name, "name": name, "status": "0",
                     "interfaces": [{"ip": "192.0.2.1", "type": "2", "available": "1"}]}], 0
        assert "lastclock" in params["output"]
        assert params["hostids"] == ["1"]
        return rows, 0

    monkeypatch.setattr(monitoring, "_zabbix_call", call)
    settings = Settings(DATABASE_URL="sqlite://", SECRET_KEY=TEST_SECRET,
                        ZABBIX_URL="https://example.test", ZABBIX_TOKEN="test", _env_file=None)
    fetch = getattr(monitoring, f"get_{kind}_health")
    device = fetch(settings)[0]
    assert device.status == "ok"
    assert int(device.last_updated_at.timestamp()) == now - 30
    assert len(device.metric_sampled_at) == 2

    # One fresh metric must not conceal an old core/WAN/resource sample.
    rows[0]["lastclock"] = str(now - 1000)
    rows[1]["lastclock"] = str(now)
    device = fetch(settings)[0]
    assert device.status == "degraded"
    assert int(device.last_updated_at.timestamp()) == now
    assert min(t.timestamp() for t in device.metric_sampled_at.values()) == now - 1000
    assert calls == ["host.get", "item.get", "host.get", "item.get"]

    for row in rows:
        row["lastclock"] = "0"
    device = fetch(settings)[0]
    assert device.last_updated_at is None and device.status == "degraded"
    # Unsupported/disabled or unmapped items must not advance the displayed clock.
    rows.extend([
        {**rows[0], "lastclock": str(now), "state": "1"},
        {**rows[0], "lastclock": str(now), "status": "1"},
        {**rows[0], "lastclock": str(now), "key_": "irrelevant.item"},
    ])
    assert fetch(settings)[0].last_updated_at is None


def test_speedfusion_aggregate_uses_oldest_sample(monkeypatch):
    now = int(datetime.now(UTC).timestamp())

    def call(_, method, params):
        if method == "host.get":
            return [{"hostid": "1", "host": "Peplink-A1", "status": "0"}], 0
        return [{"hostid": "1", "key_": f"pepVpnStatusConnectionState[{i}]",
                 "state": "0", "status": "0", "lastvalue": "4", "lastclock": str(clock)}
                for i, clock in enumerate([now - 1000, now])], 0

    monkeypatch.setattr(monitoring, "_zabbix_call", call)
    settings = Settings(DATABASE_URL="sqlite://", SECRET_KEY=TEST_SECRET,
                        ZABBIX_URL="https://example.test", ZABBIX_TOKEN="test", _env_file=None)
    device = monitoring.get_peplink_health(settings)[0]
    assert device.metric_sampled_at["SpeedFusion 已連線"].timestamp() == now - 1000
