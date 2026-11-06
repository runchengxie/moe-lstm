import { defineConfig } from "astro/config";

// Project Pages URL: https://runchengxie.github.io/moe-lstm/
export default defineConfig({
  site: "https://runchengxie.github.io",
  base: "/moe-lstm",
  trailingSlash: "always",
  build: {
    inlineStylesheets: "always",
  },
});
