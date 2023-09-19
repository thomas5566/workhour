<template>
  <div>
    <b-table :items="userlistes" :fields="fields" striped responsive="sm">
      <template #cell(show_details)="row">
        <b-button size="sm" @click="row.toggleDetails" class="mr-2">{{ row.detailsShowing ? "Hide" : "Show" }}
          Details</b-button>
      </template>
      <template #cell(check_permission)="row">
        <b-check size="sm" class="mr-2">{{ row.detailsShowing ? "Hide" : "Show" }} Check</b-check>
      </template>

      <template #row-details="row">
        <b-card v-for="worklist in row.item.workhours" :key="worklist.id">
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>taskname:</b>
            </b-col>
            <b-col>{{ worklist.task.taskname }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col sm="3" class="text-sm-right">
              <b>date:</b>
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
              <b>overtime_hour:</b>
            </b-col>
            <b-col>{{ worklist.overtime_hour }}/hr</b-col>
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
import { getUsersAllAPI } from "../../service/apis.js";

export default {
  data() {
    return {
      form: {
        taskname: "",
        fullname: "",
        organization: "",
      },
      isBusy: false,
      userlistes: [],
      fields: [
        {
          key: "username",
          label: "組員名單",
          sortable: true,
        },
        {
          key: "department.department_name",
          label: "department",
        },
        "show_details",
        "check_permission",
      ],
    };
  },
  computed: {},
  mounted() {
    this.get_members();
  },
  methods: {
    get_members() {
      getUsersAllAPI()
        .then((response) => (this.userlistes = response.data))
        .catch((err) => {
          console.error(err)
        });
    },
  },
};
</script>