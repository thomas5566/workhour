<template>
  <base-card v-if="isLoggedIn">
    <b-button
      squared
      variant="outline-primary"
      v-for="tab in tabs"
      :key="tab"
      @click="component = tab"
      >{{ tab }}
    </b-button>
    <keep-alive>
      <component :is="component" />
    </keep-alive>
  </base-card>
  <base-card v-else>No Data</base-card>
</template>
<script>
import Vue from "vue";
import axios from "axios";

import 工作項目清單 from "../worklist/WorkhourLists.vue";
import 支出項目清單 from "../expenlist/ExpenLists.vue";

Vue.use(axios);

export default {
  name: "Home",
  components: {
    工作項目清單,
    支出項目清單,
  },
  props: {
    msg: String,
  },
  data() {
    return {
      tabs: ["工作項目清單", "支出項目清單"],
      component: "工作項目清單",
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function () {},
  created() {},
  methods: {},
};
</script>
