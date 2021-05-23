<template>
  <div>
    <div class="workhours" v-if="workhour">
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
          <tr>
            <td>{{ workhour.id }}</td>
            <td>{{ workhour.user.username }}</td>
            <td>{{ workhour.task.taskname }}</td>
            <td>{{ workhour.date }}</td>
            <td>{{ workhour.hour }}</td>
            <td>{{ workhour.description }}</td>
            <td>{{ workhour.is_overtime }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { getWorkhourIdAPI } from "../service/apis.js";
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
    return {
      workhour: null,
    };
  },
  mounted: function () {
    this.get_workhour();
  },
  methods: {
    async get_workhour() {
      await getWorkhourIdAPI(this.$route.params.id).then(
        (response) => (this.workhour = response.data)
      );
    },
  },
};
</script>