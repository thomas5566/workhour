<template>
  <div id="app">
    <the-header></the-header>
    <the-header-nav></the-header-nav>
    <router-view />
  </div>
</template>
<script>
// @ is an alias to /src
// import NavBar from "@/components/NavBar.vue";
import TheHeaderNav from "@/components/layouts/TheHeaderNav.vue";
import TheHeader from "@/components/layouts/TheHeaders.vue";

export default {
  components: {
    // NavBar,
    TheHeaderNav,
    TheHeader,
  },
};
</script>
