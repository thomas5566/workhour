<script src="https://cdnjs.cloudflare.com/ajax/libs/vue/2.5.17/vue.js"></script>

<template>
  <div> 
    <div class="home" v-if="isLoggedIn">
    <div>
      <p><b>Whork Hour Lists</b></p>
      <ejs-grid
        ref="grid1"
        id="FirstGrid"
        :dataSource="workhours"
        :allowFiltering="true"
        :toolbar="toolbarOptions"
        :allowPaging="true"
        :allowExcelExport="true"
        :toolbarClick="toolbarClick"
      >
        <e-columns>
          <e-column
            field="id"
            headerText="ID"
            textAlign="Right"
            width="120"
          ></e-column>
          <e-column field="date" headerText="Date" width="150"></e-column>
          <e-column
            field="user.username"
            headerText="User Name"
            width="150"
          ></e-column>
          <e-column
            field="task.taskname"
            headerText="Task Name"
            width="150"
          ></e-column>
          <e-column field="hour" headerText="Hour" width="150"></e-column>
          <e-column
            field="description"
            headerText="Description"
            width="150"
          ></e-column>
        </e-columns>
      </ejs-grid>
      <p><b>Expen Lists</b></p>
      <ejs-grid
        ref="grid2"
        id="SecondGrid"
        :allowFiltering="true"
        :dataSource="expens"
        :allowExcelExport="true"
      >
        <e-columns>
          <e-column
            field="id"
            headerText="Expen ID"
            textAlign="Right"
            width="120"
          ></e-column>
          <e-column field="date" headerText="Date" width="150"></e-column>
          <e-column
            field="user.username"
            headerText="User Name"
            width="150"
          ></e-column>
          <e-column
            field="expentask.expentask_name"
            headerText="ExpenTask Name"
            width="150"
          ></e-column>
          <e-column field="price" headerText="Price" width="150"> </e-column>
          <e-column
            field="description"
            headerText="Description"
            width="150"
          ></e-column>
        </e-columns>
      </ejs-grid>
    </div>
  </div>
  <div v-else>No workhours</div>
  </div>
</template>
<script>
import Vue from "vue";
import axios from "axios";
import { getWorkhourAPI, getExpenAPI } from "../service/apis.js";
import {
  GridPlugin,
  Toolbar,
  ExcelExport,
  Filter,
} from "@syncfusion/ej2-vue-grids";
Vue.use(axios);
Vue.use(GridPlugin);
export default {
  name: "Excle",
  components: {},
  props: {
    msg: String,
  },
  data() {
    return {
      fData: this.workhour,
      sData: this.expens,

      workhours: [],
      expens: [],

      toolbarOptions: ["ExcelExport"],
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function () {
    this.get_workhour();
    this.get_expen();
  },
  created() {},
  methods: {
    async get_workhour() {
      await getWorkhourAPI().then(
        (response) => (this.workhours = response.data)
      );
    },
    async get_expen() {
      await getExpenAPI().then((response) => (this.expens = response.data));
    },
    toolbarClick: function (args) {
      if (args.item.id === "FirstGrid_excelexport") {
        // 'Grid_excelexport' -> Grid component id + _ + toolbar item name
        let appendExcelExportProperties = {
          enableFilter: true,
          multipleExport: { type: "NewSheet" },
        };
        let firstGridExport = this.$refs.grid1.excelExport(
          appendExcelExportProperties,
          true
        );
        firstGridExport.then((fData) => {
          this.$refs.grid2.excelExport(
            appendExcelExportProperties,
            false,
            fData
          );
        });
      }
    },
  },
  provide: {
    grid: [Toolbar, ExcelExport, Filter],
  },
};
</script>

<style>
@import "../../node_modules/@syncfusion/ej2-base/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-buttons/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-calendars/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-dropdowns/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-inputs/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-navigations/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-popups/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-splitbuttons/styles/material.css";
@import "../../node_modules/@syncfusion/ej2-vue-grids/styles/material.css";
</style>