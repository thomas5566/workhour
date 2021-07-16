<template>
  <section class="post_dayoff" v-if="isLoggedIn">
    <form @submit.prevent="post_dayoff">
      <!-- <div class="form-control">
        <label for="department">ID</label>
        <label id="department" name="department">{{ user_id }}</label>
      </div> -->
      <div class="form-control">
        <label for="department">部門：</label>
        <label id="department" name="department">{{ department }}</label>
      </div>
      <div class="form-control">
        <label for="user-name">姓名：</label>
        <label id="user-name" name="user-name">{{ username }}</label>
      </div>
      <div class="form-control">
        <label for="dayoff-datepicker">休假日期:</label>
        <b-form-datepicker
          id="dayoff-datepicker"
          v-model="daysoff_date"
          size="sm"
          locale="zh"
          class="mb-2"
        ></b-form-datepicker>
      </div>
      <div class="form-control">
        <label for="hour">休假時數:</label>
        <input id="hour" name="hour" type="number" v-model="daysoff_hour" />
      </div>
      <div class="form-control">
        <label>休假類別:</label>
        <b-form-group v-slot="{ ariaDescribedby }">
          <b-form-radio-group
            v-model="selected"
            :options="options"
            :aria-describedby="ariaDescribedby"
            name="radios-stacked"
            stacked
          ></b-form-radio-group>
        </b-form-group>
      </div>
      <div>
        <button @click="$emit('close')">新增</button>
        <button @click.prevent="$emit('close')">取消</button>
      </div>
    </form>
  </section>
</template>
<script>
import { postDaysoffAPI } from "../../service/apis.js";
export default {
  emits: ["close"],
  data() {
    return {
      userNameValidity: "pending",

      user_id: this.$store.getters.getUserId,
      username: this.$store.getters.getUsername,
      department: this.$store.getters.getDepartment.department_name,
      daysoff_date: null,
      daysoff_hour: null,
      daysoff_name: null,

      selected: null,
      options: [
        { text: "請假", value: "請假" },
        { text: "補修", value: "補修" },
      ],
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
  },
  methods: {
    validateInput() {
      if (this.editDayoffData.daysoff_hour === "0") {
        this.userNameValidity = "invalid";
      } else {
        this.userNameValidity = "valid";
      }
    },
    post_dayoff() {
      try {
        var data = {
          user_id: this.user_id,
          daysoff_date: this.daysoff_date,
          daysoff_name: this.selected,
          daysoff_hour: this.daysoff_hour,
        };
        postDaysoffAPI(data).then((response) => {
          if (response.status == 200) {
            // reflash data list when chiled component update data
            this.$root.$emit("get_daysoff");
            this.daysoff_date = "";
            this.daysoff_name = "";
            this.daysoff_hour = "";
          }
        });
      } catch (error) {
        throw "Sorry you can't create a new Dayoff now!";
      }
      // await getWorkhourAPI().then(
      //   (response) => (this.workhours = response.data)
      // );
    },
  },
};
</script>
<style scoped>
form {
  margin: 7rem auto;
  max-width: 25rem;
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

input[type="checkbox"] + label,
input[type="radio"] + label {
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