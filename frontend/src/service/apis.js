import axios from '../service/http'

export function postUserLogInAPI(data){
    return axios({
        url: "/user/login",
        method: 'post',
        data: data
    })
}

export function getUserAPI(){
    return axios({
        url: "/user/",
        method: 'get'
    })
}

export function getUserIdAPI(user_id){
    return axios({
        url: "/user/" + user_id,
        method: 'get'
    })
}

export function getUserMyAPI(){
    return axios({
        url: "/user/my",
        method: 'get'
    })
}

export function postUserAPI(data){
    return axios({
        url: "/user/",
        method: 'post',
        data: data
    })
}

export function getTaskAPI(){
    return axios({
        url: "/task/",
        method: 'get'
    })
}

export function getTaskIdAPI(task_id){
    return axios({
        url: "/task/" + task_id,
        method: 'get'
    })
}

export function postTaskAPI(data){
    return axios({
        url: "/task/",
        method: 'post',
        data: data
    })
}

export function getWorkhourAPI(){
    return axios({
        url: "/workhour/",
        method: 'get'
    })
}

export function getWorkhourIdAPI(workhour_id){
    return axios({
        url: "/workhour/" + workhour_id,
        method: 'get'
    })
}

export function getWorkhourMyPI(){
    return axios({
        url: "/workhour/my",
        method: 'get'
    })
}

export function postWorkhourAPI(data){
    return axios({
        url: "/workhour/",
        method: 'post',
        data: data
    })
}