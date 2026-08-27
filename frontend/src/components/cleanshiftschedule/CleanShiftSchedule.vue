<template>
  <div>
    <div class="row">
      <div class="card text-center">
        <div class="card-header" style="text-align: center">
          <h4>打掃清單</h4>
        </div>
        <div class="card-body">
          <div class="table-responsive-xl">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">地點</th>
                  <th scope="col">設備名稱</th>
                  <th scope="col">Server IP</th>
                  <th scope="col">帳號</th>
                  <th scope="col">密碼</th>
                  <th scope="col">備註</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="server in pageOfServers" :key="server.id">
                  <td>{{ server.server_location }}</td>
                  <td>{{ server.server_name }}</td>
                  <td>{{ server.server_ip }}</td>
                  <td>{{ server.server_acc }}</td>
                  <td>{{ server.server_pass ? "已設定" : "未設定" }}</td>
                  <td>{{ server.server_remark }}</td>
                  <td>
                    <button type="button" class="btn btn-sm btn-outline-warning" @click="toggleServerListId(server.id)">
                      編輯
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <!-- <div class="card-footer pb-0 pt-3">
          <jw-pagination :items="filteredServerLists" @changePage="onChangeServerPage"></jw-pagination>
        </div> -->
      </div>
    </div>

  </div>
</template>

<script>
// import {
//   getBranchListAPI,
//   getServerListAPI,
//   getServerListByBranchIdAPI
// } from "../../service/apis.js";


export default {
  emits: ["close"],
  name: "CleanShiftSchedule",
  components: {},
  data() {
    return {
      branch_lists: [],
      server_lists: [],
      pageOfServers: [],

      selected_branch: 0,
      selected_server: 0,

      searchKeyWord: null,
      activeServerList: null,
      dialogIsVisible: true,
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    filteredServerLists() {
      // KeyWord Search
      let server_lists = this.server_lists;
      const searchKeyWord = (server) => {
        const hasServerIpFilter = server.server_ip.includes(this.searchKeyWord);
        const hasServerNameFilter = server.server_name.toLowerCase().includes(this.searchKeyWord.toLowerCase());
        const hasServerLocationFilter = server.server_location.toLowerCase().includes(this.searchKeyWord.toLowerCase());

        if (hasServerIpFilter == true) {
          return hasServerIpFilter
        } else if (hasServerNameFilter == true) {
          return hasServerNameFilter
        } else if (hasServerLocationFilter == true) {
          return hasServerLocationFilter
        }
      }

      if (this.searchKeyWord) {
        server_lists = server_lists.filter(searchKeyWord);
      }

      return server_lists;
    },
  },
  mounted: function () {
  },
  created() {
    // reflash data list when chiled component update data
    this.$root.$on("get_serverlists", this.get_server_lists);
  },
  methods: {

  },
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to

/* .fade-leave-active below version 2.1.8 */
  {
  opacity: 0;
}

.model-enter-active,
.model-leave-active {
  transition: opacity 0.5s;
}

.model-enter,
.model-leave-to

/* .fade-leave-active below version 2.1.8 */
  {
  opacity: 0;
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 200vh;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.75);
}
</style>
