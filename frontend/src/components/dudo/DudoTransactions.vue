<template>
  <div>
    <div class="form-row">
      <div class="col">
        <date-picker v-model="datefilter" format='YYYY-MM-DD' valueType="format" range placeholder="請選擇日期範圍"
          @change="dateSelected(datefilter)"></date-picker>
      </div>
      <div class="col">
        <select class="custom-select" v-model="selected_shop_id" @change="onSelectedChange(selected_shop_id)"
          :disabled="disableOption">
          <option value="0" selected>請選擇門店ID</option>
          <option v-for="shop in shop_lists" :key="shop" :value="shop">
            {{ shop }}
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
          <h4>Dudo Transactions</h4>
        </div>
        <div class="card-body">
          <div class="table-responsive-xl">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">shop_id</th>
                  <th scope="col">amount</th>
                  <th scope="col">sale_id</th>
                  <th scope="col">sale_amount</th>
                  <th scope="col">pos_id</th>
                  <th scope="col">canceled</th>
                  <th scope="col">transaction_id</th>
                  <th scope="col">service_amount</th>
                  <th scope="col">discount_amount</th>
                  <th scope="col">sale_deleted</th>
                  <th scope="col">employee_username</th>
                  <th scope="col">shipping_fee</th>
                  <th scope="col">create_time</th>
                  <th scope="col">update_time</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="transaction in pageOfTransactions" :key="transaction.id">
                  <td>{{ transaction.shop_id }}</td>
                  <td>{{ transaction.amount }}</td>
                  <td>{{ transaction.sale_id }}</td>
                  <td>{{ transaction.sale_amount }}</td>
                  <td>{{ transaction.pos_id }}</td>
                  <td>{{ transaction.canceled }}</td>
                  <td>{{ transaction.transaction_id }}</td>
                  <td>{{ transaction.service_amount }}</td>
                  <td>{{ transaction.discount_amount }}</td>
                  <td>{{ transaction.sale_deleted }}</td>
                  <td>{{ transaction.employee_username }}</td>
                  <td>{{ transaction.shipping_fee }}</td>
                  <td>{{ transaction.create_time }}</td>
                  <td>{{ transaction.update_time }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer pb-0 pt-3">
          <jw-pagination :items="filteredTransactionLists" @changePage="onChangeTransactionPage"></jw-pagination>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import {
  getDudoTransactionsListsAPI,
  getDudoTransactionsByShopIdAPI
} from "../../service/apis.js";

import { PaginationPlugin } from "bootstrap-vue";

import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";

Vue.use(PaginationPlugin);

export default {
  emits: ["close"],
  name: "DudoTransactions",
  components: { DatePicker },
  data() {
    return {
      shop_lists: [13580, 8428, 13578, 13579, 13581, 8439, 13659, 13583, 13577, 13657, 8437, 13658, 8438, 13582, 8470, 13661, 13660, 8430],
      scope_lists: ['SHOP', 'BRAND', 'ALL'],

      transactions: [],
      pageOfTransactions: [],
      datefilter: null,
      selected_shop_id: 0,
      selected_scope_id: 0,

      searchKeyWord: null,
      activeServerList: null,
      dialogIsVisible: true,
      disableOption: true
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
    filteredTransactionLists() {
      // KeyWord Search
      let transactions_lists = this.transactions;
      const searchKeyWord = (transaction) => {
        const hasTransactionShopIdFilter = transaction.shop_id.includes(this.searchKeyWord);
        const hasTransactionEmployeeUsernameFilter = transaction.employee_username.toLowerCase().includes(this.searchKeyWord.toLowerCase());
        const hasTransactionPosIdFilter = transaction.pos_id.toLowerCase().includes(this.searchKeyWord.toLowerCase());

        if (hasTransactionShopIdFilter == true) {
          return hasTransactionShopIdFilter
        } else if (hasTransactionEmployeeUsernameFilter == true) {
          return hasTransactionEmployeeUsernameFilter
        } else if (hasTransactionPosIdFilter == true) {
          return hasTransactionPosIdFilter
        }
      }

      if (this.searchKeyWord) {
        transactions_lists = transactions_lists.filter(searchKeyWord);
      }

      return transactions_lists;
    },
  },
  mounted: function () {
    //this.get_dudoserver_transactions();
  },
  created() {
  },
  methods: {
    async get_dudoserver_transactions() {
      this.transactions = [];

      await getDudoTransactionsListsAPI().then((response) => (this.transactions = response.data))
        .catch((err) => {
          console.error(err)
        });

      console.log(this.transactions)
    },
    async get_dudoserver_transactions_by_shopId(shop_id) {
      shop_id = this.selected_shop_id;
      let search_date_start = this.datefilter[0];
      let search_date_end = this.datefilter[1];
      this.transactions = [];
      await getDudoTransactionsByShopIdAPI(shop_id, search_date_start, search_date_end).then((response) => (this.transactions = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
    onSelectedChange(selected_shop_id) {
      if (selected_shop_id === "0") {
        this.get_dudoserver_transactions();
      } else {
        this.get_dudoserver_transactions_by_shopId(selected_shop_id);
      }
    },
    onChangeTransactionPage(pageOfTransactions) {
      // update page of items
      this.pageOfTransactions = pageOfTransactions;
    },
    dateSelected(datefilter) {
      if (datefilter != null) {
        this.disableOption = false
      }
      if (datefilter[0] === null) {
        this.disableOption = true
        this.selected_shop_id = 0
      }
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