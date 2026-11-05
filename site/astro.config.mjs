import { defineConfig } from "astro/config";

// Project Pages URL: https://runchengxie.github.io/moe_lstm/
export default defineConfig({
  site: "https://runchengxie.github.io",
  base: "/moe_lstm",
  trailingSlash: "always",
  build: {
    inlineStylesheets: "always",
  },
});
