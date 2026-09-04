from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

IntegrationState = Literal["ok", "degraded", "unconfigured"]


class IntegrationHealth(BaseModel):
    name: Literal["zabbix", "firewall"]
    configured: bool
    status: IntegrationState
    message: str
    latency_ms: int | None = Field(default=None, ge=0)
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class FirewallHealth(BaseModel):
    host_id: str
    name: str
    ip_address: str | None = None
    status: IntegrationState
    message: str
    last_updated_at: datetime | None = None
    metric_sampled_at: dict[str, datetime | None] = Field(default_factory=dict)
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class ServerHealth(BaseModel):
    host_id: str
    name: str
    host_name: str
    ip_address: str | None = None
    group_names: list[str] = Field(default_factory=list)
    status: IntegrationState
    message: str
    last_updated_at: datetime | None = None
    metric_sampled_at: dict[str, datetime | None] = Field(default_factory=dict)
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class NetworkDeviceHealth(BaseModel):
    host_id: str | None = None
    name: str
    ip_address: str | None = None
    status: IntegrationState
    message: str
    last_updated_at: datetime | None = None
    metric_sampled_at: dict[str, datetime | None] = Field(default_factory=dict)
    unsupported_item_details: list[str] = Field(default_factory=list)
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class BranchPeplinkHealth(NetworkDeviceHealth):
    """Track freshness per metric so a live WAN cannot hide stale resource data."""

    host_name: str
    enabled: bool = True
    # Alert severity is independent of sample quality (missing/stale is not 0%).
    alert_severity: int = Field(default=0, ge=0, le=5)
    metric_severities: dict[str, int] = Field(default_factory=dict)
    metric_states: dict[str, Literal["ok", "missing", "stale", "unsupported", "unknown"]] = (
        Field(default_factory=dict)
    )
    metric_sampled_at: dict[str, datetime | None] = Field(default_factory=dict)


class MonitoringProblem(BaseModel):
    event_id: str
    host_name: str
    severity: int = Field(ge=2, le=5)
    severity_label: str
    occurred_at: datetime
    acknowledged: bool
    message: str
    source: Literal["zabbix", "workhour"] = "zabbix"
    # Exact trigger associations prevent text matching from hiding unrelated alarms.
    host_ids: list[str] = Field(default_factory=list)
    item_keys: list[str] = Field(default_factory=list)


class MssqlMetric(BaseModel):
    """Expose an allowlisted SQL metric, never the collector script or credentials."""

    item_id: str
    key: str
    label: str
    value: int | float | str | None = None
    units: str = ""
    sampled_at: datetime | None = None
    status: Literal["ok", "warning", "critical", "unknown", "stale", "unsupported"]
    severity: int = Field(default=0, ge=0, le=5)


class MssqlHealth(BaseModel):
    host_id: str
    name: str
    host_name: str
    instance: str
    status: IntegrationState
    metrics: list[MssqlMetric] = Field(default_factory=list)
    problems: list[MonitoringProblem] = Field(default_factory=list)


class MonitoringSummary(BaseModel):
    status: IntegrationState
    checked_at: datetime
    integrations: list[IntegrationHealth]
    firewalls: list[FirewallHealth] = Field(default_factory=list)
    peplinks: list[NetworkDeviceHealth] = Field(default_factory=list)
    branch_peplinks: list[BranchPeplinkHealth] = Field(default_factory=list)
    branch_peplinks_error: str | None = None
    servers: list[ServerHealth] = Field(default_factory=list)
    nutanix: list[NetworkDeviceHealth] = Field(default_factory=list)
    mssql: list[MssqlHealth] = Field(default_factory=list)
    mssql_error: str | None = None
    problems: list[MonitoringProblem] = Field(default_factory=list)
