<template>
  <small class="monitoring-sample-time" :class="{ 'sample-warning': stale }">
    {{ label }}：{{ sampledAt ? formatted : "尚無取樣資料" }}
    <span v-if="sampledAt && stale">（逾 10 分鐘無新取樣或時間異常）</span>
  </small>
</template>

<script>
export default {
  props: {
    sampledAt: { type: String, default: null },
    referenceTime: { type: String, default: null },
    label: { type: String, default: "取樣" },
  },
  computed: {
    formatted() {
      return new Date(this.sampledAt).toLocaleString("zh-TW", { hour12: false });
    },
    stale() {
      if (!this.sampledAt) return true;
      // React to each background snapshot; a page refresh is not a device sample.
      const age = new Date(this.referenceTime || Date.now()) - new Date(this.sampledAt);
      return !Number.isFinite(age) || age < 0 || age > 600000;
    },
  },
};
</script>

<style scoped>
.monitoring-sample-time { display: block; margin: 6px 0; color: #64748b; font-size: .75rem; }
.sample-warning { color: #996000; }
</style>
