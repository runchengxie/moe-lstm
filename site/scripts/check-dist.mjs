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

const docFiles = [
  "docs/index.html",
  "docs/setup/index.html",
  "docs/data/index.html",
  "docs/training/index.html",
  "docs/ci/index.html",
];
const missingDocs = docFiles.filter((rel) => !existsSync(join(dist, rel)));
if (missingDocs.length > 0) {
  console.error("check-dist: docs routes are missing:\n" + missingDocs.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}
if (!index.includes("/moe_lstm/docs/")) {
  console.error("check-dist: home page does not link to /moe_lstm/docs/");
  process.exit(1);
}
const homeNeedles = [
  "coming once quant-backtest-engine is wired",
  "这些格子是占位",
  "data-value=\"empty\"",
  "data-chart=\"equity\"",
  "THRESHOLD = 0.002",
  "MOE_DATA_PARQUET",
];
const missingHome = homeNeedles.filter((needle) => !index.includes(needle));
if (missingHome.length > 0) {
  console.error("check-dist: home page is missing:\n" + missingHome.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}
const emptyCells = [...index.matchAll(/data-value="empty"[^>]*>([^<]*)</g)].map((match) => match[1]);
const filled = emptyCells.filter((text) => /\d/.test(text));
if (emptyCells.length < 8 || filled.length > 0) {
  console.error(`check-dist: expected empty metric cells, found ${emptyCells.length} cells, ${filled.length} with digits`);
  process.exit(1);
}
if (!existsSync(join(dist, "changelog/index.html"))) {
  console.error("check-dist: changelog/index.html is missing");
  process.exit(1);
}
const dataHtml = readFileSync(join(dist, "docs/data/index.html"), "utf8");
const docNeedles = [
  "Hive minute bars are the primary input",
  "主输入是 Hive 分钟线",
  "/moe_lstm/docs/setup/",
  "/moe_lstm/docs/training/",
  "/moe_lstm/docs/ci/",
  "data-locale=\"en\"",
  "data-locale=\"zh\"",
  "https://github.com/runchengxie/moe_lstm/blob/main/README.md",
  "https://github.com/runchengxie/moe_lstm/blob/main/docs/data.md",
];
const missingDocCopy = docNeedles.filter((needle) => !dataHtml.includes(needle));
if (missingDocCopy.length > 0) {
  console.error("check-dist: docs/data is missing:\n" + missingDocCopy.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}

const unprefixed = [];
for (const file of html) {
  const text = readFileSync(file, "utf8");
  const hrefs = [...text.matchAll(/\s(?:href|src)="([^"]+)"/g)].map((match) => match[1]);
  const localAssets = hrefs.filter((href) => href.includes("/_astro/") || href.endsWith(".svg") || href.endsWith(".css") || href.endsWith(".js"));
  for (const href of localAssets) {
    if (href.startsWith("/") && !href.startsWith("/moe_lstm/")) unprefixed.push(`${file}: ${href}`);
  }
}
if (unprefixed.length > 0) {
  console.error("check-dist: local assets are missing the /moe_lstm/ base:\n" + unprefixed.join("\n"));
  process.exit(1);
}

console.log(`check-dist: ok (${html.length} html files)`);
