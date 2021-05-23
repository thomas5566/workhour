import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Register from '../views/Register'
import Login from '../views/Login'
import User from '../views/User'
import Task from '../views/Task'
import Expen from '../views/Expen'
import Expentask from '../views/Expentask'
import Workhour from '../views/Workhour'
import UserDetail from '../views/UserDetail'
import TaskDetail from '../views/TaskDetail'
import WorkhourDetail from '../views/WorkhourDetail'

Vue.use(VueRouter)
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/register',
    name: "Register",
    component: Register,
    meta: { guest: true },
  },
  {
    path: '/login',
    name: "Login",
    component: Login,
    meta: { guest: true },
  },
  {
    path: '/user',
    name: "User",
    component: User,
  },
  {
    path: '/task',
    name: "Task",
    component: Task,
  },
  {
    path: '/expentask',
    name: "Expentask",
    component: Expentask,
  },
  {
    path: '/workhour',
    name: "Workhour",
    component: Workhour,
  },
  {
    path: '/expen',
    name: "Expen",
    component: Expen,
  },
  {
    path: '/user/:id',
    name: "UserDetail",
    component: UserDetail,
  },
  {
    path: '/task/:id',
    name: "TaskDetail",
    component: TaskDetail,
  },
  {
    path: '/workhour/:id',
    name: "WorkhourDetail",
    component: WorkhourDetail,
  },
]
const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
