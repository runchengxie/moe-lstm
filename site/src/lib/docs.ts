import { readFileSync } from "node:fs";
import { join } from "node:path";
import { Marked } from "marked";
import { L, type Locale, type Localized } from "../i18n/copy";

// Astro bundles this module under site/dist, so import.meta.url is not the source file.
// `astro build` runs with the working directory set to site/.
const docsDir = join(process.cwd(), "../docs");
const repoBlob = "https://github.com/runchengxie/moe-lstm/blob/main/";
const repoTree = "https://github.com/runchengxie/moe-lstm/tree/main/";

export const docPages = [
  { slug: "setup", en: "setup.md", zh: "setup.zh-CN.md" },
  { slug: "data", en: "data.md", zh: "data.zh-CN.md" },
  { slug: "training", en: "training.md", zh: "training.zh-CN.md" },
  { slug: "engine", en: "engine.md", zh: "engine.zh-CN.md" },
  { slug: "ci", en: "ci.md", zh: "ci.zh-CN.md" },
] as const;

export type DocSlug = (typeof docPages)[number]["slug"];

const fileToSlug = new Map<string, DocSlug>();
for (const page of docPages) {
  fileToSlug.set(page.en, page.slug);
  fileToSlug.set(page.zh, page.slug);
}

const marked = new Marked({ gfm: true, breaks: false });

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

marked.use({
  renderer: {
    html({ text }) {
      return escapeHtml(text);
    },
  },
});

function stripLangSwitch(markdown: string): string {
  return markdown.replace(
    /^(?:\*\*English\*\* \| \[简体中文\]\([^)]+\)|\[English\]\([^)]+\) \| \*\*简体中文\*\*)\r?\n+/,
    "",
  );
}

function slugify(text: string): string {
  const slug = text
    .replace(/<[^>]+>/g, "")
    .replace(/[`*_]/g, "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\p{L}\p{N}-]+/gu, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return slug || "section";
}

function mapHref(href: string, siteBase: string): string {
  if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith("#") || href.startsWith("//")) {
    return href;
  }
  const hashAt = href.indexOf("#");
  const hash = hashAt >= 0 ? href.slice(hashAt) : "";
  const path = hashAt >= 0 ? href.slice(0, hashAt) : href;
  const slug = fileToSlug.get(path);
  if (slug) return `${siteBase}docs/${slug}/${hash}`;
  if (path.startsWith("../")) {
    const rel = path.slice(3);
    if (rel.endsWith("/")) return `${repoTree}${rel.slice(0, -1)}${hash}`;
    return `${repoBlob}${rel}${hash}`;
  }
  return href;
}

function addHeadingIds(html: string, locale: Locale): string {
  const used = new Map<string, number>();
  return html.replace(/<h([1-6])>([\s\S]*?)<\/h\1>/g, (_match, level: string, inner: string) => {
    const base = `${locale}-${slugify(inner)}`;
    const seen = used.get(base) ?? 0;
    used.set(base, seen + 1);
    const id = seen === 0 ? base : `${base}-${seen + 1}`;
    return `<h${level} id="${id}">${inner}</h${level}>`;
  });
}

function renderMarkdown(markdown: string, locale: Locale, siteBase: string): string {
  const parsed = marked.parse(markdown, { async: false });
  if (typeof parsed !== "string") {
    throw new Error("Expected synchronous Markdown output.");
  }
  return addHeadingIds(parsed, locale)
    .replace(/href="([^"]*)"/g, (_match, href: string) => `href="${mapHref(href, siteBase)}"`)
    .replace(/<table>/g, '<div class="table-wrap"><table>')
    .replace(/<\/table>/g, "</table></div>");
}

function firstHeading(markdown: string): string {
  const match = markdown.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : "";
}

function plainParagraph(paragraph: string): string {
  return paragraph
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

function firstProse(markdown: string): string {
  for (const block of markdown.split(/\n{2,}/)) {
    const text = block.trim();
    if (!text || text.startsWith("#")) continue;
    if (text === "本文与英文文档描述同一套行为，事实以英文和代码为准。") continue;
    if (/^(?:\[[^\]]+\]\([^)]+\)|\s|·)+$/.test(text)) continue;
    return plainParagraph(text);
  }
  return "";
}

export type RenderedDoc = {
  slug: DocSlug;
  title: Localized;
  blurb: Localized;
  html: Localized;
  source: Localized;
};

export const docsIndexCopy = {
  title: L("文档", "Docs"),
  lede: L(
    "这些页面在构建时读取仓库根目录的 docs/，和根 README 指向的是同一批说明。仍由现有的 Pages 工作流发布。",
    "These pages are read from the repository docs/ folder at build time, the same notes the root README links to. The existing Pages workflow publishes them.",
  ),
  sourceLabel: L("仓库里的原文", "Source in the repository"),
};

function siteBaseOf(base: string): string {
  return base.endsWith("/") ? base : `${base}/`;
}

export function loadDocs(base: string): RenderedDoc[] {
  const siteBase = siteBaseOf(base);
  return docPages.map((page) => {
    const en = stripLangSwitch(readFileSync(join(docsDir, page.en), "utf8"));
    const zh = stripLangSwitch(readFileSync(join(docsDir, page.zh), "utf8"));
    return {
      slug: page.slug,
      title: L(firstHeading(zh), firstHeading(en)),
      blurb: L(firstProse(zh), firstProse(en)),
      html: L(renderMarkdown(zh, "zh", siteBase), renderMarkdown(en, "en", siteBase)),
      source: L(`${repoBlob}docs/${page.zh}`, `${repoBlob}docs/${page.en}`),
    };
  });
}

export function loadDoc(slug: string, base: string): RenderedDoc {
  const doc = loadDocs(base).find((item) => item.slug === slug);
  if (!doc) throw new Error(`Unknown docs page: ${slug}`);
  return doc;
}
