<template>
<div>
  <div class="post_workhour" v-if="isLoggedIn">
    <form @submit.prevent="post_workhour">
        <b-container fluid>
          <b-row class="my-1" v-if="tasks">
            <b-col sm="2">
              <label for="input-default">Task:</label>
            </b-col>
            <b-col sm="10">
              <b-form-select v-model="form.task_id" :select-size="6" class="form-control" required>
                <b-form-select-option v-for="t in tasks" :key="t.id" :value="t.id"> {{t.id}}.{{t.taskname}}  {{t.fullname}} </b-form-select-option>
            </b-form-select>  
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Date:</label>
            </b-col>
            <b-col sm="10">
              <b-form-datepicker
                  placeholder="dd-mm-yyyy"
                  v-model="form.date" 
                  :min="minDate" 
                  :max="maxDate" 
                  required
                  locale="zh" 
                  menu-class="w-100" 
                  calendar-width="100%"
                  today-button
                  close-button>
                  </b-form-datepicker>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Hour:</label>
            </b-col>
            <b-col sm="1">
              <b-form-input type='number' min=0.5 max=8 step=0.5 id="input-default" placeholder="Enter hour(s) of work" v-model="form.hour" required></b-form-input>
            </b-col>
             <b-col sm="9">
              <b-form-input id="type-range" type="range" min=0.5 max=8 step=0.5 class="w-100 p-3 bg-secondary text-light" v-model="form.hour" required></b-form-input>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Description:</label>
            </b-col>
            <b-col sm="10">
              <b-form-textarea placeholder="Enter description (Optional)" rows="4" v-model="form.description"></b-form-textarea>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">is_overtime:</label>
            </b-col>
            <b-col sm="1">
              <b-form-checkbox id="checkbox-1" v-model="form.is_overtime" name="checkbox-1" switch> </b-form-checkbox>
            </b-col>
          
          <b-col sm="9">
            <b-button pill variant="primary" type="submit">Add Workhour</b-button>
          </b-col>
          </b-row>
          <p></p>
          
          <p></p>
    </b-container>
    </form>
  </div>
  <div class="workhours" v-if="workhours">
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
                <router-link v-for="w in workhours" :key="w.id" :to="{name:'WorkhourDetail', params: { id: w.id}}" tag="tr">
                    <td>{{w.id}}</td>
                    <td>{{w.user.username}}</td>
                    <td>{{w.task.taskname}}</td>
                    <td>{{w.date}}</td>
                    <td>{{w.hour}}</td>
                    <td>{{w.description}}</td>
                    <td>{{w.is_overtime}}</td>
                </router-link>
            </tbody>
        </table>
      </div>
      <div v-else>
        No workhours
      </div>
</div>
</template>

<script>
import { getTaskAPI, getWorkhourAPI, postWorkhourAPI } from "../service/apis.js";
export default {
  components: {
  },
  props: {
    msg: String
  },
  computed: {
    isLoggedIn : function(){ return this.$store.getters.isAuthenticated},
  },
  data() {
    const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      // 15th two months prior
      const minDate = new Date(today)
      minDate.setMonth(minDate.getMonth() - 2)
      // 15th in two months
      const maxDate = new Date(today)
      maxDate.setMonth(maxDate.getMonth() + 2)
    return {
      tasks: null,
      workhours: null,
      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,
      form: {
        task_id: '',
        date: today.toISOString().substring(0, 10),
        hour: 1,
        description: '',
        is_overtime: false
      },
    }
  },
  mounted: function () {
    this.get_workhour()
    this.get_task()
  },
   methods: {
    async get_task(){
      await getTaskAPI().then(response => (this.tasks = response.data))
    },
    async get_workhour(){
      await getWorkhourAPI().then(response => (this.workhours = response.data))
    },
    async post_workhour() {
      try {
        var data = {
          "task_id": this.form.task_id,
          "date": this.form.date,
          "hour": this.form.hour,
          "description": this.form.description,
          "is_overtime": this.form.is_overtime,
        }
        await postWorkhourAPI(data).then(response =>{
            if(response.status == 200){
              this.form.task_id = ""
              this.form.date = this.toDate,
              this.form.hour = 1
              this.form.description = ""
              this.form.is_overtime = false
            }
        })
        }
        catch (error) {
        throw "Sorry you can't create a new task now!"
      }
      await getWorkhourAPI().then(response => (this.workhours = response.data))
      }
  }
}
</script>
