<template>
  <div v-if="isLoggedIn">
    <div class="list-toolbar">
      <div>
        <h2>設備清單</h2>
        <p>管理各地點的 Server 設備與登入資訊</p>
      </div>
      <router-link to="/serverlist/add" class="btn btn-primary add-device-button">
        <i class="fas fa-plus"></i> 新增設備
      </router-link>
    </div>
    <div class="inventory-filter-row">
      <div class="inventory-filter-select">
        <select class="custom-select" v-model="selected_branch" @change="onSelectedChange(selected_branch)">
          <option value="0" selected>設備清單 - 全部</option>
          <option v-for="branch in branch_lists" :key="branch.id" :value="branch.id">
            {{ branch.branch_title }} - {{ branch.branch_name }}
          </option>
        </select>
      </div>
      <div class="inventory-filter-search">
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
                  <td class="credential-cell">
                    <code v-if="revealedPasswords[server.id]">{{ revealedPasswords[server.id] }}</code>
                    <span v-else>{{ server.server_pass ? "••••••••" : "未設定" }}</span>
                    <button v-if="server.server_pass" type="button" class="reveal-button" :disabled="revealingServerId === server.id" @click="togglePassword(server)">
                      <i :class="revealedPasswords[server.id] ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                      {{ revealedPasswords[server.id] ? "隱藏" : (revealingServerId === server.id ? "讀取中…" : "顯示") }}
                    </button>
                  </td>
                  <td>{{ server.server_remark }}</td>
                  <td>
                    <div class="action-buttons">
                      <button type="button" class="btn btn-sm btn-outline-warning" @click="toggleServerListId(server.id)">
                        編輯
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-danger"
                        :disabled="deletingServerId === server.id"
                        @click="deleteServer(server)"
                      >
                        {{ deletingServerId === server.id ? "刪除中…" : "刪除" }}
                      </button>
                    </div>
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
            :server-name="activeServerList.server_name"
            :server-remark="activeServerList.server_remark" @updated="handleServerUpdated"
            @onClose="toggleServerListId">
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
  deleteServerListAPI,
  getServerListAPI,
  getServerListByBranchIdAPI,
  revealServerPasswordAPI
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
      deletingServerId: null,
      revealingServerId: null,
      revealedPasswords: {},
      revealTimers: {},
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
  beforeUnmount() {
    Object.values(this.revealTimers).forEach((timer) => window.clearTimeout(timer));
    this.revealedPasswords = {};
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
    async deleteServer(server) {
      const confirmed = window.confirm(`確定要刪除設備「${server.server_name}」嗎？此操作無法復原。`);
      if (!confirmed) return;
      this.deletingServerId = server.id;
      try {
        await deleteServerListAPI(server.id);
        this.server_lists = this.server_lists.filter((item) => item.id !== server.id);
      } catch (error) {
        window.alert(error.response?.data?.detail || "刪除設備失敗，請稍後再試。");
      } finally {
        this.deletingServerId = null;
      }
    },
    async togglePassword(server) {
      if (this.revealedPasswords[server.id]) {
        this.hidePassword(server.id);
        return;
      }
      this.revealingServerId = server.id;
      try {
        const response = await revealServerPasswordAPI(server.id);
        this.revealedPasswords = { ...this.revealedPasswords, [server.id]: response.data.password || "未設定" };
        window.clearTimeout(this.revealTimers[server.id]);
        this.revealTimers[server.id] = window.setTimeout(() => this.hidePassword(server.id), 30000);
      } catch (error) {
        window.alert(error.response?.data?.detail || "無法顯示密碼。請確認管理者權限。");
      } finally {
        this.revealingServerId = null;
      }
    },
    hidePassword(serverId) {
      window.clearTimeout(this.revealTimers[serverId]);
      const passwords = { ...this.revealedPasswords };
      delete passwords[serverId];
      this.revealedPasswords = passwords;
    },
    async handleServerUpdated() {
      this.activeServerList = null;
      await this.get_server_lists();
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
.list-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 18px 20px; margin-bottom: 14px; border: 1px solid #dce4ee; border-radius: 12px; background: white; }
.list-toolbar h2 { margin: 0; font-size: 1.45rem; }.list-toolbar p { margin: 5px 0 0; color: #6b778c; }
.inventory-filter-row { display: flex; align-items: center; gap: 12px; width: 100%; margin-bottom: 14px; }
.inventory-filter-select { flex: 0 1 380px; min-width: 240px; }
.inventory-filter-search { flex: 1 1 360px; min-width: 240px; }
.inventory-filter-row select, .inventory-filter-row input { width: 100%; height: 42px; margin: 0; }
.add-device-button { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
.action-buttons { display: flex; justify-content: center; gap: 7px; white-space: nowrap; }
.credential-cell { min-width: 190px; }.credential-cell code { color: #b42318; }.reveal-button { margin-left: 8px; padding: 4px 8px; color: #1769e0; border: 1px solid #1769e0; border-radius: 6px; background: #fff; white-space: nowrap; }.reveal-button:disabled { opacity: .55; }
@media (max-width: 600px) { .list-toolbar { align-items: stretch; flex-direction: column; }.add-device-button { justify-content: center; }.inventory-filter-row { align-items: stretch; flex-direction: column; }.inventory-filter-select, .inventory-filter-search { flex-basis: auto; width: 100%; min-width: 0; } }
</style>
