<template>
  <div>
    <date-picker
      v-model="datefilter"
      type="date"
      range
      placeholder="Select date range"
    ></date-picker>
    <b-input-group size="sm" class="mb-2">
      <b-input-group-prepend is-text>
        <b-icon icon="search"></b-icon>
      </b-input-group-prepend>
      <b-form-input
        type="search"
        v-model="search"
        placeholder="搜尋計畫名稱"
      ></b-form-input>
    </b-input-group>
  </div>
</template>

<script>
import DatePicker from "vue2-datepicker";
import "vue2-datepicker/index.css";
import "vue2-datepicker/locale/zh-cn";

export default {
  components: { DatePicker },
  data() {
    return {
      search: null,
      datefilter: null,
    };
  },
  computed: {
    resultQuery() {
      const byDate = (workhour) => {
        const workhourDate = new Date(workhour.date);
        const startDate = new Date(this.datefilter[0]);
        const endDate = new Date(this.datefilter[1]);
        return (
          workhourDate >= startDate &&
          workhourDate <= endDate.setDate(endDate.getDate() + 1)
        );
      };

      const byTitle = (workhour) =>
        workhour.task.taskname.includes(this.search);

      let workhours = this.workhours;

      if (this.search) {
        workhours = workhours.filter(byTitle);
      }

      const hasDateFilter =
        this.datefilter?.length >= 2 &&
        this.datefilter[0] &&
        this.datefilter[1];
      if (hasDateFilter) {
        workhours = workhours.filter(byDate);
      }

      return workhours;
    },
  },
};
</script>
