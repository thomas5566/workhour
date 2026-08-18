<template>
  <div class="chart-container">
    <canvas ref="canvas"></canvas>
  </div>
</template>
<script>
import Chart from "chart.js/auto";
import { isReactive, markRaw, toRaw } from "vue";

function unwrapChartConfig(value) {
  const rawValue = isReactive(value) ? toRaw(value) : value;
  if (Array.isArray(rawValue)) {
    return rawValue.map(unwrapChartConfig);
  }
  if (rawValue && typeof rawValue === "object") {
    return Object.fromEntries(
      Object.entries(rawValue).map(([key, item]) => [key, unwrapChartConfig(item)]),
    );
  }
  return rawValue;
}

export default {
  name: 'Chart',
  props: {
    'chart-config': {
      type: Object,
      validator: function (value) {
        const keys = Object.keys(value)
        if (!keys.includes('type')) {
          console.error('[Chart.js] Object must has type (key)')
          return false
        }
        if (!keys.includes('data')) {
          console.error('[Chart.js] Object must has data (key)')
          return false
        }
        return true
      }
    }
  },
  data() {
    return { chart: null };
  },
  watch: {
    chartConfig: {
      deep: true,
      handler(config) {
        if (!this.chart) return;
        const plainConfig = unwrapChartConfig(config);
        this.chart.data = plainConfig.data;
        this.chart.options = plainConfig.options || {};
        this.chart.update();
      },
    },
  },
  mounted() {
    // Chart.js mutates its config internally. Passing Vue proxies here causes
    // recursive Proxy.splice calls, so it receives a detached plain object.
    this.chart = markRaw(new Chart(
      this.$refs.canvas.getContext("2d"),
      unwrapChartConfig(this.chartConfig),
    ));
  },
  beforeUnmount() {
    // Chart.js registers resize listeners and animation frames globally. Always
    // destroy the instance so leaving Dashboard cannot block later navigation.
    this.chart?.destroy()
    this.chart = null
  },
}

</script>

<style scoped>
.chart-container {
  height: 20rem;
  max-width: 100%;
  position: relative;
  width: 100%;
}

.chart-container canvas {
  display: block;
  max-height: 100%;
  max-width: 100%;
}
</style>
