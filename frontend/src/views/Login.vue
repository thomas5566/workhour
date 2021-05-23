<template>
  <div class="login">
    <div>
      <form @submit.prevent="submit">
        <b-container fluid>
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">Username:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input id="input-default" placeholder="Enter User Name" v-model="form.username" required></b-form-input>
            </b-col>
          </b-row>
          <b-row class="my-2">
            <b-col sm="2">
              <label for="input-default-2">Password:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input id="input-default-2" type="password" placeholder="Enter password" v-model="form.password" required></b-form-input>
            </b-col>
          </b-row>
          <b-button pill variant="primary" type="submit">Submit</b-button>
        </b-container>
        </form>
      <p v-if="showError" id="error">Username or Password is incorrect</p>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  name: "Login",
  components: {},
  data() {
    return {
      form: {
        username: "",
        password: "",
      },
      showError: false
    };
  },
  methods: {
    ...mapActions(["LogIn"]),
    async submit() {
      const User = new FormData();
      User.append("username", this.form.username);
      User.append("password", this.form.password);
      try {
          await this.LogIn(User);
          this.$router.push("/");
          this.showError = false
      } catch (error) {
        this.showError = true
      }
    },
  },
};
</script>