import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const dist = fileURLToPath(new URL("../dist/", import.meta.url));

function walk(dir, files = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) walk(path, files);
    else files.push(path);
  }
  return files;
}

const files = walk(dist);
const html = files.filter((path) => path.endsWith(".html"));
const blobs = files
  .filter((path) => path.endsWith(".html") || path.endsWith(".css") || path.endsWith(".js"))
  .map((path) => readFileSync(path, "utf8"));
const all = blobs.join("\n");
const indexPath = join(dist, "index.html");
if (!existsSync(indexPath)) {
  console.error("check-dist: dist/index.html is missing");
  process.exit(1);
}
const index = readFileSync(indexPath, "utf8");

const required = [
  "/moe_lstm/",
  "不是交易系统",
  "not a trading system",
  "No market data",
  "没有行情数据",
  "MOE_DATA_CSV",
  "MOE_DATA_PARQUET",
  "MOE_SYMBOL",
  "MOE_SECURITY",
  "Python 3.12",
  "TensorFlow 2.21.0",
  "uv sync",
  "uv sync --frozen",
  "pyproject.toml",
  "uv.lock",
  "src/moe_lstm",
  "37671ab",
  "已合并",
  "Merged",
  "https://github.com/runchengxie/moe_lstm/pull/1",
  "https://github.com/runchengxie/moe_lstm/pull/2",
  "https://github.com/runchengxie/moe_lstm/pull/3",
  "https://github.com/runchengxie/moe_lstm/pull/4",
  "https://github.com/runchengxie/moe_lstm/pull/5",
  "https://github.com/runchengxie/moe_lstm/pull/6",
  "https://github.com/runchengxie/moe_lstm/pull/7",
  "https://github.com/runchengxie/quant-backtest-engine",
  "https://runchengxie.github.io/moe_lstm/",
  "data-theme",
  "data-set-lang=\"en\"",
  "data-set-theme=\"system\"",
  "prefers-color-scheme",
  "0309d55",
  "THRESHOLD = 0.002",
];

const forbidden = [
  "Open pull requests",
  "Open at write time",
  "开放的 pull request",
  "撰写时仍开放",
  "开放 · 撰写时",
  "Suggested merge order",
  "建议的合并顺序",
  "仍是下界",
  "still lower bounds",
];

const missing = required.filter((needle) => !all.includes(needle) && !index.includes(needle));
if (missing.length > 0) {
  console.error("check-dist: built site is missing:\n" + missing.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}

const stale = forbidden.filter((needle) => all.includes(needle) || index.includes(needle));
if (stale.length > 0) {
  console.error("check-dist: built site still has pre-merge copy:\n" + stale.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}

const assetHrefs = [...index.matchAll(/\s(?:href|src)="([^"]+)"/g)].map((match) => match[1]);
const localAssets = assetHrefs.filter((href) => href.includes("/_astro/") || href.endsWith(".svg") || href.endsWith(".css") || href.endsWith(".js"));
const unprefixed = localAssets.filter((href) => href.startsWith("/") && !href.startsWith("/moe_lstm/"));
if (unprefixed.length > 0) {
  console.error("check-dist: local assets are missing the /moe_lstm/ base:\n" + unprefixed.join("\n"));
  process.exit(1);
}

console.log(`check-dist: ok (${html.length} html files)`);
