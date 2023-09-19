import Vue from "vue";
import VueRouter from "vue-router";
import HomePage from "../components/loginpage/HomePage.vue";
import RegisterPage from "../components/loginpage/RegisterPage";
import LoginPage from "../components/loginpage/LoginPage";
import User from "../components/user/UserList";
import UserDetail from "../components/user/UserDetail";
import Task from "../components/task/AddTask";
import TaskDetail from "../components/task/TaskDetail";
import Expen from "../components/expenlist/AddExpen";
import Expentask from "../components/expenlist/AddExpentask";
import Workhour from "../components/worklist/AddWorkhour";
import WorkhourDetail from "../components/worklist/WorkhourDetail";
import Excel from "@/components/Excel.vue";
import PdfPage from "@/components/layouts/PdfPage.vue";
import DaysOffLists from "../components/hr/DaysOffLists.vue";
import StoredMembers from "../components/hr/StoredMembers.vue";
import AlluserWorklists from "../pages/AlluserWorklists.vue";
import DashboardV2 from "../pages/DashboardV2.vue";
import AllWorkLists from "../components/worklist/AllWorkLists.vue";
import ChartExample from "../components/worklist/ChartExample.vue";

import store from "@/store";

Vue.use(VueRouter);
const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/home",
    name: "HomePage",
    component: HomePage,
  },
  {
    path: "/register",
    name: "RegisterPage",
    component: RegisterPage,
    meta: { guest: true },
  },
  {
    path: "/login",
    name: "LoginPage",
    component: LoginPage,
    meta: { guest: true },
  },

  {
    path: "/userbydp",
    name: "User",
    component: User,
  },
  {
    path: "/task",
    name: "Task",
    component: Task,
  },
  {
    path: "/expentask",
    name: "Expentask",
    component: Expentask,
  },
  {
    path: "/workhour",
    name: "Workhour",
    component: Workhour,
    meta: { requiresAuth: true },
  },
  {
    path: "/allworkhourlist",
    name: "AllWorkhourList",
    component: AllWorkLists,
    meta: { requiresAuth: true },
  },
  {
    path: "/chartExample",
    name: "ChartExample",
    component: ChartExample,
  },
  {
    path: "/expen",
    name: "Expen",
    component: Expen,
  },
  {
    path: "/excel",
    name: "Excel",
    component: Excel,
  },
  {
    path: "/user/:id",
    name: "UserDetail",
    component: UserDetail,
  },
  // {
  //   path: "/task/:id",
  //   name: "TaskDetail",
  //   component: TaskDetail,
  // },
  {
    path: "/taskbg/",
    name: "TaskDetail",
    component: TaskDetail,
  },
  {
    path: "/workhour/:id",
    name: "WorkhourDetail",
    component: WorkhourDetail,
  },
  {
    path: "/pdfpage",
    name: "PdfPage",
    component: PdfPage,
  },
  {
    path: "/daysoff",
    name: "DaysOffLists",
    component: DaysOffLists,
  },
  {
    path: "/members",
    name: "StoredMembers",
    component: StoredMembers,
  },
  {
    path: "/alluserworklists",
    name: "AlluserWorklists",
    component: AlluserWorklists,
  },
  {
    path: "/dashboardV2",
    name: "DashboardV2",
    component: DashboardV2,
  },
];

const router = new VueRouter({
  mode: "hash",
  hash: true,
  // base: process.env.BASE_URL,
  routes,
});

router.beforeEach((to, from, next) => {
  // 一開始於Login寫入的Token
  const token = window.sessionStorage.getItem("token");
  // 有token又到登入頁，就導向HomePage
  if (to.name === "LoginPage" && token) {
    next({ name: "HomePage" });
  }
  // 判斷有要求權限的頁面檢查token
  if (to.matched.some((res) => res.meta.requiresAuth)) {
    if (token) {
      // 同步sessionStorage的token至vuex中
      store.dispatch("root/setToken", token);
      next();
    } else {
      next({ name: "LoginPage" });
    }
  } else {
    next();
  }
});

export default router;
