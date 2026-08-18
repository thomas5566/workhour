<template>
  <input
    class="form-control"
    type="date"
    :value="currentValue"
    :aria-controls="ariaControls"
    @input="updateValue"
  />
</template>

<script>
export default {
  name: "BFormDatepicker",
  props: {
    modelValue: { type: String, default: undefined },
    value: { type: String, default: undefined },
    ariaControls: { type: String, default: undefined },
  },
  emits: ["update:modelValue", "input", "context"],
  computed: {
    currentValue() { return this.modelValue ?? this.value ?? ""; },
  },
  methods: {
    updateValue(event) {
      const value = event.target.value;
      this.$emit("update:modelValue", value);
      this.$emit("input", value);
      this.$emit("context", { selectedYMD: value });
    },
  },
};
</script>
