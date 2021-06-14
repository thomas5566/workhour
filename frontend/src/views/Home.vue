<template>
  <div>
    <div class="home" v-if="isLoggedIn">
      <div>
        <b-button
          pill
          variant="outline-info"
          v-for="tab in tabs"
          :key="tab"
          @click="component = tab"
          >{{ tab }}
        </b-button>

        <keep-alive>
          <component :is="component" />
        </keep-alive>
      </div>
    </div>
    <div v-else>No Data</div>
  </div>
</template>
<script>
import Vue from "vue";
import axios from "axios";

import 工作項目清單 from "../components/WorkhourLists.vue";
import 支出項目清單 from "../components/ExpenLists.vue";

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