import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";

export default [
  { ignores: ["dist/**", "node_modules/**", "login-form-15/**", "src/vendor/**", "src/static/**"] },
  js.configs.recommended,
  ...pluginVue.configs["flat/essential"],
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        atob: "readonly",
        confirm: "readonly",
        console: "readonly",
        document: "readonly",
        FormData: "readonly",
        localStorage: "readonly",
        process: "readonly",
        setInterval: "readonly",
        sessionStorage: "readonly",
        window: "readonly",
        $: "readonly",
      },
    },
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "warn",
      "no-useless-assignment": "warn",
      "vue/multi-word-component-names": "off",
      "vue/no-deprecated-slot-attribute": "warn",
      "vue/no-deprecated-router-link-tag-prop": "warn",
      "vue/no-reserved-component-names": "warn",
      "vue/require-v-for-key": "warn",
      "vue/valid-v-for": "warn",
    },
  },
];
