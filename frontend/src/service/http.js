import axios from "axios";
import { ElLoading, ElMessage } from "element-plus";

import router from "../router";
import store from "../store";

const http = axios.create({
  // Development uses Vite's /api proxy; deployments can provide an absolute URL.
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

let loadingInstance;
let activeRequests = 0;

function startLoading() {
  activeRequests += 1;
  if (!loadingInstance) {
    const contentTarget = document.querySelector(".content-wrapper");
    // Keep navigation available while data-heavy Dashboard requests load.
    // Guest pages do not have a content wrapper, so they skip this indicator.
    if (!contentTarget) return;
    loadingInstance = ElLoading.service({
      target: contentTarget,
      fullscreen: false,
      lock: false,
      text: "載入中…",
      background: "rgba(244, 246, 249, 0.72)",
    });
  }
}

function endLoading() {
  activeRequests = Math.max(0, activeRequests - 1);
  if (activeRequests === 0 && loadingInstance) {
    loadingInstance.close();
    loadingInstance = undefined;
  }
}

function resetLoading() {
  activeRequests = 0;
  if (loadingInstance) {
    loadingInstance.close();
    loadingInstance = undefined;
  }
}

// Router imports the store, which imports this HTTP module. A DOM event avoids
// calling the still-uninitialized router during that circular module load.
window.addEventListener("workhour:navigation", resetLoading);

http.interceptors.request.use(
  (config) => {
    if (!config.background) startLoading();
    const token = store.getters.getToken || window.sessionStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    if (!error.config?.background) endLoading();
    return Promise.reject(error);
  },
);

http.interceptors.response.use(
  (response) => {
    if (!response.config.background) endLoading();
    return response;
  },
  async (error) => {
    if (!error.config?.background) endLoading();
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    if (!error.config?.silent) {
      ElMessage.error(typeof detail === "string" ? detail : "伺服器連線失敗，請稍後再試");
    }

    if (status === 401) {
      await store.dispatch("LogOut");
      if (router.currentRoute.value.name !== "LoginPage") {
        await router.push({ name: "LoginPage" });
      }
    }
    return Promise.reject(error);
  },
);

export default http;
