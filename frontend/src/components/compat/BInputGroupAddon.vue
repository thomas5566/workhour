<template>
  <span :class="positionClass"><span class="input-group-text"><slot /></span></span>
</template>

<script>
export default {
  name: "BInputGroupAddon",
  props: { position: { type: String, required: true } },
  computed: { positionClass() { return `input-group-${this.position}`; } },
};
</script>
