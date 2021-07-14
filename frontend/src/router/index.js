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
// import StoredMembers from '../components/hr/StoredMembers.vue'

Vue.use(VueRouter);
const routes = [
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
    path: "/user",
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
  // {
  //   path: "/members",
  //   name: "StoredMembers",
  //   component: StoredMembers,
  // },
];
const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
