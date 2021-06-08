<template>
  <div>
    <div id="nav">
      <router-link to="/home">Home</router-link> |
      <router-link to="/workhour">Workhours</router-link> |
      <router-link to="/expen">Expen</router-link> |
      <router-link to="/excel">Export Excel</router-link> |
      <router-link to="/user">User</router-link> |
      <router-link to="/task">Tasks</router-link> |
      <router-link to="/expentask">Expentasks</router-link> |
      <span v-if="isLoggedIn">
        <a @click="logout">Logout</a> ({{ username }})
      </span>
      <span v-else>
        <router-link to="/register">Register</router-link> |
        <router-link to="/login">Login</router-link>
      </span>
    </div>
    <div v-if="isLoggedIn">
      <p>G'day {{ fullname }}!</p>
    </div>
    <div v-else>
      <p>Please log in to add workhour.</p>
    </div>
    <hr />
  </div>
</template>
<script>

export default {
  name: "NavBar",
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    username: function () {
      return this.$store.getters.getUsername;
    },
    fullname: function () {
      return this.$store.getters.getFullname;
    },
  },
  methods: {
    async logout() {
      await this.$store.getters.isAuthenticated;
      this.$router.push("/login");
    },
  },
};
</script>
<style>
#nav {
  padding: 30px;
}
#nav a {
  font-weight: bold;
  color: #2c3e50;
}
a:hover {
  cursor: pointer;
}
#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
