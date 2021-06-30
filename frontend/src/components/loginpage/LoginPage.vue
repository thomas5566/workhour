<template>
  <div class="login">
    <body class="img js-fullheight" :style="cssProps">
      <section class="ftco-section">
        <div class="container">
          <div class="row justify-content-center">
            <div class="col-md-6 text-center mb-5">
              <h1 class="heading-section">YC Consultant</h1>
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
              <div class="login-wrap p-0">
                <!-- <h3 class="mb-4 text-center">Have an account?</h3> -->
                <form @submit.prevent="submit" class="signin-form">
                  <div class="form-group">
                    <b-input-group class="mb-2">
                      <b-input-group-prepend is-text>
                        <b-icon icon="person-fill"></b-icon>
                      </b-input-group-prepend>
                      <b-form-input
                        type="text"
                        placeholder="Username"
                        v-model="form.username"
                        required
                      ></b-form-input>
                    </b-input-group>
                    <!-- <input
                      type="text"
                      class="form-control"
                      placeholder="Username"
                      v-model="form.username"
                      required
                    /> -->
                  </div>
                  <div class="form-group">
                    <b-input-group class="mb-2">
                      <b-input-group-prepend is-text>
                        <b-icon icon="lock-fill"></b-icon>
                      </b-input-group-prepend>
                      <b-form-input
                        type="password"
                        placeholder="Password"
                        v-model="form.password"
                        required
                      ></b-form-input>
                    </b-input-group>
                    <!-- <input
                      id="password-field"
                      type="password"
                      class="form-control"
                      placeholder="Password"
                      v-model="form.password"
                      required
                    /> -->
                    <span
                      toggle="#password-field"
                      class="fa fa-fw fa-eye field-icon toggle-password"
                    ></span>
                  </div>
                  <div class="form-group">
                    <button
                      type="submit"
                      class="form-control btn btn-primary submit px-3"
                    >
                      Sign In
                    </button>
                  </div>
                  <div class="form-group d-md-flex">
                    <div class="w-50">
                      <label class="checkbox-wrap checkbox-primary"
                        >Remember Me
                        <input type="checkbox" checked />
                        <span class="checkmark"></span>
                      </label>
                    </div>
                    <div class="w-50 text-md-right">
                      <a href="/register" style="color: #fff">Sign Up</a>
                    </div>
                  </div>
                </form>
                <p class="w-100 text-center">&mdash; Or Visit &mdash;</p>
                <div class="social d-flex text-center">
                  <a @click="linktofb" class="px-2 py-2 mr-md-1 rounded"
                    ><span class="ion-logo-facebook mr-2"></span> Facebook</a
                  >
                  <a @click="linktoyt" class="px-2 py-2 ml-md-1 rounded"
                    ><span class="ion-logo-twitter mr-2"></span> Youtube</a
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </body>

    <!-- <section class="ftco-section">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-5 col-lg-4">
            <div class="wrap">
              <div class="img">
                <img src="../images/5566.gif" height="230px" width="430px" />
              </div>
              <div class="login-wrap p-4 p-md-5">
                <div class="d-flex">
                  <div class="w-100">
                    <h3 class="mb-4">YC Consultant</h3>
                  </div>
                  <div class="w-100">
                    <p class="social-media d-flex justify-content-end">
                      <a
                        href="#"
                        class="
                          social-icon
                          d-flex
                          align-items-center
                          justify-content-center
                        "
                        ><span class="fa fa-facebook"></span
                      ></a>
                      <a
                        href="#"
                        class="
                          social-icon
                          d-flex
                          align-items-center
                          justify-content-center
                        "
                        ><span class="fa fa-twitter"></span
                      ></a>
                    </p>
                  </div>
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
                  <div class="form-group d-md-flex">
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
                  </div>
                </form>
                <p class="text-center">
                  Not a member?
                  <a data-toggle="tab" href="/register">Sign Up</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section> -->
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  name: "Login",
  components: {},
  data() {
    return {
      cssProps: {
        backgroundImage: `url(${require("../../images/2.jpg")})`,
      },
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
    linktofb() {
      window.open(
        "https://www.facebook.com/%E6%B0%B8%E6%99%BA%E9%A1%A7%E5%95%8F%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8-100589515034076"
      );
    },
    linktoyt() {
      window.open("https://www.youtube.com/channel/UC105KwWByx2gju0bploT5Cg");
    },
  },
};
</script>

<style scoped src="../../static/css/loginpage.css">
</style>