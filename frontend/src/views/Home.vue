<template>
  <div>
    <div class="home" v-if="isLoggedIn">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="8">home</th>
          </tr>
          <tr>
            <th>id</th>
            <th>username</th>
            <th>taskname</th>
            <th>date</th>
            <th>description</th>
            <th>is_overtime</th>
            <th>hour</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="w in workhours"
            :key="w.id"
            :to="{ params: { id: w.id } }"
            tag="tr"
          >
            <td>{{ w.id }}</td>
            <td>{{ w.user.username }}</td>
            <td>{{ w.task.taskname }}</td>
            <td>{{ w.date }}</td>
            <td>{{ w.description }}</td>
            <td>{{ w.is_overtime }}</td>
            <td>{{ w.hour }}</td>
            <td>
              <button class="btn btn-sm btn-outline-danger">Delete</button>
            </td>
          </router-link>
        </tbody>
        <tr>
          <th>TotalHours: {{ totalhours }}</th>
        </tr>
        <thead>
          <tr>
            <th>id</th>
            <th>username</th>
            <th>expentaskname</th>
            <th>date</th>
            <th>description</th>
            <th>price</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="e in expens"
            :key="e.id"
            :to="{ params: { id: e.id } }"
            tag="tr"
          >
            <td>{{ e.id }}</td>
            <td>{{ e.user.username }}</td>
            <td>{{ e.expentask.expentask_name }}</td>
            <td>{{ e.date }}</td>
            <td>{{ e.description }}</td>
            <td>{{ e.price }}</td>
            <td>
              <button
                class="btn btn-sm btn-outline-danger"
                v-on:click="deleteEpen(e.id)"
              >
                Delete
              </button>
            </td>
          </router-link>
        </tbody>
        <tr>
          <th>TotalSpend: {{ totalspends }}</th>
        </tr>
      </table>
    </div>
    <div v-else>No workhours</div>
    <div class="card mt-5">
      <div class="card-header">Product List</div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th scope="col">Product ID</th>
                <th>Product Name</th>
                <th>Product Price</th>
                <th>Product Name</th>
                <th>Product Price</th>
                <th>Product Price</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="expen in expens" v-bind:key="expen.id">
                <template v-if="editId == expen.id">
                  <td><input v-model="editExpenData.id" type="text" /></td>
                  <td>
                    <input v-model="editExpenData.username" type="text" />
                  </td>
                  <td>
                    <input v-model="editExpenData.expentask_name" type="text" />
                  </td>
                  <td><input v-model="editExpenData.date" type="text" /></td>
                  <td>
                    <input v-model="editExpenData.description" type="text" />
                  </td>
                  <td><input v-model="editExpenData.price" type="text" /></td>
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
                    {{ expen.user.username }}
                  </td>
                  <td>
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
                    <a href="#" class="icon">
                      <i v-on:click="onEdit(expen)" class="fa fa-pencil"></i>
                    </a>
                    <router-link
                      :to="{
                        name: 'Home',
                        params: { id: expen.id },
                      }"
                      class="icon"
                    >
                      <i class="fa fa-eye"></i>
                    </router-link>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import {
  getWorkhourAPI,
  getExpenAPI,
  deleteExpenAPI,
  updateExpenAPI,
} from "../service/apis.js";
import Vue from "vue";
import axios from "axios";
Vue.use(axios);
export default {
  name: "Home",
  components: {},
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
      console.log(this.expens);
      return this.expens.reduce(function (totalspends, item) {
        return totalspends + item.price;
      }, 0);
    },
  },
  data() {
    return {
      editId: "",
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
        username: "",
        expentask_name: "",
        date: "",
        description: "",
        price: "",
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
      await deleteExpenAPI(id).then(() => {
        this.get_expen();
      });
    },
    async updateEpen(id) {
      await deleteExpenAPI(id).then(() => {
        this.get_expen();
      });
    },
    onEdit(expen) {
      this.editId = expen.id;
      this.editExpenData.id = expen.id;
      this.editExpenData.username = expen.user.username;
      this.editExpenData.expentask_name = expen.expentask.expentask_name;
      this.editExpenData.datee = expen.date;
      this.editExpenData.description = expen.description;
      this.editExpenData.price = expen.price;
    },
    onCancel() {
      this.editId = "";
      this.editExpenData.id = "";
      this.editExpenData.username = "";
      this.editExpenData.expentask_name = "";
      this.editExpenData.date = "";
      this.editExpenData.description = "";
      this.editExpenData.price = "";
    },
    async onEditSubmit() {
      await updateExpenAPI(
        this.editId,
        this.editExpenData.id,
        this.editExpenData.username,
        this.editExpenData.expentask_name,
        this.editExpenData.date,
        this.editExpenData.description,
        this.editExpenData.price
      )
      // postExpenAPI(id).then(() => {
      //   this.editId = "";
      //   this.editExpenData.id = "";
      //   this.editExpenData.username = "";
      //   this.editExpenData.expentask_name = "";
      //   this.editExpenData.date = "";
      //   this.editExpenData.description = "";
      //   this.editExpenData.price = "";
      //   });
    },
    // async post_expen() {
    //   try {
    //     var data = {
    //       expentask_id: this.form.expentask_id,
    //       date: this.form.date,
    //       price: this.form.price,
    //       description: this.form.description,
    //     };
    //     await postExpenAPI(data).then((response) => {
    //       if (response.status == 200) {
    //         this.form.expentask_id = "";
    //         (this.form.date = this.toDate), (this.form.price = "");
    //         this.form.description = "";
    //       }
    //     });
    //   } catch (error) {
    //     throw "Sorry you can't create a new task now!";
    //   }
    //   await getWorkhourAPI().then(
    //     (response) => (this.workhours = response.data)
    //   );
    // },
  },
};
</script>