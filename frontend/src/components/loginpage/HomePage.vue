<template>
  <div v-if="isLoggedIn">
    <!-- <b-button
        squared
        variant="outline-primary"
        v-for="tab in tabs"
        :key="tab"
        @click="component = tab"
        >{{ tab }}
      </b-button> -->
    <keep-alive>
      <component :is="component" />
    </keep-alive>
  </div>
  <base-card v-else>No Data</base-card>
</template>
<script>
import Vue from "vue";
import axios from "axios";

import WorkhourLists from "../worklist/WorkhourLists.vue";
import DaysOffLists from "../hr/DaysOffLists.vue";

Vue.use(axios);

export default {
  name: "Home",
  components: {
    WorkhourLists,
    DaysOffLists,
  },
  props: {
    msg: String,
  },
  data() {
    return {
      // tabs: ["WorkhourLists", "DaysOffLists"],
      component: "WorkhourLists",
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function () {},
  methods: {},
};
</script>
