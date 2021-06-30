<template>
  <div class="register">
    <!-- <div>
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
          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default-3">department:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                type="text"
                id="input-default-3"
                placeholder="Enter password"
                v-model="form.department_id.id"
                required
              ></b-form-input>
            </b-col>
          </b-row>
          <b-button pill variant="primary" type="submit">Register</b-button>
        </b-container>
      </form>
    </div> 
    <p v-if="showError" id="error">Username already exists</p>-->
    <section class="ftco-section">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-5 col-lg-5">
            <div class="wrap">
              <div class="img">
                <img src="../../images/5566.gif" height="230px" width="440px" />
              </div>
              <div class="login-wrap p-4 p-md-6">
                <div class="d-flex">
                  <div class="w-100">
                    <h3 class="mb-6">YC Consultant</h3>
                  </div>
                </div>
                <form class="signin-form" @submit.prevent="post_user">
                  <div class="form-group mt-4">
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

                  <div class="form-group mt-4">
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

                  <div class="form-group mt-4">
                    <select
                      id="department-field"
                      type="text"
                      class="form-control"
                      v-model="form.department_id"
                      required
                    >
                      <option value="0" disabled selected>
                        ---------------------請選擇部門---------------------
                      </option>
                      <option
                        v-for="department in departments"
                        :value="department"
                        :key="department.id"
                      >
                        {{ department.id }}.
                        {{ department.department_name }}
                      </option>
                    </select>
                    <label class="form-control-placeholder" for="department"
                      >Department</label
                    >
                    <span
                      toggle="#department-field"
                      class="fa fa-fw fa-eye field-icon toggle-department"
                    ></span>
                  </div>

                  <div class="form-group">
                    <button
                      type="submit"
                      class="form-control btn btn-primary rounded submit px-3"
                      @submit.prevent="submit"
                    >
                      Sign Up
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <p v-if="showError" id="error">Username already exists</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { postUserAPI, getDepartmentsAPI } from "../../service/apis.js";
import router from "../../router/index.js";
import { MessageBox } from "element-ui";
export default {
  name: "Register",
  components: {},
  data() {
    return {
      departments: [],
      form: {
        username: "",
        password: "",
        department_id: 0,
        is_superuser: false,
      },
      showError: false,
    };
  },
  mounted: function () {
    this.get_departments();
  },
  methods: {
    async post_user() {
      try {
        var data = {
          username: this.form.username,
          password: this.form.password,
          department_id: this.form.department_id.id,
          is_superuser: this.form.is_superuser,
        };
        await postUserAPI(data).then((response) => {
          if (response.status == 200) {
            this.form.username = "";
            this.form.password = "";
            this.form.department_id = 0;
            this.form.is_superuser = false;
            MessageBox("註冊成功!!");
            router.push("/login");
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new user now!";
      }
    },
    get_departments() {
      getDepartmentsAPI().then(
        (response) => (this.departments = response.data)
      );
    },
  },
};
</script>

<style scoped src="../../static/css/registerpage.css">
</style>
