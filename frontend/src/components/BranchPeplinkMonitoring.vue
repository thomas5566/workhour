<template>
  <section aria-labelledby="branch-peplink-title">
    <header class="heading">
      <h2 id="branch-peplink-title">分店Peplink 健康狀態</h2>
      <span>{{ devices.length }} 台可讀取設備</span>
    </header>
    <p>自動同步「Peplink」群組與 Peplink-數字主機；新設備於背景更新後加入，搜尋與分頁保留。</p>
    <p>FET／Cellular：Standby 綠色、Disable 紅色但不列入警告；WAN Disconnect 會列入警告事件。</p>
    <p>CPU／Memory ≥80% 為 Warning、≥90% 為 Critical；運行時間超過 90 天為 Warning。告警會同步列入警告事件，Wi-Fi WAN／VLAN WAN 不顯示。</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-else-if="!devices.length" class="empty">沒有可讀取的分店設備。請確認 Zabbix API 帳號對「Peplink」Host group 有 Read 權限。</p>
    <div class="filters">
      <label>搜尋分店
        <input :value="query" type="search" placeholder="主機名稱或 IP" @input="query = $event.target.value" />
      </label>
      <span>{{ filtered.length }} 台符合條件</span>
    </div>
    <div class="cards">
      <article v-for="device in pageDevices" :key="device.host_id">
        <header class="heading">
          <h3>{{ device.name }}</h3>
          <strong :class="device.alert_severity >= 4 ? 'bad' : device.status === 'ok' ? 'good' : 'attention'">{{ device.alert_severity >= 4 ? 'Critical' : device.alert_severity >= 2 ? 'Warning' : device.status === 'ok' ? '正常' : '需要注意' }}</strong>
        </header>
        <small>{{ device.host_name }} · {{ device.ip_address || '未提供 IP' }}</small>
        <p>{{ device.message }}</p>
        <div class="resources">
          <div v-for="resource in resources" :key="resource.key" :class="resourceClass(device, resource.key)">
            <span>{{ resource.label }}</span>
            <strong>{{ resourceValue(device, resource.key) }}</strong>
            <small v-if="device.metric_severities?.[resource.key] >= 2">{{ device.metric_severities[resource.key] >= 4 ? 'Critical' : 'Warning' }}</small>
            <small>{{ stateLabel(device, resource.key) }}</small>
            <small>{{ sampleTime(device, resource.key) }}</small>
          </div>
        </div>
        <div class="wan-wrap">
          <table v-if="wanNames(device).length">
            <caption>WAN 狀態與健康檢查</caption>
            <thead><tr><th>WAN</th><th>狀態</th><th>健康檢查</th></tr></thead>
            <tbody>
              <tr v-for="wan in wanNames(device)" :key="wan">
                <th>{{ wan }}</th>
                <td v-for="suffix in ['狀態', '健康檢查']" :key="suffix" :class="wanClass(device, wan, suffix)">
                  <strong>{{ wanValue(device, wan, suffix) }}</strong>
                  <small>{{ sampleTime(device, `${wan} ${suffix}`) }}</small>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else>尚未取得 WAN 指標；請確認 Template 與 Discovery 已完成採集。</p>
        </div>
      </article>
    </div>
    <p v-if="devices.length && !filtered.length">沒有符合搜尋條件的設備。</p>
    <nav v-if="filtered.length" class="pager" aria-label="分店Peplink 分頁">
      <button type="button" :disabled="currentPage <= 1" @click="page = currentPage - 1">上一頁</button>
      <span>第 {{ currentPage }} / {{ pageCount }} 頁 · 每頁 {{ pageSize }} 台</span>
      <button type="button" :disabled="currentPage >= pageCount" @click="page = currentPage + 1">下一頁</button>
    </nav>
  </section>
</template>

<script>
import { getResourceUtilizationClass } from '@/utils/monitoringAlerts';

export default {
  name: 'BranchPeplinkMonitoring',
  props: {
    devices: { type: Array, default: () => [] },
    error: { type: String, default: '' },
  },
  data: () => ({
    query: '', page: 1, pageSize: 12,
    resources: [{ key: 'cpu', label: 'CPU' }, { key: 'memory', label: 'Memory' },
      { key: 'uptime_seconds', label: '運行時間' }],
  }),
  computed: {
    filtered() {
      const query = this.query.trim().toLowerCase();
      return this.devices.filter(device => [device.name, device.host_name, device.ip_address]
        .some(value => String(value || '').toLowerCase().includes(query)))
        .slice().sort((a, b) => a.host_name.localeCompare(b.host_name, undefined, { numeric: true }));
    },
    pageCount() { return Math.max(1, Math.ceil(this.filtered.length / this.pageSize)); },
    currentPage() { return Math.min(this.page, this.pageCount); },
    pageDevices() { return this.filtered.slice((this.currentPage - 1) * this.pageSize, this.currentPage * this.pageSize); },
  },
  watch: { query() { this.page = 1; } },
  methods: {
    stateLabel(device, key) {
      return { ok: '', missing: '尚未提供', stale: '資料已過期', unsupported: '採集不支援', unknown: '資料未知' }[device.metric_states?.[key] || 'missing'];
    },
    sampleTime(device, key) {
      const value = device.metric_sampled_at?.[key];
      return value ? `取樣 ${new Date(value).toLocaleString('zh-TW', { hour12: false })}` : '';
    },
    resourceValue(device, key) {
      const value = device.metrics[key];
      if (this.stateLabel(device, key) || value == null) return '—';
      if (key !== 'uptime_seconds') return `${value}%`;
      return `${Math.floor(value / 86400)} 天 ${Math.floor(value % 86400 / 3600)} 小時 ${Math.floor(value % 3600 / 60)} 分`;
    },
    resourceClass(device, key) {
      if (this.stateLabel(device, key)) return 'neutral';
      const severity = device.metric_severities?.[key] || 0;
      if (severity >= 4) return 'metric-critical';
      if (severity >= 2) return 'metric-warning';
      if (key === 'uptime_seconds') return device.metrics[key] > 90 * 86400 ? 'metric-warning' : 'metric-healthy';
      return getResourceUtilizationClass(key, device.metrics[key]);
    },
    wanNames(device) {
      return [...new Set(Object.keys(device.metrics).filter(key => / (狀態|健康檢查)$/.test(key))
        .map(key => key.replace(/ (狀態|健康檢查)$/, '')))]
        .filter(wan => !['wi-fi wan', 'wi-fi wan on 2.4 ghz', 'wi-fi wan on 5 ghz', 'vlan wan'].includes(wan.trim().toLowerCase())
          && !/^VLAN WAN\s+\d+$/i.test(wan.trim()))
        .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    },
    wanValue(device, wan, suffix) {
      const key = `${wan} ${suffix}`;
      return this.stateLabel(device, key) || device.metrics[key] || '未知';
    },
    wanClass(device, wan, suffix) {
      const key = `${wan} ${suffix}`;
      if (this.stateLabel(device, key)) return 'neutral';
      const value = device.metrics[key];
      // Backup links intentionally show a red disabled state without generating alarms.
      const backup = /^(FET|Cellular)(\s+\d+)?$/i.test(wan);
      if (backup && suffix === '狀態' && value === 'Standby') return 'good';
      if (backup && suffix === '狀態' && ['Disable', 'Disabled'].includes(value)) return 'bad';
      // Disabled/standby links retain their raw health result but do not imply an outage.
      if (suffix === '健康檢查' && !this.stateLabel(device, `${wan} 狀態`)
        && ['Disable', 'Disabled', 'Standby'].includes(device.metrics[`${wan} 狀態`])) return 'neutral';
      if (device.metric_severities?.[key] >= 4) return 'bad';
      if (['Disconnect', 'Disconnected', 'Fail', 'Health-check-fail'].includes(value)) return 'bad';
      if (device.metric_severities?.[key] >= 2) return 'attention';
      if (['Connected', 'Success'].includes(value)) return 'good';
      return 'neutral';
    },
  },
};
</script>

<style scoped>
.heading, .filters, .pager { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
h2 { font-size: 1.35rem; } h3 { margin: 0; font-size: 1.05rem; }
.filters { margin: 16px 0; } label { display: flex; align-items: center; gap: 10px; }
input { padding: 9px 12px; max-width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; }
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; gap: 16px; }
article { min-width: 0; padding: 18px; border: 1px solid #dce4ee; border-radius: 14px; background: white; }
.resources { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 14px 0; }
.resources > div { display: flex; flex-direction: column; gap: 5px; padding: 10px; border-radius: 8px; background: #f5f8fb; overflow-wrap: anywhere; }
small { display: block; color: #64748b; font-size: .72rem; }
.wan-wrap { overflow-x: auto; } table { width: 100%; border-collapse: collapse; }
caption { caption-side: top; color: #334155; } td, th { text-align: left; padding: 10px; border-bottom: 1px solid #e2e8f0; }
.good { color: #087f5b; background: #eafaf4; }
.bad, .error, .resources > .metric-critical { color: #b42318; background: #fff0ef; }
.attention, .resources > .metric-warning { color: #8a5700; background: #fff8e6; }
.neutral { color: #64748b; } .resources > .metric-healthy { border-left: 3px solid #12a873; }
.pager { justify-content: center; margin-top: 18px; } button { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 8px; background: white; }
button:disabled { opacity: .45; } .empty { padding: 15px; background: #fff8e6; }
@media (max-width: 1100px) { .cards { grid-template-columns: 1fr; } }
@media (max-width: 480px) { .resources { grid-template-columns: 1fr; } label { flex-wrap: wrap; } }
</style>
