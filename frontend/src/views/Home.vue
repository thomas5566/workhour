<template>
  <div>
    <div class="home" v-if="isLoggedIn">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="7">home</th>
          </tr>
          <tr>
            <th>id</th>
            <th>username</th>
            <th>taskname</th>
            <th>date</th>
            <th>description</th>
            <th>is_overtime</th>
            <th>hour</th>
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
          </router-link>
        </tbody>
        <button class="btn btn-sm btn-outline-danger" @click="delete_expen">
          Delete
        </button>
        <tr>
          <th>TotalSpend: {{ totalspends }}</th>
        </tr>
      </table>
    </div>
    <div v-else>No workhours</div>
  </div>
</template>
<script>
import {
  getWorkhourAPI,
  getExpenAPI,
  deleteExpenAPI,
} from "../service/apis.js";
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
      workhours: null,
      expens: null,
      form: {
        task_id: "",
        hour: 1,
        description: "",
        is_overtime: false,
      },
    };
  },
  mounted: function () {
    this.get_workhour();
    this.get_expen();
    this.delete_expen();
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
    async delete_expen() {
      await deleteExpenAPI().then((response) => (this.expens = response.data));
    },
  },
};
</script>
