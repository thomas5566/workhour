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
        </div>
        <div class="card-header">Work List</div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Work ID</th>
                  <th>User ID</th>
                  <th>User Name</th>
                  <th>Task ID</th>
                  <th>Task Name</th>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Hour</th>
                  <th>is_overtime</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="workhour in workhours" v-bind:key="workhour.id">
                  <template v-if="editWorkhourId == workhour.id">
                    <td><input v-model="workhour.id" type="text" /></td>
                    <td>
                      <input v-model="editWorkhourData.user_id" type="text" />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.username" type="text" />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.task_id" type="text" />
                    </td>
                    <td>
                      <input v-model="editWorkhourData.task_name" type="text" />
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
                      {{ workhour.user.id }}
                    </td>
                    <td>
                      {{ workhour.user.username }}
                    </td>
                    <td>
                      {{ workhour.task.id }}
                    </td>
                    <td>
                      {{ workhour.task.taskname }}
                    </td>
                    <td>
                      {{ workhour.date }}
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
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteWorkhour(workhour.id)"
                      >
                        Delete
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-warning"
                        v-on:click="onWorkhourEdit(workhour)"
                      >
                        Edit
                      </button>
                    </td>
                  </template>
                </tr>
              </tbody>
              <tr>
                <th>Total Hours: {{ totalhours }}</th>
              </tr>
            </table>
          </div>
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
                <tr v-for="expen in filterItem" v-bind:key="expen.id">
                  <template v-if="editId == expen.id">
                    <td><input v-model="editExpenData.id" type="text" /></td>
                    <td>
                      <input v-model="editExpenData.username" type="text" />
                    </td>
                    <td>
                      <input v-model="editExpenData.expentask_id" type="text" />
                    </td>
                    <td>
                      <input
                        v-model="editExpenData.expentask_name"
                        type="text"
                      />
                    </td>
                    <td><input v-model="editExpenData.date" type="text" /></td>
                    <td>
                      <input v-model="editExpenData.description" type="text" />
                    </td>
                    <td><input v-model="editExpenData.price" type="text" /></td>
                    <td>
                      <input v-model="editExpenData.user_id" type="text" />
                    </td>
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
                        class="btn btn-sm btn-outline-danger"
                        v-on:click="deleteEpen(expen.id)"
                      >
                        Delete
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-warning"
                        v-on:click="onEdit(expen)"
                      >
                        Edit
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
import { MonthPicker } from "vue-month-picker";
import { MonthPickerInput } from "vue-month-picker";
import axios from "axios";

Vue.use(axios);
Vue.use(MonthPicker);
Vue.use(MonthPickerInput);

export default {
  name: "Home",
  components: {
    MonthPickerInput,
  },
  props: {
    msg: String,
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    totalhours: function () {
      console.log(this.workhours);
      return this.workhours.reduce(function (totalhours, item) {
        return totalhours + item.hour;
      }, 0);
    },
    totalspends: function () {
      console.log(this.filterItem);
      return this.filterItem.reduce(
        function (totalspends, item) {
          return totalspends + item.price;
        }, 0);
    },
    filterItem() {
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
  },
  data() {
    return {
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
    };
  },
  mounted: function () {
    this.get_workhour();
    this.get_expen();
    // this.delete_expen();
  },
  methods: {
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
      return new Intl.DateTimeFormat("en-US", { dateStyle: "long" }).format(
        new Date(date)
      );
    },
    // checkDate() {
    //   if (this.fromdate != "") {
    //     var fromdate = new Date(this.fromdate);
    //     var todate = new Date(this.todate);

    //     if (fromdate.getTime() > todate.getTime()) {
    //       var currentDate = new Date();

    //       var day = fromdate.getDate();
    //       var month = fromdate.getMonth();
    //       var year = fromdate.getFullYear();

    //       this.todate = new Date(year, month, day);
    //     }
    //   }
    // },
    // fetchRecords() {
    //   if (this.fromdate != "" && this.todate != "") {
    //     getExpenAPI(this.fromdate, this.todate)
    //       .then(function (response) {
    //         this.expens = response.data;

    //         // Display no record found <tr> if record not found
    //         if (this.expens.length == 0) {
    //           app.recordNotFound = true;
    //         } else {
    //           app.recordNotFound = false;
    //         }
    //       })
    //       .catch(function (error) {
    //         console.log(error);
    //       });
    //   }
    // },
  },
};
</script>