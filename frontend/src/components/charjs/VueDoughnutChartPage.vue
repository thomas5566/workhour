<template>
    <div>
        <canvas id="doughnutchart"></canvas>
    </div>
</template>

<script>
import Chart from "../../../node_modules/admin-lte/plugins/chart.js/Chart";

export default {
    name: 'DoughnutChartJs',
    props: {
        type: String,
        data: {}
    },
    mounted() {
        const chrt = document.getElementById('doughnutchart');
        const chart = new Chart(chrt, {
            type: this.type,
            data: this.data
        });
        chart;
    }
}
</script>

<style></style>