import axios from '../service/http'

export function postUserLogInAPI(data) {
    return axios({
        url: "/user/login",
        // url: "login/token",
        method: 'post',
        data: data
    })
}

export function getUserAPI() {
    return axios({
        url: "/user/",
        method: 'get'
    })
}

export function getUserByDpAPI() {
    return axios({
        url: "/user/get-dpuser",
        method: 'get'
    })
}

export function getUserIdAPI(user_id) {
    return axios({
        url: "/user/" + user_id,
        method: 'get'
    })
}

export function getUserMyAPI() {
    return axios({
        url: "/user/my",
        method: 'get'
    })
}

export function postUserAPI(data) {
    return axios({
        url: "/user/",
        method: 'post',
        data: data
    })
}

export function getTaskAPI() {
    return axios({
        url: "/task/",
        method: 'get'
    })
}

export function getTaskIdAPI(task_id) {
    return axios({
        url: "/task/" + task_id,
        method: 'get'
    })
}

export function getTaskByGroupAPI() {
    return axios({
        url: "/task/tasksgbw/",
        method: 'get'
    })
}

export function postTaskAPI(data) {
    return axios({
        url: "/task/",
        method: 'post',
        data: data
    })
}

export function deleteTaskAPI(task_id) {
    return axios({
        url: `/task/${task_id}`,
        method: 'delete'
    })
}

export function getExpentaskAPI() {
    return axios({
        url: "/expentask/",
        method: 'get'
    })
}

export function getExpentaskIdAPI(Expentask_id) {
    return axios({
        url: "/expentask/" + Expentask_id,
        method: 'get'
    })
}

export function postExpentaskAPI(data) {
    return axios({
        url: "/expentask/",
        method: 'post',
        data: data
    })
}

export function getWorkhourAPI() {
    return axios({
        url: "/workhour/workhours",
        method: 'get'
    })
}

export function getWorkhourIdAPI(workhour_id) {
    return axios({
        url: "/workhour/" + workhour_id,
        method: 'get'
    })
}

export function getMonthlyWorkhourAPI(user_id) {
    return axios({
        url: "/workhour/totalhour/" + user_id,
        method: 'get'
    })
}

export function getWorkhourMyAPI(user_id) {
    return axios({
        url: "/workhour/my/" + user_id,
        method: 'get'
    })
}

export function postWorkhourAPI(data) {
    return axios({
        url: "/workhour/",
        method: 'post',
        data: data
    })
}

export function updateWorkhourAPI(workhour_id, data) {
    return axios({
        url: `/workhour/${workhour_id}`,
        method: 'put',
        data: data
    })
}

export function deleteWorkhourAPI(workhour_id) {
    return axios({
        url: `/workhour/${workhour_id}`,
        method: 'delete'
    })
}

export function getExpenAPI() {
    return axios({
        url: "/expen/expens",
        method: 'get'
    })
}

export function getExpenIdAPI(expen_id) {
    return axios({
        url: "/expen/" + expen_id,
        method: 'get'
    })
}

export function getMonthlyExpenAPI(user_id) {
    return axios({
        url: "/expen/totalexpen/" + user_id,
        method: 'get'
    })
}

export function postExpenAPI(data) {
    return axios({
        url: "/expen/",
        method: 'post',
        data: data
    })
}

export function getExpenMyAPI(user_id) {
    return axios({
        url: "/expen/my/" + user_id,
        method: 'get'
    })
}

export function deleteExpenAPI(expen_id) {
    return axios({
        url: `/expen/${expen_id}`,
        method: 'delete'
    })
}

export function updateExpenAPI(expen_id, data) {
    return axios({
        url: `/expen/${expen_id}`,
        method: 'put',
        data: data
    })
}

export function getDepartmentsAPI() {
    return axios({
        url: "/department/",
        method: 'get'
    })
}

export function getDaysoffAPI() {
    return axios({
        url: "/daysoff/daysoffbyuser/",
        method: 'get'
    })
}

export function postDaysoffAPI(data) {
    return axios({
        url: "/daysoff/",
        method: 'post',
        data: data
    })
}

export function updateDaysoffAPI(dayoffId, data) {
    return axios({
        url: `/daysoff/${dayoffId}`,
        method: 'put',
        data: data
    })
}

export function deleteDaysoffAPI(dayoff_id) {
    return axios({
        url: `/daysoff/${dayoff_id}`,
        method: 'delete'
    })
}
