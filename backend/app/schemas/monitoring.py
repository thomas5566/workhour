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
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class ServerHealth(BaseModel):
    host_id: str
    name: str
    host_name: str
    ip_address: str | None = None
    group_names: list[str] = Field(default_factory=list)
    status: IntegrationState
    message: str
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class NetworkDeviceHealth(BaseModel):
    host_id: str | None = None
    name: str
    ip_address: str | None = None
    status: IntegrationState
    message: str
    last_updated_at: datetime | None = None
    unsupported_item_details: list[str] = Field(default_factory=list)
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)


class MonitoringProblem(BaseModel):
    event_id: str
    host_name: str
    severity: int = Field(ge=2, le=5)
    severity_label: str
    occurred_at: datetime
    acknowledged: bool
    message: str


class MonitoringSummary(BaseModel):
    status: IntegrationState
    checked_at: datetime
    integrations: list[IntegrationHealth]
    firewalls: list[FirewallHealth] = Field(default_factory=list)
    peplinks: list[NetworkDeviceHealth] = Field(default_factory=list)
    servers: list[ServerHealth] = Field(default_factory=list)
    nutanix: list[NetworkDeviceHealth] = Field(default_factory=list)
    problems: list[MonitoringProblem] = Field(default_factory=list)
