<template>
  <div>
    <div class="post_workhour" v-if="isLoggedIn">
      <form @submit.prevent="post_workhour">
        <b-container fluid>
          <b-row class="my-1" v-if="tasks">
            <b-col sm="2">
              <label for="input-default">計劃項目:</label>
            </b-col>
            <b-col sm="10">
              <b-form-select
                v-model="form.task_id"
                :select-size="20"
                class="form-control"
                required
              >
                <b-form-select-option
                  v-for="t in tasks"
                  :key="t.id"
                  :value="t.id"
                >
                  {{ t.id }}.{{ t.taskname }} {{ t.fullname }}
                </b-form-select-option>
              </b-form-select>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">日期:</label>
            </b-col>
            <b-col sm="10">
              <b-form-datepicker
                placeholder="dd-mm-yyyy"
                v-model="form.date"
                :min="minDate"
                :max="maxDate"
                required
                locale="zh"
                menu-class="w-100"
                calendar-width="100%"
                today-button
                close-button
              >
              </b-form-datepicker>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">時間:</label>
            </b-col>
            <b-col sm="1">
              <b-form-input
                type="number"
                min="0.5"
                max="8"
                step="0.5"
                id="input-default"
                placeholder="Enter hour(s) of work"
                v-model="form.hour"
                required
              ></b-form-input>
            </b-col>
            <b-col sm="9">
              <b-form-input
                id="type-range"
                type="range"
                min="0.5"
                max="8"
                step="0.5"
                class="w-100 p-3 bg-secondary text-light"
                v-model="form.hour"
                required
              ></b-form-input>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">工作說明:</label>
            </b-col>
            <b-col sm="10">
              <b-form-textarea
                placeholder="Enter description (Optional)"
                rows="4"
                v-model="form.description"
              ></b-form-textarea>
            </b-col>
          </b-row>

          <b-row class="my-1">
            <b-col sm="2">
              <label for="input-default">加班:</label>
            </b-col>
            <b-col sm="1">
              <b-form-checkbox
                id="checkbox-1"
                v-model="checked"
                name="checkbox-1"
                switch
              >
              </b-form-checkbox>
            </b-col>
            <div class="container" id="app-container" v-if="checked">
              <b-row class="my-1">
                <b-col sm="2">
                  <label for="input-default">加班時間:</label>
                </b-col>
                <b-col sm="1">
                  <b-form-input
                    type="number"
                    min="0.5"
                    max="8"
                    step="0.5"
                    id="input-default"
                    placeholder="Enter hour(s) of work"
                    v-model="form.overtime_hour"
                    required
                  ></b-form-input>
                </b-col>
                <b-col sm="9">
                  <b-form-input
                    id="type-range"
                    type="range"
                    min="0.5"
                    max="8"
                    step="0.5"
                    class="w-100 p-3 bg-secondary text-light"
                    v-model="form.overtime_hour"
                    required
                  ></b-form-input>
                </b-col>
              </b-row>
            </div>
          </b-row>
          <b-row>
            <b-col sm="9">
              <b-button
                pill
                variant="primary"
                type="submit"
                @click="showAlert"
                class="m-1"
                >新增</b-button
              >
            </b-col>
          </b-row>
          <b-alert
            :show="dismissCountDown"
            variant="success"
            @dismissed="dismissCountDown = 0"
            @dismiss-count-down="countDownChanged"
          >
            新增計畫項目 成功!!
          </b-alert>
        </b-container>
      </form>
      <!-- <div class="workhours" v-if="workhours">
        <table class="table table-striped table-bordered">
          <thead>
            <tr>
              <th colspan="7">Workhours</th>
            </tr>
            <tr>
              <th>id</th>
              <th>username</th>
              <th>taskname</th>
              <th>date</th>
              <th>hour</th>
              <th>description</th>
              <th>is_overtime</th>
            </tr>
          </thead>
          <tbody>
            <router-link
              v-for="w in workhours"
              :key="w.id"
              :to="{ name: 'WorkhourDetail', params: { id: w.id } }"
              tag="tr"
            >
              <td>{{ w.id }}</td>
              <td>{{ w.user.username }}</td>
              <td>{{ w.task.taskname }}</td>
              <td>{{ w.date }}</td>
              <td>{{ w.hour }}</td>
              <td>{{ w.description }}</td>
              <td>{{ w.is_overtime }}</td>
            </router-link>
          </tbody>
        </table>
      </div>
      <div v-else>No workhours</div> -->
    </div>
  </div>
</template>

<script>
import {
  getTaskAPI,
  getWorkhourAPI,
  postWorkhourAPI,
} from "../service/apis.js";

export default {
  components: {},
  props: {
    msg: String,
  },
  computed: {
    isLoggedIn() {
      return this.$store.getters.isAuthenticated;
    },
  },
  data() {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    // 15th two months prior
    const minDate = new Date(today);
    minDate.setMonth(minDate.getMonth() - 2);
    // 15th in two months
    const maxDate = new Date(today);
    maxDate.setMonth(maxDate.getMonth() + 2);
    return {
      checked: false,

      dismissSecs: 2,
      dismissCountDown: 0,
      showDismissibleAlert: false,

      tasks: null,
      workhours: null,
      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,

      form: {
        task_id: "",
        date: today.toISOString().substring(0, 10),
        hour: 1,
        description: "",
        is_overtime: false,
        overtime_hour: 0,
      },
    };
  },
  mounted: function () {
    this.get_workhour();
    this.get_task();
  },
  methods: {
    async get_task() {
      await getTaskAPI().then((response) => (this.tasks = response.data));
    },
    async get_workhour() {
      await getWorkhourAPI().then(
        (response) => (this.workhours = response.data)
      );
    },
    async post_workhour() {
      try {
        var data = {
          task_id: this.form.task_id,
          date: this.form.date,
          hour: this.form.hour,
          description: this.form.description,
          is_overtime: this.form.is_overtime,
          overtime_hour: this.form.overtime_hour,
        };
        await postWorkhourAPI(data).then((response) => {
          if (response.status == 200) {
            this.form.task_id = "";
            (this.form.date = this.toDate), 
            (this.form.hour = 1);
            this.form.description = "";
            (this.form.is_overtime = false);
            (this.form.overtime_hour = 0);
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new 5566 now!";
      }
      await getWorkhourAPI().then(
        (response) => (this.workhours = response.data)
      );
    },
    countDownChanged(dismissCountDown) {
      this.dismissCountDown = dismissCountDown;
    },
    showAlert() {
      this.dismissCountDown = this.dismissSecs;
    },
  },
};
</script>
