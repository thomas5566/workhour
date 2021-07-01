<template>
  <div v-if="isLoggedIn">
    <div>
      <h4 style="text-align: center">工作項目清單</h4>
      <ejs-grid
        ref="grid1"
        id="FirstGrid"
        :dataSource="workhours"
        :allowFiltering="true"
        :toolbar="toolbarOptions"
        :allowPaging="true"
        :allowExcelExport="true"
        :toolbarClick="toolbarClick"
        :pageSettings="pageSettings"
        height="323"
        :load="load"
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
    </div>

    <div style="text-align: center">
      <h4>支出項目清單</h4>
      <ejs-grid
        ref="grid2"
        id="SecondGrid"
        :allowFiltering="true"
        :dataSource="expens"
        :allowExcelExport="true"
        :allowPaging="true"
        :pageSettings="pageSettings"
        height="323"
        :load2="load2"
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
  <base-card v-else>No Data</base-card>
</template>
<script>
import Vue from "vue";
import axios from "axios";
import ElementUI from "element-ui";
import "element-ui/lib/theme-chalk/index.css";
import "@/plugins/element.js";
import { getWorkhourAPI, getExpenAPI } from "../service/apis.js";
import {
  GridPlugin,
  Toolbar,
  ExcelExport,
  Filter,
  Page,
} from "@syncfusion/ej2-vue-grids";
Vue.use(axios);
Vue.use(GridPlugin);
Vue.use(ElementUI);
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

      pageSettings: { pageSize: 10 },
      toolbarOptions: ["ExcelExport"],
    };
  },
  computed: {
    isLoggedIn: function() {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted: function() {
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
    toolbarClick: function(args) {
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
    load: function() {
      let rowHeight = this.$refs.grid1.ej2Instances.getRowHeight(); //height of the each row
      let gridHeight = this.$refs.grid1.height; //grid height
      let pageSize = this.$refs.grid1.pageSettings.pageSize; //initial page size
      let pageResize = (gridHeight - pageSize * rowHeight) / rowHeight; //new page size is obtained here
      this.$refs.grid1.pageSettings = {
        pageSize: pageSize + Math.round(pageResize),
      };
    },
    load2: function() {
      let rowHeight2 = this.$refs.grid2.ej2Instances.getRowHeight(); //height of the each row
      let gridHeight2 = this.$refs.grid2.height2; //grid height
      let pageSize2 = this.$refs.grid2.pageSettings2.pageSize2; //initial page size
      let pageResize2 = (gridHeight2 - pageSize2 * rowHeight2) / rowHeight2; //new page size is obtained here
      this.$refs.grid2.pageSettings2 = {
        pageSize2: pageSize2 + Math.round(pageResize2),
      };
    },
  },
  provide: {
    grid: [Toolbar, ExcelExport, Filter, Page],
  },
};
</script>

<style scoped>
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
