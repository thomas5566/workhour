<template>
  <div>
    <div v-if="isLoggedIn">
      <div class="card mt-5">
        <div>
          <label for="">From</label>
          <input type="date" v-model="startDate" />

          <label for="">To</label>
          <input type="date" v-model="endDate" />
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

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
  name: "WorkhourLists",
  components: {},
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
      form: {
        task_id: "",
        hour: 1,
        description: "",
        is_overtime: false,
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
  created() {
    this.fetchData();
  },
  methods: {
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
  },
};
</script>