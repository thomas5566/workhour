<template>
  <section class="alert-history" aria-labelledby="alert-history-title">
    <header class="heading">
      <div>
        <p class="eyebrow">HIGH AND ABOVE HISTORY</p>
        <h2 id="alert-history-title">High 等級以上告警紀錄</h2>
      </div>
      <span>共 {{ total }} 筆</span>
    </header>

    <form class="filters" @submit.prevent="search">
      <label>
        開始時間
        <input v-model="filters.from" type="datetime-local" />
      </label>
      <label>
        結束時間
        <input v-model="filters.to" type="datetime-local" />
      </label>
      <label class="message-filter">
        警告訊息
        <input v-model.trim="filters.message" type="search" maxlength="500" placeholder="輸入訊息關鍵字" />
      </label>
      <button type="submit" :disabled="loading">{{ loading ? "查詢中" : "查詢" }}</button>
      <button type="button" class="secondary" :disabled="loading" @click="reset">清除</button>
    </form>

    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div class="table-wrap">
      <table v-if="items.length">
        <thead>
          <tr><th>等級</th><th>主機</th><th>來源</th><th>警告訊息</th><th>發生時間</th><th>最後觀測</th><th>狀態</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td><span class="severity" :class="`severity-${item.severity}`">{{ item.severity_label }}</span></td>
            <td>{{ item.host_name }}</td>
            <td>{{ item.source === "workhour" ? "本頁規則" : "Zabbix" }}</td>
            <td>{{ item.message }}</td>
            <td>{{ formatDate(item.occurred_at) }}</td>
            <td>{{ formatDate(item.last_observed_at) }}</td>
            <td>{{ item.resolved_at ? `已恢復 ${formatDate(item.resolved_at)}` : "持續中" }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!loading" class="empty">查詢範圍內沒有 High 或 Disaster 告警紀錄。</p>
    </div>

    <nav v-if="total > limit" class="pager" aria-label="告警紀錄分頁">
      <button type="button" :disabled="loading || offset === 0" @click="previousPage">上一頁</button>
      <span>第 {{ currentPage }} / {{ pageCount }} 頁</span>
      <button type="button" :disabled="loading || offset + limit >= total" @click="nextPage">下一頁</button>
    </nav>
  </section>
</template>

<script>
import { getMonitoringAlertLogsAPI } from "@/service/apis";

export default {
  name: "AlertLogHistory",
  data() {
    return {
      filters: { from: "", to: "", message: "" },
      items: [],
      total: 0,
      limit: 100,
      offset: 0,
      loading: false,
      errorMessage: "",
    };
  },
  computed: {
    currentPage() {
      return Math.floor(this.offset / this.limit) + 1;
    },
    pageCount() {
      return Math.max(1, Math.ceil(this.total / this.limit));
    },
  },
  mounted() {
    this.load();
  },
  methods: {
    toIso(value) {
      return value ? new Date(value).toISOString() : undefined;
    },
    async load() {
      this.loading = true;
      this.errorMessage = "";
      try {
        const response = await getMonitoringAlertLogsAPI({
          from: this.toIso(this.filters.from),
          to: this.toIso(this.filters.to),
          message: this.filters.message || undefined,
          offset: this.offset,
          limit: this.limit,
        });
        this.items = response.data.items;
        this.total = response.data.total;
      } catch {
        this.errorMessage = "無法取得告警紀錄，請稍後再試。";
      } finally {
        this.loading = false;
      }
    },
    search() {
      this.offset = 0;
      this.load();
    },
    reset() {
      this.filters = { from: "", to: "", message: "" };
      this.offset = 0;
      this.load();
    },
    previousPage() {
      this.offset = Math.max(0, this.offset - this.limit);
      this.load();
    },
    nextPage() {
      this.offset += this.limit;
      this.load();
    },
    formatDate(value) {
      if (!value) return "—";
      return new Intl.DateTimeFormat("zh-TW", {
        dateStyle: "medium", timeStyle: "medium", hour12: false,
      }).format(new Date(value));
    },
  },
};
</script>

<style scoped>
.alert-history { padding: 0 0 2rem; }
.heading { display: flex; align-items: end; justify-content: space-between; margin: 1.5rem 0 1rem; }
.heading h2 { margin: .2rem 0 0; color: #0f2745; }
.eyebrow { margin: 0; color: #5575a4; font-size: .75rem; letter-spacing: .12em; }
.filters { display: grid; grid-template-columns: repeat(2, minmax(180px, 1fr)) minmax(240px, 2fr) auto auto; gap: .75rem; align-items: end; padding: 1rem; background: white; border: 1px solid #d7e0ec; border-radius: 12px; }
.filters label { display: grid; gap: .35rem; color: #536781; font-size: .82rem; }
.filters input { min-height: 40px; padding: .5rem .65rem; border: 1px solid #cbd7e6; border-radius: 7px; }
.filters button, .pager button { min-height: 40px; padding: .5rem 1rem; border: 0; border-radius: 7px; color: white; background: #1769e0; }
.filters button.secondary { color: #29425f; background: #e7edf5; }
button:disabled { opacity: .55; cursor: not-allowed; }
.table-wrap { margin-top: 1rem; overflow-x: auto; border: 1px solid #d7e0ec; border-radius: 12px; background: white; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: .8rem; border-bottom: 1px solid #e0e7f0; text-align: left; vertical-align: top; white-space: nowrap; }
td:nth-child(4) { min-width: 280px; white-space: normal; }
.severity { display: inline-block; padding: .2rem .5rem; border-radius: 999px; color: white; }
.severity-4 { background: #e12d39; }
.severity-5 { background: #991b1b; }
.empty, .error { padding: 1rem; margin: 0; }
.error { margin-top: 1rem; border-radius: 8px; color: #a61b25; background: #fff0f1; }
.pager { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem; }
@media (max-width: 1000px) {
  .filters { grid-template-columns: 1fr 1fr; }
  .message-filter { grid-column: 1 / -1; }
}
</style>
