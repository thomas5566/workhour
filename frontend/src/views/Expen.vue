<template>
  <div>
    <div class="post_expen" v-if="isLoggedIn">
      <form @submit.prevent="post_expen">
        <b-container fluid>
          <b-row class="my-1" v-if="expentasks">
            <b-col sm="2">
              <label for="input-default">ExpenTask:</label>
            </b-col>
            <b-col sm="10">
              <b-form-select
                v-model="form.expentask_id"
                :select-size="6"
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
              <label for="input-default">Date:</label>
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
              <label for="input-default">Description:</label>
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
              <label for="input-default">Spend:</label>
            </b-col>
            <b-col sm="10">
              <b-form-input
                rows="1"
                v-model="form.price"
              ></b-form-input>
            </b-col>
          </b-row>
          <b-row class="my-1">
            <b-col sm="9">
              <b-button pill variant="primary" type="submit"
                >Add Expen</b-button
              >
            </b-col>
          </b-row>
        </b-container>
      </form>
    </div>
  </div>
</template>

<script>
import {
  getExpentaskAPI,
  postExpenAPI,
} from "../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  computed: {
    isLoggedIn: function () {
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
      expentasks: null,
      toDate: today.toISOString().substring(0, 10),
      minDate: minDate,
      maxDate: maxDate,
      form: {
        expentask_id: "",
        date: today.toISOString().substring(0, 10),
        price: "",
        description: "",
      },
    };
  },
  mounted: function () {
    // this.get_workhour();
    this.get_expentask();
  },
  methods: {
    async get_expentask() {
      await getExpentaskAPI().then((response) => (this.expentasks = response.data));
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
            (this.form.date = this.toDate), 
            (this.form.price = "");
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
  },
};
</script>
