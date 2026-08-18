import { createBootstrap } from "bootstrap-vue-next";
import { configureCompat, createApp, defineComponent, h } from "vue";

import App from "./App.vue";
import BaseButton from "./components/UI/BaseButton.vue";
import BaseCard from "./components/UI/BaseCard.vue";
import JwPagination from "./components/UI/JwPagination.vue";
import BFormDatepicker from "./components/compat/BFormDatepicker.vue";
import BIcon from "./components/compat/BIcon.vue";
import BInputGroupAddon from "./components/compat/BInputGroupAddon.vue";
import router from "./router";
import store from "./store";

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "element-plus/dist/index.css";
import "admin-lte/dist/css/adminlte.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

// MODE 2 keeps legacy Options API views operational while warnings guide cleanup.
configureCompat({ MODE: 2 });

const app = createApp(App);
const inputGroupAddon = (position) => defineComponent({
  name: `BInputGroup${position === "append" ? "Append" : "Prepend"}`,
  setup(_props, { slots }) {
    return () => h(BInputGroupAddon, { position }, slots);
  },
});
app.use(store);
app.use(router);
app.use(createBootstrap());
app.component("BaseCard", BaseCard);
app.component("BaseButton", BaseButton);
app.component("JwPagination", JwPagination);
app.component("BFormDatepicker", BFormDatepicker);
app.component("BIcon", BIcon);
app.component("BInputGroupAppend", inputGroupAddon("append"));
app.component("BInputGroupPrepend", inputGroupAddon("prepend"));
app.mount("#app");
