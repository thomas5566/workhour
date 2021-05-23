<template>
  <div>
    <div v-if="tasks">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="4">Tasks</th>
          </tr>
          <tr>
            <th>id</th>
            <th>taskname</th>
            <th>fullname</th>
            <th>organization</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="t in tasks"
            :key="t.id"
            :to="{ name: 'TaskDetail', params: { id: t.id } }"
            tag="tr"
          >
            <td>{{ t.id }}</td>
            <td>{{ t.taskname }}</td>
            <td>{{ t.fullname }}</td>
            <td>{{ t.organization }}</td>
          </router-link>
        </tbody>
      </table>
    </div>
    <div v-else>No tasks</div>
    <div></div>
    <div>
      <form @submit.prevent="post_task">
        <b-container fluid>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Task Name:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default"
                placeholder="Enter task name"
                v-model="form.taskname"
                required
              ></b-form-input>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Full Name:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default"
                placeholder="Enter task full name"
                v-model="form.fullname"
                required
              ></b-form-input>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Organization Name:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default"
                placeholder="Enter task organization name"
                v-model="form.organization"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-button pill variant="primary" type="submit">Submit</b-button>
        </b-container>
      </form>
    </div>
  </div>
</template>

<script>
import { getTaskAPI, postTaskAPI } from "../service/apis.js";
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
  },
};
</script>