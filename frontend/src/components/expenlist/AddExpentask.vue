<template>
  <div>
    <base-card v-if="expentasks">
      <table class="table table-striped table-bordered">
        <thead style="text-align: center">
          <tr>
            <th colspan="4"><h4>支出項目</h4></th>
          </tr>
          <tr>
            <th>id</th>
            <th>支出項目</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="t in expentasks"
            :key="t.id"
            :to="{ expentask_name: 'ExpentaskDetail', params: { id: t.id } }"
            tag="tr"
          >
            <td>{{ t.id }}</td>
            <td>{{ t.expentask_name }}</td>
          </router-link>
        </tbody>
      </table>
    </base-card>
    <base-card v-else>No tasks</base-card>

    <form @submit.prevent="post_expentask">
      <b-container fluid>
        <b-row class="my-1" align-h="center">
          <b-col sm="2">
            <label for="input-default">支出項目:</label>
          </b-col>
          <b-col sm="4">
            <b-form-input
              id="input-default"
              placeholder="請輸入支出項目名稱"
              v-model="form.expentask_name"
              required
            ></b-form-input>
          </b-col>
          <b-col sm="1">
            <b-button pill variant="primary" type="submit">新增</b-button>
          </b-col>
        </b-row>
      </b-container>
    </form>
  </div>
</template>

<script>
import { getExpentaskAPI, postExpentaskAPI } from "../../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  data() {
    return {
      expentasks: null,
      form: {
        expentask_name: "",
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
          expentask_name: this.form.expentask_name,
        };
        await postExpentaskAPI(body).then((response) => {
          if (response.status == 200) {
            this.form.expentask_name = "";
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