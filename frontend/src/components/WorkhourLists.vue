<template>
  <div>
    <div v-if="isLoggedIn">
      <div class="card mt-5">
        <div>
          <label for="">From:</label>
          <input type="date" v-model="startDate" />
          <label for="">To:</label>
          <input type="date" v-model="endDate"  />

    <!-- <date-range-picker
            ref="picker"
            :opens="opens"
            :locale-data="{ firstDay: 1, format: 'yyyy-mm-dd' }"
            :minDate="minDate" 
            :maxDate="maxDate"
            :singleDatePicker="singleDatePicker"
            :showWeekNumbers="showWeekNumbers"
            :showDropdowns="showDropdowns"
            :autoApply="autoApply"
            v-model="dateRange"
            :linkedCalendars="linkedCalendars"
    >
        <template v-slot:input="picker" style="min-width: 350px;">
            {{ picker.startDate | date }} - {{ picker.endDate | date }}
        </template>
    </date-range-picker> -->
        </div>
        <div class="card-header">工作項目清單</div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <!-- <th scope="col">Work ID</th> -->
                  <th>部門</th>
                  <th>姓名</th>
                  <th>計畫名稱</th>
                  <th>日期</th>
                  <th>工作說明</th>
                  <th>工時</th>
                  <th>加班</th>
                  <th>加班工時</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="workhour in pageOfWorkhours"
                  v-bind:key="workhour.id"
                >
                  <template v-if="editWorkhourId == workhour.id">
                    <!-- <td>
                      <input
                        v-model="editWorkhourData.id"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td> -->
                    <td>
                      <input
                      v-model="editWorkhourData.department_name"
                      type="text"
                      :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <input
                        v-model="editWorkhourData.user_id"
                        type="text"
                        :disabled="isDisabled"
                      />
                      <input
                        v-model="editWorkhourData.username"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <input
                        v-model="editWorkhourData.task_id"
                        type="text"
                        :disabled="isDisabled"
                      />
                      <input
                        v-model="editWorkhourData.task_name"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input v-model="editWorkhourData.date" type="text" /> -->
                      
                      <th>
                      <div>
                        <b-input-group class="mb-3">
                          <b-form-input
                            id="example-input"
                            v-model="editWorkhourData.date"
                            type="text"
                            placeholder="YYYY-MM-DD"
                            autocomplete="off"
                          ></b-form-input>
                          <b-input-group-append>
                            <b-form-datepicker
                              v-model="editWorkhourData.date"
                              button-only
                              size="sm"
                              right
                              locale="zh-CN"
                              aria-controls="example-input"
                              @context="onContext"
                            ></b-form-datepicker>
                          </b-input-group-append>
                        </b-input-group>
                      </div>
                      </th>
                      
                    </td>
                    <td>
                      <input
                        v-model="editWorkhourData.description"
                        type="text"
                      />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.hour" type="text" />
                    </td>
                    <td>
                      <input
                        v-model="editWorkhourData.is_overtime"
                        type="checkbox"
                      />
                      <label>{{ editWorkhourData.is_overtime ? "是" : "否" }}</label>
                    </td>
                    <td>
                      <input
                        v-model="editWorkhourData.overtime_hour"
                        type="text"
                      />
                    </td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        @click="onEditWorkhourSubmit(workhour.id)"
                      >
                        更新
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        @click="onWorkhourCancel"
                      >
                        取消
                      </button>
                    </td>
                  </template>
                  <template v-else>
                    <!-- <td>
                      {{ workhour.id }}
                    </td> -->
                    <td>
                      {{ workhour.user.department.department_name }}
                    </td>
                    <td>
                      {{ workhour.user.id }}.
                      {{ workhour.user.username }}
                    </td>
                    <td>
                      {{ workhour.task.id }}.
                      {{ workhour.task.taskname }}
                    </td>
                    <td>
                      {{ formatDate(workhour.date) }}
                    </td>
                    <td>
                      {{ workhour.description }}
                    </td>
                    <td>
                      {{ workhour.hour }}
                    </td>
                    <td>
                      {{ workhour.is_overtime ? "是" : "否" }}
                    </td>
                    <td>
                      {{ workhour.overtime_hour }}
                    </td>
                    
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-warning"
                        v-on:click="onWorkhourEdit(workhour)"
                      >
                        編輯
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteWorkhour(workhour.id)"
                      >
                        刪除
                      </button>
                    </td>
                  </template>
                </tr>
                <tr>
                  <th>所選日期 總工時: {{ totalhours }}</th>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination
            :items="filterWorkhours"
            @changePage="onChangeWorkhourPage"
          ></jw-pagination>
        </div>
      </div>
    </div>
    <div v-else>No workhours</div>
  </div>
</template>
<script>
import {
  getWorkhourAPI,
  deleteWorkhourAPI,
  updateWorkhourAPI,
} from "../service/apis.js";
import Vue from "vue";
import axios from "axios";
// options components
import { PaginationPlugin } from "bootstrap-vue";
// import DateRangePicker from 'vue2-daterange-picker'
import 'vue2-daterange-picker/dist/vue2-daterange-picker.css'

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
  name: "WorkhourLists",

  components: {},
  props: {
    msg: String,
  },
  data() {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    // 15th two months prior
    const minDate = new Date(today);
    minDate.setMonth(minDate.getMonth() - 2);
    // 15th in two months
    const maxDate = new Date(today);
    maxDate.setMonth(maxDate.getMonth() + 2);

    let dpstartDate = new Date();
    let dpendDate = new Date();
    dpendDate.setDate(dpendDate.getDate())

    return {
      direction: 'ltr',
      format: 'yyyy/mm/dd/',
      separator: ' - ',
      applyLabel: 'Apply',
      cancelLabel: 'Cancel',
      weekLabel: 'W',
      customRangeLabel: 'Custom Range',
      daysOfWeek: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      monthNames: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      firstDay: 0,
      opens:'right',
      singleDatePicker:'range',
      showWeekNumbers: true,
      showDropdowns: true,
      autoApply: true,
      linkedCalendars: true,

      
      

      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,
      
      dateRange: { dpstartDate, dpendDate },

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

      // form: {
      //   task_id: "",
      //   hour: 1,
      //   description: "",
      //   is_overtime: false,
      // },
      
      editWorkhourData: {
        id: "",
        user_id: "",
        username: "",
        department_name: "",
        task_id: "",
        task_name: "",
        date: "",
        description: "",
        is_overtime: false,
        hour: "",
        overtime_hour: "",
      },
    };
  },
  filters: {
    dateCell (value) {
      let dt = new Date(value)

      return dt.getDate()
    },
    date (val) {
      return val ? val.toLocaleString() : ''
    }
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    totalhours: function () {
      console.log(this.filterWorkhours);
      return this.filterWorkhours.reduce(function (totalhours, item) {
        return totalhours + item.hour;
      }, 0);
    },
    filterWorkhours() {
      let filterType = this.selectedType;
      let startDate = this.localizeDate(this.startDate);
      let endDate = this.localizeDate(this.endDate);
      const itemsByType = filterType
        ? this.workhours.filter((workhours) => workhours.type === filterType)
        : this.workhours;
      return itemsByType.filter((workhours) => {
        const itemDate = new Date(workhours.date);
        if (startDate && endDate) {
          return startDate <= itemDate && itemDate <= endDate;
        }
        if (startDate && !endDate) {
          return startDate <= itemDate;
        }
        if (!startDate && endDate) {
          return itemDate <= endDate;
        }
        return true;
      });
    },
  },
  mounted: function () {
    this.get_workhour();
    console.log("WorkhourLists has been mounted");
  },
  activated() {
    console.log("WorkhourLists has been activated");
  },
  deactivated() {
    console.log("WorkhourLists has been deactivated");
  },
  created() {},
  methods: {
    onContext(ctx) {
      // The date formatted in the locale, or the `label-no-date-selected` string
      this.formatted = ctx.selectedFormatted;
      // The following will be an empty string until a valid date is entered
      this.selected = ctx.selectedYMD;
    },
    onChangeWorkhourPage(pageOfWorkhours) {
      // update page of items
      this.pageOfWorkhours = pageOfWorkhours;
    },
    async get_workhour() {
      await getWorkhourAPI().then(
        (response) => (this.workhours = response.data)
      );
    },
    async deleteWorkhour(id) {
      if (confirm("Are you sure you want to delete this Workhour?")) {
        await deleteWorkhourAPI(id).then(() => {
          this.get_workhour();
        });
      }
    },
    onWorkhourEdit(workhour) {
      this.editWorkhourId = workhour.id;
      this.editWorkhourData.id = workhour.id;
      this.editWorkhourData.department_name =
        workhour.user.department.department_name;
      this.editWorkhourData.user_id = workhour.user.id;
      this.editWorkhourData.username = workhour.user.username;
      this.editWorkhourData.task_id = workhour.task_id;
      this.editWorkhourData.task_name = workhour.task.taskname;
      this.editWorkhourData.date = workhour.date;
      this.editWorkhourData.description = workhour.description;
      this.editWorkhourData.hour = workhour.hour;
      this.editWorkhourData.is_overtime = workhour.is_overtime;
      this.editWorkhourData.overtime_hour = workhour.overtime_hour;
    },
    onWorkhourCancel() {
      this.editWorkhourId = "";
      this.editWorkhourData.department_name = "";
      this.editWorkhourData.id = "";
      this.editWorkhourData.user_id = "";
      this.editWorkhourData.username = "";
      this.editWorkhourData.task_id = "";
      this.editWorkhourData.task_name = "";
      this.editWorkhourData.date = "";
      this.editWorkhourData.description = "";
      this.editWorkhourData.hour = "";
      this.editWorkhourData.is_overtime = false;
      this.editWorkhourData.overtime_hour = "";
    },
    onEditWorkhourSubmit() {
      updateWorkhourAPI(this.editWorkhourData.id, this.editWorkhourData)
        .then((response) => {
          this.get_workhour();
          this.editWorkhourId = "";
          this.editWorkhourData.department_name = "";
          this.editWorkhourData.id = "";
          this.editWorkhourData.user_id = "";
          this.editWorkhourData.username = "";
          this.editWorkhourData.task_id = "";
          this.editWorkhourData.task_name = "";
          this.editWorkhourData.date = "";
          this.editWorkhourData.description = "";
          this.editWorkhourData.hour = "";
          this.editWorkhourData.is_overtime = false;
          this.editWorkhourData.overtime_hour = null;
          console.log(response.data);
          this.message = "The Expen was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },
    localizeDate(date) {
      // Date picker uses ISO format (yyyy-mm-dd), which is UTC. The data
      // contains locale specific date strings (mm/dd/yyyy), which `Date`
      // parses with local time-zone offset instead of UTC. Normalize the
      // ISO date so we're comparing local times.
      if (!date || !date.includes("-")) return date;
      const [yyyy, mm, dd] = date.split("-");
      return new Date(`${mm}/${dd}/${yyyy}`);
    },
    formatDate(date) {
      return new Intl.DateTimeFormat("zh-CN", { dateStyle: "long" }).format(
        new Date(date)
      );
    },
    dateFormat (classes) {
      // if (!classes.disabled) {
      //   classes.disabled = date.getTime() < new Date()
      // }
      return classes
    }
  },
};
</script>