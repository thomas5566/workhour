<template>
  <div class="card mt-5">
    <!-- <div>
      <date-picker
        v-model="datefilter"
        type="date"
        range
        placeholder="請選擇欲搜尋日期範圍"
      ></date-picker>
      <b-input-group size="sm" class="mb-2">
        <b-input-group-prepend is-text>
          <b-icon icon="search"></b-icon>
        </b-input-group-prepend>
        <b-form-input
          type="search"
          v-model="search"
          placeholder="請輸入欲搜尋支出項目之名稱"
        ></b-form-input>
      </b-input-group>
    </div> -->
    <div class="card text-center m-3">
      <div>
        <b-row>
          <b-col md="1" class="mb-0">
            <b-button
              size="lg"
              variant="outline-primary"
              class="mb-2"
              @click="showAddDayoff()"
            >
              <b-icon icon="file-earmark-plus" animation="cylon"></b-icon>
            </b-button>
          </b-col>
        </b-row>
      </div>
      <div class="card-header">
        <h4>休假紀錄</h4>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>部門</th>
                <th>姓名</th>
                <th>休假日期</th>
                <th>時數</th>
                <th>休假說明</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.id">
                <template>
                  <td>
                    {{ item.user.department.department_name }}
                  </td>
                  <td>
                    {{ item.user.username }}
                  </td>

                  <td>
                    {{ item.daysoff_date }}
                  </td>
                  <td>
                    {{ item.daysoff_hour }}
                  </td>
                  <td>
                    {{ item.daysoff_name }}
                  </td>
                  <td>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-warning"
                      @click="toggleDaysoffId(item.id)"
                    >
                      編輯
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteDayoff(item.id)"
                    >
                      刪除
                    </button>
                  </td>
                </template>
              </tr>
              <!-- <tr>
                <th>所選日期 休假總時數: {{ totalspends }}</th>
              </tr> -->
            </tbody>
          </table>
        </div>
      </div>
      <!-- <div class="card-footer pb-0 pt-3">
        <jw-pagination
          :items="resultQuery"
          @changePage="onChangeExpenPage"
        ></jw-pagination>
      </div> -->
    </div>

    <div>
      <transition name="fade">
        <div v-if="addDayoffIsVisible" class="backdrop">
          <add-dayoff @close="hideAddDayoff"></add-dayoff>
        </div>
      </transition>
      <transition name="fade">
        <div v-if="this.activeTopic" class="backdrop">
          <edit-daysoff
            :key="activeTopic.id"
            :id="activeTopic.id"
            :department-name="activeTopic.user.department.department_name"
            :user-id="activeTopic.user_id"
            :user-name="activeTopic.user.username"
            :daysoff-name="activeTopic.daysoff_name"
            :daysoff-date="activeTopic.daysoff_date"
            :daysoff-hour="activeTopic.daysoff_hour"
            @onClose="toggleDaysoffId"
          ></edit-daysoff>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { getDaysoffAPI, deleteDaysoffAPI } from "../../service/apis";
import EditDaysoff from "./EditDaysoff.vue";
import AddDayoff from "./AddDaysoff.vue";
export default {
  components: { EditDaysoff, AddDayoff },
  computed: {},
  data() {
    return {
      items: [],
      itemId: null,
      dialogIsVisible: true,
      addDayoffIsVisible: false,
      activeTopic: null,
      activeAdddayoff: null,
    };
  },
  mounted() {
    this.get_daysoff();
  },
  created() {
    // reflash data list when chiled component update data
    this.$root.$on("get_daysoff", this.get_daysoff);
  },
  methods: {
    deleteDayoff(id) {
      if (confirm("確定要刪除這筆資料嗎?")) {
        deleteDaysoffAPI(id).then(() => {
          this.get_daysoff();
        });
      }
    },
    get_daysoff() {
      getDaysoffAPI().then((response) => (this.items = response.data));
    },
    toggleDaysoffId(dayoffId) {
      console.log(dayoffId);
      this.activeTopic = this.items.find((item) => item.id === dayoffId);
      console.log("Data:");
      console.log(this.activeTopic);
      this.dialogIsVisible = false;
    },
    showAddDayoff() {
      this.addDayoffIsVisible = true;
    },
    hideAddDayoff() {
      this.addDayoffIsVisible = false;
    },
  },
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}

.model-enter-active,
.model-leave-active {
  transition: opacity 0.5s;
}
.model-enter, .model-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
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