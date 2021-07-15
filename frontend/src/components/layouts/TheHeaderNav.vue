<template>
  <div>
    <b-card title="Card Title" no-body>
      <b-card-header header-tag="nav">
        <b-nav card-header tabs justified>
          <b-nav-item to="/home">首頁</b-nav-item>
          <b-nav-item to="/workhour">計畫項目</b-nav-item>
          <b-nav-item to="/expen">支出費用</b-nav-item>
          <b-nav-item to="/task">計畫項目清單</b-nav-item>
          <b-nav-item to="/expentask">支出費用清單</b-nav-item>
          <b-nav-item to="/taskbg" v-show="checklistAll_permission === 2"
            >週報總覽</b-nav-item
          >
          <b-nav-item to="/user" v-show="checklistAll_permission === 1"
            >組員名單</b-nav-item
          >
          <b-nav-item to="/task" v-show="checklistAll_permission === 1"
            >計畫項目清單</b-nav-item
          >
          <b-nav-item to="/excel">匯出Excel</b-nav-item>
          <b-nav-item href="./123.pdf" target="_blank">
            <b-icon icon="info-circle-fill" variant="info"></b-icon>
          </b-nav-item>
          <b-nav pills>
            <span v-if="isLoggedIn">
              <b-button variant="outline-info" class="mb-2" @click="logout">
                <b-icon icon="power" aria-hidden="true"></b-icon>Logout
              </b-button>
              ({{ username }})
            </span>
            <span v-else>
              <!-- <b-button variant="info" to="/register"> Sign Up </b-button> | -->
              <b-button variant="outline-success" to="/login">Login</b-button>
            </span>
          </b-nav>
        </b-nav>
      </b-card-header>
    </b-card>
  </div>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      // pdfLink: require("../../assets/系統操作手冊.pdf"),
    };
  },
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
