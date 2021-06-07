<script src="https://cdnjs.cloudflare.com/ajax/libs/vue/2.5.17/vue.js"></script>

<template>
  <div>
    <div class="home" v-if="isLoggedIn">
      <div class="card mt-5">
        <div>
          <label for="">From</label>
          <input type="date" v-model="startDate" />

          <label for="">To</label>
          <input type="date" v-model="endDate" />
          <!-- <div>
            <FilenameOption v-model="filename" />
            <AutoWidthOption v-model="autoWidth" />
            <BookTypeOption v-model="bookType" />
            <el-button
              :loading="downloadLoading"
              style="margin: 0 0 20px 20px"
              type="primary"
              icon="el-icon-document"
              @click="handleDownload"
            >
              Export Excel
            </el-button>
            <a
              href="https://panjiachen.github.io/vue-element-admin-site/feature/component/excel.html"
              target="_blank"
              style="margin-left: 15px"
            >
              <el-tag type="info">Documentation</el-tag>
            </a>
            <hr />
            <h2>Fetch Example</h2>
            <downloadexcel
              class="btn"
              :fetch="fetchData2"
              :fields="json_fields"
              :before-generate="startDownload"
              :before-finish="finishDownload"
              type="xsl"
            >
              Download Excel
            </downloadexcel>
          </div> -->
        </div>
        <div class="card-header">Work List</div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Work ID</th>
                  <th>User ID/Name</th>
                  <th>Task ID/Name</th>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Hour</th>
                  <th>is_overtime</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="workhour in pageOfWorkhours"
                  v-bind:key="workhour.id"
                >
                  <template v-if="editWorkhourId == workhour.id">
                    <td>
                      <input
                        v-model="editWorkhourData.id"
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
                      <input v-model="editWorkhourData.date" type="text" />
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
                    </td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        @click="onEditWorkhourSubmit(workhour.id)"
                      >
                        Submit
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        @click="onWorkhourCancel"
                      >
                        Cancel
                      </button>
                    </td>
                  </template>
                  <template v-else>
                    <td>
                      {{ workhour.id }}
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
                      {{ workhour.is_overtime }}
                    </td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-warning"
                        v-on:click="onWorkhourEdit(workhour)"
                      >
                        Edit
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteWorkhour(workhour.id)"
                      >
                        Delete
                      </button>
                    </td>
                  </template>
                </tr>
                <tr>
                  <th>Total Hours: {{ totalhours }}</th>
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

      <div class="card mt-5">
        <div class="card-header">Expen List</div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Expen ID</th>
                  <th>User ID/Name</th>
                  <th>Expen ID/Name</th>
                  <th>Date</th>
                  <th>description</th>
                  <th>Product Price</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="expen in pageOfExpens" v-bind:key="expen.id">
                  <template v-if="editId == expen.id">
                    <td>
                      <input
                        v-model="editExpenData.id"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <input
                        v-model="editExpenData.user_id"
                        type="text"
                        :disabled="isDisabled"
                      />
                      <input
                        v-model="editExpenData.username"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <input
                        v-model="editExpenData.expentask_id"
                        type="text"
                        :disabled="isDisabled"
                      />
                      <input
                        v-model="editExpenData.expentask_name"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td><input v-model="editExpenData.date" type="text" /></td>
                    <td>
                      <input v-model="editExpenData.description" type="text" />
                    </td>
                    <td><input v-model="editExpenData.price" type="text" /></td>
                    <td></td>
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        @click="onEditSubmit(expen.id)"
                      >
                        Submit
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        @click="onCancel"
                      >
                        Cancel
                      </button>
                    </td>
                  </template>
                  <template v-else>
                    <td>
                      {{ expen.id }}
                    </td>
                    <td>
                      {{ expen.user.id }}.
                      {{ expen.user.username }}
                    </td>
                    <td>
                      {{ expen.expentask.id }}.
                      {{ expen.expentask.expentask_name }}
                    </td>
                    <td>
                      {{ formatDate(expen.date) }}
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
                        Edit
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteEpen(expen.id)"
                      >
                        Delete
                      </button>
                    </td>
                  </template>
                </tr>
                <tr>
                  <th>Total Spends: {{ totalspends }}</th>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination
            :items="filterExpens"
            @changePage="onChangeExpenPage"
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
  getExpenAPI,
  deleteExpenAPI,
  updateExpenAPI,
  deleteWorkhourAPI,
  updateWorkhourAPI,
} from "../service/apis.js";
import Vue from "vue";
import axios from "axios";
// options components
import { parseTime } from "@/utils";
import FilenameOption from "../components/FilenameOption";
import AutoWidthOption from "../components/AutoWidthOption";
import BookTypeOption from "../components/BookTypeOption";
import downloadexcel from "vue-json-excel";
import { PaginationPlugin } from "bootstrap-vue";

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
  name: "Home",
  components: {
    FilenameOption,
    AutoWidthOption,
    BookTypeOption,
    downloadexcel,
  },
  props: {
    msg: String,
  },
  data() {
    return {
      pageOfExpens: [],
      pageOfWorkhours: [],
      rows: 100,
      perPage: 10,
      currentPage: 1,
      isDisabled() {
        // evaluate whatever you need to determine disabled here...
        return this.form.validated;
      },
      // export Excel
      list: null,
      listLoading: true,
      downloadLoading: false,
      filename: "",
      autoWidth: true,
      bookType: "xlsx",
      // Time Pick
      selectedType: "",
      startDate: null,
      endDate: null,
      editId: "",
      editWorkhourId: "",
      workhours: [],
      expens: [],
      form: {
        task_id: "",
        hour: 1,
        description: "",
        is_overtime: false,
      },
      editExpenData: {
        id: "",
        user_id: "",
        username: "",
        expentask_id: "",
        expentask_name: "",
        date: "",
        description: "",
        price: "",
      },
      editWorkhourData: {
        id: "",
        user_id: "",
        username: "",
        task_id: "",
        task_name: "",
        date: "",
        description: "",
        is_overtime: false,
        hour: "",
      },
      json_fields: {
        Date: "date",
        Username: "user.username",
        Taskname: "task.fullname",
        Hour: "hour",
        Description: "description",
        "Task name2": {
          field: "task.taskname",
          callback: (value) => {
            return `Task Name - ${value}`;
          },
        },
      },
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    totalhours: function () {
      console.log(this.pageOfWorkhours);
      return this.pageOfWorkhours.reduce(function (totalhours, item) {
        return totalhours + item.hour;
      }, 0);
    },
    totalspends: function () {
      console.log(this.pageOfExpens);
      return this.pageOfExpens.reduce(function (totalspends, item) {
        return totalspends + item.price;
      }, 0);
    },
    filterExpens() {
      let filterType = this.selectedType;
      let startDate = this.localizeDate(this.startDate);
      let endDate = this.localizeDate(this.endDate);
      const itemsByType = filterType
        ? this.expens.filter((expen) => expen.type === filterType)
        : this.expens;
      return itemsByType.filter((expens) => {
        const itemDate = new Date(expens.date);
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
    this.get_expen();
  },
  created() {
    this.fetchData();
  },
  methods: {
    onChangeWorkhourPage(pageOfWorkhours) {
      // update page of items
      this.pageOfWorkhours = pageOfWorkhours;
    },
    onChangeExpenPage(pageOfExpens) {
      // update page of items
      this.pageOfExpens = pageOfExpens;
    },
    async get_workhour() {
      await getWorkhourAPI().then(
        (response) => (this.workhours = response.data)
      );
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
    async deleteWorkhour(id) {
      if (confirm("Are you sure you want to delete this Workhour?")) {
        await deleteWorkhourAPI(id).then(() => {
          this.get_workhour();
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
          console.log(response.data);
          this.message = "The Expen was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },
    onWorkhourEdit(workhour) {
      this.editWorkhourId = workhour.id;
      this.editWorkhourData.id = workhour.id;
      this.editWorkhourData.user_id = workhour.user.id;
      this.editWorkhourData.username = workhour.user.username;
      this.editWorkhourData.task_id = workhour.task_id;
      this.editWorkhourData.task_name = workhour.task.taskname;
      this.editWorkhourData.date = workhour.date;
      this.editWorkhourData.description = workhour.description;
      this.editWorkhourData.hour = workhour.hour;
      this.editWorkhourData.is_overtime = workhour.is_overtime;
    },
    onWorkhourCancel() {
      this.editWorkhourId = "";
      this.editWorkhourData.id = "";
      this.editWorkhourData.user_id = "";
      this.editWorkhourData.username = "";
      this.editWorkhourData.task_id = "";
      this.editWorkhourData.task_name = "";
      this.editWorkhourData.date = "";
      this.editWorkhourData.description = "";
      this.editWorkhourData.hour = "";
      this.editWorkhourData.is_overtime = "";
    },
    onEditWorkhourSubmit() {
      updateWorkhourAPI(this.editWorkhourData.id, this.editWorkhourData)
        .then((response) => {
          this.get_workhour();
          this.editWorkhourId = "";
          this.editWorkhourData.id = "";
          this.editWorkhourData.user_id = "";
          this.editWorkhourData.username = "";
          this.editWorkhourData.task_id = "";
          this.editWorkhourData.task_name = "";
          this.editWorkhourData.date = "";
          this.editWorkhourData.description = "";
          this.editWorkhourData.hour = "";
          this.editWorkhourData.is_overtime = "";
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
    fetchData() {
      this.listLoading = true;
      getWorkhourAPI().then((response) => {
        this.list = response.data;
        this.listLoading = false;
      });
    },
    handleDownload() {
      this.downloadLoading = true;
      import("@/vendor/Export2Excel").then((excel) => {
        const tHeader = ["Id", "User", "Task", "Hours", "Description", "Date"];
        const filterVal = [
          "id",
          "username",
          "taskname",
          "hour",
          "description",
          "date",
        ];
        const list = this.list;
        const data = this.formatJson(filterVal, list);
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: this.filename,
          autoWidth: this.autoWidth,
          bookType: this.bookType,
        });
        this.downloadLoading = false;
      });
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map((v) =>
        filterVal.map((j) => {
          if (j === "timestamp") {
            return parseTime(v[j]);
          } else {
            return v[j];
          }
        })
      );
    },
    startDownload() {
      alert("show loading");
    },
    finishDownload() {
      alert("hide loading");
    },
    async fetchData2() {
      const response = await getWorkhourAPI();
      console.log(response);
      return response.data;
    },
  },
};
</script>