<template>
  <div class="posts" v-if="users">
    <table class="table table-striped table-bordered">
      <thead>
        <tr>
          <th colspan="4">Users</th>
        </tr>
        <tr>
          <th>id</th>
          <th>username</th>
          <th>fullname</th>
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
          <td>{{ u.username }}</td>
          <td>{{ u.fullname }}</td>
        </router-link>
      </tbody>
    </table>
  </div>
  <div v-else>No users</div>
</template>

<script>
import { getUserAPI } from "../service/apis.js";
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
      form: {
        username: "",
        fullname: "",
      },
    };
  },
  mounted: function () {
    this.get_user();
  },
  methods: {
    async get_user() {
      await getUserAPI().then((response) => (this.users = response.data));
    },
  },
};
</script>