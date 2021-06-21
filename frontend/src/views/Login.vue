<template>
  <div class="login">
    <!-- <div>
      <form @submit.prevent="submit">
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
          <b-row class="my-2">
            <b-col sm="2">
              <label for="input-default-2">Password:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                id="input-default-2"
                type="password"
                placeholder="Enter password"
                v-model="form.password"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-button pill variant="primary" type="submit">Submit5566</b-button>
        </b-container>
      </form>
      <p v-if="showError" id="error">Username or Password is incorrect</p>
    </div> -->

    <section class="ftco-section">
      <div class="container">
        <!-- <div class="row justify-content-center">
          <div class="col-md-6 text-center mb-5">
            <h2 class="heading-section">Login</h2>
          </div>
        </div> -->
        <div class="row justify-content-center">
          <div class="col-md-7 col-lg-5">
            <div class="wrap">
              <div class="img">
                <img src="../images/YC.jpg">
              </div>
              <div class="login-wrap p-4 p-md-5">
                <div class="d-flex">
                  <div class="w-100">
                    <h3 class="mb-4">YC Consultant</h3>
                  </div>
                  <!-- <div class="w-100">
                    <p class="social-media d-flex justify-content-end">
                      <a
                        href="#"
                        class="social-icon d-flex align-items-center justify-content-center"
                        ><span class="fa fa-facebook"></span
                      ></a>
                      <a
                        href="#"
                        class="social-icon d-flex align-items-center justify-content-center"
                        ><span class="fa fa-twitter"></span
                      ></a>
                    </p>
                  </div> -->
                </div>
                <form class="signin-form" @submit.prevent="submit">
                  <div class="form-group mt-3">
                    <input
                      type="text"
                      class="form-control"
                      required
                      v-model="form.username"
                    />
                    <label class="form-control-placeholder" for="username"
                      >Username</label
                    >
                  </div>
                  <div class="form-group">
                    <input
                      id="password-field"
                      type="password"
                      class="form-control"
                      v-model="form.password"
                      required
                    />
                    <label class="form-control-placeholder" for="password"
                      >Password</label
                    >
                    <span
                      toggle="#password-field"
                      class="fa fa-fw fa-eye field-icon toggle-password"
                    ></span>
                  </div>
                  <div class="form-group">
                    <button
                      type="submit"
                      class="form-control btn btn-primary rounded submit px-3"
                      @submit.prevent="submit"
                    >
                      Sign In
                    </button>
                  </div>
                  <!-- <div class="form-group d-md-flex">
                    <div class="w-50 text-left">
                      <label class="checkbox-wrap checkbox-primary mb-0"
                        >Remember Me
                        <input type="checkbox" checked />
                        <span class="checkmark"></span>
                      </label>
                    </div>
                    <div class="w-50 text-md-right">
                      <a href="#">Forgot Password</a>
                    </div>
                  </div> -->
                </form>
                <p class="text-center">
                  Not a member? <a data-toggle="tab" href="/register">Sign Up</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
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
      showError: false,
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
        this.$router.push("/home");
        this.showError = false;
      } catch (error) {
        this.showError = true;
      }
    },
    login() {
      this.$store.commit({
        type: "setUserData",
        userData: this.user,
      });
      this.$router.push("/home");
    },
  },
};
</script>

