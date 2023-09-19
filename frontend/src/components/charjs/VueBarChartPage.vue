<template>
    <div>
        <canvas id="barchart"></canvas>
    </div>
</template>

<script>
import Chart from "../../../node_modules/admin-lte/plugins/chart.js/Chart";

export default {
    name: 'BarChartJs',
    props: {
        type: String,
        data: {}
    },
    mounted() {
        const barchrt = document.getElementById('barchart');
        const barchart = new Chart(barchrt, {
            type: this.type,
            data: this.data,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            },
        });
        barchart;
    }
}
</script>

<style>
</style>