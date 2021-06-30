<template>
  <section>
    <table class="table table-striped table-bordered">
      <thead>
        <tr>
          <th colspan="4">
            <h3 style="text-align: center">Monthly-Hours</h3>
          </th>
        </tr>
        <tr>
          <th>Year Month</th>
          <th>總工時(hr)</th>
          <th>總加班工時(hr)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="mtw in monthlyworkhour" :key="mtw.year_month">
          <td>{{ mtw.year_month }}</td>
          <td>{{ mtw.total_hour }}</td>
          <td>{{ mtw.total_overtime_hour }}</td>
        </tr>
      </tbody>
    </table>
    <div class="card text-center m-3">
      <div>
        <date-picker
          v-model="datefilter"
          type="date"
          range
          placeholder="Select date range"
        ></date-picker>
        <b-input-group size="sm" class="mb-2">
          <b-input-group-prepend is-text>
            <b-icon icon="search"></b-icon>
          </b-input-group-prepend>
          <b-form-input
            type="search"
            v-model="search"
            placeholder="搜尋計畫名稱"
          ></b-form-input>
        </b-input-group>
      </div>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="8">
              <h3 style="text-align: center">WorkList By User</h3>
            </th>
          </tr>
          <tr>
            <th>id</th>
            <th>姓名</th>
            <th>計畫名稱</th>
            <th>日期</th>
            <th>工作說明</th>
            <th>工時(hr)</th>
            <th>加班</th>
            <th>加班工時(hr)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="worklist in pageofworklist" :key="worklist.id">
            <td>{{ worklist.user_id }}</td>
            <td>{{ worklist.user.username }}</td>
            <td>{{ worklist.task.taskname }}</td>
            <td>{{ worklist.date }}</td>
            <td>{{ worklist.hour }}</td>
            <td>{{ worklist.description }}</td>
            <td>{{ worklist.is_overtime ? "是" : "否" }}</td>
            <td>{{ worklist.overtime_hour }}</td>
          </tr>
        </tbody>
      </table>
      <div class="card-footer pb-0 pt-3">
        <jw-pagination
          :items="resultQuery"
          @changePage="onChangeWorkhourPage"
        ></jw-pagination>
      </div>
    </div>
  </section>
</template>

<script>
import Vue from "vue";
import { PaginationPlugin } from "bootstrap-vue";
import { getMonthlyWorkhourAPI, getWorkhourMyAPI } from "../../service/apis.js";
import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";
Vue.use(PaginationPlugin);

export default {
  components: { DatePicker },
  data() {
    return {
      monthlyworkhour: [],
      worklistbyuser: [],
      pageofworklist: [],
      rows: 100,
      perPage: 10,
      currentPage: 1,
      search: null,
      datefilter: null,
    };
  },
  mounted: function () {
    this.get_monthly_workhour();
    this.get_worklist_by_userid();
  },
  computed: {
    resultQuery() {
      const byDate = (worklist) => {
        const workhourDate = new Date(worklist.date);
        const startDate = new Date(this.datefilter[0]);
        const endDate = new Date(this.datefilter[1]);
        return (
          workhourDate >= startDate &&
          workhourDate <= endDate.setDate(endDate.getDate() + 1)
        );
      };

      const byTitle = (worklist) =>
        worklist.task.taskname.includes(this.search);

      let worklistbyuser = this.worklistbyuser;

      if (this.search) {
        worklistbyuser = worklistbyuser.filter(byTitle);
      }

      const hasDateFilter =
        this.datefilter?.length >= 2 &&
        this.datefilter[0] &&
        this.datefilter[1];
      if (hasDateFilter) {
        worklistbyuser = worklistbyuser.filter(byDate);
      }

      return worklistbyuser;
    },
  },
  methods: {
    get_monthly_workhour() {
      getMonthlyWorkhourAPI(this.$route.params.id).then(
        (response) => (this.monthlyworkhour = response.data)
      );
    },
    get_worklist_by_userid() {
      getWorkhourMyAPI(this.$route.params.id).then(
        (response) => (this.worklistbyuser = response.data)
      );
    },
    onChangeWorkhourPage(pageofworklist) {
      // update page of items
      this.pageofworklist = pageofworklist;
    },
  },
};
</script>