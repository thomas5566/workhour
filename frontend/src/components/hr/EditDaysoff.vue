<template>
  <form @submit.prevent="onEditDayoffSubmit">
    <!-- <div class="form-control">
      <label for="user-id">User Id：</label>
      <label id="user-id" name="user-id">{{
        editDayoffData.dayoffUserId
      }}</label>
    </div> -->
    <div class="form-control">
      <label for="department">部門：</label>
      <label id="department" name="department">{{
        editDayoffData.departMent
      }}</label>
    </div>
    <div class="form-control">
      <label for="user-name">姓名：</label>
      <label id="user-name" name="user-name">{{
        editDayoffData.dayoffUser
      }}</label>
    </div>
    <!-- <div
      class="form-control"
      :class="{ invalid: userNameValidity === 'invalid' }"
    >
      <label for="user-name">姓名</label>
      <input
        id="user-name"
        name="user-name"
        type="text"
        v-model.trim="dayoffUser"
        @blur="validateInput"
      />
      <p v-if="userNameValidity === 'invalid'">Please enter a valid name</p>
    </div> -->
    <div class="form-control">
      <label for="date">休假日期</label>
      <input
        id="date"
        name="date"
        type="date"
        v-model="editDayoffData.daysoff_date"
        ref="dayoffdateInput"
      />
    </div>
    <!-- <div
      class="form-control"
      :class="{ invalid: userNameValidity === 'invalid' }"
    >
      <label for="user-name">姓名</label>
      <input
        id="user-name"
        name="user-name"
        type="text"
        v-model.trim="dayoffUser"
        @blur="validateInput"
      />
      <p v-if="userNameValidity === 'invalid'">Please enter a valid name</p>
    </div> -->
    <div
      class="form-control"
      :class="{ invalid: userNameValidity === 'invalid' }"
    >
      <label for="hour">休假時數</label>
      <input
        id="hour"
        name="hour"
        type="number"
        v-model="editDayoffData.daysoff_hour"
        @blur="validateInput"
      />
      <p v-if="userNameValidity === 'invalid'">Please enter a valid name</p>
    </div>

    <div class="form-control">
      <label for="type">休假說明</label>
      <input
        id="type"
        name="type"
        type="text"
        v-model="editDayoffData.daysoff_name"
        ref="dayofftypeInput"
      />
    </div>
    <!-- <div class="form-control">
        <label for="referrer">How did you hear about us?</label>
        <select id="referrer" name="referrer" v-model="referrer">
          <option value="google">Google</option>
          <option value="wom">Word of mouth</option>
          <option value="newspaper">Newspaper</option>
        </select>
      </div>
    <div class="form-control">
      <h2>休假型態</h2>
      <div>
        <input
          id="type-dayoff"
          name="type"
          type="checkbox"
          value="請假"
          v-model="editDayoffData.daysoff_name"
        />
        <label for="type-dayoff">請假</label>
      </div>
      <div>
        <input
          id="type-leave"
          name="type"
          type="checkbox"
          value="補修"
          v-model="editDayoffData.daysoff_name"
        />
        <label for="type-leave">補修</label>
      </div>
      <div>
        <input
          id="interest-nothing"
          name="interest"
          type="checkbox"
          value="nothing"
          v-model="interest"
        />
        <label for="interest-nothing">Nothing</label>
      </div> 
    </div> -->
    <div>
      <button @click="$emit('onClose')">更新</button>
      <button @click.prevent="$emit('onClose')">取消</button>
    </div>
  </form>
</template>
<script>
import { updateDaysoffAPI } from "../../service/apis.js";
export default {
  computed: {},
  components: {},
  props: {
    id: {
      type: Number,
      required: true,
    },
    departmentName: {
      type: String,
      required: true,
    },
    userId: {
      type: Number,
      required: true,
    },
    userName: {
      type: String,
      required: true,
    },
    daysoffName: {
      type: String,
      required: true,
    },
    daysoffDate: {
      type: String,
      required: true,
    },
    daysoffHour: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      editDayoffData: {
        dayoffId: this.id,
        departMent: this.departmentName,
        dayoffUserId: this.userId,
        dayoffUser: this.userName,
        daysoff_date: this.daysoffDate,
        daysoff_hour: this.daysoffHour,
        daysoff_name: this.daysoffName,
      },

      // type: [],
      // how: null,
      // confirm: false,
      // rating: null,
      userNameValidity: "pending",
      emits: ["onClose"],
    };
  },

  methods: {
    onEditDayoffSubmit() {
      updateDaysoffAPI(this.editDayoffData.dayoffId, this.editDayoffData)
        .then((response) => {
          // reflash data list when chiled component update data
          this.$root.$emit("get_daysoff");
          this.dayoffId = "";
          this.departMent = "";
          this.dayoffUserId = "";
          this.dayoffUser = "";
          this.daysoff_date = "";
          this.daysoff_hour = null;
          this.daysoff_name = "";
          console.log(response.data);
          this.message = "The Dayoff Data was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },
    validateInput() {
      if (this.editDayoffData.daysoff_hour === "0") {
        this.userNameValidity = "invalid";
      } else {
        this.userNameValidity = "valid";
      }
    },
  },
};
</script>
<style scoped>
form {
  margin: 8rem auto;
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