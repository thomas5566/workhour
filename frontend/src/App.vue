<template>
  <!-- Guest pages must not inherit AdminLTE's sidebar offsets and fixed layout. -->
  <router-view v-if="isGuestPage" />

  <div v-else class="hold-transition sidebar-mini layout-fixed">
    <div class="wrapper">
      <Navbar></Navbar>
      <Sidebar></Sidebar>

      <div class="content-wrapper">
        <section class="content">
          <div class="container-fluid">
            <div>
              <router-view />
            </div>
          </div>
        </section>
      </div>

      <SiteFooter></SiteFooter>
      <ControlSidebar></ControlSidebar>
    </div>
  </div>
</template>
<script>
// @ is an alias to /src
// import NavBar from "@/components/NavBar.vue";

// import TheHeaderNav from "@/components/layouts/TheHeaderNav.vue";
// import TheHeader from "@/components/layouts/TheHeaders.vue";
// import ContentHeader from "./dashboard/ContentHeader.vue";

import Navbar from "./dashboard/Navbar.vue";
import Sidebar from "./dashboard/Sidebar.vue";
import SiteFooter from "./dashboard/Footer.vue";
import ControlSidebar from "./dashboard/ControlSidebar.vue";

export default {
  components: {
    // NavBar,
    // TheHeaderNav,
    // TheHeader,
    // ContentHeader,
    Navbar,
    Sidebar,
    SiteFooter,
    ControlSidebar,
  },
  computed: {
    isGuestPage() {
      return this.$route.matched.some((route) => route.meta.guest);
    },
  },
  methods: {},
  mounted() { },
};
</script>

<!--
  The dashboard templates still use AdminLTE 3 class names. AdminLTE 4 renamed
  its shell classes, so these project-owned styles preserve the existing Vue
  views while the dashboard components are migrated incrementally.
-->
<style>
:root {
  --workhour-header-height: 3.6rem;
  --workhour-sidebar-width: 16rem;
}

html,
body,
#app {
  min-height: 100%;
}

body {
  background: #f4f6f9;
  margin: 0;
}

.wrapper {
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

.main-header {
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  margin-left: var(--workhour-sidebar-width);
  min-height: var(--workhour-header-height);
  padding: 0.35rem 1rem;
  position: sticky;
  top: 0;
  z-index: 1030;
}

.main-header .navbar-nav {
  align-items: center;
  flex-direction: row;
}

.main-header .navbar-nav.ms-auto,
.main-header .navbar-nav.ml-auto {
  margin-left: auto !important;
}

/* The old data-widget search requires AdminLTE 3 JavaScript; keep it closed. */
.main-header .navbar-search-block {
  display: none;
}

.main-sidebar {
  background: #263238;
  bottom: 0;
  color: #c2c7d0;
  left: 0;
  overflow-x: hidden;
  overflow-y: auto;
  position: fixed;
  top: 0;
  width: var(--workhour-sidebar-width);
  z-index: 1040;
}

.main-sidebar .brand-link {
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  display: flex;
  gap: 0.75rem;
  min-height: var(--workhour-header-height);
  padding: 0.55rem 1rem;
  text-decoration: none;
}

.main-sidebar .brand-image {
  border-radius: 50%;
  flex: 0 0 2.25rem;
  height: 2.25rem;
  margin: 0;
  max-width: 2.25rem;
  object-fit: cover;
  width: 2.25rem;
}

.main-sidebar .brand-text {
  font-size: 1.15rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main-sidebar .sidebar {
  padding: 0.75rem;
}

.main-sidebar .form-inline,
.main-sidebar .input-group {
  display: flex;
  width: 100%;
}

.main-sidebar .form-control-sidebar {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.18);
  color: #fff;
  min-width: 0;
}

.main-sidebar .btn-sidebar {
  border-color: rgba(255, 255, 255, 0.18);
  color: #c2c7d0;
}

.nav-sidebar {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-sidebar .nav-link {
  align-items: center;
  border-radius: 0.35rem;
  color: #c2c7d0;
  display: flex;
  gap: 0.65rem;
  padding: 0.65rem 0.75rem;
  text-decoration: none;
  width: 100%;
}

.nav-sidebar .nav-link:hover,
.nav-sidebar .router-link-active {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.nav-sidebar .nav-icon {
  flex: 0 0 1.25rem;
  text-align: center;
}

.nav-sidebar .nav-link p {
  align-items: center;
  display: flex;
  flex: 1;
  justify-content: space-between;
  margin: 0;
  min-width: 0;
}

.content-wrapper {
  background: #f4f6f9;
  margin-left: var(--workhour-sidebar-width);
  min-height: calc(100vh - var(--workhour-header-height));
  padding: 1rem;
}

.content-wrapper .container-fluid {
  margin: 0 auto;
  max-width: 100%;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.content-wrapper .card {
  max-width: 100%;
  width: 100%;
}

.content-wrapper .table-responsive,
.content-wrapper .table-responsive-sm,
.content-wrapper .table-responsive-md,
.content-wrapper .table-responsive-lg,
.content-wrapper .table-responsive-xl {
  overflow-x: auto;
  width: 100%;
}

.main-footer {
  background: #fff;
  border-top: 1px solid #dee2e6;
  margin-left: var(--workhour-sidebar-width);
  min-height: 3rem;
  padding: 0.75rem 1rem;
}

@media (max-width: 991.98px) {
  .main-sidebar {
    display: none;
  }

  .main-header,
  .content-wrapper,
  .main-footer {
    margin-left: 0;
  }

  .content-wrapper {
    padding: 0.75rem 0.25rem;
  }
}
</style>
