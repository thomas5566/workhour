<template>
  <div>
    <the-header></the-header>
    <the-header-nav></the-header-nav>
    <!-- <div>
      <b-navbar>
        <b-navbar-brand>
          <img src="../images/YCLogo.jpg" alt="YC" />
          <img
            src="../images/7788.gif"
            height="110px"
            width="200px"
            alt="YC2"
          />
        </b-navbar-brand>
        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav class="ml-auto">
            <b-nav-form>
              <b-navbar-brand to="/home">首頁 |</b-navbar-brand>
              <b-navbar-brand to="/workhour">計畫項目 |</b-navbar-brand>
              <b-navbar-brand to="/expen">支出費用 |</b-navbar-brand>
              <b-navbar-brand to="/excel">匯出Excel |</b-navbar-brand>
              <b-navbar-brand to="/task">計畫項目清單 | </b-navbar-brand>
              <b-navbar-brand to="/expentask">支出費用清單 |</b-navbar-brand>
              <div v-show="checklistAll_permission === 1">
                <b-navbar-brand to="/user">組員名單 |</b-navbar-brand>
              </div>
            </b-nav-form>
          </b-navbar-nav>
        </b-collapse>

        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav class="ml-auto">
            <b-nav-form>
              <span v-if="isLoggedIn">
                <b-button @click="logout" variant="primary">Logout</b-button>
                ({{ username }})
              </span>
              <span v-else>
                <b-button variant="info" to="/register"> Sign Up </b-button> |
                <b-button variant="success" to="/login"> Login </b-button>
              </span>
            </b-nav-form>
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
    </div> -->

    <!-- <div id="nav">
      <section>
        <div>
          <b-img
            left
            v-img
            :src="require('../images/YCLogo.jpg')"
            alt="Left image"
          ></b-img>
        </div>
      </section>
      <section>
        <div class="container">
          <router-link to="/home">首頁</router-link> |
          <router-link to="/workhour">計畫項目</router-link> |
          <router-link to="/expen">支出費用</router-link> |
          <router-link to="/excel">匯出Excel</router-link> |
          <router-link to="/task">計畫項目清單</router-link> |
          <router-link to="/expentask">支出費用清單</router-link> |
          <router-link to="/user">組員名單</router-link> |
          <span v-if="isLoggedIn">
            <a @click="logout">Logout</a> ({{ username }})
          </span>
          <span v-else>
            <router-link to="/register">Register</router-link> |
            <router-link to="/login">Login</router-link> |
          </span>
          <div v-if="isLoggedIn">
            <p>G'day {{ fullname }}!</p>
          </div>
          <div v-else>
            <p>Please log in to add workhour.</p>
          </div>
          <hr />
        </div>
      </section>
    </div> -->
  </div>
</template>
<script>
import TheHeaderNav from "./TheHeaderNav.vue";
import TheHeader from "./TheHeaders.vue";
export default {
  name: "NavBar",
  data() {
    return {};
  },
  components: {
    TheHeaderNav,
    TheHeader,
  },
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
    checklistAll_permission() {
      return this.$store.getters.getchecklistAll_permission;
    },
  },
  methods: {
    async logout() {
      await this.$store.dispatch("LogOut");
      this.$router.push("/login");
    },
  },
};
</script>

