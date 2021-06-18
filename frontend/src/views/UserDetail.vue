<template>
  <div class="user-detail" v-if="user">
    <div>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="4">User Detail</th>
          </tr>
          <tr>
            <th>id</th>
            <th>部門</th>
            <th>username</th>
            <th>TotalHours</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.department.department_name }}</td>
            <td>{{ user.username }}</td>
            <td>{{ total }}</td>
            <!-- <td>{{ getworkMonth }}</td> -->
            
          </tr>
        </tbody>
      </table>
    </div>
    <div class="workhours" v-if="user.workhours.length">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="7">Workhours</th>
          </tr>
          <tr>
            <th>id</th>
            <th>username</th>
            <th>taskname</th>
            <th>date</th>
            <th>hour</th>
            <th>description</th>
            <th>is_overtime</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="w in user.workhours" :key="w.id">
            <td>{{ w.id }}</td>
            <td>{{ w.user.username }}</td>
            <td>{{ w.task.taskname }}</td>
            <td>{{ w.date }}</td>
            <td>{{ w.hour }}</td>
            <td>{{ w.description }}</td>
            <td>{{ w.is_overtime }}</td>            
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>No workhours</div>

  </div>
</template>

<script>
import { getUserIdAPI } from "../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    isUser: function () {
      return this.user != null;
    },
    total: function () {
      console.log(this.user.workhours);
      return this.user.workhours.reduce(function (total, item) {
        return total + item.hour;
      }, 0);
    },
    // getworkMonth() {
    //   const workMonth = this.user.workhours.date.slice(1, 5);
    //   console.log(workMonth) // JS starts numbering months from 0
    //   return workMonth
    // }
  },
  data() {
    return {
      user: null,
      form: {
        username: "",
        fullname: "",
      },
    };
  },
  mounted: function () {
    this.get_user_id();
  },
  methods: {
    async get_user_id() {
      await getUserIdAPI(this.$route.params.id).then(
        (response) => (this.user = response.data)
      );
    },
  },
};
</script>