<template>
    <div>
        <div class="row">
            <div class="col-sm">
                <div class="info-box bg-info">
                    <span class="info-box-icon"><i class="far fa-bookmark"></i></span>
                    <div class="info-box-content">
                        <span class="info-box-text">總案件</span>
                        <span class="info-box-number">{{ this.count_total_case }}</span>

                    </div>
                </div>
            </div>
            <div class="col-sm">
                <div class="info-box bg-success">
                    <span class="info-box-icon"><i class="far fa-thumbs-up"></i></span>
                    <div class="info-box-content">
                        <span class="info-box-text">結案</span>
                        <span class="info-box-number">{{ this.count_true }}</span>

                    </div>
                </div>
            </div>
            <div class="col-sm">
                <div class="info-box bg-gradient-warning">
                    <span class="info-box-icon"><i class="far fa-calendar-alt"></i></span>
                    <div class="info-box-content">
                        <span class="info-box-text">未結案</span>
                        <span class="info-box-number">{{ this.count_false }}</span>

                    </div>
                </div>
            </div>

        </div>

        <div class="row">
            <date-picker v-model="datefilter" type="date" range placeholder="請選擇日期範圍"></date-picker>
            <b-input-group size="sm" class="mb-2">
                <b-input-group-prepend is-text>
                    <b-icon icon="search"></b-icon>
                </b-input-group-prepend>
                <b-form-input type="search" v-model="search" placeholder="請輸入服務對象"></b-form-input>
            </b-input-group>
        </div>
        <section class='content'>
            <div class='box'>
                <div class='box-body'>
                    <div class='row'>
                        <div class='col-md-4'>
                            <p class='text-center'>
                                <strong>報修案件統計 (年\月)</strong>
                            </p>
                            <va-chart :chart-config='barChartConfig'></va-chart>
                        </div>
                        <div class='col-md-4'>
                            <p class='text-center'>
                                <strong>報修案件統計 (部門\門店)</strong>
                            </p>
                            <va-chart :chart-config='doughnutChartConfig'></va-chart>
                        </div>
                        <div class='col-md-4'>
                            <p class='text-center'>
                                <strong>報修案件統計 (處理人員)</strong>
                            </p>
                            <va-chart :chart-config='chartConfig'></va-chart>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <div class="row">
            <div class="card text-center ">
                <div class="card-header" style="text-align: center">
                    <h4>報修紀錄清單</h4>
                </div>
                <div class="card-body">
                    <div class="table-responsive-xl">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>處理人員</th>
                                    <th>報修對象</th>
                                    <th>報修日期/時間</th>
                                    <th>報修內容</th>
                                    <th>故障原因</th>
                                    <th>處理方式</th>
                                    <th>結束日期/時間</th>
                                    <th>結案</th>
                                    <th>備註</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="workhour in pageOfWorkhours" v-bind:key="workhour.id">
                                    <template>
                                        <td>
                                            {{ workhour.user.fullname }}
                                        </td>
                                        <td>
                                            {{ workhour.task.taskname }} - {{ workhour.shop.shop_name }}({{
                                                workhour.shop.shop_number }})
                                        </td>
                                        <td>
                                            {{ workhour.start_date }}
                                        </td>
                                        <td>
                                            {{ workhour.description }}
                                        </td>
                                        <td>
                                            {{ workhour.cause_issue }}
                                        </td>
                                        <td>
                                            {{ workhour.processing_method }}
                                        </td>
                                        <td>
                                            {{ workhour.end_date }}
                                        </td>

                                        <td>
                                            {{ workhour.case_close ? "是" : "否" }}
                                        </td>
                                        <td>
                                            {{ workhour.todo }}
                                        </td>
                                    </template>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card-footer pb-0 pt-3">
                    <jw-pagination :items="resultQuery" @changePage="onChangeWorkhourPage"></jw-pagination>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import {
    getAllWorkhourAPI,
    getAllWorkListsByDateAPI,
    getAllWorkListsByShopIdAPI,
    getAllWorkListsByUserIdAPI,
    getUserAPI
} from "../../service/apis.js";
import Vue from "vue";
import axios from "axios";
import { PaginationPlugin } from "bootstrap-vue";
import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";
import VAChart from '../charjs/VAChart.vue'

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
    name: "AllWorkhourLists",
    components: {
        DatePicker,
        'va-chart': VAChart,
    },
    data() {
        return {
            chartConfig: {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: dynamicBorderColor,
                        hoverBackgroundColor: dynamicBorderColor,
                        borderWidth: 1,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: !this.isMobile,
                    legend: {
                        position: 'bottom',
                        display: true
                    },
                    plugins: {
                        colors: {
                            forceOverride: true
                        }
                    }
                }
            },

            barChartConfig: {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: '總案件',
                            backgroundColor: dynamicBackgroundColor,
                            borderColor: dynamicBorderColor,
                            borderWidth: 1,
                            data: []
                        }
                    ]
                },
                options: {
                    scales: {
                        xAxes: [{
                            stacked: true
                        }],
                        yAxes: [{
                            ticks: {
                                stepSize: 1
                            },
                            stacked: true
                        }]
                    },
                    plugins: {
                        colors: {
                            forceOverride: true
                        }
                    }
                }
            },

            doughnutChartConfig: {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [
                        {
                            data: [],
                            backgroundColor: dynamicBorderColor,
                            hoverOffset: 4
                        }]
                },
                options: {
                    animation: {
                        animateScale: true
                    },
                    plugins: {
                        colors: {
                            forceOverride: true
                        }
                    }
                }
            },

            search: null,
            datefilter: null,
            addWorkListIsVisible: false,
            pageOfExpens: [],
            pageOfWorkhours: [],
            rows: 100,
            perPage: 10,
            currentPage: 1,
            isDisabled() {
                // evaluate whatever you need to determine disabled here...
                return this.form.validated;
            },
            // Time Pick
            selectedType: "",
            startDate: null,
            endDate: null,
            editId: "",
            editWorkhourId: "",
            workhours: [],
            cstshops: [],
            workListsbyDate: [],
            workListsbyUserid: [],
            workListsbyShtopid: [],
            userList: [],

            count_true: 0,
            count_false: 0,
            count_total_case: 0,

            activeWorkhour: null,
            dialogIsVisible: true,
        };
    },
    computed: {
        resultQuery() {
            const byDate = (workhour) => {
                const workhourDate = new Date(workhour.date);
                const startDate = new Date(this.datefilter[0]);
                const endDate = new Date(this.datefilter[1]);
                return (
                    workhourDate >= startDate &&
                    workhourDate <= endDate.setDate(endDate.getDate() + 1)
                );
            };

            // KeyWord Search by shop_name or shop_number or taskname
            let workhours = this.workhours;
            const searchKeyWord = (workhour) => {
                const hasShopNameFilter = workhour.shop.shop_name.includes(this.search);
                const hasShopNumberFilter = workhour.shop.shop_number.includes(this.search);
                const hasTaskNameFilter = workhour.task.taskname.includes(this.search);

                if (hasShopNameFilter == true) {
                    return hasShopNameFilter
                }
                if (hasShopNumberFilter == true) {
                    return hasShopNumberFilter
                }
                if (hasTaskNameFilter == true) {
                    return hasTaskNameFilter
                }
            }

            if (this.search) {
                workhours = workhours.filter(searchKeyWord);
            }

            const hasDateFilter =
                this.datefilter?.length >= 2 &&
                this.datefilter[0] &&
                this.datefilter[1];
            if (hasDateFilter) {
                workhours = workhours.filter(byDate);
            }

            return workhours;
        },
        isLoggedIn: function () {
            return this.$store.getters.isAuthenticated;
        }
    },
    mounted: function () {
        this.get_user_lists();
        this.get_all_workhour();
        this.get_worklists_by_date();
        this.get_worklists_by_userid();
        this.get_worklists_by_shopid();
    },
    methods: {
        onChangeWorkhourPage(pageOfWorkhours) {
            // update page of items
            this.pageOfWorkhours = pageOfWorkhours;
        },
        async get_user_lists() {
            this.userList = null;

            await getUserAPI().then(
                (response) => (this.userList = response.data)
            ).catch((err) => {
                console.error(err)
            });
        },
        async get_all_workhour() {
            await getAllWorkhourAPI().then(
                (response) => (this.workhours = response.data)
            ).catch((err) => {
                console.error(err)
            });

            var i = 0;
            this.count_true = 0;
            this.count_false = 0;

            if (this.workhours.length !== 0) {
                this.count_total_case = this.workhours.length;
                for (i = 0; i < this.workhours.length; i++) {
                    if (this.workhours[i].case_close) {
                        this.count_true++;
                    } else {
                        this.count_false++;
                    }
                }
            }
        },
        async get_worklists_by_date() {
            this.workListsbyDate = null;

            await getAllWorkListsByDateAPI().then(
                (response) => (this.workListsbyDate = response.data)
            ).catch((err) => {
                console.error(err)
            });
            if (this.workListsbyDate.length > 0) {
                this.barChartConfig.data.datasets[0].data.splice(0)
                this.barChartConfig.data.labels.splice(0)
                this.workListsbyDate.forEach((items) => {
                    this.barChartConfig.data.datasets[0].data.push(items.total_events);
                    this.barChartConfig.data.labels.push((items.year_month).slice(0, -3));
                });
            }
        },
        async get_worklists_by_shopid() {
            this.workListsbyShtopid = null;

            await getAllWorkListsByUserIdAPI().then(
                (response) => (this.workListsbyShtopid = response.data)
            ).catch((err) => {
                console.error(err)
            });
            if (this.workListsbyShtopid.length > 0) {
                this.doughnutChartConfig.data.datasets[0].data.splice(0)
                this.doughnutChartConfig.data.labels.splice(0)
                this.workListsbyShtopid.forEach((items) => {
                    this.doughnutChartConfig.data.datasets[0].data.push(items.total_events);
                    this.doughnutChartConfig.data.labels.push(items.shop_name);
                });
            }
        },
        async get_worklists_by_userid() {
            await getAllWorkListsByShopIdAPI().then(
                (response) => (this.workListsbyUserid = response.data)
            ).catch((err) => {
                console.error(err)
            });

            if (this.workListsbyUserid.length > 0) {
                this.chartConfig.data.datasets[0].data.splice(0)
                this.chartConfig.data.labels.splice(0)
                this.workListsbyUserid.forEach((items) => {
                    this.chartConfig.data.datasets[0].data.push(items.total_events);
                    this.chartConfig.data.labels.push(items.fullname);
                });
            }
        }
    },
};

var dynamicBackgroundColor = function () {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    var a = 0.2;
    return "rgb(" + r + "," + g + "," + b + "," + a + ")";
}

var dynamicBorderColor = function () {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to

/* .fade-leave-active below version 2.1.8 */
    {
    opacity: 0;
}

.model-enter-active,
.model-leave-active {
    transition: opacity 0.5s;
}

.model-enter,
.model-leave-to

/* .fade-leave-active below version 2.1.8 */
    {
    opacity: 0;
}

.backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 200vh;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.75);
}
</style>
