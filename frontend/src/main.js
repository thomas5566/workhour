import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
// import ElementUI from 'element-ui';
// import 'element-ui/lib/theme-chalk/index.css';
// import './plugins/element.js'

// Import Bootstrap an BootstrapVue CSS files (order is important)
import { BootstrapVue, IconsPlugin } from "bootstrap-vue";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

// register jw pagination component globally
import JwPagination from "jw-vue-pagination";

// Custom UI
import BaseCard from "./components/UI/BaseCard.vue";
import BaseButton from "./components/UI/BaseButton.vue";

//import adminlte styles
import "../node_modules/admin-lte/dist/css/adminlte.min.css";
import "../node_modules/admin-lte/plugins/overlayScrollbars/css/OverlayScrollbars.min.css";
import "../node_modules/admin-lte/plugins/summernote/summernote-bs4.min.css";
import "../node_modules/admin-lte/plugins/daterangepicker/daterangepicker.css";
import "../node_modules/admin-lte/plugins/jqvmap/jqvmap.min.css";
import "../node_modules/admin-lte/plugins/icheck-bootstrap/icheck-bootstrap.min.css";
import "../node_modules/admin-lte/plugins/tempusdominus-bootstrap-4/css/tempusdominus-bootstrap-4.min.css";
import "../node_modules/admin-lte/plugins/bootstrap4-duallistbox/bootstrap-duallistbox.min.css";
import "../node_modules/admin-lte/plugins/bs-stepper/css/bs-stepper.min.css";
import "../node_modules/admin-lte/plugins/dropzone/min/dropzone.min.css";
import "../node_modules/admin-lte/plugins/fontawesome-free/css/all.min.css";

Vue.component("jw-pagination", JwPagination);
Vue.component("base-card", BaseCard);
Vue.component("base-button", BaseButton);
// Make BootstrapVue available throughout your project
Vue.use(BootstrapVue);
// Optionally install the BootstrapVue icon components plugin
Vue.use(IconsPlugin);
// Vue.use(ElementUI);

Vue.config.productionTip = false;
export default new Vue({
  store,
  router,
  render: (h) => h(App),
}).$mount("#app");
