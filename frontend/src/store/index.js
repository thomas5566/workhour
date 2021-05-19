import Vuex from 'vuex';
import Vue from 'vue';
import createPersistedState from "vuex-persistedstate";
import auth from './modules/auth';

// Load Vuex
Vue.use(Vuex);
// Create store
const store = new Vuex.Store({
  modules: {
    auth
  },
  plugins: [createPersistedState()]
});

export default store