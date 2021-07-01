<template>
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
                  <!-- <th scope="col">Expen ID</th> -->
                  <th>部門</th>
                  <th>姓名</th>
                  <th>支出項目</th>
                  <th>日期</th>
                  <th>支出說明</th>
                  <th>支出費用</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="expen in pageOfExpens" v-bind:key="expen.id">
                  <template v-if="editId == expen.id">
                    <!-- <td>
                      <input
                        v-model="editExpenData.id"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td> -->
                    <td>
                      <input
                      size="10"
                      v-model="editExpenData.department_name"
                      type="text"
                      :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input
                        v-model="editExpenData.user_id"
                        type="text"
                        :disabled="isDisabled"
                      /> -->
                      <input
                      size="8"
                        v-model="editExpenData.username"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input
                        v-model="editExpenData.expentask_id"
                        type="text"
                        :disabled="isDisabled"
                      /> -->
                      <input
                      size="10"
                        v-model="editExpenData.expentask_name"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input v-model="editExpenData.date" type="text" /> -->
                      <th>
                      <div>
                        <b-input-group class="mb-3">
                          <!-- <b-form-input
                            id="example-input"
                            v-model="editExpenData.date"
                            type="text"
                            placeholder="YYYY-MM-DD"
                            autocomplete="off"
                          ></b-form-input> -->
                          <b-input-group-append>
                            <b-form-datepicker
                              v-model="editExpenData.date"
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
                      <input v-model="editExpenData.description" type="text" />
                    </td>
                    <td><input size="5" v-model="editExpenData.price" type="text" /></td>
                    
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        @click="onEditSubmit(expen.id)"
                      >
                        更新
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        @click="onCancel"
                      >
                        取消
                      </button>
                    </td>
                  </template>
                  <template v-else>
                    <!-- <td>
                      {{ expen.id }}
                    </td> -->
                    <td>
                      {{ expen.user.department.department_name }}
                    </td>
                    <td>
                      <!-- {{ expen.user.id }}. -->
                      {{ expen.user.username }}
                    </td>
                    <td>
                      <!-- {{ expen.expentask.id }}. -->
                      {{ expen.expentask.expentask_name }}
                    </td>
                    <td>
                      {{ expen.date }}
                    </td>
                    <td>
                      {{ expen.description }}
                    </td>
                    <td>
                      {{ expen.price }}
                    </td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-warning"
                        v-on:click="onEdit(expen)"
                      >
                        編輯
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteEpen(expen.id)"
                      >
                        刪除
                      </button>
                    </td>
                  </template>
                </tr>
                <tr>
                  <th>所選日期 總花費: {{ totalspends }}</th>
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
  <!-- <div v-if="isLoggedIn">

  </div>
   <div v-else>尚無任何資料</div> -->
</template>
<script>
import {
  getExpenAPI,
  deleteExpenAPI,
  updateExpenAPI,
} from "../../service/apis.js";
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
  name: "ExpenLists",
  components: { DatePicker },
  props: {
    msg: String,
  },
  data() {
    return {
      search: null,
      datefilter: null,

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
      expens: [],
      editExpenData: {
        id: "",
        user_id: "",
        username: "",
        expentask_id: "",
        expentask_name: "",
        date: "",
        description: "",
        price: "",
        department_name: "",
      },
      // editWorkhourData: {
      //   id: "",
      //   user_id: "",
      //   username: "",
      //   task_id: "",
      //   task_name: "",
      //   date: "",
      //   description: "",
      //   is_overtime: false,
      //   hour: "",
      // },
    };
  },
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

      let expens = this.expens;

      if (this.search) {
        expens = expens.filter(byTitle);
      }

      const hasDateFilter =
        this.datefilter?.length >= 2 &&
        this.datefilter[0] &&
        this.datefilter[1];
      if (hasDateFilter) {
        expens = expens.filter(byDate);
      }

      return expens;
    },
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    totalspends: function () {
      console.log(this.resultQuery);
      return this.resultQuery.reduce(function (totalspends, item) {
        return totalspends + item.price;
      }, 0);
    },
    // filterExpens() {
    //   let filterType = this.selectedType;
    //   let startDate = this.localizeDate(this.startDate);
    //   let endDate = this.localizeDate(this.endDate);
    //   const itemsByType = filterType
    //     ? this.expens.filter((expen) => expen.type === filterType)
    //     : this.expens;
    //   return itemsByType.filter((expens) => {
    //     const itemDate = new Date(expens.date);
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
    this.get_expen();
    console.log("ExpenLists has been mounted");
  },
  activated() {
    console.log("ExpenLists has been activated");
  },
  deactivated() {
    console.log("ExpenLists has been deactivated");
  },
  created() {},
  methods: {
    onContext(ctx) {
      // The date formatted in the locale, or the `label-no-date-selected` string
      this.formatted = ctx.selectedFormatted;
      // The following will be an empty string until a valid date is entered
      this.selected = ctx.selectedYMD;
    },
    onChangeExpenPage(pageOfExpens) {
      // update page of items
      this.pageOfExpens = pageOfExpens;
    },
    async get_expen() {
      await getExpenAPI().then((response) => (this.expens = response.data));
    },
    async deleteEpen(id) {
      if (confirm("Are you sure you want to delete this Expn?")) {
        await deleteExpenAPI(id).then(() => {
          this.get_expen();
        });
      }
    },
    onEdit(expen) {
      this.editId = expen.id;
      this.editExpenData.id = expen.id;
      this.editExpenData.username = expen.user.username;
      this.editExpenData.expentask_id = expen.expentask.id;
      this.editExpenData.expentask_name = expen.expentask.expentask_name;
      this.editExpenData.date = expen.date;
      this.editExpenData.description = expen.description;
      this.editExpenData.price = expen.price;
      this.editExpenData.user_id = expen.user.id;
      this.editExpenData.department_name =
        expen.user.department.department_name;
    },
    onCancel() {
      this.editId = "";
      this.editExpenData.id = "";
      this.editExpenData.username = "";
      this.editExpenData.expentask_id = "";
      this.editExpenData.expentask_name = "";
      this.editExpenData.date = "";
      this.editExpenData.description = "";
      this.editExpenData.price = "";
      this.editExpenData.user_id = "";
      this.editExpenData.department_name = "";
    },
    onEditSubmit() {
      updateExpenAPI(this.editExpenData.id, this.editExpenData)
        .then((response) => {
          this.get_expen();
          this.editId = "";
          this.editExpenData.id = "";
          this.editExpenData.username = "";
          this.editExpenData.expentask_id = "";
          this.editExpenData.expentask_name = "";
          this.editExpenData.date = "";
          this.editExpenData.description = "";
          this.editExpenData.price = "";
          this.editExpenData.user_id = "";
          this.editExpenData.department_name = "";
          console.log(response.data);
          this.message = "The Expen was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },
    // localizeDate(date) {
    //   // Date picker uses ISO format (yyyy-mm-dd), which is UTC. The data
    //   // contains locale specific date strings (mm/dd/yyyy), which `Date`
    //   // parses with local time-zone offset instead of UTC. Normalize the
    //   // ISO date so we're comparing local times.
    //   if (!date || !date.includes("-")) return date;
    //   const [yyyy, mm, dd] = date.split("-");
    //   return new Date(`${mm}/${dd}/${yyyy}`);
    // },
    // formatDate(date) {
    //   return new Intl.DateTimeFormat("zh-CN", { dateStyle: "long" }).format(
    //     new Date(date)
    //   );
    // },
  },
};
</script>