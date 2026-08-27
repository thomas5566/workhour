<template>
  <div v-if="isLoggedIn">
    <div class="inventory-filter-row">
      <div class="inventory-filter-action">
        <router-link to="/fetnetlist/add" class="btn btn-primary"><i class="fas fa-plus"></i> 新增遠傳資料</router-link>
      </div>
      <div class="inventory-filter-select">
        <select class="custom-select" v-model="selected_branch" @change="onSelectedChange(selected_branch)">
          <option value="0" selected>遠傳清單 - 全部門店</option>
          <!-- <option v-for="branch in branch_lists" :key="branch.id" :value="branch.id">
            {{ branch.branch_title }} - {{ branch.branch_name }}
          </option> -->
        </select>
      </div>
      <div class="inventory-filter-search">
        <input type="search" v-model="searchKeyWord" class="form-control" placeholder="Search Key Word">
      </div>
    </div>
    <div class="row">
      <div class="card text-center">
        <div class="card-header" style="text-align: center">
          <h4>遠傳清單</h4>
          <h6>報修專線：4499112 手機需加區碼02</h6>
          <h6>進入後語音宣告按照1、2、0的順續即可</h6>
          <h6>遠傳客服4499365-2-0</h6>
        </div>
        <div class="card-body">
          <div class="table-responsive-xl">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">店別/名</th>
                  <th scope="col">統編</th>
                  <th scope="col">安裝地址</th>
                  <th scope="col">公司名稱</th>
                  <th scope="col">電話/市話</th>
                  <th scope="col">簡碼</th>
                  <th scope="col">光世代電路號碼(網路)</th>
                  <th scope="col">市話NGN號碼(網路電話)</th>
                  <th scope="col">ADSL金流附掛(刷卡機網路)</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="fetnet in pageOfFetnets" :key="fetnet.id">
                  <td>{{ fetnet.shop_id }} {{ fetnet.shop_name }}</td>
                  <td>{{ fetnet.shop_tax }}</td>
                  <td>{{ fetnet.shop_location }}</td>
                  <td>{{ fetnet.fetnetlist_remark }}</td>
                  <td>{{ fetnet.shop_phone_number }}</td>
                  <td>{{ fetnet.shop_phone_short_code }}</td>
                  <td>{{ fetnet.adsl_number }}</td>
                  <td>{{ fetnet.fetnet_phone_number }}</td>
                  <td>{{ fetnet.adsl_bank_number }}</td>
                  <td>
                    <button type="button" class="btn btn-sm btn-outline-warning" @click="toggleFetnetListId(fetnet.id)">
                      編輯
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination :items="filteredFetnetLists" @changePage="onChangeFetnetPage"></jw-pagination>
        </div>
      </div>
    </div>
    <div class="row">
      <transition name="fade">
        <div v-if="activeFetnetList" class="backdrop">
          <EditFetnetListDetail :key="activeFetnetList.id" :id="activeFetnetList.id"
            :branch-id="activeFetnetList.branch_id" :shop-id="activeFetnetList.shop_id"
            :shop-name="activeFetnetList.shop_name" :shop-tax="activeFetnetList.shop_tax"
            :shop-location="activeFetnetList.shop_location" :shop-phone-number="activeFetnetList.shop_phone_number"
            :shop-phone-short-code="activeFetnetList.shop_phone_short_code" :adsl-number="activeFetnetList.adsl_number"
            :fetnet-phone-number="activeFetnetList.fetnet_phone_number"
            :adsl-bank-number="activeFetnetList.adsl_bank_number"
            :fetnetlist-remark="activeFetnetList.fetnetlist_remark" @onClose="activeFetnetList = null"
            @updated="handleUpdated">
          </EditFetnetListDetail>
        </div>
      </transition>
    </div>
  </div>
  <base-card v-else>No Data</base-card>
</template>

<script>
import {
  getBranchListAPI,
  getFetnetListAPI,
  getFetnetByBranchIdAPI
} from "../../service/apis.js";

import EditFetnetListDetail from "./EditFetnetListDetail.vue"

export default {
  emits: ["close"],
  name: "FetnetLists",
  components: { EditFetnetListDetail },
  data() {
    return {
      branch_lists: [],
      fetnet_lists: [],
      pageOfFetnets: [],

      selected_branch: 0,
      selected_fetnet: 0,

      searchKeyWord: null,
      activeFetnetList: null,
      dialogIsVisible: true,
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    filteredFetnetLists() {
      // KeyWord Search
      let fetnet_lists = this.fetnet_lists;
      const searchKeyWord = (fetnet) => {
        let shop_id = fetnet.shop_id.toString();
        const hasShopIdFilter = shop_id.includes(this.searchKeyWord);
        const hasShopNameFilter = fetnet.shop_name.toLowerCase().includes(this.searchKeyWord.toLowerCase());

        if (hasShopIdFilter == true) {
          return hasShopIdFilter
        } else if (hasShopNameFilter == true) {
          return hasShopNameFilter
        }
      }

      if (this.searchKeyWord) {
        fetnet_lists = fetnet_lists.filter(searchKeyWord);
      }

      return fetnet_lists;
    },
  },
  mounted: function () {
    this.get_branch_lists();
    this.get_fetnet_lists();
  },
  methods: {
    async get_branch_lists() {
      await getBranchListAPI().then((response) => (this.branch_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    async get_fetnet_lists() {
      await getFetnetListAPI().then((response) => (this.fetnet_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    async get_fetnet_lists_by_branchId(branch_id) {
      this.fetnet_lists = [];
      await getFetnetByBranchIdAPI(branch_id).then((response) => (this.fetnet_lists = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    onSelectedChange(selected_branch_id) {
      if (selected_branch_id === "0") {
        this.get_fetnet_lists();
      } else {
        this.get_fetnet_lists_by_branchId(selected_branch_id);
      }
    },
    onChangeFetnetPage(pageOfFetnets) {
      // update page of items
      this.pageOfFetnets = pageOfFetnets;
    },
    toggleFetnetListId(fetnetId) {
      this.activeFetnetList = this.fetnet_lists.find((item) => item.id === fetnetId);
      this.dialogIsVisible = false;
    },
    async handleUpdated() {
      this.activeFetnetList = null;
      await this.get_fetnet_lists();
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

.inventory-filter-row { display: flex; align-items: center; gap: 12px; width: 100%; margin-bottom: 14px; }
.inventory-filter-action { flex: 0 0 auto; }
.inventory-filter-select { flex: 0 1 340px; min-width: 230px; }
.inventory-filter-search { flex: 1 1 360px; min-width: 240px; }
.inventory-filter-row select, .inventory-filter-row input { width: 100%; height: 42px; margin: 0; }
@media (max-width: 700px) { .inventory-filter-row { align-items: stretch; flex-direction: column; }.inventory-filter-action a { width: 100%; }.inventory-filter-select, .inventory-filter-search { flex-basis: auto; width: 100%; min-width: 0; } }
</style>
