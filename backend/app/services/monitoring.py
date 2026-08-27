import ipaddress
import json
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
    FirewallHealth,
    IntegrationHealth,
    MonitoringProblem,
    MonitoringSummary,
    NetworkDeviceHealth,
    ServerHealth,
)

# Zabbix severities 2 through 5 represent Warning, Average, High, and Disaster.
# Use one definition for both the overview counter and the event table so the UI
# cannot report different totals for the same set of active incidents.
WARNING_SEVERITIES = [2, 3, 4, 5]


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
                "output": ["hostid", "key_", "lastvalue", "units", "status", "state"],
                "hostids": host_ids,
            },
        )
        metrics_by_host: dict[str, dict[str, int | float | str | bool | None]] = {
            host_id: {} for host_id in host_ids
        }
        for item in items:
            if str(item.get("status")) != "0" or str(item.get("state")) != "0":
                continue
            metric = _metric_name(str(item.get("key_", "")))
            host_id = str(item.get("hostid", ""))
            if metric and host_id in metrics_by_host and metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = _metric_value(
                    item.get("lastvalue"), str(item.get("units", ""))
                )

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
            has_core_metrics = "memory" in metrics and "uptime_seconds" in metrics
            healthy = available and has_core_metrics and str(host.get("status")) == "0"
            results.append(
                FirewallHealth(
                    host_id=host_id,
                    name=str(host.get("name") or host.get("host") or host_id),
                    ip_address=str(snmp_interface.get("ip")) if snmp_interface else None,
                    status="ok" if healthy else "degraded",
                    message=(
                        "SNMP monitoring is available"
                        if healthy
                        else "SNMP or core monitoring items are unavailable"
                    ),
                    metrics=metrics,
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
        latest_by_host = {host_id: 0 for host_id in host_ids}
        for item in items:
            if str(item.get("state")) != "0":
                continue
            key = str(item.get("key_", ""))
            metric = _server_metric_name(key)
            host_id = str(item.get("hostid", ""))
            if metric and host_id in metrics_by_host and metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = _metric_value(
                    item.get("lastvalue"), str(item.get("units", ""))
                )
            if host_id in latest_by_host:
                latest_by_host[host_id] = max(
                    latest_by_host[host_id], int(item.get("lastclock") or 0)
                )

        now = int(datetime.now(UTC).timestamp())
        results: list[ServerHealth] = []
        for host in server_hosts:
            host_id = str(host["hostid"])
            interfaces = host.get("interfaces", [])
            interface = next((row for row in interfaces if row.get("ip")), None)
            metrics = metrics_by_host[host_id]
            data_is_fresh = latest_by_host[host_id] >= now - 600
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
                )
            )
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


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
            if "peplink" in f"{host.get('host', '')} {host.get('name', '')}".lower()
        }
        host_ids = [str(host["hostid"]) for host in host_by_name.values()]
        items: list[dict[str, Any]] = []
        if host_ids:
            items, _ = _zabbix_call(
                settings,
                "item.get",
                {
                    "output": ["hostid", "key_", "lastvalue", "units", "status", "state"],
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
        for item in items:
            if str(item.get("state")) != "0":
                continue
            metric = _peplink_metric_name(str(item.get("key_", "")))
            host_id = str(item.get("hostid", ""))
            if not metric or host_id not in metrics_by_host:
                continue
            value = _mapped_item_value(item)
            if metric.startswith("SpeedFusion "):
                vpn_counts[host_id]["total"] += 1
                if value == "Connected":
                    vpn_counts[host_id]["connected"] += 1
            elif metric not in metrics_by_host[host_id]:
                metrics_by_host[host_id][metric] = value

        for host_id, counts in vpn_counts.items():
            if counts["total"]:
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
            results.append(
                NetworkDeviceHealth(
                    host_id=host_id,
                    name=expected_name,
                    ip_address=str(snmp_interface.get("ip")) if snmp_interface else None,
                    status="ok" if available and enabled else "degraded",
                    message=(
                        "SNMP monitoring is available"
                        if available and enabled
                        else "SNMP monitoring is unavailable"
                    ),
                    metrics=metrics_by_host[host_id],
                )
            )
        return results
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


SEVERITY_LABELS = {2: "Warning", 3: "Average", 4: "High", 5: "Disaster"}


def get_warning_problems(settings: Settings) -> list[MonitoringProblem]:
    """Return active Warning-or-higher Zabbix problems and their source hosts."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return []
    try:
        problems, _ = _zabbix_call(
            settings,
            "problem.get",
            {
                "output": ["eventid", "objectid", "name", "severity", "clock", "acknowledged"],
                "severities": WARNING_SEVERITIES,
                # `recent=True` also returns recently resolved events, which
                # made this page disagree with Zabbix's current Problems view.
                "recent": False,
                "suppressed": False,
                "sortfield": ["eventid"],
                "sortorder": "DESC",
                "limit": 100,
            },
        )
        trigger_ids = [str(problem.get("objectid")) for problem in problems]
        triggers, _ = _zabbix_call(
            settings,
            "trigger.get",
            {
                "output": ["triggerid"],
                "triggerids": trigger_ids,
                "selectHosts": ["hostid", "name"],
            },
        ) if trigger_ids else ([], 0)
        hosts_by_trigger = {
            str(trigger.get("triggerid")): ", ".join(
                str(host.get("name")) for host in trigger.get("hosts", [])
            )
            for trigger in triggers
        }
        return [
            MonitoringProblem(
                event_id=str(problem.get("eventid")),
                host_name=hosts_by_trigger.get(str(problem.get("objectid")), "未知主機"),
                severity=int(problem.get("severity", 2)),
                severity_label=SEVERITY_LABELS.get(int(problem.get("severity", 2)), "Warning"),
                occurred_at=datetime.fromtimestamp(int(problem.get("clock", 0)), UTC),
                acknowledged=str(problem.get("acknowledged")) == "1",
                message=str(problem.get("name") or "Zabbix problem"),
            )
            for problem in problems
        ]
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return []


def build_monitoring_summary(settings: Settings) -> MonitoringSummary:
    integrations = [check_zabbix(settings)]
    firewalls = get_fortigate_health(settings)
    peplinks = get_peplink_health(settings)
    servers = get_server_health(settings)
    nutanix = get_nutanix_health(settings)
    problems = get_warning_problems(settings)
    states = {integration.status for integration in integrations}
    resources = [*firewalls, *servers, *peplinks, *nutanix]
    if (
        "degraded" in states
        or any(resource.status == "degraded" for resource in resources)
        or problems
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
        servers=servers,
        nutanix=nutanix,
        problems=problems,
    )
