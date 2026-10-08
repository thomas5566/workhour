import { reactive } from "vue";

import { getMonitoringSummaryAPI } from "@/service/apis";
import { getCriticalProblemCount, getSpeedFusionDrop } from "@/utils/monitoringAlerts";

const emptySummary = () => ({
  status: "unconfigured",
  checked_at: null,
  integrations: [
    { name: "zabbix", configured: false, status: "unconfigured", message: "尚未檢查", latency_ms: null, metrics: {} },
  ],
  firewalls: [],
  peplinks: [],
  branch_peplinks: [],
  branch_peplinks_error: null,
  servers: [],
  synology_nas: [],
  synology_nas_error: null,
  nutanix: [],
  mssql: [],
  mssql_error: null,
  problems: [],
});

export const monitoringState = reactive({
  summary: emptySummary(),
  loading: false,
  errorMessage: "",
  criticalProblemCount: 0,
  speedFusionDrops: {},
});

let refreshTimer = null;
let activeRequest = null;

function updateSpeedFusionDrops(nextDevices) {
  const previousCounts = Object.fromEntries(
    monitoringState.summary.peplinks.map((device) => [
      device.name,
      Number(device.metrics["SpeedFusion 已連線"]),
    ]),
  );
  const nextDrops = {};
  nextDevices.forEach((device) => {
    const drop = getSpeedFusionDrop(
      previousCounts[device.name],
      Number(device.metrics["SpeedFusion 已連線"]),
      Number(device.metrics["SpeedFusion 總數"]),
    );
    if (drop) nextDrops[device.name] = drop;
  });
  monitoringState.speedFusionDrops = nextDrops;
}

export function refreshMonitoring({ foreground = false } = {}) {
  // Reuse an in-flight request so Sidebar and the monitoring page never poll twice.
  if (activeRequest) return activeRequest;

  monitoringState.loading = true;
  monitoringState.errorMessage = "";
  activeRequest = getMonitoringSummaryAPI({
    background: !foreground,
    silent: !foreground,
  })
    .then((response) => {
      const summary = response.data;
      updateSpeedFusionDrops(summary.peplinks || []);
      monitoringState.summary = summary;
      monitoringState.criticalProblemCount = getCriticalProblemCount(summary.problems);
      return true;
    })
    .catch((error) => {
      monitoringState.criticalProblemCount = 0;
      monitoringState.errorMessage = error.response?.status === 403
        ? "此頁面僅供管理員使用。"
        : "監控 API 暫時無法使用，請稍後再試。";
      // Background timers must not create an unhandled rejected Promise.
      return false;
    })
    .finally(() => {
      monitoringState.loading = false;
      activeRequest = null;
    });
  return activeRequest;
}

export function startMonitoringPolling() {
  if (refreshTimer) return;
  void refreshMonitoring();
  refreshTimer = window.setInterval(() => {
    void refreshMonitoring();
  }, 60000);
}

export function stopMonitoringPolling() {
  if (refreshTimer) window.clearInterval(refreshTimer);
  refreshTimer = null;
}
