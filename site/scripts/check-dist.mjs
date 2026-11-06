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
  "/moe-lstm/",
  "脚本在终端打印指标",
  "The script prints metrics in the terminal.",
  "Price files stay outside the repository.",
  "行情文件留在仓库外面",
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
  "https://github.com/runchengxie/moe-lstm/pull/1",
  "https://github.com/runchengxie/moe-lstm/pull/2",
  "https://github.com/runchengxie/moe-lstm/pull/3",
  "https://github.com/runchengxie/moe-lstm/pull/4",
  "https://github.com/runchengxie/moe-lstm/pull/5",
  "https://github.com/runchengxie/moe-lstm/pull/6",
  "https://github.com/runchengxie/moe-lstm/pull/7",
  "https://github.com/runchengxie/quant-backtest-engine",
  "https://runchengxie.github.io/moe-lstm/",
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
if (!index.includes("/moe-lstm/docs/")) {
  console.error("check-dist: home page does not link to /moe-lstm/docs/");
  process.exit(1);
}
const homeNeedles = [
  "2026-11-06",
  "^GSPC",
  "2254a46",
  "2de4f96",
  "0.548",
  "0.528",
  "0.501",
  "0.524",
  "0.347",
  "-0.189",
  "0.866",
  "NaN",
  "data-chart=\"equity\"",
  "data-value=\"run\"",
  "/moe-lstm/results/equity-card.png",
  "/moe-lstm/results/confusion.png",
  "/moe-lstm/results/run.json",
  "THRESHOLD = 0.002",
  "MOE_DATA_PARQUET",
];
const missingHome = homeNeedles.filter((needle) => !index.includes(needle));
if (missingHome.length > 0) {
  console.error("check-dist: home page is missing:\n" + missingHome.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}
const staleHome = ["data-value=\"empty\"", "这些格子是占位", "The page has no stored run.", "格子空着"];
const staleHit = staleHome.filter((needle) => index.includes(needle));
if (staleHit.length > 0) {
  console.error("check-dist: home page still has empty-cell copy:\n" + staleHit.map((item) => `  - ${item}`).join("\n"));
  process.exit(1);
}
const runCells = [...index.matchAll(/data-value="run"[^>]*>([^<]*)</g)].map((match) => match[1].trim());
const numbered = runCells.filter((text) => /\d/.test(text) || text === "NaN");
if (numbered.length < 24) {
  console.error(`check-dist: expected filled run cells, found ${numbered.length}`);
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
  "/moe-lstm/docs/setup/",
  "/moe-lstm/docs/training/",
  "/moe-lstm/docs/ci/",
  "data-locale=\"en\"",
  "data-locale=\"zh\"",
  "https://github.com/runchengxie/moe-lstm/blob/main/README.md",
  "https://github.com/runchengxie/moe-lstm/blob/main/docs/data.md",
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
    if (href.startsWith("/") && !href.startsWith("/moe-lstm/")) unprefixed.push(`${file}: ${href}`);
  }
}
if (unprefixed.length > 0) {
  console.error("check-dist: local assets are missing the /moe-lstm/ base:\n" + unprefixed.join("\n"));
  process.exit(1);
}

console.log(`check-dist: ok (${html.length} html files)`);
