<template>
  <base-card class="posts" v-if="users">
    <table class="table table-striped table-bordered">
      <thead style="text-align: center">
        <tr>
          <th colspan="4" style="text-align: center"><h4>組員名單</h4></th>
        </tr>
        <tr>
          <th>id</th>
          <th>部門名稱</th>
          <th>Username</th>
        </tr>
      </thead>
      <tbody>
        <router-link
          v-for="u in users"
          :key="u.id"
          :to="{ name: 'UserDetail', params: { id: u.id } }"
          tag="tr"
        >
          <td>{{ u.id }}</td>
          <td>{{ u.department.department_name }}</td>
          <td>{{ u.username }}</td>
        </router-link>
      </tbody>
    </table>
  </base-card>

  <base-card v-else>No users</base-card>
</template>

<script>
// import { getUserAPI } from "../service/apis.js";
import { getUserByDpAPI } from "../../service/apis.js";
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
  },
  data() {
    return {
      user: null,
      users: null,
    };
  },
  mounted: function () {
    this.get_user();
  },

  methods: {
    async get_user() {
      await getUserByDpAPI().then((response) => (this.users = response.data));
    },
  },
};
</script>
