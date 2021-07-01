<template>
  <section class="post_expen" v-if="isLoggedIn">
    <form @submit.prevent="post_expen">
      <b-container fluid>
        <b-row class="my-1" v-if="expentasks">
          <b-col sm="2">
            <h5 for="input-default">支出項目:</h5>
          </b-col>
          <b-col sm="10">
            <b-form-select
              v-model="form.expentask_id"
              :select-size="20"
              class="form-control"
              required
            >
              <b-form-select-option
                v-for="t in expentasks"
                :key="t.id"
                :value="t.id"
              >
                {{ t.id }}.{{ t.expentask_name }}
              </b-form-select-option>
            </b-form-select>
          </b-col>
        </b-row>

        <b-row class="my-1">
          <b-col sm="2">
            <h5 for="input-default">日期:</h5>
          </b-col>
          <b-col sm="10">
            <b-form-datepicker
              placeholder="dd-mm-yyyy"
              v-model="form.date"
              :min="minDate"
              :max="maxDate"
              required
              locale="zh-CN"
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
            <h5 for="input-default">支出說明:</h5>
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
            <h5 for="input-default">支出費用($):</h5>
          </b-col>
          <b-col sm="10">
            <b-form-input
              rows="1"
              v-model="form.price"
              :state="pricState"
            ></b-form-input>

            <!-- This will only be shown if the preceding input has an invalid state -->
            <b-form-invalid-feedback id="input-live-feedback">
              請輸入金額
            </b-form-invalid-feedback>

            <!-- This is a form text block (formerly known as help block) -->
            <b-form-text id="input-live-help">金額至少大於0$</b-form-text>
          </b-col>
        </b-row>
        <b-row class="my-1">
          <b-col sm="9">
            <b-button
              pill
              variant="primary"
              type="submit"
              @click="showAlert"
              style="margin: 0 auto; display: block"
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
          新增花費項目 成功!!
        </b-alert>
      </b-container>
    </form>
  </section>
</template>

<script>
import { getExpentaskAPI, postExpenAPI } from "../../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  computed: {
    isLoggedIn: function() {
      return this.$store.getters.isAuthenticated;
    },
    pricState() {
      return this.form.price != 0 ? true : false;
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
      dismissSecs: 2,
      dismissCountDown: 0,
      showDismissibleAlert: false,
      expentasks: null,

      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,

      form: {
        expentask_id: "",
        date: today.toISOString().substring(0, 10),
        price: 0,
        description: "",
      },
    };
  },
  mounted: function() {
    // this.get_workhour();
    this.get_expentask();
  },
  methods: {
    async get_expentask() {
      await getExpentaskAPI().then(
        (response) => (this.expentasks = response.data)
      );
    },
    // async get_workhour() {
    //   await getWorkhourAPI().then(
    //     (response) => (this.workhours = response.data)
    //   );
    // },
    async post_expen() {
      try {
        var data = {
          expentask_id: this.form.expentask_id,
          date: this.form.date,
          price: this.form.price,
          description: this.form.description,
        };
        await postExpenAPI(data).then((response) => {
          if (response.status == 200) {
            this.form.expentask_id = "";
            this.form.date = this.toDate;
            this.form.price = "";
            this.form.description = "";
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new task now!";
      }
      // await getWorkhourAPI().then(
      //   (response) => (this.workhours = response.data)
      // );
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
}
</style>
