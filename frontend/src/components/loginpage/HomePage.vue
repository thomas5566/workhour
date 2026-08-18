<template>
  <div v-if="isLoggedIn">
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

Vue.use(axios);

export default {
  name: "Home",
  components: {
    WorkhourLists,
  },
  props: {
    msg: String,
  },
  data() {
    return {
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
