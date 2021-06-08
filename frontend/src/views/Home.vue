<script src="https://cdnjs.cloudflare.com/ajax/libs/vue/2.5.17/vue.js"></script>

<template>
  <div>
    <div class="home" v-if="isLoggedIn">
      <div>
        <button v-for="tab in tabs" :key="tab" @click="component = tab">
          {{ tab }}
        </button>
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

import WorkhourLists from "../components/WorkhourLists.vue";
import ExpenLists from "../components/ExpenLists.vue"

Vue.use(axios);

export default {
  name: "Home",
  components: {
    WorkhourLists,
    ExpenLists,
  },
  props: {
    msg: String,
  },
  data() {
    return {
      tabs: ["WorkhourLists", "ExpenLists"],
      component: "WorkhourLists",
    }
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function () {
  },
  created() {
  },
  methods: {
  },
};
</script>