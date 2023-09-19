<template>
  <body class="hold-transition sidebar-mini layout-fixed">
    <div class="wrapper">
      <Navbar></Navbar>
      <Sidebar></Sidebar>

      <div class="content-wrapper">
        <ContentHeader></ContentHeader>
        <section class="content">
          <div class="container-fluid">
            <div id="app">
              <!-- <the-header></the-header> -->
              <!-- <the-header-nav></the-header-nav> -->
              <router-view />
            </div>
          </div>
        </section>
      </div>

      <Footer></Footer>
      <ControlSidebar></ControlSidebar>
    </div>
  </body>
</template>
<script>
// @ is an alias to /src
// import NavBar from "@/components/NavBar.vue";

// import TheHeaderNav from "@/components/layouts/TheHeaderNav.vue";
// import TheHeader from "@/components/layouts/TheHeaders.vue";

import ContentHeader from "./dashboard/ContentHeader.vue";
import Navbar from "./dashboard/Navbar.vue";
import Sidebar from "./dashboard/Sidebar.vue";
import Footer from "./dashboard/Footer.vue";
import ControlSidebar from "./dashboard/ControlSidebar.vue";

export default {
  components: {
    // NavBar,
    // TheHeaderNav,
    // TheHeader,
    ContentHeader,
    Navbar,
    Sidebar,
    Footer,
    ControlSidebar,
  },
  methods: {},
  mounted() { },
};
</script>
