<template>
  <div>
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
  </div>
</template>

<script>
import Vue from "vue";
import {
  getBranchListAPI,
  getServerListAPI,
  getServerListByBranchIdAPI
} from "../../service/apis.js";

import { PaginationPlugin } from "bootstrap-vue";
Vue.use(PaginationPlugin);

export default {
  name: "ServerLists",
  components: {},
  data() {
    return {
      branch_lists: [],
      server_lists: [],
      pageOfServers: [],

      selected_branch: 0,
      selected_server: 0,

      searchKeyWord: null,
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
        const hasServerNameFilter = server.server_name.includes(this.searchKeyWord);

        if (hasServerIpFilter == true) {
          return hasServerIpFilter
        } else if (hasServerNameFilter == true) {
          return hasServerNameFilter
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
      console.log(this.server_lists)
    },
    onSelectedChange(selected_branch_id) {
      console.log(selected_branch_id)
      if (selected_branch_id === "0") {
        this.get_server_lists();
      } else {
        this.get_server_lists_by_branchId(selected_branch_id);
      }
    },
    onChangeServerPage(pageOfServers) {
      // update page of items
      this.pageOfServers = pageOfServers;
    }
  },
};
</script>
