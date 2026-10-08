<template>
  <section class="monitoring-page" aria-labelledby="monitoring-title">
    <header class="monitoring-header">
      <div>
        <p class="eyebrow">INFRASTRUCTURE HEALTH</p>
        <h1 id="monitoring-title">基礎設施監控</h1>
        <p class="subtitle">由 Zabbix 統一提供 Server、MSSQL 與網路設備唯讀健康狀態</p>
      </div>
      <button class="refresh-button" type="button" :disabled="loading" @click="loadSummary">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        {{ loading ? "檢查中" : "立即更新" }}
      </button>
    </header>

    <div v-if="errorMessage" class="monitoring-alert" role="alert">
      <i class="fas fa-exclamation-triangle"></i>
      <div>
        <strong>無法取得監控資訊</strong>
        <p>{{ errorMessage }}</p>
      </div>
    </div>

    <div class="summary-strip">
      <span class="status-dot" :class="`status-${summary.status}`"></span>
      <div>
        <strong>{{ overallLabel }}</strong>
        <small>最後更新：{{ formattedCheckedAt }}</small>
      </div>
      <span class="auto-refresh">背景每 60 秒自動更新</span>
    </div>

    <nav class="monitoring-tabs" aria-label="監控類型">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>{{ tab.label }}
        <span v-if="tab.count != null">{{ tab.count }}</span>
      </button>
    </nav>

    <div v-if="activeTab === 'overview'" class="integration-grid" :aria-busy="loading">
      <article v-for="integration in summary.integrations" :key="integration.name" class="integration-card">
        <div class="card-topline" :class="`accent-${integration.status}`"></div>
        <header class="card-header">
          <div class="service-icon" :class="integration.name">
            <i :class="integration.name === 'zabbix' ? 'fas fa-chart-line' : 'fas fa-shield-alt'"></i>
          </div>
          <div>
            <p class="service-kicker">{{ integration.name === "zabbix" ? "MONITORING" : "SECURITY" }}</p>
            <h2>{{ integration.name === "zabbix" ? "Zabbix Server" : "防火牆" }}</h2>
          </div>
          <span class="status-pill" :class="`status-${integration.status}`">
            {{ statusLabel(integration.status) }}
          </span>
        </header>

        <p class="service-message">{{ integration.message }}</p>

        <div v-if="Object.keys(integration.metrics).length" class="metric-grid">
          <div v-for="(value, key) in integration.metrics" :key="key" class="metric">
            <span>{{ metricLabel(key) }}</span>
            <strong>{{ displayValue(value, key) }}</strong>
          </div>
        </div>
        <div v-else class="empty-state">
          <i class="fas fa-plug"></i>
          <p>{{ integration.configured ? "目前沒有可顯示的健康指標" : "請在 Backend 環境變數設定此整合" }}</p>
        </div>

        <footer class="card-footer">
          <span><i class="far fa-clock"></i> 回應時間</span>
          <strong>{{ integration.latency_ms == null ? "—" : `${integration.latency_ms} ms` }}</strong>
        </footer>
      </article>
    </div>

    <section v-if="activeTab === 'firewalls'" class="firewall-section" aria-labelledby="firewall-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">FORTIGATE DEVICES</p>
          <h2 id="firewall-title">FortiGate 健康狀態</h2>
        </div>
        <span>{{ summary.firewalls.length }} 台設備</span>
      </header>
      <div class="firewall-grid">
        <article v-for="firewall in summary.firewalls" :key="firewall.host_id" class="firewall-card">
          <header>
            <div>
              <h3>{{ firewall.name }}</h3>
              <small>{{ firewall.ip_address || "未提供管理 IP" }}</small>
            </div>
            <span class="status-pill" :class="`status-${firewall.status}`">
              {{ statusLabel(firewall.status) }}
            </span>
          </header>
          <p>{{ firewall.message }}</p>
          <MonitoringSampleTime :sampled-at="firewall.last_updated_at" :reference-time="summary.checked_at" label="Zabbix 最新指標取樣" />
          <div class="firewall-metrics">
            <div v-for="(value, key) in firewall.metrics" :key="key">
              <span>{{ metricLabel(key) }}</span>
              <strong>{{ displayValue(value, key) }}</strong>
              <MonitoringSampleTime :sampled-at="firewall.metric_sampled_at?.[key]" :reference-time="summary.checked_at" />
            </div>
          </div>
        </article>
      </div>
      <div v-if="!summary.firewalls.length" class="page-empty">Zabbix 中沒有 FortiGate 監控資料。</div>
    </section>

    <section v-if="activeTab === 'servers'" class="firewall-section" aria-labelledby="server-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">VIRTUAL MACHINES</p>
          <h2 id="server-title">VM Server 狀態</h2>
        </div>
        <span>{{ summary.servers.length }} 台主機</span>
      </header>
      <div class="firewall-grid">
        <article v-for="server in summary.servers" :key="server.host_id" class="firewall-card">
          <header>
            <div>
              <h3>{{ server.name }}</h3>
              <small>{{ server.ip_address || server.host_name }}</small>
            </div>
            <span class="status-pill" :class="`status-${server.status}`">
              {{ statusLabel(server.status) }}
            </span>
          </header>
          <p>{{ server.message }}</p>
          <MonitoringSampleTime :sampled-at="server.last_updated_at" :reference-time="summary.checked_at" label="Zabbix 最新指標取樣" />
          <div v-if="server.group_names.length" class="group-list">
            <span v-for="group in server.group_names" :key="group">{{ group }}</span>
          </div>
          <div class="firewall-metrics">
            <div
              v-for="(value, key) in server.metrics"
              :key="key"
              :class="metricStatusClass(key, value)"
            >
              <span>{{ metricLabel(key) }}</span>
              <strong>{{ displayValue(value, key) }}</strong>
              <MonitoringSampleTime :sampled-at="server.metric_sampled_at?.[key]" :reference-time="summary.checked_at" />
            </div>
          </div>
        </article>
      </div>
      <div v-if="!summary.servers.length" class="page-empty">Zabbix 中沒有 VM Server 監控資料。</div>
    </section>

    <section v-if="activeTab === 'synology-nas'" class="firewall-section" aria-labelledby="synology-nas-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">NETWORK ATTACHED STORAGE</p>
          <h2 id="synology-nas-title">Synology NAS 健康狀態</h2>
        </div>
        <span>{{ (summary.synology_nas || []).length }} 台設備</span>
      </header>
      <div v-if="summary.synology_nas_error" class="monitoring-alert" role="alert">
        <i class="fas fa-exclamation-triangle"></i>
        <div><strong>無法取得 Synology NAS 資料</strong><p>{{ summary.synology_nas_error }}</p></div>
      </div>
      <div class="firewall-grid">
        <article v-for="nas in summary.synology_nas || []" :key="nas.host_id" class="firewall-card">
          <header>
            <div>
              <h3>{{ nas.name }}</h3>
              <small>{{ nas.ip_address || "未提供管理 IP" }}</small>
            </div>
            <span class="status-pill" :class="`status-${nas.status}`">
              {{ statusLabel(nas.status) }}
            </span>
          </header>
          <p>{{ nas.message }}</p>
          <MonitoringSampleTime :sampled-at="nas.last_updated_at" :reference-time="summary.checked_at" label="Zabbix 最新指標取樣" />
          <div class="firewall-metrics">
            <div
              v-for="(value, key) in nas.metrics"
              :key="key"
              :class="metricStatusClass(key, value)"
            >
              <span>{{ metricLabel(key) }}</span>
              <strong>{{ displayValue(value, key) }}</strong>
              <MonitoringSampleTime :sampled-at="nas.metric_sampled_at?.[key]" :reference-time="summary.checked_at" />
            </div>
          </div>
        </article>
      </div>
      <div v-if="!summary.synology_nas_error && !(summary.synology_nas || []).length" class="page-empty">
        Zabbix API 尚未取得「Synology NAS」Host group 資料，請確認 API 使用者具有 Read 權限。
      </div>
    </section>

    <BranchPeplinkMonitoring v-if="activeTab === 'branch-peplinks'" :devices="summary.branch_peplinks || []" :error="summary.branch_peplinks_error || ''" />
    <MssqlMonitoring v-if="activeTab === 'mssql'" :servers="summary.mssql || []" :error="summary.mssql_error || ''" />
    <AlertLogHistory v-if="activeTab === 'logs'" />

    <section v-if="activeTab === 'nutanix'" class="firewall-section" aria-labelledby="nutanix-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">HYPERCONVERGED INFRASTRUCTURE</p>
          <h2 id="nutanix-title">Nutanix 健康狀態</h2>
        </div>
        <span>{{ summary.nutanix.length }} 台主機</span>
      </header>
      <div class="firewall-grid">
        <article v-for="host in summary.nutanix" :key="host.host_id" class="firewall-card">
          <header>
            <div>
              <h3>{{ host.name }}</h3>
              <small>{{ host.ip_address || "未提供管理 IP" }}</small>
            </div>
            <span class="status-pill" :class="`status-${host.status}`">
              {{ statusLabel(host.status) }}
            </span>
          </header>
          <p>{{ host.message }}</p>
          <p v-if="host.last_updated_at" class="sample-time">
            <i class="far fa-clock"></i> 指標取樣：{{ formatDate(host.last_updated_at) }}
          </p>
          <div class="firewall-metrics">
            <div
              v-for="(value, key) in host.metrics"
              :key="key"
              :class="metricStatusClass(key, value)"
            >
              <span>{{ metricLabel(key) }}</span>
              <strong>{{ displayValue(value, key) }}</strong>
            </div>
          </div>
          <details v-if="host.unsupported_item_details?.length" class="unsupported-details">
            <summary>查看 {{ host.unsupported_item_details.length }} 個不支援項目</summary>
            <ul>
              <li v-for="detail in host.unsupported_item_details" :key="detail">{{ detail }}</li>
            </ul>
          </details>
        </article>
      </div>
      <div v-if="!summary.nutanix.length" class="page-empty">Zabbix 中沒有 Nutanix Host 或 Host group 資料。</div>
    </section>

    <section v-if="activeTab === 'peplinks'" class="firewall-section" aria-labelledby="peplink-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">PEPLINK DEVICES</p>
          <h2 id="peplink-title">Peplink 健康狀態</h2>
        </div>
        <span>{{ summary.peplinks.length }} 台設備</span>
      </header>
      <div class="firewall-grid">
        <article
          v-for="device in summary.peplinks"
          :key="device.name"
          class="firewall-card"
          :class="{ 'speedfusion-drop': speedFusionDrops[device.name] }"
        >
          <header>
            <div>
              <h3>{{ device.name }}</h3>
              <small>{{ device.ip_address || "尚未取得管理 IP" }}</small>
            </div>
            <span class="status-pill" :class="`status-${device.status}`">
              {{ statusLabel(device.status) }}
            </span>
          </header>
          <div v-if="speedFusionDrops[device.name]" class="speedfusion-alert" role="alert">
            <i class="fas fa-exclamation-triangle"></i>
            SpeedFusion 已連線數由 {{ speedFusionDrops[device.name].previous }} 降至
            {{ speedFusionDrops[device.name].current }}
          </div>
          <p>{{ device.message }}</p>
          <MonitoringSampleTime :sampled-at="device.last_updated_at" :reference-time="summary.checked_at" label="Zabbix 最新指標取樣" />
          <div v-if="Object.keys(device.metrics).length" class="firewall-metrics">
            <div
              v-for="(value, key) in device.metrics"
              :key="key"
              :class="metricStatusClass(key, value)"
            >
              <span>{{ metricLabel(key) }}</span>
              <strong>{{ displayValue(value, key) }}</strong>
              <MonitoringSampleTime :sampled-at="device.metric_sampled_at?.[key]" :reference-time="summary.checked_at" />
            </div>
          </div>
          <div v-else class="device-empty">建立 Zabbix Host 並連接 SNMP Template 後自動顯示指標。</div>
        </article>
      </div>
    </section>

    <section v-if="activeTab === 'problems'" class="problem-section" aria-labelledby="problem-title">
      <header class="section-heading">
        <div>
          <p class="eyebrow">WARNING AND ABOVE</p>
          <h2 id="problem-title">Warning 等級以上事件</h2>
        </div>
        <span>{{ summary.problems.length }} 筆未結事件</span>
      </header>
      <div class="problem-table-wrap">
        <table v-if="summary.problems.length" class="problem-table">
          <thead><tr><th>等級</th><th>主機</th><th>來源</th><th>事件內容</th><th>發生／觀測時間</th><th>確認</th></tr></thead>
          <tbody>
            <tr v-for="problem in summary.problems" :key="problem.event_id">
              <td><span class="severity" :class="`severity-${problem.severity}`">{{ problem.severity_label }}</span></td>
              <td>{{ problem.host_name }}</td>
              <td>{{ problem.source === 'workhour' ? '本頁規則' : 'Zabbix' }}</td>
              <td>{{ problem.message }}</td>
              <td>{{ formatDate(problem.occurred_at) }}</td>
              <td>{{ problem.source === 'workhour' ? '不適用' : problem.acknowledged ? "已確認" : "未確認" }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="page-empty">目前沒有 Warning 等級以上的未結事件。</div>
      </div>
    </section>
  </section>
</template>

<script>
import {
  monitoringState,
  refreshMonitoring,
  startMonitoringPolling,
} from "@/service/monitoringBackground";
import { getResourceUtilizationClass } from "@/utils/monitoringAlerts";
import MssqlMonitoring from "@/components/MssqlMonitoring.vue";
import BranchPeplinkMonitoring from "@/components/BranchPeplinkMonitoring.vue";
import MonitoringSampleTime from "@/components/MonitoringSampleTime.vue";
import AlertLogHistory from "@/components/AlertLogHistory.vue";

export default {
  name: "InfrastructureMonitoring",
  components: {
    MssqlMonitoring, BranchPeplinkMonitoring, MonitoringSampleTime, AlertLogHistory,
  },
  data() {
    return {
      activeTab: "overview",
    };
  },
  computed: {
    summary() {
      return monitoringState.summary;
    },
    loading() {
      return monitoringState.loading;
    },
    errorMessage() {
      return monitoringState.errorMessage;
    },
    speedFusionDrops() {
      return monitoringState.speedFusionDrops;
    },
    tabs() {
      return [
        { id: "overview", label: "總覽", icon: "fas fa-chart-pie", count: null },
        { id: "firewalls", label: "FortiGate", icon: "fas fa-shield-alt", count: this.summary.firewalls.length },
        { id: "peplinks", label: "Peplink", icon: "fas fa-network-wired", count: this.summary.peplinks.length },
        { id: "branch-peplinks", label: "分店Peplink", icon: "fas fa-store", count: (this.summary.branch_peplinks || []).length },
        { id: "servers", label: "VM Server", icon: "fas fa-server", count: this.summary.servers.length },
        { id: "synology-nas", label: "Synology NAS", icon: "fas fa-hard-drive", count: (this.summary.synology_nas || []).length },
        { id: "mssql", label: "MSSQL", icon: "fas fa-database", count: (this.summary.mssql || []).length },
        { id: "nutanix", label: "Nutanix", icon: "fas fa-cubes", count: this.summary.nutanix.length },
        { id: "problems", label: "警告事件", icon: "fas fa-exclamation-triangle", count: this.summary.problems.length },
        { id: "logs", label: "告警紀錄", icon: "fas fa-history", count: null },
      ];
    },
    overallLabel() {
      return {
        ok: "所有已設定的服務皆正常",
        degraded: "部分服務需要注意",
        unconfigured: "監控服務尚未設定",
      }[this.summary.status] || "狀態未知";
    },
    formattedCheckedAt() {
      if (!this.summary.checked_at) return "尚未檢查";
      return new Intl.DateTimeFormat("zh-TW", {
        dateStyle: "medium",
        timeStyle: "medium",
        hour12: false,
      }).format(new Date(this.summary.checked_at));
    },
  },
  mounted() {
    startMonitoringPolling();
  },
  methods: {
    async loadSummary() {
      await refreshMonitoring({ foreground: true });
    },
    statusLabel(status) {
      return { ok: "正常", degraded: "異常", unconfigured: "未設定" }[status] || "未知";
    },
    formatDate(value) {
      return new Intl.DateTimeFormat("zh-TW", {
        dateStyle: "medium", timeStyle: "medium", hour12: false,
      }).format(new Date(value));
    },
    metricLabel(key) {
      return {
        version: "版本",
        hosts: "主機總數",
        enabled_hosts: "啟用主機",
        available_agents: "Agent 可用",
        active_problems: "目前問題（本頁規則）",
        active_alerts: "未結警告事件",
        monitored_items: "正常監控項目",
        supported_items: "正常監控項目",
        unsupported_items: "不支援監控項目",
        storage_containers: "Storage Container",
        storage_capacity_bytes: "儲存總容量",
        storage_used_bytes: "儲存已使用",
        storage_free_bytes: "儲存剩餘",
        storage_utilization: "儲存使用率",
        virtual_machines: "VM 數量",
        nodes: "節點數量",
        hypervisor_name: "Hypervisor 版本",
        degraded_status: "降級狀態",
        cpu_model: "CPU 型號",
        cpu_cores: "CPU 核心數",
        memory_total_bytes: "記憶體總容量",
        boot_time: "最近啟動時間",
        status: "狀態",
        hostname: "設備名稱",
        serial: "序號",
        serial_number: "Serial Number",
        dsm_version: "DSM 版本",
        system_status: "System Status",
        power_status: "Power Status",
        cpu_fan_status: "CPU Fan Status",
        system_fan_status: "System Fan Status",
        cpu: "CPU",
        memory: "記憶體",
        active_sessions: "IPv4 Sessions",
        uptime_seconds: "運行時間",
        firmware: "FortiOS",
        ipsec_vpn_tunnels: "IPsec VPN",
        ssl_vpn_state: "SSL VPN 狀態",
        ha_mode: "HA 模式",
        description: "設備資訊",
        ping: "ICMP Ping",
      }[key] || (key.startsWith("disk_usage:")
        ? `${key.slice("disk_usage:".length)} 磁碟使用率`
        : key.startsWith("volume_usage:")
          ? `${key.slice("volume_usage:".length)} 儲存使用率`
          : key.startsWith("disk_status:")
            ? `${key.slice("disk_status:".length)} Disk Status`
            : key.startsWith("disk_temperature:")
              ? `${key.slice("disk_temperature:".length)} 硬碟溫度`
              : key.startsWith("disk_bad_sectors:")
                ? `${key.slice("disk_bad_sectors:".length)} 壞軌數量`
                : key.startsWith("raid_status:")
                  ? `${key.slice("raid_status:".length)} Status`
                  : key);
    },
    displayValue(value, key) {
      if (value === null || value === "") return "—";
      if (typeof value === "boolean") return value ? "是" : "否";
      if (["cpu", "memory"].includes(key)
        || key.startsWith("disk_usage:")
        || key.startsWith("volume_usage:")) return `${value}%`;
      if (key === "storage_utilization") return `${value}%`;
      if (key.startsWith("disk_temperature:")) return `${value}°C`;
      if (key.endsWith("_bytes")) {
        const bytes = Number(value);
        if (!Number.isFinite(bytes)) return value;
        const units = ["B", "KB", "MB", "GB", "TB", "PB"];
        const unitIndex = bytes > 0
          ? Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
          : 0;
        return `${(bytes / (1024 ** unitIndex)).toFixed(unitIndex ? 1 : 0)} ${units[unitIndex]}`;
      }
      if (key === "uptime_seconds") {
        const days = Math.floor(Number(value) / 86400);
        const hours = Math.floor((Number(value) % 86400) / 3600);
        return `${days} 天 ${hours} 小時`;
      }
      if (key === "ha_mode") return { 1: "Standalone", 2: "Active-Active", 3: "Active-Passive" }[value] || value;
      if (key === "ping") return Number(value) === 1 ? "正常" : "無回應";
      if (key === "boot_time") return this.formatDate(new Date(Number(value) * 1000));
      if (key === "degraded_status") {
        const normalized = String(value).trim().toLowerCase();
        return ["0", "not degraded", "normal"].includes(normalized) ? "正常" : "已降級";
      }
      if (["system_status", "power_status", "cpu_fan_status", "system_fan_status"].includes(key)) {
        return { Normal: "Normal（正常）", Failed: "Failed（異常）" }[value] || value;
      }
      if (key.startsWith("disk_status:")) {
        return {
          Normal: "Normal（正常）",
          Initialized: "Initialized（已初始化）",
          "Not Initialized": "Not Initialized（未初始化）",
          "System Partition Failed": "System Partition Failed（系統分割區損壞）",
          Crashed: "Crashed（磁碟損壞）",
        }[value] || value;
      }
      if (key.startsWith("raid_status:")) {
        return {
          Normal: "Normal（正常）",
          Repairing: "Repairing（修復中）",
          Migrating: "Migrating（移轉中）",
          Expanding: "Expanding（擴充中）",
          Deleting: "Deleting（刪除中）",
          Creating: "Creating（建立中）",
          "RAID Syncing": "RAID Syncing（同步中）",
          "RAID Parity Checking": "RAID Parity Checking（同位檢查中）",
          "RAID Assembling": "RAID Assembling（組裝中）",
          Canceling: "Canceling（取消中）",
          Degraded: "Degraded（降級）",
          Crashed: "Crashed（損毀）",
        }[value] || value;
      }
      return value;
    },
    metricStatusClass(key, value) {
      const utilizationClass = getResourceUtilizationClass(key, value);
      if (utilizationClass) return utilizationClass;
      if (["system_status", "power_status", "cpu_fan_status", "system_fan_status"].includes(key)) {
        return value === "Normal" ? "metric-connected" : "metric-disconnected";
      }
      if (String(key).startsWith("disk_status:")) {
        return ["Normal", "Initialized"].includes(value)
          ? "metric-connected"
          : "metric-disconnected";
      }
      if (String(key).startsWith("raid_status:")) {
        if (value === "Normal") return "metric-connected";
        if (["Degraded", "Crashed"].includes(value)) return "metric-critical";
        return "metric-warning";
      }
      if (String(key).startsWith("disk_temperature:")) {
        const temperature = Number(value);
        if (!Number.isFinite(temperature)) return "";
        if (temperature >= 60) return "metric-critical";
        if (temperature >= 50) return "metric-warning";
        return "metric-healthy";
      }
      if (String(key).startsWith("disk_bad_sectors:")) {
        const badSectors = Number(value);
        if (!Number.isFinite(badSectors)) return "";
        return badSectors > 0 ? "metric-critical" : "metric-healthy";
      }
      // Only connection-state items receive semantic colors; disabled links stay neutral.
      if (!String(key).endsWith("狀態")) return "";
      if (value === "Connected") return "metric-connected";
      if (value === "Disconnect") return "metric-disconnected";
      return "";
    },
  },
};
</script>

<style scoped>
.monitoring-page { min-height: 100%; padding: 28px; color: #172033; background: #f3f6fa; }
.monitoring-header { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin-bottom: 24px; }
.eyebrow, .service-kicker { margin: 0 0 5px; color: #68809b; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.16em; }
h1 { margin: 0; font-size: clamp(1.75rem, 3vw, 2.4rem); font-weight: 750; }
.subtitle { margin: 7px 0 0; color: #6b778c; }
.refresh-button { padding: 11px 17px; color: white; border: 0; border-radius: 10px; background: #1769e0; box-shadow: 0 7px 18px rgba(23, 105, 224, .2); }
.refresh-button:disabled { opacity: .65; }
.refresh-button i { margin-right: 7px; }
.monitoring-alert { display: flex; gap: 13px; padding: 15px 18px; margin-bottom: 18px; color: #8c2e28; border: 1px solid #ffd4d0; border-radius: 12px; background: #fff4f2; }
.monitoring-alert p { margin: 3px 0 0; }
.summary-strip { display: flex; align-items: center; gap: 12px; padding: 15px 18px; margin-bottom: 20px; border: 1px solid #dce4ee; border-radius: 12px; background: white; }
.summary-strip small { display: block; margin-top: 2px; color: #7a8798; }
.auto-refresh { margin-left: auto; color: #718096; font-size: .84rem; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 0 0 5px rgba(100, 116, 139, .12); }
.status-ok { color: #087f5b; background-color: #12a873; }
.status-degraded { color: #b54708; background-color: #f59e0b; }
.status-unconfigured { color: #64748b; background-color: #94a3b8; }
.monitoring-tabs { display: flex; gap: 8px; margin-bottom: 20px; padding: 6px; overflow-x: auto; border: 1px solid #dce4ee; border-radius: 12px; background: white; }
.monitoring-tabs button { display: flex; align-items: center; gap: 8px; padding: 10px 15px; white-space: nowrap; color: #526174; border: 0; border-radius: 8px; background: transparent; }
.monitoring-tabs button.active { color: white; background: #1769e0; box-shadow: 0 5px 12px rgba(23, 105, 224, .2); }
.monitoring-tabs button span { min-width: 22px; padding: 2px 6px; border-radius: 999px; color: #526174; background: #e8eef5; font-size: .72rem; }
.monitoring-tabs button.active span { color: #1769e0; background: white; }
.integration-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 20px; }
.integration-card { position: relative; overflow: hidden; border: 1px solid #dce4ee; border-radius: 15px; background: white; box-shadow: 0 10px 30px rgba(30, 48, 75, .06); }
.card-topline { height: 4px; }
.accent-ok { background: #12a873; }.accent-degraded { background: #f59e0b; }.accent-unconfigured { background: #94a3b8; }
.card-header { display: flex; align-items: center; gap: 13px; padding: 21px 21px 12px; border: 0; background: transparent; }
.card-header h2 { margin: 0; font-size: 1.18rem; }
.service-icon { display: grid; width: 45px; height: 45px; place-items: center; border-radius: 12px; font-size: 1.2rem; }
.service-icon.zabbix { color: #c52828; background: #fff0f0; }.service-icon.firewall { color: #1769e0; background: #edf5ff; }
.status-pill { margin-left: auto; padding: 5px 10px; border-radius: 999px; color: white; font-size: .75rem; font-weight: 750; }
.service-message { min-height: 42px; margin: 0; padding: 0 21px 16px; color: #68768a; }
.metric-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; margin: 0 21px 20px; overflow: hidden; border: 1px solid #e7ecf2; border-radius: 10px; background: #e7ecf2; }
.metric { display: flex; flex-direction: column; min-height: 75px; justify-content: center; padding: 12px 15px; background: #f9fbfd; }
.metric span { color: #7a8798; font-size: .78rem; }.metric strong { margin-top: 3px; font-size: 1.12rem; overflow-wrap: anywhere; }
.empty-state { display: grid; min-height: 170px; place-items: center; align-content: center; margin: 0 21px 20px; padding: 20px; color: #7a8798; text-align: center; border: 1px dashed #ccd6e2; border-radius: 10px; background: #fafbfd; }
.empty-state i { margin-bottom: 10px; font-size: 1.45rem; }.empty-state p { margin: 0; }
.card-footer { display: flex; justify-content: space-between; padding: 13px 21px; color: #758296; border-top: 1px solid #edf0f4; background: #fbfcfe; font-size: .84rem; }
.card-footer strong { color: #364152; }
.firewall-section { margin-top: 25px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 14px; }
.section-heading h2 { margin: 0; font-size: 1.35rem; }.section-heading > span { color: #6b778c; }
.firewall-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.firewall-card { padding: 19px; border: 1px solid #dce4ee; border-radius: 14px; background: white; box-shadow: 0 7px 20px rgba(30, 48, 75, .05); }
.firewall-card > header { display: flex; align-items: start; justify-content: space-between; gap: 14px; }
.firewall-card h3 { margin: 0; font-size: 1.05rem; }.firewall-card small { color: #7a8798; }
.firewall-card > p { margin: 13px 0; color: #68768a; }
.firewall-card > .sample-time { margin-top: -6px; font-size: .78rem; }
.firewall-metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.firewall-metrics > div { display: flex; flex-direction: column; padding: 10px 12px; border-radius: 8px; background: #f5f8fb; }
.firewall-metrics span { color: #7a8798; font-size: .75rem; }.firewall-metrics strong { margin-top: 2px; overflow-wrap: anywhere; }
.firewall-metrics > .metric-connected { color: #087f5b; border: 1px solid #a7e5cf; background: #eafaf4; }
.firewall-metrics > .metric-connected span { color: #087f5b; }
.firewall-metrics > .metric-disconnected { color: #b42318; border: 1px solid #f3b7b2; background: #fff0ef; }
.firewall-metrics > .metric-disconnected span { color: #b42318; }
.firewall-metrics > .metric-healthy { border-left: 3px solid #12a873; }
.firewall-metrics > .metric-warning { color: #9a6700; border: 1px solid #f4cc73; background: #fff8e6; }
.firewall-metrics > .metric-warning span { color: #9a6700; }
.firewall-metrics > .metric-critical { color: #b42318; border: 1px solid #f3b7b2; background: #fff0ef; animation: resource-alert-pulse 1.3s ease-in-out infinite; }
.firewall-metrics > .metric-critical span { color: #b42318; }
.unsupported-details { margin-top: 12px; color: #66758a; font-size: .8rem; }
.unsupported-details summary { cursor: pointer; font-weight: 700; }
.unsupported-details ul { margin: 8px 0 0; padding-left: 20px; }
.group-list { display: flex; flex-wrap: wrap; gap: 6px; margin: -3px 0 13px; }
.group-list span { padding: 4px 8px; border-radius: 999px; color: #1769e0; background: #edf5ff; font-size: .72rem; }
.device-empty { padding: 13px; color: #758296; border: 1px dashed #ccd6e2; border-radius: 8px; background: #fafbfd; font-size: .82rem; }
.speedfusion-drop { border-color: #d92d20; animation: speedfusion-alert-pulse 1s ease-in-out infinite; }
.speedfusion-alert { display: flex; align-items: center; gap: 8px; padding: 10px 12px; margin-top: 13px; color: #b42318; border-radius: 8px; background: #fff0ef; font-weight: 700; }
@keyframes speedfusion-alert-pulse {
  0%, 100% { box-shadow: 0 0 0 1px rgba(217, 45, 32, .35), 0 8px 22px rgba(217, 45, 32, .08); }
  50% { box-shadow: 0 0 0 4px rgba(217, 45, 32, .9), 0 8px 28px rgba(217, 45, 32, .3); }
}
@keyframes resource-alert-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(217, 45, 32, .1); }
  50% { box-shadow: 0 0 0 3px rgba(217, 45, 32, .45); }
}
@media (prefers-reduced-motion: reduce) { .speedfusion-drop, .metric-critical { animation: none; border-width: 3px; } }
.problem-section { margin-top: 5px; }
.problem-table-wrap { overflow-x: auto; border: 1px solid #dce4ee; border-radius: 14px; background: white; }
.problem-table { width: 100%; border-collapse: collapse; }
.problem-table th, .problem-table td { padding: 13px 15px; text-align: left; vertical-align: top; border-bottom: 1px solid #e7ecf2; }
.problem-table th { color: #66758a; background: #f7f9fc; font-size: .78rem; white-space: nowrap; }
.problem-table td { color: #344054; }.problem-table tr:last-child td { border-bottom: 0; }
.severity { display: inline-block; padding: 4px 8px; border-radius: 999px; color: white; font-size: .72rem; font-weight: 750; }
.severity-2 { background: #d99a00; }.severity-3 { background: #e66a1f; }.severity-4 { background: #d92d20; }.severity-5 { background: #8f1d18; }
.page-empty { padding: 38px 20px; color: #758296; text-align: center; }
@media (max-width: 850px) { .integration-grid { grid-template-columns: 1fr; }.monitoring-header { align-items: flex-start; flex-direction: column; }.refresh-button { width: 100%; }.monitoring-page { padding: 18px; } }
@media (max-width: 850px) { .firewall-grid { grid-template-columns: 1fr; } }
@media (max-width: 460px) { .metric-grid, .firewall-metrics { grid-template-columns: 1fr; }.auto-refresh { display: none; } }
</style>
