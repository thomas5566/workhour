import axios from "../service/http";

export function postUserLogInAPI(data) {
  return axios({
    url: "/user/login",
    // url: "login/token",
    method: "post",
    data: data,
  });
}

export function postUserLogoutAPI() {
  return axios({
    url: "/user/logout",
    method: "post",
    background: true,
    silent: true,
    // An expired token may make logout return 401. Avoid dispatching logout
    // recursively from the global response interceptor.
    skipAuthLogout: true,
  });
}

export function getUserAPI() {
  return axios({
    url: "/user/",
    method: "get",
  });
}

export function getUserByDpAPI() {
  return axios({
    url: "/user/get-dpuser",
    method: "get",
  });
}

export function getUsersAllAPI() {
  return axios({
    url: "/user/users-alldata",
    method: "get",
  });
}

export function getUserIdAPI(user_id) {
  return axios({
    url: "/user/" + user_id,
    method: "get",
  });
}

export function getUserMyAPI() {
  return axios({
    url: "/user/my",
    method: "get",
  });
}

export function postUserAPI(data) {
  return axios({
    url: "/user/",
    method: "post",
    data: data,
  });
}

export function createAdminUserAPI(data) {
  return axios({
    url: "/user/admin",
    method: "post",
    data,
  });
}

export function updateAdminUserAPI(userId, data) {
  return axios({
    url: `/user/admin/${userId}`,
    method: "put",
    data,
  });
}

export function deleteAdminUserAPI(userId) {
  return axios({
    url: `/user/admin/${userId}`,
    method: "delete",
  });
}

export function registerUserAPI(data) {
  return axios({
    url: "/user/register",
    method: "post",
    data,
  });
}

export function getRegistrationDepartmentsAPI() {
  return axios({
    url: "/user/registration-departments",
    method: "get",
  });
}

export function getTaskAPI() {
  return axios({
    url: "/task/",
    method: "get",
  });
}

export function getTaskIdAPI(task_id) {
  return axios({
    url: "/task/" + task_id,
    method: "get",
  });
}

export function getTaskByGroupAPI() {
  return axios({
    url: "/task/tasksgbw/",
    method: "get",
  });
}

export function postTaskAPI(data) {
  return axios({
    url: "/task/",
    method: "post",
    data: data,
  });
}

export function deleteTaskAPI(task_id) {
  return axios({
    url: `/task/${task_id}`,
    method: "delete",
  });
}

export function getExpentaskAPI() {
  return axios({
    url: "/expentask/",
    method: "get",
  });
}

export function getExpentaskIdAPI(Expentask_id) {
  return axios({
    url: "/expentask/" + Expentask_id,
    method: "get",
  });
}

export function postExpentaskAPI(data) {
  return axios({
    url: "/expentask/",
    method: "post",
    data: data,
  });
}

export function getWorkhourAPI() {
  return axios({
    url: "/workhour/workhours",
    method: "get",
  });
}

export function getAllWorkhourAPI() {
  return axios({
    url: "/workhour/allworkhours",
    method: "get",
  });
}

export function getAllWorkListsByDateAPI() {
  return axios({
    url: "/workhour/worklist-year-month",
    method: "get",
  });
}

export function getAllWorkListsByUserIdAPI() {
  return axios({
    url: "/workhour/worklist-userid",
    method: "get",
  });
}

export function getAllWorkListsByShopIdAPI() {
  return axios({
    url: "/workhour/worklist-shopid",
    method: "get",
  });
}

export function getWorkhourIdAPI(workhour_id) {
  return axios({
    url: "/workhour/" + workhour_id,
    method: "get",
  });
}

export function getMonthlyWorkhourAPI(user_id) {
  return axios({
    url: "/workhour/totalhour/" + user_id,
    method: "get",
  });
}

export function getWorkhourMyAPI(user_id) {
  return axios({
    url: "/workhour/my/" + user_id,
    method: "get",
  });
}

export function postWorkhourAPI(data) {
  return axios({
    url: "/workhour/",
    method: "post",
    data: data,
  });
}

export function updateWorkhourAPI(workhour_id, data) {
  return axios({
    url: `/workhour/${workhour_id}`,
    method: "put",
    data: data,
  });
}

export function deleteWorkhourAPI(workhour_id) {
  return axios({
    url: `/workhour/${workhour_id}`,
    method: "delete",
  });
}

export function getExpenAPI() {
  return axios({
    url: "/expen/expens",
    method: "get",
  });
}

export function getExpenIdAPI(expen_id) {
  return axios({
    url: "/expen/" + expen_id,
    method: "get",
  });
}

export function getMonthlyExpenAPI(user_id) {
  return axios({
    url: "/expen/totalexpen/" + user_id,
    method: "get",
  });
}

export function postExpenAPI(data) {
  return axios({
    url: "/expen/",
    method: "post",
    data: data,
  });
}

export function getExpenMyAPI(user_id) {
  return axios({
    url: "/expen/my/" + user_id,
    method: "get",
  });
}

export function deleteExpenAPI(expen_id) {
  return axios({
    url: `/expen/${expen_id}`,
    method: "delete",
  });
}

export function updateExpenAPI(expen_id, data) {
  return axios({
    url: `/expen/${expen_id}`,
    method: "put",
    data: data,
  });
}

export function getDepartmentsAPI() {
  return axios({
    url: "/department/",
    method: "get",
  });
}

export function getBranchListAPI() {
  return axios({
    url: "/branchlist/",
    method: "get",
  });
}

export function createBranchListAPI(data) {
  return axios({
    url: "/branchlist/",
    method: "post",
    data,
  });
}

export function updateBranchListAPI(id, data) {
  return axios({
    url: `/branchlist/${id}`,
    method: "put",
    data,
  });
}

export function deleteBranchListAPI(id) {
  return axios({
    url: `/branchlist/${id}`,
    method: "delete",
  });
}

export function getCstShopsAPI(mainDepartmentId) {
  return axios({
    url: "/cstshop/",
    method: "get",
    params: { main_department_id: mainDepartmentId },
  });
}

export function createCstShopAPI(data) {
  return axios({
    url: "/cstshop/",
    method: "post",
    data,
  });
}

export function updateCstShopAPI(id, data) {
  return axios({
    url: `/cstshop/${id}`,
    method: "put",
    data,
  });
}

export function deleteCstShopAPI(id) {
  return axios({
    url: `/cstshop/${id}`,
    method: "delete",
  });
}

export function createDepartmentAPI(data) {
  return axios({
    url: "/department/",
    method: "post",
    data,
  });
}

export function updateDepartmentAPI(id, data) {
  return axios({
    url: `/department/${id}`,
    method: "put",
    data,
  });
}

export function deleteDepartmentAPI(id) {
  return axios({
    url: `/department/${id}`,
    method: "delete",
  });
}

export function getServerListAPI() {
  return axios({
    url: "/serverlist/",
    method: "get",
  });
}

export function createServerListAPI(data) {
  return axios({
    url: "/serverlist/",
    method: "post",
    data,
  });
}

export function deleteServerListAPI(serverlist_id) {
  return axios({
    url: `/serverlist/${serverlist_id}`,
    method: "delete",
  });
}

export function getServerListByBranchIdAPI(branch_id) {
  return axios({
    url: "/serverlist/serverlist-branchid?branch_id=" + branch_id,
    method: "get",
  });
}

export function updateServerListByIdAPI(serverlist_id, data) {
  return axios({
    url: `/serverlist/${serverlist_id}`,
    method: "put",
    data: data,
  });
}

export function revealServerPasswordAPI(serverlist_id) {
  return axios({
    url: `/serverlist/${serverlist_id}/reveal-password`,
    method: "post",
  });
}

export function getFetnetListAPI() {
  return axios({
    url: "/fetnetlist/",
    method: "get",
  });
}

export function createFetnetListAPI(data) {
  return axios({
    url: "/fetnetlist/",
    method: "post",
    data,
  });
}

export function getFetnetByBranchIdAPI(branch_id) {
  return axios({
    url: "/fetnetlist/fetnetlist-branchid?branch_id=" + branch_id,
    method: "get",
  });
}

export function updateFetnetListByIdAPI(fetnetlist_id, data) {
  return axios({
    url: `/fetnetlist/${fetnetlist_id}`,
    method: "put",
    data: data,
  });
}

export function deleteFetnetListAPI(fetnetlist_id) {
  return axios({
    url: `/fetnetlist/${fetnetlist_id}`,
    method: "delete",
  });
}

export function getIpcamListAPI() {
  return axios({
    url: "/ipcamlist/",
    method: "get",
  });
}

export function createIpcamListAPI(data) {
  return axios({
    url: "/ipcamlist/",
    method: "post",
    data,
  });
}

export function updateIpCamListByIdAPI(ipcamlist_id, data) {
  return axios({
    url: `/ipcamlist/${ipcamlist_id}`,
    method: "put",
    data: data,
  });
}

export function deleteIpCamListAPI(ipcamlist_id) {
  return axios({
    url: `/ipcamlist/${ipcamlist_id}`,
    method: "delete",
  });
}

export function revealIpCamPasswordsAPI(ipcamlist_id) {
  return axios({
    url: `/ipcamlist/${ipcamlist_id}/reveal-passwords`,
    method: "post",
  });
}

export function getMonitoringSummaryAPI({ background = false, silent = false } = {}) {
  return axios({
    url: "/monitoring/summary",
    method: "get",
    // Background polling must not cover whichever page the user is viewing.
    background,
    silent,
  });
}

export function getMonitoringAlertLogsAPI(params = {}) {
  return axios({
    url: "/monitoring/alert-logs",
    method: "get",
    params,
  });
}
