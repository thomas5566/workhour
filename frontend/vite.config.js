import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue({ template: { compilerOptions: { compatConfig: { MODE: 2 } } } })],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      vue: "@vue/compat",
    },
  },
  server: {
    port: 8080,
    proxy: {
      "/api": {
        target: process.env.VITE_BACKEND_PROXY_TARGET || "http://127.0.0.1:5566",
        changeOrigin: true,
      },
    },
  },
  test: { environment: "jsdom", setupFiles: ["./tests/setup.js"] },
});
