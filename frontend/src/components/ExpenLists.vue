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
                  <th>Description</th>
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
  getExpenAPI,
  deleteExpenAPI,
  updateExpenAPI,
} from "../service/apis.js";
import Vue from "vue";
import axios from "axios";
// options components
import { PaginationPlugin } from "bootstrap-vue";

Vue.use(PaginationPlugin);
Vue.use(axios);

export default {
  name: "ExpenLists",
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
  },
};
</script>