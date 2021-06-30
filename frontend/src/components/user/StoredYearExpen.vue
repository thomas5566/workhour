<template>
  <section>
    <table class="table table-striped table-bordered">
      <thead>
        <tr>
          <th colspan="4">
            <h3 style="text-align: center">Monthly-Expens</h3>
          </th>
        </tr>
        <tr>
          <th>Year Month</th>
          <th>總支出(＄)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="mte in monthlyexpen" :key="mte.year_month">
          <td>{{ mte.year_month }}</td>
          <td>{{ mte.total_pric }}</td>
        </tr>
      </tbody>
    </table>
    <div class="card mt-5">
      <div>
        <!-- <label for="">From</label>
          <input type="date" v-model="startDate" />

          <label for="">To</label>
          <input type="date" v-model="endDate" /> -->
        <date-picker
          v-model="datefilter"
          type="date"
          range
          placeholder="請選擇欲搜尋日期範圍"
        ></date-picker>
        <b-input-group size="sm" class="mb-2">
          <b-input-group-prepend is-text>
            <b-icon icon="search"></b-icon>
          </b-input-group-prepend>
          <b-form-input
            type="search"
            v-model="search"
            placeholder="請輸入欲搜尋支出項目之名稱"
          ></b-form-input>
        </b-input-group>
      </div>
      <div class="card text-center m-3">
        <div class="card-header">
          <h4>支出項目清單</h4>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>姓名</th>
                  <th>支出項目</th>
                  <th>日期</th>
                  <th>支出說明</th>
                  <th>支出費用</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="expen in pageOfExpens" v-bind:key="expen.id">
                  <template>
                    <td>{{ expen.user.username }}</td>
                    <td>{{ expen.expentask.expentask_name }}</td>
                    <td>{{ expen.date }}</td>
                    <td>{{ expen.description }}</td>
                    <td>{{ expen.price }}</td>
                  </template>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination
            :items="resultQuery"
            @changePage="onChangeExpenPage"
          ></jw-pagination>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { getMonthlyExpenAPI, getExpenMyAPI } from "../../service/apis.js";
import Vue from "vue";
import axios from "axios";
// options components
import { PaginationPlugin } from "bootstrap-vue";
import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";

Vue.use(PaginationPlugin);
Vue.use(axios);
export default {
  data() {
    return {
      search: null,
      datefilter: null,
      monthlyexpen: [],
      expenbyuser: [],
      pageOfExpens: [],
      expens: [],
      rows: 100,
      perPage: 10,
      currentPage: 1,
    };
  },
  components: { DatePicker },
  computed: {
    resultQuery() {
      const byDate = (expen) => {
        const expenDate = new Date(expen.date);
        const startDate = new Date(this.datefilter[0]);
        const endDate = new Date(this.datefilter[1]);
        return (
          expenDate >= startDate &&
          expenDate <= endDate.setDate(endDate.getDate() + 1)
        );
      };

      const byTitle = (expen) =>
        expen.expentask.expentask_name.includes(this.search);

      let expenbyuser = this.expenbyuser;

      if (this.search) {
        expenbyuser = expenbyuser.filter(byTitle);
      }

      const hasDateFilter =
        this.datefilter?.length >= 2 &&
        this.datefilter[0] &&
        this.datefilter[1];
      if (hasDateFilter) {
        expenbyuser = expenbyuser.filter(byDate);
      }

      return expenbyuser;
    },
  },
  mounted: function () {
    this.get_monthly_expen();
    this.get_expen_by_userid();
  },
  methods: {
    get_monthly_expen() {
      getMonthlyExpenAPI(this.$route.params.id).then(
        (response) => (this.monthlyexpen = response.data)
      );
    },
    onChangeExpenPage(pageOfExpens) {
      // update page of items
      this.pageOfExpens = pageOfExpens;
    },
    get_expen_by_userid() {
      getExpenMyAPI(this.$route.params.id).then(
        (response) => (this.expenbyuser = response.data)
      );
    },
  },
};
</script>