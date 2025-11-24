<template>
  <div v-if="isLoggedIn">
    <div class="form-row">
      <div class="col">
        <select class="custom-select" v-model="selected_branch" @change="onSelectedChange(selected_branch)">
          <option value="0" selected>監視器清單 - 全部門店</option>
          <!-- <option v-for="branch in branch_lists" :key="branch.id" :value="branch.id">
            {{ branch.branch_title }} - {{ branch.branch_name }}
          </option> -->
        </select>
      </div>
      <div class="col">
        <input type="search" v-model="searchKeyWord" class="form-control" placeholder="Search Key Word">
      </div>
    </div>
    <div class="row">
      <div class="card text-center">
        <div class="card-header" style="text-align: center">
          <h4>監視器清單</h4>
        </div>
        <div class="card-body">
          <div class="table-responsive-xl">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">店別/名</th>
                  <th scope="col">監視器品牌</th>
                  <th scope="col">IP</th>
                  <th scope="col">管理者帳號</th>
                  <th scope="col">管理者密碼</th>
                  <th scope="col">使用者帳號</th>
                  <th scope="col">使用者密碼</th>
                  <th scope="col">手機埠號</th>
                  <th scope="col">http埠號</th>
                  <th scope="col">tcp埠號</th>
                  <th scope="col">備註</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ipcam in pageOfIpcams" :key="ipcam.id">
                  <td>{{ ipcam.shop_id }} {{ ipcam.shop_name }}</td>
                  <td>{{ ipcam.ipcam_brand }}</td>
                  <td>{{ ipcam.ipcam_ip }}</td>
                  <td>{{ ipcam.admin_acc }}</td>
                  <td>{{ ipcam.admin_pass }}</td>
                  <td>{{ ipcam.user_acc }}</td>
                  <td>{{ ipcam.user_pass }}</td>
                  <td>{{ ipcam.phone_port }}</td>
                  <td>{{ ipcam.http_port }}</td>
                  <td>{{ ipcam.tcp_port }}</td>
                  <td>{{ ipcam.remark }}</td>
                  <td>
                    <button type="button" class="btn btn-sm btn-outline-warning" @click="toggleIpcamListId(ipcam.id)">
                      編輯
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination :items="filteredIpcamLists" @changePage="onChangeIpcamPage"></jw-pagination>
        </div>
      </div>
    </div>
    <div class="row">
      <transition name="fade">
        <div v-if="this.activeIpcamList" class="backdrop">
          <EditIpcamListDetail :key="activeIpcamList.id" :id="activeIpcamList.id" :shop-id="activeIpcamList.shop_id"
            :shop-name="activeIpcamList.shop_name" :ipcam-brand="activeIpcamList.ipcam_brand"
            :ipcam-ip="activeIpcamList.ipcam_ip" :admin-acc="activeIpcamList.admin_acc"
            :admin-pass="activeIpcamList.admin_pass" :user-acc="activeIpcamList.user_acc"
            :user-pass="activeIpcamList.user_pass" :phone-port="activeIpcamList.phone_port"
            :http-port="activeIpcamList.http_port" :tcp-port="activeIpcamList.tcp_port"
            :re-mark="activeIpcamList.remark" @onClose="toggleIpcamListId">
          </EditIpcamListDetail>
        </div>
      </transition>
    </div>
  </div>
  <base-card v-else>No Data</base-card>
</template>

<script>
import Vue from "vue";
import {
  getBranchListAPI,
  getIpcamListAPI
} from "../../service/apis.js";

import { PaginationPlugin } from "bootstrap-vue";
import EditIpcamListDetail from "./EditIpCamListDetail.vue"
Vue.use(PaginationPlugin);

export default {
  emits: ["close"],
  name: "IpcamLists",
  components: { EditIpcamListDetail },
  data() {
    return {
      branch_lists: [],
      ipcam_lists: [],
      pageOfIpcams: [],

      selected_branch: 0,
      selected_ipcam: 0,

      searchKeyWord: null,
      activeIpcamList: null,
      dialogIsVisible: true,
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    filteredIpcamLists() {
      // KeyWord Search
      let ipcam_lists = this.ipcam_lists;
      const searchKeyWord = (ipcam) => {
        let shop_id = ipcam.shop_id.toString();
        const hasShopIdFilter = shop_id.includes(this.searchKeyWord);
        const hasShopNameFilter = ipcam.shop_name.toLowerCase().includes(this.searchKeyWord.toLowerCase());

        if (hasShopIdFilter == true) {
          return hasShopIdFilter
        } else if (hasShopNameFilter == true) {
          return hasShopNameFilter
        }
      }

      if (this.searchKeyWord) {
        ipcam_lists = ipcam_lists.filter(searchKeyWord);
      }

      return ipcam_lists;
    },
  },
  mounted: function () {
    this.get_branch_lists();
    this.get_ipcam_lists();
  },
  created() {
    // reflash data list when chiled component update data
    this.$root.$on("get_ipcam_lists", this.get_ipcam_lists);
  },
  methods: {
    async get_branch_lists() {
      await getBranchListAPI().then((response) => (this.branch_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    async get_ipcam_lists() {
      await getIpcamListAPI().then((response) => (this.ipcam_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    onSelectedChange(selected_branch_id) {
      if (selected_branch_id === "0") {
        this.get_ipcam_lists();
      } else {
        this.get_ipcam_lists_by_branchId(selected_branch_id);
      }
    },
    onChangeIpcamPage(pageOfIpcams) {
      // update page of items
      this.pageOfIpcams = pageOfIpcams;
    },
    toggleIpcamListId(ipcamId) {
      console.log(ipcamId);
      this.activeIpcamList = this.ipcam_lists.find((item) => item.id === ipcamId);
      console.log(this.activeIpcamList);
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