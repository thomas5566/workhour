<template>
  <div>
    <base-card>
      <b-button
        squared
        variant="outline-primary"
        v-for="tab in tabs"
        :key="tab"
        @click="component = tab"
        >{{ tab }}</b-button
      >
      <keep-alive>
        <component :is="component" />
      </keep-alive>
    </base-card>

    <!-- <div class="workhours" v-if="user.workhours.length">
      <div>
        <table class="table table-striped table-bordered">
          <thead>
            <tr>
              <th colspan="4"><h3>Monthly-Hours</h3></th>
            </tr>
            <tr>
              <th>Year Month</th>
              <th>TotalHours</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in monthlyworkhour" :key="m.year_month">
              <td>{{ m.year_month }}</td>
              <td>{{ m.total_hour }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th colspan="7"><h3>Work-Lists</h3></th>
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
          <tr v-for="w in user.workhours" :key="w.id">
            <td>{{ w.id }}</td>
            <td>{{ w.user.username }}</td>
            <td>{{ w.task.taskname }}</td>
            <td>{{ w.date }}</td>
            <td>{{ w.hour }}</td>
            <td>{{ w.description }}</td>
            <td>{{ w.is_overtime }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>No workhours</div> -->
  </div>
</template>

<script>
import 年度總工時 from "./StoredYearHours.vue";
import 年度總支出 from "./StoredYearExpen.vue";

export default {
  components: { 年度總工時, 年度總支出 },
  props: { msg: String },
  data() {
    return {
      tabs: ["年度總工時", "年度總支出"],
      component: "年度總工時",
      // form: {
      //   username: "",
      //   fullname: "",
      // },
      // pageOfWorkhours: [],
      // rows: 100,
      // perPage: 10,
      // currentPage: 1,
    };
  },
  computed: {
    isUser: function () {
      return this.user != null;
    },
    // total: function () {
    //   console.log(this.user.workhours);
    //   return this.user.workhours.reduce(function (total, item) {
    //     return total + item.hour;
    //   }, 0);
    // },
    // getworkMonth() {
    //   const workMonth = this.user.workhours.date.slice(1, 5);
    //   console.log(workMonth) // JS starts numbering months from 0
    //   return workMonth
    // }
  },

  // mounted: function () {
  //   this.get_user_id();
  // },

  methods: {
    // onChangeWorkhourPage(pageOfWorkhours) {
    //   // update page of items
    //   this.pageOfWorkhours = pageOfWorkhours;
    // },
    // async get_user_id() {
    //   await getUserIdAPI(this.$route.params.id).then(
    //     (response) => (this.user = response.data)
    //   );
    // },
  },
};
</script>
