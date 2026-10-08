import ipaddress
import json
import math
import re
import socket
import ssl
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import Settings
from app.schemas.monitoring import (
    BranchPeplinkHealth,
    FirewallHealth,
    IntegrationHealth,
    MonitoringProblem,
    MonitoringSummary,
    MssqlHealth,
    MssqlMetric,
    NetworkDeviceHealth,
    ServerHealth,
)

# Zabbix severities 2 through 5 represent Warning, Average, High, and Disaster.
# Use one definition for both the overview counter and the event table so the UI
# cannot report different totals for the same set of active incidents.
WARNING_SEVERITIES = [2, 3, 4, 5]
HIGH_SEVERITIES = [4, 5]


def _request_json(
    url: str,
    *,
    timeout: float,
    token: str = "",
    payload: dict[str, Any] | None = None,
) -> tuple[Any, int]:
    """Perform a small read-only request without leaking response or token data."""
    headers = {"Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request = Request(url, data=data, headers=headers, method="POST" if data else "GET")
    started = perf_counter()
    with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
        body = json.load(response)
    return body, round((perf_counter() - started) * 1000)


def _zabbix_call(settings: Settings, method: str, params: dict[str, Any]) -> tuple[Any, int]:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    response, latency = _request_json(
        settings.ZABBIX_URL,
        timeout=settings.MONITORING_TIMEOUT_SECONDS,
        # Current Zabbix versions recommend the Bearer header. apiinfo.version
        # remains public and therefore intentionally sends no credential.
        token=settings.ZABBIX_TOKEN if method != "apiinfo.version" else "",
        payload=payload,
    )
    if not isinstance(response, dict) or "error" in response or "result" not in response:
        raise ValueError("Unexpected Zabbix response")
    return response["result"], latency


def _connection_failure_message(service: str, error: Exception) -> str:
    """Classify failures without returning URLs, tokens, or response bodies."""
    if isinstance(error, HTTPError):
        if error.code in {401, 403}:
            return f"{service} rejected the monitoring credentials"
        if error.code == 404:
            return f"{service} API path was not found"
        return f"{service} API returned HTTP {error.code}"
    if isinstance(error, URLError):
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            return f"{service} TLS certificate validation failed"
        if isinstance(error.reason, socket.gaierror):
            return f"{service} DNS lookup failed"
        if isinstance(error.reason, ConnectionRefusedError):
            return f"{service} connection was refused"
        if isinstance(error.reason, (TimeoutError, socket.timeout)):
            return f"{service} health check timed out"
        return f"{service} connection failed"
    if isinstance(error, TimeoutError):
        return f"{service} health check timed out"
    return f"{service} API returned an invalid response"


def check_zabbix(settings: Settings) -> IntegrationHealth:
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return IntegrationHealth(
            name="zabbix",
            configured=False,
            status="unconfigured",
            message="Zabbix integration is not configured",
        )
    try:
        version, version_latency = _zabbix_call(settings, "apiinfo.version", {})
        hosts, hosts_latency = _zabbix_call(
            settings,
            "host.get",
            {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "type", "available"],
            },
        )
        problems, problems_latency = _zabbix_call(
            settings,
            "problem.get",
            {
                "output": ["eventid"],
                "severities": WARNING_SEVERITIES,
                # Match Zabbix's current-problems view: recovered and
                # maintenance-suppressed events are not active incidents.
                "recent": False,
                "suppressed": False,
            },
        )
        host_rows = hosts if isinstance(hosts, list) else []
        problem_rows = problems if isinstance(problems, list) else []
        available = sum(
            any(
                str(interface.get("available", "0")) == "1"
                for interface in host.get("interfaces", [])
            )
            for host in host_rows
        )
        enabled = sum(str(host.get("status", "1")) == "0" for host in host_rows)
        return IntegrationHealth(
            name="zabbix",
            configured=True,
            status="ok",
            message="Zabbix API is responding",
            latency_ms=version_latency + hosts_latency + problems_latency,
            metrics={
                "version": str(version),
                "hosts": len(host_rows),
                "enabled_hosts": enabled,
                "available_agents": available,
                "active_problems": len(problem_rows),
            },
        )
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        return IntegrationHealth(
            name="zabbix",
            configured=True,
            status="degraded",
            message=_connection_failure_message("Zabbix", error),
        )


FORTIGATE_ITEM_KEYS = {
    "system.name": "hostname",
    "system.hw.firmware": "firmware",
}
FORTIGATE_ITEM_PREFIXES = {
    "vdom.cpu.usage[": "cpu",
    "vm.memory.util[": "memory",
    "net.ipv4.sessions[": "active_sessions",
    "system.uptime[": "uptime_seconds",
    "vpn.tunnel.active[": "ipsec_vpn_tunnels",
    "vpn.ssl.state[": "ssl_vpn_state",
    "ha.mode[": "ha_mode",
}


def _metric_name(item_key: str) -> str | None:
    if item_key in FORTIGATE_ITEM_KEYS:
        return FORTIGATE_ITEM_KEYS[item_key]
    return next(
        (
            metric
            for prefix, metric in FORTIGATE_ITEM_PREFIXES.items()
            if item_key.startswith(prefix)
        ),
        None,
    )


def _metric_value(value: Any, units: str) -> int | float | str | None:
    if units in {"%", "uptime"} or value == "0" or str(value).isdigit():
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return round(float(value), 2)
            except (TypeError, ValueError):
                return str(value) if value is not None else None
    return str(value) if value is not None else None


def _item_sample_time(item: dict[str, Any]) -> datetime | None:
    """Use the actual Zabbix sample clock, never the API request/refresh time."""
    clock = int(item.get("lastclock") or 0)
    return datetime.fromtimestamp(clock, UTC) if clock > 0 else None


def _latest_sample(samples: dict[str, datetime | None]) -> datetime | None:
    return max((value for value in samples.values() if value is not None), default=None)


def _sample_is_fresh(sample: datetime | None) -> bool:
    return sample is not None and 0 <= (datetime.now(UTC) - sample).total_seconds() <= 600


def get_fortigate_health(settings: Settings) -> list[FirewallHealth]:
    """Read FortiGate health exclusively from existing Zabbix SNMP items."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    try:
        hosts, _ = _zabbix_call(
            settings,
            "host.get",
            {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "type", "available"],
            },
        )
        firewall_hosts = [
            host
            for host in hosts
            if "fortigate" in f"{host.get('host', '')} {host.get('name', '')}".lower()
        ]
        host_ids = [str(host["hostid"]) for host in firewall_hosts]
        if not host_ids:
            return []
        items, _ = _zabbix_call(
            settings,
            "item.get",
            {
                "output": ["hostid", "key_", "lastvalue", "units", "status", "state", "lastclock"],
                "hostids": host_ids,
            },
        )
        metrics_by_host: dict[str, dict[str, int | float | str | bool | None]] = {
            host_id: {} for host_id in host_ids
        }
        samples_by_host: dict[str, dict[str, datetime | None]] = {h: {} for h in host_ids}
        for item in sorted(items, key=lambda row: (
            _metric_name(str(row.get("key_", ""))) or "", -int(row.get("lastclock") or 0),
        )):
            if str(item.get("status")) != "0" or str(item.get("state")) != "0":
                continue
            metric = _metric_name(str(item.get("key_", "")))
            host_id = str(item.get("hostid", ""))
            if metric and host_id in metrics_by_host and metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = _metric_value(
                    item.get("lastvalue"), str(item.get("units", ""))
                )
                samples_by_host[host_id][metric] = _item_sample_time(item)

        results: list[FirewallHealth] = []
        for host in firewall_hosts:
            interfaces = host.get("interfaces", [])
            snmp_interface = next(
                (interface for interface in interfaces if str(interface.get("type")) == "2"),
                None,
            )
            available = bool(snmp_interface and str(snmp_interface.get("available")) == "1")
            host_id = str(host["hostid"])
            metrics = metrics_by_host[host_id]
            samples = samples_by_host[host_id]
            latest = _latest_sample(samples)
            has_core_metrics = "memory" in metrics and "uptime_seconds" in metrics
            healthy = (available and has_core_metrics and str(host.get("status")) == "0"
                       and all(_sample_is_fresh(samples.get(key))
                               for key in ("memory", "uptime_seconds")))
            results.append(
                FirewallHealth(
                    host_id=host_id,
                    name=str(host.get("name") or host.get("host") or host_id),
                    ip_address=str(snmp_interface.get("ip")) if snmp_interface else None,
                    status="ok" if healthy else "degraded",
                    message=(
                        "SNMP monitoring is available"
                        if healthy
                        else "SNMP or core monitoring items are unavailable or stale"
                    ),
                    metrics=metrics,
                    last_updated_at=latest,
                    metric_sampled_at=samples,
                )
            )
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


SERVER_ITEM_KEYS = {
    "system.cpu.util": "cpu",
    "system.uptime": "uptime_seconds",
    "vm.memory.util": "memory",
    "vm.memory.utilization": "memory",
}

SERVER_FILESYSTEM_KEY_PREFIXES = (
    "vfs.fs.size[",
    "vfs.fs.dependent.size[",
)


def _server_metric_name(item_key: str) -> str | None:
    """Map supported server item keys, preserving each discovered filesystem."""
    direct_metric = SERVER_ITEM_KEYS.get(item_key)
    if direct_metric:
        return direct_metric

    lowered_key = item_key.lower()
    if not lowered_key.endswith(",pused]"):
        return None
    if not lowered_key.startswith(SERVER_FILESYSTEM_KEY_PREFIXES):
        return None

    parameters = item_key[item_key.find("[") + 1 : -1]
    filesystem = parameters.rsplit(",", 1)[0].strip().strip('"')
    return f"disk_usage:{filesystem}" if filesystem else None


def _is_nutanix_host(host: dict[str, Any]) -> bool:
    """Identify parent and LLD-created Nutanix hosts without relying on names."""
    discovery_rule = host.get("discoveryRule")
    discovery_key = (
        str(discovery_rule.get("key_", ""))
        if isinstance(discovery_rule, dict)
        else ""
    )
    if discovery_key.startswith("nutanix."):
        return True
    identifiers = [
        str(host.get("host", "")),
        str(host.get("name", "")),
        *(str(group.get("name", "")) for group in host.get("hostgroups", [])),
        *(str(template.get("name", "")) for template in host.get("parentTemplates", [])),
    ]
    return "nutanix" in " ".join(identifiers).lower()


def _is_synology_nas_host(host: dict[str, Any]) -> bool:
    """Match the dedicated Zabbix Host group without relying on host naming."""
    return any(
        str(group.get("name", "")).strip().casefold() == "synology nas"
        for group in host.get("hostgroups", [])
    )


SYNOLOGY_DIRECT_ITEM_KEYS = {
    "synoSystem.serialNumber": "serial_number",
    "synoSystem.version": "dsm_version",
    "synoSystem.systemStatus": "system_status",
    "synoSystem.powerStatus": "power_status",
    "synoSystem.sysUpTime": "uptime_seconds",
}
SYNOLOGY_STORAGE_USED_PATTERN = re.compile(
    r"^Storage Used on (?P<volume>.+?) \(%\)$", re.IGNORECASE
)
SYNOLOGY_TOP_LEVEL_VOLUME_PATTERN = re.compile(r"^/volume\d+$", re.IGNORECASE)
SYNOLOGY_DISK_STATUS_PREFIX = "synoDisk.diskTable.diskEntry.diskStatus."


def _synology_metric_name(item_name: str, item_key: str) -> str | None:
    """Map only approved Synology items while preserving volumes and drives."""
    direct_metric = SYNOLOGY_DIRECT_ITEM_KEYS.get(item_key)
    if direct_metric:
        return direct_metric

    storage_match = SYNOLOGY_STORAGE_USED_PATTERN.match(item_name.strip())
    volume = storage_match.group("volume").strip() if storage_match else ""
    if (
        volume
        and SYNOLOGY_TOP_LEVEL_VOLUME_PATTERN.match(volume)
        and item_key.endswith(",pct]")
    ):
        return f"volume_usage:{volume}"

    if item_key.startswith(SYNOLOGY_DISK_STATUS_PREFIX):
        drive_name = re.sub(r"\s+Status$", "", item_name.strip(), flags=re.IGNORECASE)
        return f"disk_status:{drive_name or item_key.rsplit('.', 1)[-1]}"
    return None


def _synology_metric_value(
    metric: str,
    item: dict[str, Any],
) -> int | float | str | None:
    """Normalize approved values after Zabbix has applied item preprocessing."""
    raw_value = str(item.get("lastvalue", "")).strip()
    if not raw_value:
        return None
    if metric == "uptime_seconds":
        # The Synology template multiplies SNMP TimeTicks by 0.01 before the
        # value is stored. item.get therefore already returns seconds.
        return _metric_value(raw_value, str(item.get("units", "")))

    status_maps = {
        "system_status": {"1": "Normal", "2": "Failed"},
        "power_status": {"1": "Normal", "2": "Failed"},
    }
    if metric.startswith("disk_status:"):
        status_maps[metric] = {
            "1": "Normal",
            "2": "Initialized",
            "3": "Not Initialized",
            "4": "System Partition Failed",
            "5": "Crashed",
        }
    if metric in status_maps:
        mapped = _mapped_item_value(item)
        return status_maps[metric].get(raw_value, mapped)
    if metric.startswith("volume_usage:"):
        return _metric_value(raw_value, "%")
    return raw_value


def get_server_health(settings: Settings) -> list[ServerHealth]:
    """Return non-FortiGate hosts with fresh, supported Zabbix agent metrics."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    try:
        hosts, _ = _zabbix_call(
            settings,
            "host.get",
            {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "type", "available"],
                "selectHostGroups": ["name"],
                "selectParentTemplates": ["name"],
                "selectDiscoveryRule": ["name", "key_"],
            },
        )
        server_hosts = [
            host
            for host in hosts
            if not any(
                device_type in f"{host.get('host', '')} {host.get('name', '')}".lower()
                for device_type in ("fortigate", "peplink")
            )
            and not _is_nutanix_host(host)
            and not _is_synology_nas_host(host)
            and not _is_branch_peplink(host)
        ]
        host_ids = [str(host["hostid"]) for host in server_hosts]
        if not host_ids:
            return []
        items, _ = _zabbix_call(
            settings,
            "item.get",
            {
                "output": ["hostid", "key_", "lastvalue", "units", "lastclock", "status", "state"],
                "hostids": host_ids,
                "filter": {"status": "0"},
                "search": {
                    "key_": [*SERVER_ITEM_KEYS, *SERVER_FILESYSTEM_KEY_PREFIXES],
                },
                "searchByAny": True,
            },
        )
        metrics_by_host: dict[str, dict[str, int | float | str | bool | None]] = {
            host_id: {} for host_id in host_ids
        }
        samples_by_host: dict[str, dict[str, datetime | None]] = {h: {} for h in host_ids}
        for item in sorted(items, key=lambda row: (
            _server_metric_name(str(row.get("key_", ""))) or "", -int(row.get("lastclock") or 0),
        )):
            if str(item.get("state")) != "0" or str(item.get("status", "0")) != "0":
                continue
            key = str(item.get("key_", ""))
            metric = _server_metric_name(key)
            host_id = str(item.get("hostid", ""))
            if metric and host_id in metrics_by_host and metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = _metric_value(
                    item.get("lastvalue"), str(item.get("units", ""))
                )
                samples_by_host[host_id][metric] = _item_sample_time(item)

        results: list[ServerHealth] = []
        for host in server_hosts:
            host_id = str(host["hostid"])
            interfaces = host.get("interfaces", [])
            interface = next((row for row in interfaces if row.get("ip")), None)
            metrics = metrics_by_host[host_id]
            samples = samples_by_host[host_id]
            latest = _latest_sample(samples)
            data_is_fresh = bool(samples) and all(_sample_is_fresh(t) for t in samples.values())
            healthy = str(host.get("status")) == "0" and data_is_fresh and bool(metrics)
            results.append(
                ServerHealth(
                    host_id=host_id,
                    name=str(host.get("name") or host.get("host") or host_id),
                    host_name=str(host.get("host") or host_id),
                    ip_address=str(interface.get("ip")) if interface else None,
                    group_names=[str(group.get("name")) for group in host.get("hostgroups", [])],
                    status="ok" if healthy else "degraded",
                    message=(
                        "Zabbix agent data is current"
                        if healthy
                        else "Zabbix agent data is unavailable or stale"
                    ),
                    metrics=metrics,
                    last_updated_at=latest,
                    metric_sampled_at=samples,
                )
            )
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


def get_synology_nas_health(
    settings: Settings,
    problems: list[MonitoringProblem],
) -> list[NetworkDeviceHealth]:
    """Discover visible NAS hosts and expose an allowlist of Synology metrics."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []

    hosts, _ = _zabbix_call(settings, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "selectInterfaces": ["ip", "type", "available"],
        "selectHostGroups": ["name"],
    })
    nas_hosts = [host for host in hosts if _is_synology_nas_host(host)]
    host_ids = [str(host["hostid"]) for host in nas_hosts]
    if not host_ids:
        return []

    items, _ = _zabbix_call(settings, "item.get", {
        "output": [
            "hostid", "name", "key_", "lastvalue", "units", "lastclock",
            "status", "state",
        ],
        "hostids": host_ids,
        "filter": {"status": "0"},
        "monitored": True,
        "selectValueMap": ["name", "mappings"],
    })
    supported = {host_id: 0 for host_id in host_ids}
    unsupported = {host_id: 0 for host_id in host_ids}
    latest_clock = {host_id: 0 for host_id in host_ids}
    metrics_by_host: dict[str, dict[str, int | float | str | bool | None]] = {
        host_id: {} for host_id in host_ids
    }
    samples_by_host: dict[str, dict[str, datetime | None]] = {
        host_id: {} for host_id in host_ids
    }
    for item in sorted(items, key=lambda row: -int(row.get("lastclock") or 0)):
        host_id = str(item.get("hostid", ""))
        if host_id not in supported:
            continue
        if str(item.get("state", "0")) == "0":
            supported[host_id] += 1
            latest_clock[host_id] = max(
                latest_clock[host_id], int(item.get("lastclock") or 0)
            )
            metric = _synology_metric_name(
                str(item.get("name", "")), str(item.get("key_", ""))
            )
            if metric and metric not in metrics_by_host[host_id]:
                value = _synology_metric_value(metric, item)
                if value is not None:
                    metrics_by_host[host_id][metric] = value
                    samples_by_host[host_id][metric] = _item_sample_time(item)
        else:
            unsupported[host_id] += 1

    results: list[NetworkDeviceHealth] = []
    for host in nas_hosts:
        host_id = str(host["hostid"])
        related = [problem for problem in problems if host_id in problem.host_ids]
        highest = max((problem.severity for problem in related), default=0)
        interfaces = host.get("interfaces", [])
        interface = next((row for row in interfaces if row.get("ip")), None)
        # Zabbix availability 2 means unavailable; 0 may be unknown during startup.
        interface_available = not interface or str(interface.get("available", "0")) != "2"
        sampled_at = (
            datetime.fromtimestamp(latest_clock[host_id], UTC)
            if latest_clock[host_id] > 0 else None
        )
        fresh = _sample_is_fresh(sampled_at)
        healthy = (
            str(host.get("status")) == "0"
            and interface_available
            and supported[host_id] > 0
            and fresh
            and highest == 0
        )
        metrics = {
            **metrics_by_host[host_id],
            "monitored_items": supported[host_id],
            "unsupported_items": unsupported[host_id],
            "active_alerts": len(related),
        }
        results.append(NetworkDeviceHealth(
            host_id=host_id,
            name=str(host.get("name") or host.get("host") or host_id),
            ip_address=str(interface.get("ip")) if interface else None,
            status="ok" if healthy else "degraded",
            message=(
                "Synology NAS monitoring data is current"
                if healthy
                else "Synology NAS has an active alert or monitoring data is unavailable or stale"
            ),
            last_updated_at=sampled_at,
            metric_sampled_at=samples_by_host[host_id],
            metrics=metrics,
        ))
    return sorted(results, key=lambda device: device.name.casefold())


NUTANIX_METRIC_NAMES = {
    "virtual machine": "virtual_machines",
    " vm ": "virtual_machines",
    "node": "nodes",
    "host count": "nodes",
    "uptime": "uptime_seconds",
}


def _nutanix_metric_name(item_name: str, item_key: str) -> str | None:
    lowered_key = item_key.lower()
    # The official Cluster/Host templates contain many CPU- and memory-related
    # cache counters. Only map the aggregate hypervisor utilization items.
    if lowered_key.endswith("hypervisor.cpu.usage.percent"):
        return "cpu"
    if lowered_key.endswith("hypervisor.memory.usage.percent"):
        return "memory"
    if lowered_key.endswith("hypervisor.name"):
        return "hypervisor_name"
    if lowered_key.endswith("general.degraded"):
        return "degraded_status"
    if lowered_key.endswith("general.cpu.model"):
        return "cpu_model"
    if lowered_key.endswith("hypervisor.cpu.cores.num"):
        return "cpu_cores"
    if lowered_key.endswith("general.memory.total.bytes"):
        return "memory_total_bytes"
    if lowered_key.endswith("general.boot.time"):
        return "boot_time"
    searchable = f" {item_name} {item_key} ".lower()
    return next(
        (metric for keyword, metric in NUTANIX_METRIC_NAMES.items() if keyword in searchable),
        None,
    )


def _nutanix_management_ip(host: dict[str, Any]) -> str | None:
    """Resolve a node IP while keeping the inherited Prism endpoint distinct."""
    interface = next(
        (row for row in host.get("interfaces", []) if row.get("ip")), None
    )
    if interface:
        return str(interface["ip"])
    prism_ip = next(
        (
            str(macro.get("value"))
            for macro in host.get("macros", [])
            if macro.get("macro") == "{$NUTANIX.PRISM.ELEMENT.IP}"
            and macro.get("value")
        ),
        None,
    )
    discovery_key = str((host.get("discoveryRule") or {}).get("key_", ""))
    if discovery_key != "nutanix.host.discovery":
        return prism_ip
    # The official template does not expose a node address. Only apply the
    # site's explicit ESXi-<last IPv4 octet> naming convention; never guess for
    # other host names or malformed addresses.
    match = re.fullmatch(r"ESXi-(\d{1,3})", str(host.get("name", "")), re.IGNORECASE)
    if not match or not prism_ip:
        return None
    try:
        address = ipaddress.IPv4Address(prism_ip)
        octet = int(match.group(1))
        if not 1 <= octet <= 254:
            return None
        return str(ipaddress.IPv4Address((int(address) & 0xFFFFFF00) | octet))
    except ipaddress.AddressValueError:
        return None


def get_nutanix_health(settings: Settings) -> list[NetworkDeviceHealth]:
    """Return Nutanix hosts discovered by host/group name and their fresh items."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    try:
        hosts, _ = _zabbix_call(
            settings,
            "host.get",
            {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "type", "available"],
                "selectHostGroups": ["name"],
                "selectParentTemplates": ["name"],
                "selectDiscoveryRule": ["name", "key_"],
                # Prism Element HTTP templates often have no host interface;
                # expose only the dedicated IP macro, never credential macros.
                "selectMacros": ["macro", "value"],
            },
        )
        nutanix_hosts = [host for host in hosts if _is_nutanix_host(host)]
        host_ids = [str(host["hostid"]) for host in nutanix_hosts]
        if not host_ids:
            return []
        items, _ = _zabbix_call(
            settings,
            "item.get",
            {
                "output": [
                    "hostid", "name", "key_", "lastvalue", "units",
                    "lastclock", "status", "state", "error",
                ],
                "hostids": host_ids,
                "filter": {"status": "0"},
                "selectValueMap": ["name", "mappings"],
            },
        )
        metrics_by_host = {host_id: {} for host_id in host_ids}
        fresh_by_host = {host_id: 0 for host_id in host_ids}
        supported_by_host = {host_id: 0 for host_id in host_ids}
        unsupported_by_host = {host_id: 0 for host_id in host_ids}
        unsupported_details_by_host: dict[str, list[str]] = {
            host_id: [] for host_id in host_ids
        }
        storage_by_host: dict[str, dict[str, dict[str, int]]] = {
            host_id: {} for host_id in host_ids
        }
        for item in items:
            host_id = str(item.get("hostid", ""))
            if host_id not in metrics_by_host:
                continue
            if str(item.get("state")) != "0":
                unsupported_by_host[host_id] += 1
                detail = str(item.get("name") or item.get("key_") or "Unknown item")
                error = str(item.get("error") or "").strip()
                unsupported_details_by_host[host_id].append(
                    f"{detail}: {error}" if error else detail
                )
                continue
            supported_by_host[host_id] += 1
            fresh_by_host[host_id] = max(
                fresh_by_host[host_id], int(item.get("lastclock") or 0)
            )
            metric = _nutanix_metric_name(
                str(item.get("name", "")), str(item.get("key_", ""))
            )
            if metric and metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = _mapped_item_value(item)
            key = str(item.get("key_", ""))
            storage_metric = next(
                (
                    metric_name
                    for key_prefix, metric_name in (
                        ("nutanix.storage.container.capacity.bytes[", "capacity"),
                        ("nutanix.storage.container.free.bytes[", "free"),
                        ("nutanix.storage.container.usage.bytes[", "used"),
                    )
                    if key.startswith(key_prefix)
                ),
                None,
            )
            if storage_metric:
                container_id = key.split("[", 1)[1]
                try:
                    storage_by_host[host_id].setdefault(container_id, {})[
                        storage_metric
                    ] = int(item.get("lastvalue") or 0)
                except (TypeError, ValueError):
                    pass

        now = int(datetime.now(UTC).timestamp())
        results: list[NetworkDeviceHealth] = []
        for host in nutanix_hosts:
            host_id = str(host["hostid"])
            data_is_fresh = fresh_by_host[host_id] >= now - 600
            enabled = str(host.get("status")) == "0"
            healthy = enabled and data_is_fresh and supported_by_host[host_id] > 0
            metrics = metrics_by_host[host_id]
            containers = storage_by_host[host_id]
            if containers:
                capacity = sum(row.get("capacity", 0) for row in containers.values())
                free = sum(row.get("free", 0) for row in containers.values())
                used = sum(row.get("used", 0) for row in containers.values())
                metrics.update({
                    "storage_containers": len(containers),
                    "storage_capacity_bytes": capacity,
                    "storage_used_bytes": used,
                    "storage_free_bytes": free,
                    "storage_utilization": round(used / capacity * 100, 1) if capacity else 0,
                })
            metrics.update({
                "supported_items": supported_by_host[host_id],
                "unsupported_items": unsupported_by_host[host_id],
            })
            results.append(NetworkDeviceHealth(
                host_id=host_id,
                name=str(host.get("name") or host.get("host") or host_id),
                ip_address=_nutanix_management_ip(host),
                status="ok" if healthy else "degraded",
                message=(
                    "Nutanix monitoring data is current"
                    if healthy else "Nutanix monitoring data is unavailable or stale"
                ),
                last_updated_at=(
                    datetime.fromtimestamp(fresh_by_host[host_id], UTC)
                    if fresh_by_host[host_id] else None
                ),
                unsupported_item_details=unsupported_details_by_host[host_id],
                metrics=metrics,
            ))
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


EXPECTED_PEPLINK_HOSTS = (
    "Peplink-A1",
    "Peplink-A2",
    "Peplink-CentralKitchen",
    "Peplink-ChouSunLeisureFarm",
    "Peplink-StaffDorm",
    "Peplink-StoreHose",
)
PEPLINK_ITEM_KEYS = {
    "system.name": "hostname",
    "system.descr": "description",
    "system.uptime": "uptime_seconds",
    "icmpping": "ping",
}


def _peplink_metric_name(item_key: str) -> str | None:
    if item_key in PEPLINK_ITEM_KEYS:
        return PEPLINK_ITEM_KEYS[item_key]
    if "[" not in item_key or not item_key.endswith("]"):
        return None
    interface_name = item_key.split("[", 1)[1][:-1]
    if item_key.startswith("wanState["):
        return f"{interface_name} 狀態"
    if item_key.startswith("wanHealthCheckState["):
        return f"{interface_name} 健康檢查"
    if item_key.startswith("pepVpnStatusConnectionState["):
        return f"SpeedFusion {interface_name}"
    return None


def _mapped_item_value(item: dict[str, Any]) -> int | float | str | None:
    """Prefer Zabbix value-map labels so vendor status codes stay readable."""
    raw_value = str(item.get("lastvalue", ""))
    value_map = item.get("valuemap") or {}
    for mapping in value_map.get("mappings", []):
        if str(mapping.get("type")) == "0" and str(mapping.get("value")) == raw_value:
            return str(mapping.get("newvalue"))
    return _metric_value(item.get("lastvalue"), str(item.get("units", "")))


def get_peplink_health(settings: Settings) -> list[NetworkDeviceHealth]:
    """Return expected Peplink devices, including explicit missing-host states."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    try:
        hosts, _ = _zabbix_call(
            settings,
            "host.get",
            {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "type", "available"],
            },
        )
        host_by_name = {
            str(host.get("name") or host.get("host")): host
            for host in hosts
            if str(host.get("name") or host.get("host")) in EXPECTED_PEPLINK_HOSTS
        }
        host_ids = [str(host["hostid"]) for host in host_by_name.values()]
        items: list[dict[str, Any]] = []
        if host_ids:
            items, _ = _zabbix_call(
                settings,
                "item.get",
                {
                    "output": [
                        "hostid", "key_", "lastvalue", "units", "status", "state", "lastclock",
                    ],
                    "hostids": host_ids,
                    "filter": {"status": "0"},
                    "selectValueMap": ["name", "mappings"],
                },
            )
        metrics_by_host: dict[str, dict[str, int | float | str | bool | None]] = {
            host_id: {} for host_id in host_ids
        }
        vpn_counts = {
            host_id: {"total": 0, "connected": 0} for host_id in host_ids
        }
        samples_by_host: dict[str, dict[str, datetime | None]] = {h: {} for h in host_ids}
        vpn_samples: dict[str, list[datetime | None]] = {h: [] for h in host_ids}
        for item in sorted(items, key=lambda row: (
            _peplink_metric_name(str(row.get("key_", ""))) or "", -int(row.get("lastclock") or 0),
        )):
            if str(item.get("state")) != "0" or str(item.get("status", "0")) != "0":
                continue
            metric = _peplink_metric_name(str(item.get("key_", "")))
            host_id = str(item.get("hostid", ""))
            if not metric or host_id not in metrics_by_host:
                continue
            value = _mapped_item_value(item)
            if metric.startswith("SpeedFusion "):
                vpn_samples[host_id].append(_item_sample_time(item))
                vpn_counts[host_id]["total"] += 1
                if value == "Connected":
                    vpn_counts[host_id]["connected"] += 1
            elif metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = value
                samples_by_host[host_id][metric] = _item_sample_time(item)

        for host_id, counts in vpn_counts.items():
            if counts["total"]:
                # A derived count is only as recent as its oldest contributing item.
                times = vpn_samples[host_id]
                oldest = min(times) if all(t is not None for t in times) else None
                for key in ("SpeedFusion 總數", "SpeedFusion 已連線", "SpeedFusion 異常"):
                    samples_by_host[host_id][key] = oldest
                metrics_by_host[host_id].update(
                    {
                        "SpeedFusion 總數": counts["total"],
                        "SpeedFusion 已連線": counts["connected"],
                        "SpeedFusion 異常": counts["total"] - counts["connected"],
                    }
                )

        results: list[NetworkDeviceHealth] = []
        for expected_name in EXPECTED_PEPLINK_HOSTS:
            host = host_by_name.get(expected_name)
            if host is None:
                results.append(
                    NetworkDeviceHealth(
                        name=expected_name,
                        status="unconfigured",
                        message="Zabbix 尚未建立此主機",
                    )
                )
                continue
            interfaces = host.get("interfaces", [])
            snmp_interface = next(
                (interface for interface in interfaces if str(interface.get("type")) == "2"),
                None,
            )
            available = bool(snmp_interface and str(snmp_interface.get("available")) == "1")
            host_id = str(host["hostid"])
            enabled = str(host.get("status")) == "0"
            samples = samples_by_host[host_id]
            latest = _latest_sample(samples)
            fresh = bool(samples) and all(_sample_is_fresh(t) for t in samples.values())
            healthy = available and enabled and fresh
            results.append(
                NetworkDeviceHealth(
                    host_id=host_id,
                    name=expected_name,
                    ip_address=str(snmp_interface.get("ip")) if snmp_interface else None,
                    status="ok" if healthy else "degraded",
                    message=(
                        "SNMP monitoring is available"
                        if healthy
                        else "SNMP monitoring is unavailable or data is stale"
                    ),
                    metrics=metrics_by_host[host_id],
                    last_updated_at=latest,
                    metric_sampled_at=samples,
                )
            )
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


# Discover every refresh; new numbered hosts and Peplink-group members need no deployment.
BRANCH_PEPLINK_HOST = re.compile(r"Peplink-0*[1-9][0-9]*", re.IGNORECASE)
HIDDEN_BRANCH_WANS = {"wi-fi wan", "wi-fi wan on 2.4 ghz", "wi-fi wan on 5 ghz", "vlan wan"}


def _is_branch_peplink(host: dict[str, Any]) -> bool:
    name = str(host.get("host", ""))
    if name.casefold() in {value.casefold() for value in EXPECTED_PEPLINK_HOSTS}:
        return False
    return bool(BRANCH_PEPLINK_HOST.fullmatch(name)) or any(
        str(group.get("name", "")).casefold() == "peplink"
        for group in host.get("hostgroups", [])
    )


def _branch_wan_name(key: str) -> str | None:
    match = re.fullmatch(r"wan(?:State|HealthCheckState)\[(.+)\]", key)
    return match[1] if match else None


def _is_backup_wan(wan: str) -> bool:
    return bool(re.fullmatch(r"(?:FET|Cellular)(?:\s+\d+)?", wan, re.IGNORECASE))


def _hidden_branch_wan(wan: str) -> bool:
    return wan.strip().casefold() in HIDDEN_BRANCH_WANS or bool(
        re.fullmatch(r"VLAN WAN\s+\d+", wan.strip(), re.IGNORECASE)
    )


BRANCH_RESOURCE_KEYS = {
    "system.cpu.util": "cpu", "system.cpu.util[,idle]": "cpu_idle",
    "vm.memory.util": "memory",
    # Template preprocessing must normalize uptime to seconds, not SNMP TimeTicks.
    "system.uptime": "uptime_seconds",
}
BRANCH_WAN_STATES = {
    "0": "Unknown", "1": "Disable", "2": "Disconnect", "3": "Connected",
    "5": "Activating", "6": "Health-check-fail", "7": "Disconnected-manually", "8": "Standby",
}


def _branch_metric_alerts(device: BranchPeplinkHealth) -> list[tuple[str, list[str], int, str]]:
    """One policy drives card colors and local events; never alarm on invalid samples."""
    if not device.enabled:
        return []
    alerts = []
    for key, value in device.metrics.items():
        if device.metric_states.get(key) != "ok" or value is None:
            continue
        if key in {"cpu", "memory"} and isinstance(value, (int, float)) and value >= 80:
            item_keys = (["system.cpu.util", "system.cpu.util[,idle]"] if key == "cpu"
                         else ["vm.memory.util"])
            alerts.append((key, item_keys, 4 if value >= 90 else 2,
                           f"{'CPU' if key == 'cpu' else 'Memory'} 使用率 {value}%"))
        elif key == "uptime_seconds" and isinstance(value, (int, float)) and value > 90 * 86400:
            alerts.append((key, ["system.uptime"], 2,
                           f"運行時間超過 90 天（{value / 86400:.2f} 天）"))
        elif key.endswith((" 狀態", " 健康檢查")):
            wan, suffix = key.rsplit(" ", 1)
            if _hidden_branch_wan(wan):
                continue
            state_key = f"{wan} 狀態"
            # A fresh disabled/standby state explains the idle health check.
            if (suffix == "健康檢查" and device.metric_states.get(state_key) == "ok"
                    and device.metrics.get(state_key) in {"Disable", "Disabled", "Standby"}):
                continue
            if value in {"Disconnect", "Disconnected", "Fail", "Health-check-fail"}:
                # A failed health check and disconnect on the same WAN form one incident.
                if (suffix == "健康檢查" and device.metric_states.get(state_key) == "ok"
                        and device.metrics.get(state_key) in {
                            "Disconnect", "Disconnected", "Health-check-fail"}):
                    continue
                alerts.append((key, [f"wanState[{wan}]", f"wanHealthCheckState[{wan}]"],
                               2, f"{wan} {suffix}: {value}"))
    return alerts


def get_branch_peplink_health(settings: Settings) -> list[BranchPeplinkHealth]:
    """Batch-read branch SNMP metrics; no per-host requests or Zabbix writes.

    Missing, unsupported and stale values stay unknown, never a fabricated 0%.
    The original six Peplink devices remain on their existing tab.
    """
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    hosts, _ = _zabbix_call(settings, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "selectHostGroups": ["name"],
        "selectInterfaces": ["ip", "type", "available"],
    })
    hosts = [host for host in hosts if _is_branch_peplink(host)]
    if not hosts:
        return []
    items, _ = _zabbix_call(settings, "item.get", {
        "output": ["itemid", "hostid", "key_", "lastvalue", "lastclock", "state", "units"],
        "hostids": [str(host["hostid"]) for host in hosts], "filter": {"status": "0"},
        "selectValueMap": ["mappings"],
    })
    by_host: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_host.setdefault(str(item["hostid"]), []).append(item)
    now = int(datetime.now(UTC).timestamp())
    result = []
    for host in sorted(hosts, key=lambda row: row["host"].lower()):
        host_id = str(host["hostid"])
        snmp = next((i for i in host.get("interfaces", []) if str(i.get("type")) == "2"), {})
        available = str(snmp.get("available")) == "1" and str(host.get("status")) == "0"
        device = BranchPeplinkHealth(
            host_id=host_id, host_name=str(host["host"]),
            name=str(host.get("name") or host["host"]),
            enabled=str(host.get("status")) == "0",
            ip_address=snmp.get("ip"), status="ok" if available else "degraded",
            message="SNMP 可用" if available else "主機已停用或 SNMP 無法連線",
            metrics={"cpu": None, "memory": None, "uptime_seconds": None},
            metric_states={"cpu": "missing", "memory": "missing", "uptime_seconds": "missing"},
        )
        # Newest sample wins if multiple equivalent resource keys are present.
        host_items = sorted(
            by_host.get(host_id, []), key=lambda row: int(row.get("lastclock") or 0)
        )
        for item in host_items:
            key = str(item.get("key_", ""))
            wan = _branch_wan_name(key)
            if wan and _hidden_branch_wan(wan):
                continue
            resource = BRANCH_RESOURCE_KEYS.get(key)
            metric = "cpu" if resource == "cpu_idle" else resource
            if not metric and key.startswith(("wanState[", "wanHealthCheckState[")):
                metric = _peplink_metric_name(key)
            if not metric:
                continue
            clock = int(item.get("lastclock") or 0)
            state = "ok"
            value = None
            if str(item.get("state")) != "0":
                state = "unsupported"
            elif clock <= 0:
                state = "unknown"
            elif clock < now - 600:
                state = "stale"
            elif resource:
                try:
                    numeric = float(item.get("lastvalue", ""))
                    if resource == "cpu_idle":
                        numeric = 100 - numeric
                    if not math.isfinite(numeric) or numeric < 0 or (
                        metric in {"cpu", "memory"} and numeric > 100
                    ):
                        raise ValueError("Invalid utilization")
                    value = round(numeric, 2)
                except (ValueError, TypeError):
                    state = "unknown"
            else:
                raw = str(item.get("lastvalue", ""))
                mapping = BRANCH_WAN_STATES if key.startswith("wanState[") else {
                    "0": "Fail", "1": "Success",
                }
                value = _mapped_item_value(item)
                if not isinstance(value, str):
                    value = mapping.get(raw, "Unknown")
                if value == "Unknown":
                    state = "unknown"
            device.metrics[metric] = value
            device.metric_states[metric] = state
            device.metric_sampled_at[metric] = (
                datetime.fromtimestamp(clock, UTC) if clock > 0 else None
            )
        times = [time for time in device.metric_sampled_at.values() if time is not None]
        device.last_updated_at = max(times) if times else None
        has_wan = any(key.endswith(" 狀態") for key in device.metrics)
        if not has_wan or any(state != "ok" for state in device.metric_states.values()):
            device.status = "degraded"
            device.message += "；部分指標尚未提供、過期或採集異常"
        if any(
            key.endswith(" 狀態") and value in {"Disconnect", "Disconnected"}
            and device.metric_states.get(key) == "ok"
            for key, value in device.metrics.items()
        ):
            device.status = "degraded"
            device.message += "；WAN 連線中斷"
        device.metric_severities = {
            key: severity for key, _, severity, _ in _branch_metric_alerts(device)
        }
        device.alert_severity = max(device.metric_severities.values(), default=0)
        if device.alert_severity:
            device.status = "degraded"
        result.append(device)
    return result


SEVERITY_LABELS = {2: "Warning", 3: "Average", 4: "High", 5: "Disaster"}


def _get_zabbix_problems(
    settings: Settings,
    severities: list[int],
    *,
    limit: int | None = None,
) -> list[MonitoringProblem]:
    """Fetch active Zabbix problems without hiding collection failures."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    params: dict[str, Any] = {
        "output": ["eventid", "objectid", "name", "severity", "clock", "acknowledged"],
        "severities": severities,
        # `recent=True` also returns recently resolved events, which made this
        # page disagree with Zabbix's current Problems view.
        "recent": False,
        "suppressed": False,
        "sortfield": ["eventid"],
        "sortorder": "DESC",
    }
    if limit is not None:
        params["limit"] = limit
    problems, _ = _zabbix_call(settings, "problem.get", params)
    trigger_ids = [str(problem.get("objectid")) for problem in problems]
    triggers, _ = (
        _zabbix_call(
            settings,
            "trigger.get",
            {
                "output": ["triggerid"],
                "triggerids": trigger_ids,
                "selectHosts": ["hostid", "name"],
                "selectItems": ["key_"],
            },
        )
        if trigger_ids
        else ([], 0)
    )
    hosts_by_trigger = {
        str(trigger.get("triggerid")): ", ".join(
            str(host.get("name")) for host in trigger.get("hosts", [])
        )
        for trigger in triggers
    }
    triggers_by_id = {str(row["triggerid"]): row for row in triggers}
    return [
        MonitoringProblem(
            event_id=str(problem.get("eventid")),
            host_name=hosts_by_trigger.get(str(problem.get("objectid")), "未知主機"),
            severity=int(problem.get("severity", 2)),
            severity_label=SEVERITY_LABELS.get(
                int(problem.get("severity", 2)), "Warning"
            ),
            occurred_at=datetime.fromtimestamp(int(problem.get("clock", 0)), UTC),
            acknowledged=str(problem.get("acknowledged")) == "1",
            message=str(problem.get("name") or "Zabbix problem"),
            host_ids=[
                str(row["hostid"])
                for row in triggers_by_id.get(
                    str(problem.get("objectid")), {}
                ).get("hosts", [])
            ],
            item_keys=[
                str(row["key_"])
                for row in triggers_by_id.get(
                    str(problem.get("objectid")), {}
                ).get("items", [])
            ],
        )
        for problem in problems
    ]


def get_high_problems(settings: Settings) -> list[MonitoringProblem]:
    """Return every active High-or-Disaster event for durable logging."""
    return _get_zabbix_problems(settings, HIGH_SEVERITIES)


def get_warning_problems(settings: Settings) -> list[MonitoringProblem]:
    """Return active Warning-or-higher Zabbix problems and their source hosts."""
    try:
        # Do not cap the snapshot: a busy device group must not push NAS alerts
        # out of the shared warning table.
        return _get_zabbix_problems(settings, WARNING_SEVERITIES)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


def apply_branch_wan_rules(
    problems: list[MonitoringProblem], devices: list[BranchPeplinkHealth],
) -> list[MonitoringProblem]:
    """Filter this page only; never acknowledge, close or modify Zabbix events.

    Local resource/WAN alerts are current observations, not persisted incident history.
    Keep Zabbix events when associations are ambiguous or samples are stale,
    except the explicitly excluded Zabbix FET Link down event name.
    """
    by_id = {device.host_id: device for device in devices}

    def excluded(device: BranchPeplinkHealth, key: str) -> bool:
        wan = _branch_wan_name(key)
        if not wan:
            return False
        if _hidden_branch_wan(wan):
            return True
        state_key = f"{wan} 狀態"
        return (_is_backup_wan(wan) and device.metric_states.get(state_key) == "ok"
                and (device.metrics.get(state_key) in {"Disable", "Disabled"}
                     or (key.startswith("wanHealthCheckState[")
                         and device.metrics.get(state_key) == "Standby")))

    visible = []
    for problem in problems:
        # Page-only exclusion, independent of host discovery or current FET state.
        # Anchor the whole event name so unrelated/mixed link alerts remain visible.
        if problem.source == "zabbix" and re.fullmatch(
            r"\s*(?:[^\r\n:：]+[:：]\s*)?FET\s+Link\s+down\s*",
            problem.message, re.IGNORECASE,
        ):
            continue
        device = by_id.get(problem.host_ids[0]) if len(problem.host_ids) == 1 else None
        if device and problem.item_keys and all(excluded(device, key) for key in problem.item_keys):
            continue
        visible.append(problem)
    for device in devices:
        device.metric_severities = {}
        device.alert_severity = 0
        if not device.enabled:
            continue
        for key, item_keys, severity, message in _branch_metric_alerts(device):
            device.metric_severities[key] = severity
            # The native incident takes precedence over the local fallback.
            if any(device.host_id in p.host_ids and set(item_keys).intersection(p.item_keys)
                   for p in visible):
                continue
            sampled_at = device.metric_sampled_at.get(key)
            if sampled_at is None:
                continue
            visible.append(MonitoringProblem(
                event_id=f"branch-metric:{device.host_id}:{key}", host_name=device.name,
                host_ids=[device.host_id], item_keys=item_keys, source="workhour",
                severity=severity, severity_label="Critical" if severity >= 4 else "Warning",
                occurred_at=sampled_at, acknowledged=False,
                message=f"{message}（本頁規則；目前取樣）",
            ))
        for problem in visible:
            if device.host_id not in problem.host_ids:
                continue
            device.alert_severity = max(device.alert_severity, problem.severity)
            # Multi-host trigger keys cannot safely be attributed to one card metric.
            if len(problem.host_ids) != 1:
                continue
            for item_key in problem.item_keys:
                resource = BRANCH_RESOURCE_KEYS.get(item_key)
                metric = "cpu" if resource == "cpu_idle" else resource
                if not metric and _branch_wan_name(item_key):
                    metric = _peplink_metric_name(item_key)
                if metric in device.metrics:
                    device.metric_severities[metric] = max(
                        device.metric_severities.get(metric, 0), problem.severity)
        device.alert_severity = max(
            device.alert_severity, max(device.metric_severities.values(), default=0)
        )
        if device.alert_severity:
            device.status = "degraded"
    return sorted(visible, key=lambda row: row.occurred_at, reverse=True)


# Match only the audited custom collector contract. Unknown MSSQL keys may
# contain raw responses, so do not send them to the browser automatically.
MSSQL_KEY = re.compile(
    r'^mssql\.([\w-]+)\.(version|service|agent|db\.(?:state|recovery|logused|'
    r'fullbackup\.age|logbackup\.age))(?:\["([^"\r\n]+)"\])?$'
)
MSSQL_LABELS = {
    "version": "SQL Server 版本", "service": "SQL Server 服務",
    "agent": "SQL Server Agent", "db.state": "資料庫狀態",
    "db.recovery": "復原模式", "db.logused": "Transaction Log 使用率",
    "db.fullbackup.age": "Full Backup 距今", "db.logbackup.age": "Log Backup 距今",
}


def get_mssql_health(settings: Settings) -> list[MssqlHealth]:
    """Read existing collectors without renaming keys or modifying Zabbix objects.

    Freshness is checked per item; a fresh service sample must not hide an old
    backup sample. Threshold severity comes from active Zabbix problems, not a
    second set of backup/log thresholds maintained in the Vue application.
    """
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    items, _ = _zabbix_call(settings, "item.get", {
        "output": ["itemid", "hostid", "key_", "lastvalue", "lastclock", "state", "status"],
        "search": {"key_": "mssql."}, "startSearch": True,
        "monitored": True, "selectHosts": ["hostid", "host", "name"],
    })
    selected = [(item, MSSQL_KEY.fullmatch(str(item.get("key_", "")))) for item in items]
    selected = [(item, match) for item, match in selected if match is not None
                and bool(match[2].startswith("db.")) == bool(match[3])]
    if not selected:
        return []
    host_ids = sorted({str(item["hostid"]) for item, _ in selected})
    problems, _ = _zabbix_call(settings, "problem.get", {
        "output": ["eventid", "objectid", "name", "severity", "clock", "acknowledged"],
        "hostids": host_ids, "severities": WARNING_SEVERITIES,
        "recent": False, "suppressed": False,
    })
    trigger_ids = list({str(row["objectid"]) for row in problems})
    triggers, _ = _zabbix_call(settings, "trigger.get", {
        "output": ["triggerid"], "triggerids": trigger_ids,
        "selectFunctions": ["itemid"],
    }) if trigger_ids else ([], 0)
    item_ids_by_trigger = {
        str(row["triggerid"]): {str(fn["itemid"]) for fn in row.get("functions", [])}
        for row in triggers
    }
    now = int(datetime.now(UTC).timestamp())
    grouped: dict[tuple[str, str], MssqlHealth] = {}
    for item, match in selected:
        host_id, instance, kind, database = str(item["hostid"]), match[1], match[2], match[3]
        host = next((h for h in item.get("hosts", []) if str(h["hostid"]) == host_id), {})
        group = grouped.setdefault((host_id, instance), MssqlHealth(
            host_id=host_id, name=str(host.get("name") or host.get("host") or host_id),
            host_name=str(host.get("host") or host_id), instance=instance, status="ok",
        ))
        item_id = str(item["itemid"])
        related = [p for p in problems
                   if item_id in item_ids_by_trigger.get(str(p["objectid"]), set())]
        severity = max((int(p["severity"]) for p in related), default=0)
        clock = int(item.get("lastclock") or 0)
        value: int | float | str | None = None
        state = "ok"
        if str(item.get("state")) != "0":
            state = "unsupported"
        elif clock <= 0:
            state = "unknown"
        else:
            # Version/recovery mode are collected less often than live health.
            max_age = {"version": 86400, "db.recovery": 3600,
                       "db.fullbackup.age": 900}.get(kind, 300)
            state = "stale" if clock < now - max_age else "ok"
            if kind == "version":
                raw = str(item.get("lastvalue", ""))
                value = raw if re.fullmatch(r"\d+(?:\.\d+){1,4}", raw) else None
            else:
                try:
                    numeric = float(item.get("lastvalue", ""))
                    if math.isfinite(numeric) and numeric >= 0:
                        value = round(numeric, 4)
                except (ValueError, TypeError):
                    pass
            if value is None:
                state = "unknown"
            elif state == "ok":
                failed = (kind in {"service", "agent"} and value != 1) or (
                    kind == "db.state" and value != 0
                )
                state = "critical" if failed or severity >= 4 else (
                    "warning" if severity >= 2 else "ok"
                )
        if state != "ok" or severity:
            group.status = "degraded"
        group.metrics.append(MssqlMetric(
            item_id=item_id, key=kind, label=f"{database} · {MSSQL_LABELS[kind]}"
            if database else MSSQL_LABELS[kind], value=value,
            units="%" if kind == "db.logused" else "s" if kind.endswith(".age") else "",
            sampled_at=datetime.fromtimestamp(clock, UTC) if clock > 0 else None,
            status=state, severity=severity,
        ))
        for problem in related:
            if any(p.event_id == str(problem["eventid"]) for p in group.problems):
                continue
            group.problems.append(MonitoringProblem(
                event_id=str(problem["eventid"]), host_name=group.name,
                severity=int(problem["severity"]),
                severity_label=SEVERITY_LABELS[int(problem["severity"])],
                occurred_at=datetime.fromtimestamp(int(problem["clock"]), UTC),
                acknowledged=str(problem.get("acknowledged")) == "1",
                message=str(problem["name"]),
            ))
    for group in grouped.values():
        group.metrics.sort(key=lambda metric: (list(MSSQL_LABELS).index(metric.key), metric.label))
    return sorted(grouped.values(), key=lambda group: (group.name, group.instance))


def build_monitoring_summary(settings: Settings) -> MonitoringSummary:
    integrations = [check_zabbix(settings)]
    firewalls = get_fortigate_health(settings)
    peplinks = get_peplink_health(settings)
    branch_peplinks_error = None
    try:
        branch_peplinks = get_branch_peplink_health(settings)
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        branch_peplinks = []
        branch_peplinks_error = _connection_failure_message("Branch Peplink", error)
    servers = get_server_health(settings)
    nutanix = get_nutanix_health(settings)
    problems = apply_branch_wan_rules(get_warning_problems(settings), branch_peplinks)
    synology_nas_error = None
    try:
        synology_nas = get_synology_nas_health(settings, problems)
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        synology_nas = []
        synology_nas_error = _connection_failure_message("Synology NAS monitoring", error)
    for integration in integrations:
        if integration.name == "zabbix" and integration.status == "ok":
            integration.metrics["active_problems"] = len(problems)
    mssql_error = None
    try:
        mssql = get_mssql_health(settings)
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        # An API failure must not look like zero healthy SQL servers.
        mssql = []
        mssql_error = _connection_failure_message("MSSQL monitoring", error)
    states = {integration.status for integration in integrations}
    resources = [
        *firewalls, *servers, *peplinks, *branch_peplinks,
        *synology_nas, *nutanix, *mssql,
    ]
    if (
        "degraded" in states
        or any(resource.status == "degraded" for resource in resources)
        or problems
        or mssql_error
        or branch_peplinks_error
        or synology_nas_error
    ):
        overall = "degraded"
    elif states == {"unconfigured"}:
        overall = "unconfigured"
    else:
        overall = "ok"
    return MonitoringSummary(
        status=overall,
        checked_at=datetime.now(UTC),
        integrations=integrations,
        firewalls=firewalls,
        peplinks=peplinks,
        branch_peplinks=branch_peplinks,
        branch_peplinks_error=branch_peplinks_error,
        servers=servers,
        synology_nas=synology_nas,
        synology_nas_error=synology_nas_error,
        nutanix=nutanix,
        mssql=mssql,
        mssql_error=mssql_error,
        problems=problems,
    )
