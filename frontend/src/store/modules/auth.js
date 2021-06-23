//store/modules/auth.js
import { postUserLogInAPI } from "../../service/apis.js";

const state = {
    token: "",
    expiration: Date.now(),
    username: null
};  
const getters = {
    getToken: (state) => state.token,
    getUsername: (state) => state.username,
    getFullname: (state) => state.fullname,
    getSuperUser: (state) => state.is_superuser,
    getchecklistAll_permission: (state) => state.checklistAll_permission,
    isAuthenticated: (state) => state.token.length > 0 && state.expiration > Date.now()
    
};
const actions = {
    async LogIn({commit}, model) {
         await postUserLogInAPI(model).then(function (response) {
                if(response.status == 200){
                    commit("LogIn", response.data)
                }
            })
    },
    async LogOut({commit}){
        commit('LogOut')
    }
};
const mutations = {
    LogIn(state,data){
        state.username = data.username
        state.fullname = data.fullname
        state.is_superuser = data.is_superuser
        state.checklistAll_permission = data.checklistAll_permission
        state.token = data.token
        state.expiration = new Date(data.expiration)
    },
    LogOut(state){
        state.username = null
        state.fullname = null
        state.is_superuser = null
        state.checklistAll_permission = null
        state.token = ""
        state.expiration = Date.now();
    },
};
export default {
  state,
  getters,
  actions,
  mutations
};
