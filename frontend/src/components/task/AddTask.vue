<template>
  <div>
    <base-card v-if="tasks">
      <table class="table table-striped table-bordered">
        <thead style="text-align: center">
          <tr>
            <th colspan="10">
              <h4>計劃項目</h4>
            </th>
          </tr>
          <tr>
            <th>id</th>
            <th>簡稱</th>
            <th>計畫全名</th>
            <th>單位</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="task in tasks"
            :key="task.id"
            :to="{ taskname: 'TaskDetail', params: { id: task.id } }"
            tag="tr"
          >
            <td>{{ task.id }}</td>
            <td>{{ task.taskname }}</td>
            <td>{{ task.fullname }}</td>
            <td>{{ task.organization }}</td>
            <td>
              <button class="btn btn-sm btn-outline-danger" v-on:click="deleteTask(task.id)">刪除</button>
            </td>
          </router-link>
        </tbody>

        <!-- <tbody v-for="task in tasks" :key="task.id">
          <tr></tr>
        </tbody>-->
      </table>
    </base-card>
    <base-card v-else>No tasks</base-card>
    <form @submit.prevent="post_task">
      <b-container fluid="xl">
        <b-row class="my-1" align-h="center">
          <b-col sm="2">
            <label for="input-default">簡稱:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input id="input-default" placeholder="請輸入計畫簡稱" v-model="form.taskname" required></b-form-input>
          </b-col>
        </b-row>

        <b-row class="my-1" align-h="center">
          <b-col sm="2">
            <label for="input-default">計畫全名:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input id="input-default" placeholder="請輸入計畫全名" v-model="form.fullname" required></b-form-input>
          </b-col>
        </b-row>

        <b-row class="my-1" align-h="center">
          <b-col sm="2">
            <label for="input-default">單位:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input
              id="input-default"
              placeholder="請輸入單位名稱"
              v-model="form.organization"
              required
            ></b-form-input>
          </b-col>
        </b-row>
        <b-button pill variant="primary" type="submit" style="margin: 0 auto; display: block">新增</b-button>
      </b-container>
    </form>
  </div>
</template>

<script>
import { getTaskAPI, postTaskAPI, deleteTaskAPI } from "../../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  data() {
    return {
      tasks: null,
      form: {
        taskname: "",
        fullname: "",
        organization: "",
      },
    };
  },
  mounted: function () {
    this.get_task();
  },
  methods: {
    async get_task() {
      await getTaskAPI().then((response) => (this.tasks = response.data));
    },
    async post_task() {
      try {
        var body = {
          taskname: this.form.taskname,
          fullname: this.form.fullname,
          organization: this.form.organization,
        };
        await postTaskAPI(body).then((response) => {
          if (response.status == 200) {
            this.form.taskname = "";
            this.form.fullname = "";
            this.form.organization = "";
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new task now!";
      }
      await getTaskAPI().then((response) => (this.tasks = response.data));
    },
    deleteTask(id) {
      if (confirm("Are you sure you want to delete this Task?")) {
        deleteTaskAPI(id).then(() => {
          this.get_task();
        });
      }
    },
  },
};
</script>