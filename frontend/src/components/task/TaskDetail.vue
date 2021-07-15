<template>
  <div>
    <b-table :items="tasksgroup" :fields="fields" striped responsive="sm">
      <template #cell(show_details)="row">
        <b-button size="sm" @click="row.toggleDetails" class="mr-2"
          >{{ row.detailsShowing ? "Hide" : "Show" }} Details</b-button
        >
      </template>

      <template #row-details="row">
        <b-card v-for="worklist in row.item.workhours" :key="worklist.id">
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>department:</b>
            </b-col>
            <b-col>{{ worklist.user.department.department_name }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>User Name:</b>
            </b-col>
            <b-col>{{ worklist.user.username }}</b-col>
          </b-row>

          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>Date:</b>
            </b-col>
            <b-col>{{ worklist.date }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>Hours:</b>
            </b-col>
            <b-col>{{ worklist.hour }}/hr</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>description:</b>
            </b-col>
            <b-col>{{ worklist.description }}</b-col>
          </b-row>
        </b-card>
        <b-button size="sm" @click="row.toggleDetails">Hide Details</b-button>
      </template>
    </b-table>
  </div>
</template>

<script>
import { getTaskByGroupAPI } from "../../service/apis.js";
export default {
  components: {},
  props: {
    msg: String,
  },
  data() {
    return {
      form: {
        taskname: "",
        fullname: "",
        organization: "",
      },
      isBusy: false,
      tasksgroup: [],
      fields: [
        {
          key: "id",
          label: "ID",
          sortable: true,
        },
        {
          key: "taskname",
          label: "簡稱",
        },
        // {
        //   key: "fullname",
        //   label: "計畫全名",
        // },
        // {
        //   key: "organization",
        //   label: "單位",
        // },
        "show_details",
      ],
    };
  },
  computed: {
    isLoggedIn: function() {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function() {
    this.get_tasks_by_group();
  },
  methods: {
    get_tasks_by_group() {
      getTaskByGroupAPI().then((response) => (this.tasksgroup = response.data));
    },
  },
};
</script>
