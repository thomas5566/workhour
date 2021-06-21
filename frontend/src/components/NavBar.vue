<template>
  <div>
    <div>
        <b-navbar>
          <b-navbar-brand>
            <img src="../images/YCLogo.jpg" alt="YC" />
          </b-navbar-brand>

          <b-navbar-brand
            ><router-link to="/home">首頁</router-link> |</b-navbar-brand
          >
          <b-navbar-brand
            ><router-link to="/workhour">計畫項目</router-link>
            |</b-navbar-brand
          >
          <b-navbar-brand
            ><router-link to="/expen">支出費用</router-link> |</b-navbar-brand
          >
          <b-navbar-brand
            ><router-link to="/excel">匯出Excel</router-link> |</b-navbar-brand
          >
          <b-navbar-brand
            ><router-link to="/excel"
              ><router-link to="/task">計畫項目清單</router-link></router-link
            >
            |
          </b-navbar-brand>
          <b-navbar-brand
            ><router-link to="/excel"
              ><router-link to="/expentask"
                >支出費用清單</router-link
              ></router-link
            >
            |</b-navbar-brand
          >
          <b-navbar-brand
            ><router-link to="/excel"
              ><router-link to="/user">組員名單</router-link></router-link
            >
            |</b-navbar-brand
          >

          <b-collapse id="nav-collapse" is-nav>
            <!-- Right aligned nav items -->

            <b-navbar-nav class="ml-auto">
              <b-nav-form>
                <!-- <b-form-input
                size="sm"
                class="mr-sm-2"
                placeholder="Search"
              ></b-form-input>
              <b-button size="sm" class="my-2 my-sm-0" type="submit"
                >Search</b-button
              > -->
                <span v-if="isLoggedIn">
                  <b-button @click="logout" variant="primary">Logout</b-button> ({{ username }})
                </span>
                <span v-else>
                  <b-navbar-brand>
                    <router-link to="/register">Register</router-link> |
                  </b-navbar-brand>
                  <b-navbar-brand>
                    <router-link to="/login">Login</router-link> |
                  </b-navbar-brand>
                </span>
              </b-nav-form>

              <!-- <b-nav-item-dropdown text="Lang" right>
              <b-dropdown-item href="#">EN</b-dropdown-item>
              <b-dropdown-item href="#">ES</b-dropdown-item>
              <b-dropdown-item href="#">RU</b-dropdown-item>
              <b-dropdown-item href="#">FA</b-dropdown-item>
            </b-nav-item-dropdown> -->

              <!-- <b-nav-item-dropdown right>
              <template #button-content>
                <em>User</em>
              </template>
              <b-dropdown-item href="#">Profile</b-dropdown-item>
              <b-dropdown-item href="#">Sign Out</b-dropdown-item>
            </b-nav-item-dropdown> -->
            </b-navbar-nav>
          </b-collapse>
        </b-navbar>
    </div>

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
export default {
  name: "NavBar",
  computed: {
    isLoggedIn: function() {
      return this.$store.getters.isAuthenticated;
    },
    username: function() {
      return this.$store.getters.getUsername;
    },
    fullname: function() {
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
