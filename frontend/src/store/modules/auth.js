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
        state.token = data.token
        state.expiration = new Date(data.expiration)
    },
    LogOut(state){
        state.username = null
        state.fullname = null
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
