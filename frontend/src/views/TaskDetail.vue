<template>
<div  v-if="task">
  <div>
        <table class="table table-striped table-bordered">
            <thead>
              <tr>
                    <th colspan="4">Task Detail</th>
                </tr>
                <tr>
                    <th>id</th>
                    <th>taskname</th>
                    <th>fullname</th>
                    <th>organization</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{task.id}}</td>
                    <td>{{task.taskname}}</td>
                    <td>{{task.fullname}}</td>
                    <td>{{task.organization}}</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="workhours" v-if="task.workhours.length">
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th colspan="7">Workhours</th>
                </tr>
                <tr>
                    <th>id</th>
                    <th>username</th>
                    <th>taskname</th>
                    <th>date</th>
                    <th>hour</th>
                    <th>description</th>
                    <th>is_overtime</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="w in task.workhours" :key="w.id">
                    <td>{{w.id}}</td>
                    <td>{{w.user.username}}</td>
                    <td>{{w.task.taskname}}</td>
                    <td>{{w.date}}</td>
                    <td>{{w.hour}}</td>
                    <td>{{w.description}}</td>
                    <td>{{w.is_overtime}}</td>
                </tr>
            </tbody>
        </table>
      </div>
      <div v-else>
        No workhours
      </div>
</div>
</template>

<script>
import { getTaskIdAPI } from "../service/apis.js";
export default {
  components:{
  },
  props: {
    msg: String
  },
  data() {
    return {
      task: null,
      form: {
        taskname: '',
        fullname: '',
        organization: '',
      }
    }
  },
  mounted: function () {
    this.get_task()
  },
  methods: {
    async get_task(){
      await getTaskIdAPI(this.$route.params.id).then(response => (this.task = response.data))
    }
  }
}
</script>