import axios from "axios";
import { Loading, Message } from "element-ui";
import router from "../router/index.js";
import store from "../store";

let loading;

function startLoading() {
  loading = Loading.service({
    lock: true,
    text: "載入中....",
    background: "rgba(0, 0, 0, 0.7)",
  });
}

function endLoading() {
  loading.close();
}

axios.defaults.withCredentials = true;
axios.defaults.baseURL = "http://10.133.6.45:8000/api/";
// axios.defaults.baseURL = "http://127.0.0.1:8000/api/";
// axios.defaults.baseURL = 'http://192.168.0.123:8000/';
// axios.defaults.baseURL = "http://192.168.0.124:8000/";
// axios.defaults.baseURL = "http://127.0.0.1:5566/";

// 請求攔截
axios.interceptors.request.use(
  (confing) => {
    startLoading();
    //設定請求頭
    if (store.getters.isAuthenticated) {
      confing.headers.Authorization = "Bearer " + store.getters.getToken;
    }
    return confing;
  },
  (error) => {
    return Promise.reject(error);
  }
);

//響應攔截
axios.interceptors.response.use(
  (response) => {
    endLoading();
    return response;
  },
  (error) => {
    console.log(error);
    Message.error(error.response.data);
    endLoading();

    // 獲取狀態碼
    const { status } = error.response;

    if (status === 401) {
      Message.error("請重新登入");
      //清楚token
      //console.log(this.$store);
      // this.$store.dispatch("LogOut");
      //跳轉到登入頁面
      router.push("/login").catch((error) => {
        console.info(error.message);
      });
    }
    if (status === 400) {
      Message.error("Bad Request");
      //清楚token
      this.$store.dispatch("LogOut");
      //跳轉到登入頁面
      router.push("/").catch((error) => {
        console.info(error.message);
      });
    }
    if (status === 404) {
      Message.error("Page Not Found");
      //跳轉到登入頁面
      router.push("/").catch((error) => {
        console.info(error.message);
      });
    }
    return Promise.reject(error);
  }
);

export default axios;
