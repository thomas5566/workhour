<template>
  <section class="post_workhour" v-if="isLoggedIn">
    <form @submit.prevent="post_workhour">
      <b-container fluid>
        <b-row class="my-1" v-if="tasks">
          <b-col sm="3">
            <h5 for="input-default">部門/門店 名稱:</h5>
          </b-col>
          <b-col sm="4">
            <b-form-select v-model="form.task_id" :select-size="10" @change="onChangeShop" class="form-control" required>
              <b-form-select-option v-for="task in tasks" :key="task.id" :value="task.id">
                {{ task.taskname }}
              </b-form-select-option>
            </b-form-select>
          </b-col>
          <b-col sm="4">
            <b-form-select v-model="form.selected_cstshop_id" :select-size="10" class="form-control" required>
              <b-form-select-option v-for="shop in selected_cstshops" :key="shop.id" :value="shop.id">
                {{ shop.shop_number }} - {{ shop.shop_name }}
              </b-form-select-option>
            </b-form-select>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">叫修日期/時間:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-datepicker placeholder="dd-mm-yyyy" v-model="form.start_date" :min="minDate" :max="maxDate" required
              locale="zh-CN" menu-class="w-100" calendar-width="100%" today-button close-button>
            </b-form-datepicker>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">結束日期/時間:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-datepicker placeholder="dd-mm-yyyy" v-model="form.end_date" :min="minDate" :max="maxDate" required
              locale="zh-CN" menu-class="w-100" calendar-width="100%" today-button close-button>
            </b-form-datepicker>
          </b-col>
        </b-row>

        <!-- <b-row class="my-1" >
          <b-col sm="3">
            <h5 for="input-default">時間(hr):</h5>
          </b-col>
          <b-col sm="3">
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
          <b-col sm="7">
            <b-form-input
              id="type-range"
              type="range"
              min="0.5"
              max="8"
              step="0.5"
              class="w-100 p-3 text-light"
              v-model="form.hour"
              required
            ></b-form-input>
          </b-col>
        </b-row> -->

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">叫修內容:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-textarea placeholder="請輸入叫修內容..." rows="2" v-model="form.description"></b-form-textarea>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">故障原因:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-textarea placeholder="請輸入故障原因..." rows="2" v-model="form.cause_issue"></b-form-textarea>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">處理方式:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-textarea placeholder="請輸入處理方式..." rows="2" v-model="form.processing_method"></b-form-textarea>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">結案(是/否):</h5>
          </b-col>
          <b-col sm="1">
            <b-form-checkbox id="checkbox-1" v-model="form.case_close" name="checkbox-1" switch>
            </b-form-checkbox>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="3">
            <h5 for="input-default">備註:</h5>
          </b-col>
          <b-col sm="9">
            <b-form-textarea placeholder="請輸入備註式..." rows="2" v-model="form.todo"></b-form-textarea>
          </b-col>
        </b-row>

        <!-- <b-row class="my-1">
          <b-col sm="2">
            <h5 for="input-default">加班(是/否):</h5>
          </b-col>
          <b-col sm="1">
            <b-form-checkbox
              id="checkbox-1"
              v-model="form.is_overtime"
              name="checkbox-1"
              switch
            >
            </b-form-checkbox>
          </b-col>
          <div class="container" id="app-container" v-if="form.is_overtime">
            <b-row class="my-1">
              <b-col sm="2">
                <h5 for="input-default">加班時間(hr):</h5>
              </b-col>
              <b-col sm="2">
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
              <b-col sm="8">
                <b-form-input
                  id="type-range"
                  type="range"
                  min="0.5"
                  max="8"
                  step="0.5"
                  class="w-100 p-3 text-light"
                  v-model="form.overtime_hour"
                  required
                ></b-form-input>
              </b-col>
            </b-row>
          </div>
        </b-row> -->
        <b-row>
          <b-col sm="3">
            <b-button pill variant="primary" type="submit" @click="showAlert"
              style="margin: 0 auto; display: block">新增</b-button>
          </b-col>
          <b-col sm="3">
            <b-button @click.prevent="$emit('close')">取消</b-button>
          </b-col>
        </b-row>
        <b-alert :show="dismissCountDown" variant="success" @dismissed="dismissCountDown = 0"
          @dismiss-count-down="countDownChanged">
          新增計畫項目 成功!!
        </b-alert>
      </b-container>
    </form>
  </section>
</template>

<script>
import {
  getTaskAPI,
  getWorkhourAPI,
  postWorkhourAPI,
} from "../../service/apis.js";



export default {
  emits: ["close"],
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
    const today = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() + 1
    );
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
      cstshops: [],
      selected_cstshops: [],
      workhours: null,
      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,

      form: {
        task_id: "",
        selected_cstshop_id: "",
        start_date: today.toISOString().substring(0, 10),
        hour: 1,
        description: "",
        case_close: false,
        overtime_hour: 0,
        end_date: today.toISOString().substring(0, 10),
        todo: "",
        cause_issue: "",
        processing_method: "",
      },
    };
  },
  mounted: function () {
    this.get_workhour();
    this.get_task();
  },
  methods: {
    onChangeShop(main_department_id) {
      this.selected_cstshops = [];
      this.cstshops.forEach((items) => {
        if (items.main_department_id === main_department_id) {
          this.selected_cstshops.push(items);
        }
      });
    },
    async get_task() {
      await getTaskAPI().then((response) => {
        this.tasks = response.data;
      });

      if (this.tasks.length > 0) {
        this.tasks.forEach((items) => {
          if (items.cstshops.length > 0) {
            items.cstshops.forEach((shop) => {
              this.cstshops.push(shop);
            });
          }
        });
      }
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
          start_date: this.form.start_date,
          hour: this.form.hour,
          description: this.form.description,
          case_close: this.form.case_close,
          overtime_hour: this.form.overtime_hour,
          end_date: this.form.end_date,
          todo: this.form.todo,
          cause_issue: this.form.cause_issue,
          processing_method: this.form.processing_method,
          shop_id: this.form.selected_cstshop_id
        };
        await postWorkhourAPI(data).then((response) => {
          if (response.status == 200) {
            // reflash data list when chiled component update data
            this.$root.$emit("get_workhour");
            this.form.task_id = "";
            this.form.start_date = this.toDate;
            this.form.hour = 1;
            this.form.description = "";
            this.form.case_close = false;
            this.form.overtime_hour = 0;
            this.form.end_date = this.toDate;
            this.form.todo = "";
            this.form.cause_issue = "";
            this.form.processing_method = "";
            this.form.selected_cstshop_id = "";
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new Work-List now!";
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

<style scoped>
section {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
  padding: 1rem;
  margin: 2rem auto;
  max-width: 80rem;
  height: auto;
}

form {
  margin: auto;
  max-width: 60rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
  padding: 2rem;
  background-color: #ffffff;
}

.form-control {
  margin: 0.5rem 0;
}

.form-control.invalid input {
  border-color: red;
}

.form-control.invalid label {
  color: red;
}

label {
  font-weight: bold;
}

h2 {
  font-size: 1rem;
  margin: 0.5rem 0;
}

input,
select {
  display: block;
  width: 100%;
  font: inherit;
  margin-top: 0.5rem;
}

select {
  width: auto;
}

input[type="checkbox"],
input[type="radio"] {
  display: inline-block;
  width: auto;
  margin-right: 1rem;
}

input[type="checkbox"]+label,
input[type="radio"]+label {
  font-weight: normal;
}

button {
  font: inherit;
  border: 1px solid #0076bb;
  background-color: #0076bb;
  color: white;
  cursor: pointer;
  padding: 0.75rem 2rem;
  border-radius: 30px;
}

button:hover,
button:active {
  border-color: #002350;
  background-color: #002350;
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.75);
}
</style>
