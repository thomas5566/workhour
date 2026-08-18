<template>
  <div v-if="isLoggedIn">
    <div class="form-row">
      <div class="col">
        <select class="custom-select" v-model="selected_branch" @change="onSelectedChange(selected_branch)">
          <option value="0" selected>設備清單 - 全部</option>
          <option v-for="branch in branch_lists" :key="branch.id" :value="branch.id">
            {{ branch.branch_title }} - {{ branch.branch_name }}
          </option>
        </select>
      </div>
      <div class="col">
        <input type="search" v-model="searchKeyWord" class="form-control" placeholder="Search Key Word">
      </div>
    </div>
    <div class="row">
      <div class="card text-center">
        <div class="card-header" style="text-align: center">
          <h4>設備清單</h4>
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
                  <td>{{ server.server_pass }}</td>
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
        <div class="card-footer pb-0 pt-3">
          <jw-pagination :items="filteredServerLists" @changePage="onChangeServerPage"></jw-pagination>
        </div>
      </div>
    </div>
    <div class="row">

      <transition name="fade">
        <div v-if="this.activeServerList" class="backdrop">
          <EditServerListDetail :key="activeServerList.id" :id="activeServerList.id"
            :branch-id="activeServerList.branch_id" :server-acc="activeServerList.server_acc"
            :server-ip="activeServerList.server_ip" :server-location="activeServerList.server_location"
            :server-name="activeServerList.server_name" :server-pass="activeServerList.server_pass"
            :server-remark="activeServerList.server_remark" @onClose="toggleServerListId">
          </EditServerListDetail>
        </div>
      </transition>
    </div>
  </div>
  <base-card v-else>No Data</base-card>
</template>

<script>
import {
  getBranchListAPI,
  getServerListAPI,
  getServerListByBranchIdAPI
} from "../../service/apis.js";

import EditServerListDetail from "./EditServerListDetail.vue"

export default {
  emits: ["close"],
  name: "ServerLists",
  components: { EditServerListDetail },
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
    this.get_branch_lists();
    this.get_server_lists();
  },
  created() {
    // reflash data list when chiled component update data
    this.$root.$on("get_serverlists", this.get_server_lists);
  },
  methods: {
    async get_branch_lists() {
      await getBranchListAPI().then((response) => (this.branch_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    async get_server_lists() {
      await getServerListAPI().then((response) => (this.server_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    async get_server_lists_by_branchId(branch_id) {
      this.server_lists = [];
      await getServerListByBranchIdAPI(branch_id).then((response) => (this.server_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    onSelectedChange(selected_branch_id) {
      if (selected_branch_id === "0") {
        this.get_server_lists();
      } else {
        this.get_server_lists_by_branchId(selected_branch_id);
      }
    },
    onChangeServerPage(pageOfServers) {
      // update page of items
      this.pageOfServers = pageOfServers;
    },
    toggleServerListId(serverId) {
      console.log(serverId);
      this.activeServerList = this.server_lists.find((item) => item.id === serverId);
      console.log(this.activeServerList);
      this.dialogIsVisible = false;
    },
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
