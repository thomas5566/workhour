<template>
  <main class="login-page" :style="cssProps">
      <section class="login-section">
        <div class="container">
          <div class="row justify-content-center">
            <div class="col-md-6 text-center mb-5">
              <h1 class="heading-section">資訊服務紀錄系統</h1>
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
              <div class="login-wrap p-0">
                <!-- <h3 class="mb-4 text-center">Have an account?</h3> -->
                <form class="signin-form" @submit.prevent="submit">
                  <div class="form-group login-field">
                    <label class="login-field__icon" for="username" aria-hidden="true">
                      <i class="fas fa-user"></i>
                    </label>
                    <!-- Native controls avoid Bootstrap 4 input-group sizing conflicts. -->
                    <input
                      id="username"
                      :value="form.username"
                      class="form-control"
                      name="username"
                      type="text"
                      autocomplete="username"
                      placeholder="使用者帳號"
                      required
                      @input="form.username = $event.target.value"
                    />
                    <!-- <input
                      type="text"
                      class="form-control"
                      placeholder="Username"
                      v-model="form.username"
                      required
                    /> -->
                  </div>
                  <div class="form-group login-field">
                    <label class="login-field__icon" for="password" aria-hidden="true">
                      <i class="fas fa-lock"></i>
                    </label>
                    <input
                      id="password"
                      :value="form.password"
                      class="form-control"
                      name="password"
                      type="password"
                      autocomplete="current-password"
                      placeholder="密碼"
                      required
                      @input="form.password = $event.target.value"
                    />
                    <!-- <input
                      id="password-field"
                      type="password"
                      class="form-control"
                      placeholder="Password"
                      v-model="form.password"
                      required
                    /> -->
                  </div>
                  <!-- <div class="form-group">
                    <row>
                      <button type="submit" class="form-control btn btn-primary submit px-3">
                        登入
                      </button>
                    </row>
                    <row>
                      <div class="form-control btn btn-primary submit px-3">
                        <a href="/register" style="color: #0a0a0a">註冊</a>
                      </div>
                    </row>
                  </div> 
                  <div class="form-group d-md-flex">
                    <div class="w-50">
                      <label class="checkbox-wrap checkbox-primary">Remember Me
                        <input type="checkbox" checked />
                        <span class="checkmark"></span>
                      </label>
                    </div>
                  </div> -->
                </form>
                <div class="login-actions">
                  <button type="button" class="btn login-button" @click="submit">登入</button>
                  <button type="button" class="btn login-button" @click="register">註冊</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
  </main>

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
</template>

<script>
import { mapActions } from "vuex";
import backgroundImage from "../../images/bg.jpg";
export default {
  name: "Login",
  components: {},
  data() {
    return {
      cssProps: {
        backgroundImage: `url(${backgroundImage})`,
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
        // sessionStorage.setItem("store", JSON.stringify(this.$store.state));
        window.sessionStorage.setItem("token", this.$store.getters.getToken);
      } catch {
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
    async register() {
      this.$router.push("/register");
    },
  },
};
</script>

<style scoped>
.login-page {
  align-items: center;
  background-position: center;
  background-size: cover;
  display: flex;
  min-height: 100vh;
  padding: 2rem 1rem;
  position: relative;
}

.login-page::before {
  background: rgba(3, 20, 36, 0.25);
  content: "";
  inset: 0;
  position: absolute;
}

.login-section {
  position: relative;
  width: 100%;
  z-index: 1;
}

.heading-section {
  color: #fff;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 600;
  margin-bottom: 2rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

.login-wrap {
  margin: 0 auto;
  max-width: 26rem;
}

.login-field {
  align-items: center;
  display: flex;
  margin-bottom: 1rem;
  position: relative;
}

.login-field__icon {
  color: #263746;
  left: 1rem;
  margin: 0;
  pointer-events: none;
  position: absolute;
  z-index: 2;
}

.login-field .form-control {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 0.5rem;
  color: #152331;
  height: 3rem;
  padding: 0.75rem 1rem 0.75rem 2.8rem;
  width: 100%;
}

.login-field .form-control:focus {
  border-color: #7cc4ff;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
  outline: 0;
}

.login-actions {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 1.25rem;
}

.login-button {
  background: #fff;
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: #152331;
  min-height: 2.75rem;
}

.login-button:hover,
.login-button:focus-visible {
  background: #152331;
  color: #fff;
}

@media (max-width: 575.98px) {
  .login-actions {
    grid-template-columns: 1fr;
  }
}
</style>
