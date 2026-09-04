<template>
  <section aria-labelledby="mssql-title">
    <header class="heading">
      <h2 id="mssql-title">MSSQL 健康狀態</h2>
      <span>{{ servers.length }} 個執行個體</span>
    </header>
    <p>唯讀同步 Zabbix；警告等級沿用 Zabbix Trigger，取樣時間以各指標為準。</p>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <p v-else-if="!servers.length">沒有可讀取的 MSSQL 自訂監控資料，請確認 Host 權限與 mssql.&lt;instance&gt;.* Items。</p>
    <div class="cards">
      <article v-for="server in servers" :key="`${server.host_id}:${server.instance}`">
        <header class="heading">
          <h3>{{ server.name }} · {{ server.instance }}</h3>
          <strong :class="server.status === 'ok' ? 'ok' : 'warning'">
            {{ server.status === 'ok' ? '正常' : '需要注意' }}
          </strong>
        </header>
        <small>{{ server.host_name }}</small>
        <div class="metrics">
          <div v-for="metric in server.metrics" :key="metric.item_id" :class="['metric', metric.status]">
            <span>{{ metric.label }}</span>
            <strong>{{ formatMetric(metric) }}</strong>
            <small>{{ statusLabels[metric.status] || '未知' }}</small>
            <small>取樣：{{ metric.sampled_at ? formatDate(metric.sampled_at) : '尚無資料' }}</small>
          </div>
        </div>
        <details v-if="server.problems.length">
          <summary>{{ server.problems.length }} 筆未恢復警告</summary>
          <ul><li v-for="problem in server.problems" :key="problem.event_id">{{ problem.severity_label }} · {{ problem.message }}</li></ul>
        </details>
      </article>
    </div>
  </section>
</template>

<script>
export function formatMetric(metric) {
  // Never present an old successful sample as the current service state.
  if (['stale', 'unsupported', 'unknown'].includes(metric.status) || metric.value == null) return '—';
  if (['service', 'agent'].includes(metric.key)) return Number(metric.value) === 1 ? '執行中' : '未執行';
  if (metric.key === 'db.state') return ({ 0: 'ONLINE', 1: 'RESTORING', 2: 'RECOVERING', 3: 'RECOVERY_PENDING', 4: 'SUSPECT', 5: 'EMERGENCY', 6: 'OFFLINE' })[metric.value] || `狀態 ${metric.value}`;
  if (metric.key === 'db.recovery') return ({ 1: 'FULL', 2: 'BULK_LOGGED', 3: 'SIMPLE' })[metric.value] || `模式 ${metric.value}`;
  if (metric.units === 's') {
    const seconds = Number(metric.value);
    return `${Math.floor(seconds / 3600)} 小時 ${Math.floor(seconds % 3600 / 60)} 分`;
  }
  return `${metric.value}${metric.units || ''}`;
}

export default {
  name: 'MssqlMonitoring',
  props: {
    servers: { type: Array, default: () => [] },
    error: { type: String, default: '' },
  },
  data: () => ({ statusLabels: {
    ok: '正常', warning: 'Zabbix 警告', critical: '異常／嚴重警告',
    stale: '資料已過期', unsupported: '採集不支援', unknown: '資料未知',
  } }),
  methods: {
    formatMetric,
    formatDate(value) { return new Date(value).toLocaleString('zh-TW', { hour12: false }); },
  },
};
</script>

<style scoped>
.heading { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
h2 { font-size: 1.35rem; } h3 { font-size: 1.05rem; margin: 0; }
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
article { padding: 19px; border: 1px solid #dce4ee; border-radius: 14px; background: white; }
.metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 14px 0; }
.metric { display: flex; flex-direction: column; gap: 4px; padding: 12px; border-radius: 8px; background: #f5f8fb; overflow-wrap: anywhere; }
small { color: #64748b; font-size: .75rem; }
.metric.ok { border-left: 3px solid #12a873; }
.ok { color: #087f5b; }
.warning, .stale, .unsupported, .unknown { color: #8a5700; background: #fff8e6; }
.critical, .error { color: #b42318; background: #fff0ef; }
.metric.critical { border: 1px solid #b42318; }
@media (max-width: 1000px) { .cards { grid-template-columns: 1fr; } }
@media (max-width: 480px) { .metrics { grid-template-columns: 1fr; } }
</style>
