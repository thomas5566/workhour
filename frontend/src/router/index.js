import { createRouter, createWebHashHistory } from "vue-router";
import LoginPage from "../components/loginpage/LoginPage.vue";
import store from "@/store";

// Lazy routes keep heavy reporting/grid libraries out of the login bundle.
const RegisterPage = () => import("../components/loginpage/RegisterPage.vue");
const HomePage = () => import("../components/loginpage/HomePage.vue");
const User = () => import("../components/user/UserList.vue");
const UserDetail = () => import("../components/user/UserDetail.vue");
const Task = () => import("../components/task/AddTask.vue");
const TaskDetail = () => import("../components/task/TaskDetail.vue");
const Expen = () => import("../components/expenlist/AddExpen.vue");
const Expentask = () => import("../components/expenlist/AddExpentask.vue");
const Workhour = () => import("../components/worklist/AddWorkhour.vue");
const WorkhourDetail = () => import("../components/worklist/WorkhourDetail.vue");
const PdfPage = () => import("@/components/layouts/PdfPage.vue");
const StoredMembers = () => import("../components/hr/StoredMembers.vue");
const AlluserWorklists = () => import("../pages/AlluserWorklists.vue");
const DashboardV2 = () => import("../pages/DashboardV2.vue");
const AllWorkLists = () => import("../components/worklist/AllWorkLists.vue");
const ChartExample = () => import("../components/worklist/ChartExample.vue");
const ServerList = () => import("../components/serverlist/ServerListDetail.vue");
const AddServerDevice = () => import("../components/serverlist/AddServerDevice.vue");
const CleanShiftSchedule = () => import("../components/cleanshiftschedule/CleanShiftSchedule.vue");
const FetnetList = () => import("../components/fetnetlist/FetnetListDetail.vue");
const AddFetnetList = () => import("../components/fetnetlist/AddFetnetList.vue");
const IpCamList = () => import("../components/ipcamlist/IpCamListDetail.vue");
const AddIpCamList = () => import("../components/ipcamlist/AddIpCamList.vue");
const InfrastructureMonitoring = () => import("../pages/InfrastructureMonitoring.vue");
const MasterDataManagement = () => import("../pages/MasterDataManagement.vue");
const UserManagement = () => import("../pages/UserManagement.vue");

export const GENERAL_USER_PATHS = new Set([
  "/home",
  "/allworkhourlist",
  "/fetnetlist",
  "/fetnetlist/add",
  "/ipcamlist",
  "/ipcamlist/add",
]);

export const IT_USER_PATHS = new Set([
  ...GENERAL_USER_PATHS,
  "/serverlist",
  "/serverlist/add",
]);

export function getAccessRole(authStore = store) {
  if (authStore.getters.getSuperUser) return "admin";
  if (authStore.getters.getchecklistAll_permission === 1) return "it";
  return "general";
}

export function canAccessPath(path, role) {
  if (role === "admin") return true;
  return (role === "it" ? IT_USER_PATHS : GENERAL_USER_PATHS).has(path);
}

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
  {
    path: "/serverlist",
    name: "ServerList",
    component: ServerList,
  },
  {
    path: "/serverlist/add",
    name: "AddServerDevice",
    component: AddServerDevice,
    meta: { requiresAuth: true },
  },
  {
    path: "/fetnetlist",
    name: "FetnetList",
    component: FetnetList,
  },
  {
    path: "/fetnetlist/add",
    name: "AddFetnetList",
    component: AddFetnetList,
    meta: { requiresAuth: true },
  },
  {
    path: "/ipcamlist",
    name: "IpCamList",
    component: IpCamList,
  },
  {
    path: "/ipcamlist/add",
    name: "AddIpCamList",
    component: AddIpCamList,
    meta: { requiresAuth: true },
  },
  {
    path: "/monitoring",
    name: "InfrastructureMonitoring",
    component: InfrastructureMonitoring,
    meta: { requiresAuth: true },
  },
  {
    path: "/master-data",
    name: "MasterDataManagement",
    component: MasterDataManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/user-management",
    name: "UserManagement",
    component: UserManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/cleanshiftschedule",
    name: "CleanShiftSchedule",
    component: CleanShiftSchedule,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to) => {
  // Clear any data-loading overlay left by the page being navigated away from.
  window.dispatchEvent(new window.Event("workhour:navigation"));
  const token = window.sessionStorage.getItem("token");
  if (to.meta.guest && token) {
    return { name: "HomePage" };
  }
  if (to.meta.guest) return true;
  if (!token) {
    return { name: "LoginPage", query: { redirect: to.fullPath } };
  }
  store.commit("RestoreToken", token);
  if (!canAccessPath(to.path, getAccessRole())) {
    return { name: "HomePage" };
  }
  return true;
});

export default router;
