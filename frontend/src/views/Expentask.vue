<template>
  <div>
    <div v-if="expentasks">
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="4">Expentasks</th>
          </tr>
          <tr>
            <th>id</th>
            <th>Expentaskname</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="t in expentasks"
            :key="t.id"
            :to="{ expentaskname: 'ExpentaskDetail', params: { id: t.id } }"
            tag="tr"
          >
            <td>{{ t.id }}</td>
            <td>{{ t.expentask_name }}</td>
          </router-link>
        </tbody>
      </table>
    </div>
    <div v-else>No tasks</div>
    <div></div>
    <div>
      <form @submit.prevent="post_expentask">
        <b-container fluid>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Expentask Name:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default"
                placeholder="Enter expentask name"
                v-model="form.expentaskname"
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
import { getExpentaskAPI, postExpentaskAPI } from "../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  data() {
    return {
      expentasks: null,
      form: {
        Expentaskname: "",
      },
    };
  },
  mounted: function () {
    this.get_expentask();
  },
  methods: {
    async get_expentask() {
      await getExpentaskAPI().then(
        (response) => (this.expentasks = response.data)
      );
    },
    async post_expentask() {
      try {
        var body = {
          expentaskname: this.form.expentaskname,
        };
        await postExpentaskAPI(body).then((response) => {
          if (response.status == 200) {
            this.form.expentaskname = "";
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new task now!";
      }
      await getExpentaskAPI().then(
        (response) => (this.expentasks = response.data)
      );
    },
  },
};
</script>