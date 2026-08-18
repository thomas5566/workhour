<template><i :class="iconClass" aria-hidden="true" /></template>

<script>
const ICONS = {
  "file-earmark-plus": "fa-file-circle-plus",
  "info-circle-fill": "fa-circle-info",
  "lock-fill": "fa-lock",
  "person-fill": "fa-user",
  power: "fa-power-off",
  search: "fa-magnifying-glass",
};

export default {
  name: "BIcon",
  props: { icon: { type: String, required: true } },
  computed: { iconClass() { return ["fa-solid", ICONS[this.icon] || "fa-circle"]; } },
};
</script>
