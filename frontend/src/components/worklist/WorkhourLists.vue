<template>
  <div>
    <div class="row">
      <!-- <div class="col-sm">
        <div class="info-box">
          <span class="info-box-icon bg-info"><i class="far fa-bookmark"></i></span>
          <div class="info-box-content">
            <span class="info-box-text">Bookmarks</span>
            <span class="info-box-number">41,410</span>
            <div class="progress">
              <div class="progress-bar bg-info" style="width: 70%"></div>
            </div>
            <span class="progress-description">
              70% Increase in 30 Days
            </span>
          </div>
        </div>
      </div> -->
      <div class="col-sm">
        <div class="info-box bg-info">
          <span class="info-box-icon"><i class="far fa-bookmark"></i></span>
          <div class="info-box-content">
            <span class="info-box-text">總案件</span>
            <span class="info-box-number">{{ this.count_total_case }}</span>
            <!-- <div class="progress">
              <div class="progress-bar" style="width: 70%"></div>
            </div>
            <span class="progress-description">
              70% Increase in 30 Days
            </span> -->
          </div>
        </div>
      </div>
      <div class="col-sm">
        <div class="info-box bg-success">
          <span class="info-box-icon"><i class="far fa-thumbs-up"></i></span>
          <div class="info-box-content">
            <span class="info-box-text">結案</span>
            <span class="info-box-number">{{ this.count_true }}</span>
            <!-- <div class="progress">
              <div class="progress-bar" style="width: 70%"></div>
            </div>
            <span class="progress-description">
              70% Increase in 30 Days
            </span> -->
          </div>
        </div>
      </div>
      <div class="col-sm">
        <div class="info-box bg-gradient-warning">
          <span class="info-box-icon"><i class="far fa-calendar-alt"></i></span>
          <div class="info-box-content">
            <span class="info-box-text">未結案</span>
            <span class="info-box-number">{{ this.count_false }}</span>
            <!-- <div class="progress">
              <div class="progress-bar" style="width: 70%"></div>
            </div>
            <span class="progress-description"> 70% Increase in 30 Days </span> -->
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

    <div class="row">
      <div class="card text-center">
        <div>
          <b-row>
            <b-col md="1" class="mb-0">
              <b-button size="lg" variant="outline-primary" class="mb-2" @click="showAddWorlist()">
                <b-icon icon="file-earmark-plus" animation="cylon"></b-icon>
              </b-button>
            </b-col>
          </b-row>
        </div>
        <div class="card-header" style="text-align: center">
          <h4>報修紀錄清單</h4>
        </div>
        <div class="card-body">
          <div class="table-responsive-xl">
            <table class="table">
              <thead>
                <tr>
                  <!-- <th scope="col">Work ID</th> -->
                  <!-- <th>部門</th> -->
                  <th>處理人員</th>
                  <th>報修對象</th>
                  <th>報修日期/時間</th>
                  <th>報修內容</th>
                  <th>故障原因</th>
                  <th>處理方式</th>
                  <th>結束日期/時間</th>
                  <!-- <th>工時(hr)</th> -->
                  <th>結案</th>
                  <th>備註</th>
                  <!-- <th>加班</th>
                <th>加班工時(hr)</th> -->
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="workhour in pageOfWorkhours" v-bind:key="workhour.id">
                  <template v-if="editWorkhourId == workhour.id">
                    <!-- <td>
                      <input
                        v-model="editWorkhourData.id"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td> -->
                    <!-- <td>
                    <input
                      size="10"
                      v-model="editWorkhourData.department_name"
                      type="text"
                      :disabled="isDisabled"
                    />
                  </td> -->
                    <td>
                      <!-- <input
                    size="2"
                    v-model="editWorkhourData.user_id"
                    type="text"
                    :disabled="isDisabled"
                  /> -->
                      <input size="8" v-model="editWorkhourData.username" type="text" :disabled="isDisabled" />
                    </td>
                    <td>
                      <!-- <input
                    v-model="editWorkhourData.task_id"
                    type="text"
                    :disabled="isDisabled"
                  /> -->
                      <input v-model="editWorkhourData.task_name" type="text" :disabled="isDisabled" />
                    </td>
                    <td>
                    <th>
                      <!-- <input v-model="editWorkhourData.date" type="text" /> -->
                      <div>
                        <b-input-group class="mb-3">
                          <!-- <b-form-input
                          id="example-input"
                          v-model="editWorkhourData.date"
                          type="text"
                          placeholder="YYYY-MM-DD"
                          autocomplete="off"
                        ></b-form-input> -->
                          <b-input-group-append>
                            <b-form-datepicker v-model="editWorkhourData.start_date" button-only size="sm" right
                              locale="zh-CN" aria-controls="example-input" @context="onContext"></b-form-datepicker>
                          </b-input-group-append>
                        </b-input-group>
                      </div>
                    </th>
                    </td>
                    <td>
                      <input v-model="editWorkhourData.description" type="text" />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.cause_issue" type="text" />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.processing_method" type="text" />
                    </td>
                    <td>
                    <th>
                      <!-- <input v-model="editWorkhourData.date" type="text" /> -->
                      <div>
                        <b-input-group class="mb-3">
                          <!-- <b-form-input
                          id="example-input"
                          v-model="editWorkhourData.date"
                          type="text"
                          placeholder="YYYY-MM-DD"
                          autocomplete="off"
                        ></b-form-input> -->
                          <b-input-group-append>
                            <b-form-datepicker v-model="editWorkhourData.end_date" button-only size="sm" right
                              locale="zh-CN" aria-controls="example-input" @context="onContext"></b-form-datepicker>
                          </b-input-group-append>
                        </b-input-group>
                      </div>
                    </th>
                    </td>
                    <!-- <td>
                    <input
                      size="2"
                      v-model="editWorkhourData.hour"
                      type="number"
                      :max="8"
                      :min="0.5"
                    />
                  </td> -->
                    <td>
                      <input v-model="editWorkhourData.case_close" type="checkbox" />
                      <label>{{
                        editWorkhourData.case_close ? "是" : "否"
                      }}</label>
                    </td>
                    <td>
                      <input v-model="editWorkhourData.todo" type="text" />
                    </td>
                    <td>
                      <button type="button" class="btn btn-sm btn-outline-success"
                        @click="onEditWorkhourSubmit(workhour.id)">
                        更新
                      </button>
                      <button type="button" class="btn btn-sm btn-outline-info" @click="onWorkhourCancel">
                        取消
                      </button>
                    </td>
                  </template>
                  <template v-else>
                    <!-- <td>
                      {{ workhour.id }}
                    </td> -->
                    <!-- <td>
                    {{ workhour.user.department.department_name }}
                  </td> -->
                    <td>
                      <!-- {{ workhour.user.id }}. -->
                      {{ workhour.user.fullname }}
                    </td>
                    <td>
                      <!-- {{ workhour.task.id }}. -->
                      {{ workhour.task.taskname }} - {{ workhour.shop.shop_name }}({{ workhour.shop.shop_number }})
                    </td>
                    <!-- <td>
                      {{ formatDate(workhour.date) }}
                    </td> -->
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
                    <!-- <td>
                    {{ workhour.hour }}
                  </td> -->
                    <td>
                      {{ workhour.case_close ? "是" : "否" }}
                    </td>
                    <td>
                      {{ workhour.todo }}
                    </td>
                    <td>
                      <!-- <button type="button" class="btn btn-sm btn-outline-warning" v-on:click="onWorkhourEdit(workhour)">
                        編輯
                      </button> -->
                      <button type="button" class="btn btn-sm btn-outline-warning" @click="toggleWorkhourId(workhour.id)">
                        編輯
                      </button>
                      <button class="btn btn-sm btn-outline-danger" v-on:click="deleteWorkhour(workhour.id)">
                        刪除
                      </button>
                    </td>
                  </template>
                </tr>
                <tr>
                  <!-- <th>工時: {{ totalhours }} 小時</th> -->
                  <!-- <th>所選日期 加班工時: {{ totalovertimehours }}</th>
                <th>所選日期 總工時（含加班）: {{ totalhours + totalovertimehours }}</th> -->
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
    <div class="row">
      <transition name="fade">
        <div v-if="addWorkListIsVisible" class="backdrop">
          <add-workhour @close="hideAddWorlist"></add-workhour>
        </div>
      </transition>
      <transition name="fade">
        <div v-if="this.activeWorkhour" class="backdrop">
          <edit-workhour :key="activeWorkhour.id" :id="activeWorkhour.id"
            :department-name="activeWorkhour.user.department.department_name" :user-id="activeWorkhour.user_id"
            :user-name="activeWorkhour.user.username" :case-close="activeWorkhour.case_close"
            :cause-issue="activeWorkhour.cause_issue" :description="activeWorkhour.description"
            :end-date="activeWorkhour.end_date" :processing-method="activeWorkhour.processing_method"
            :shop-id="activeWorkhour.shop_id" :shop-department-id="activeWorkhour.shop.main_department_id"
            :shop-department-shop-name="activeWorkhour.shop.shop_name"
            :shop-department-shop-number="activeWorkhour.shop.shop_number" :start-date="activeWorkhour.start_date"
            :task-id="activeWorkhour.task_id" :task-taskname="activeWorkhour.task.taskname" :todo="activeWorkhour.todo"
            @onClose="toggleWorkhourId">
          </edit-workhour>
        </div>
      </transition>
    </div>

  </div>
</template>
<script>
import {
  getWorkhourAPI,
  getWorkhourIdAPI,
  deleteWorkhourAPI,
  updateWorkhourAPI,
} from "../../service/apis.js";
import Vue from "vue";
import axios from "axios";
// options components
import AddWorkhour from "./AddWorkhour.vue";
import EditWorkhour from "./EditWorkhour.vue";
import { PaginationPlugin } from "bootstrap-vue";
import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
  emits: ["close"],
  name: "WorkhourLists",
  components: { DatePicker, AddWorkhour, EditWorkhour },
  props: {
    msg: String,
  },
  data() {
    return {
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

      count_true: 0,
      count_false: 0,
      count_total_case: 0,

      activeWorkhour: null,
      dialogIsVisible: true,

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
        start_date: "",
        description: "",
        case_close: false,
        hour: "",
        overtime_hour: "",
        end_date: "",
        todo: "",
        cause_issue: "",
        processing_method: "",
      },
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
    },
    totalhours: function () {
      console.log(this.resultQuery);
      return this.resultQuery.reduce(function (totalhours, item) {
        return totalhours + item.hour;
      }, 0);
    },
    totalovertimehours: function () {
      console.log(this.resultQuery);
      return this.resultQuery.reduce(function (totalovertimehours, item) {
        return totalovertimehours + item.overtime_hour;
      }, 0);
    },
    // filterWorkhours() {
    //   let filterType = this.selectedType;
    //   let startDate = this.localizeDate(this.startDate);
    //   let endDate = this.localizeDate(this.endDate);
    //   const itemsByType = filterType
    //     ? this.workhours.filter((workhours) => workhours.type === filterType)
    //     : this.workhours;
    //   return itemsByType.filter((workhours) => {
    //     const itemDate = new Date(workhours.date);
    //     if (startDate && endDate) {
    //       return startDate <= itemDate && itemDate <= endDate;
    //     }
    //     if (startDate && !endDate) {
    //       return startDate <= itemDate;
    //     }
    //     if (!startDate && endDate) {
    //       return itemDate <= endDate;
    //     }
    //     return true;
    //   });
    // },
  },
  mounted: function () {
    this.get_workhour();
    // this.get_workhour_by_id(this.$store.getters.getUserId)
    // console.log("WorkhourLists has been mounted");
  },
  created() {
    // reflash data list when chiled component update data
    this.$root.$on("get_workhour", this.get_workhour);
  },
  activated() {
    // console.log("WorkhourLists has been activated");
  },
  deactivated() {
    // console.log("WorkhourLists has been deactivated");
  },
  methods: {
    onChangeWorkhourPage(pageOfWorkhours) {
      // update page of items
      this.pageOfWorkhours = pageOfWorkhours;
    },
    onContext(ctx) {
      // The date formatted in the locale, or the `label-no-date-selected` string
      this.formatted = ctx.selectedFormatted;
      // The following will be an empty string until a valid date is entered
      this.selected = ctx.selectedYMD;
    },
    async get_workhour() {
      await getWorkhourAPI().then(
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
    async get_workhour_by_id(id) {
      await getWorkhourIdAPI(id).then(
        // (response) => (this.workhours = response.data)
        (response) => (console.log(response.data))
      ).catch((err) => {
        console.error(err)
      });
    },
    async deleteWorkhour(id) {
      if (confirm("Are you sure you want to delete this Workhour?")) {
        await deleteWorkhourAPI(id).then(() => {
          this.get_workhour();
        }).catch((err) => {
          console.error(err)
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
      this.editWorkhourData.start_date = workhour.start_date;
      this.editWorkhourData.description = workhour.description;
      this.editWorkhourData.hour = workhour.hour;
      this.editWorkhourData.case_close = workhour.case_close;
      this.editWorkhourData.overtime_hour = workhour.overtime_hour;
      this.editWorkhourData.end_date = workhour.end_date;
      this.editWorkhourData.todo = workhour.todo;
      this.editWorkhourData.cause_issue = workhour.cause_issue;
      this.editWorkhourData.processing_method = workhour.processing_method;
    },
    onWorkhourCancel() {
      this.editWorkhourId = "";
      this.editWorkhourData.department_name = "";
      this.editWorkhourData.id = "";
      this.editWorkhourData.user_id = "";
      this.editWorkhourData.username = "";
      this.editWorkhourData.task_id = "";
      this.editWorkhourData.task_name = "";
      this.editWorkhourData.start_date = "";
      this.editWorkhourData.description = "";
      this.editWorkhourData.hour = "";
      this.editWorkhourData.case_close = false;
      this.editWorkhourData.overtime_hour = "";
      this.editWorkhourData.end_date = "";
      this.editWorkhourData.todo = "";
      this.editWorkhourData.cause_issue = "";
      this.editWorkhourData.processing_method = "";
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
          this.editWorkhourData.start_date = "";
          this.editWorkhourData.description = "";
          this.editWorkhourData.hour = "";
          this.editWorkhourData.case_close = false;
          this.editWorkhourData.overtime_hour = null;
          this.editWorkhourData.end_date = "";
          this.editWorkhourData.todo = "";
          this.editWorkhourData.cause_issue = "";
          this.editWorkhourData.processing_method = "";
          console.log(response.data);
          this.message = "The Expen was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },

    toggleWorkhourId(workhourId) {
      console.log(workhourId);
      this.activeWorkhour = this.workhours.find((item) => item.id === workhourId);
      console.log("toggleWorkhour Data:");
      console.log(this.activeWorkhour);
      this.dialogIsVisible = false;
    },
    showAddWorlist() {
      this.addWorkListIsVisible = true;
    },
    hideAddWorlist() {
      this.addWorkListIsVisible = false;
    },
  },
};
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