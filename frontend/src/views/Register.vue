<template>
  <div class="register">
    <div>
      <form @submit.prevent="post_user">
        <b-container fluid>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Username:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default"
                placeholder="Enter User Name"
                v-model="form.username"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default-2">Full Name:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default-2"
                placeholder="Enter Full Name"
                v-model="form.fullname"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default-3">Password:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                type="password"
                id="input-default-3"
                placeholder="Enter password"
                v-model="form.password"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-button pill variant="primary" type="submit">Register</b-button>
        </b-container>
      </form>
    </div>
    <p v-if="showError" id="error">Username already exists</p>
  </div>
</template>

<script>
import { postUserAPI } from "../service/apis.js";
import router from "../router/index.js";
export default {
  name: "Register",
  components: {},
  data() {
    return {
      form: {
        username: "",
        full_name: "",
        password: "",
      },
      showError: false,
    };
  },
  methods: {
    async post_user() {
      try {
        var data = {
          username: this.form.username,
          fullname: this.form.fullname,
          password: this.form.password,
        };
        await postUserAPI(data).then(function (response) {
          if (response.status == 200) {
            router.push("/users");
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new user now!";
      }
    },
  },
};
</script>