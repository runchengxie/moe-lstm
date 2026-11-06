# moe_lstm 项目简报

`site/` 是一个很小的 Astro 静态站。首页是 2026-11-06 的 SPY 日线运行，稀疏 top-1 是主表，稠密是对照，再加上模型结构。文档在 `/moe-lstm/docs/`。合并记录在 `/moe-lstm/changelog/`。页面默认中文，可以切到英文。颜色跟随系统的 `prefers-color-scheme`，也可以改成浅色或深色。

站点已经发布。

https://runchengxie.github.io/moe-lstm/

这份简报对应当前 main `3f02207`（#22 的 squash，2026-11-06）。Pages 工作流是 #7 放进 main 的，squash 是 `37671ab`。`src/moe_lstm/` 随 #17 进入 main。quant-backtest-engine 适配器随 #18 进入 main。稀疏 top-1 门控随 #20 进入 main。首页的 SPY 运行随 #22 进入 main。

Python 包在 `src/moe_lstm/`。`pyproject.toml`、`uv.lock` 和 smoke 流程在仓库根目录。这个工作流只构建 `site/`。构建时读取仓库根目录的 `docs/`，说明页在 `/moe-lstm/docs/`，同一次 Pages 发布。

## 本地预览

CI 使用 npm，并提交了 `package-lock.json`。Node 版本钉在 [`.nvmrc`](.nvmrc) 的 26.13.0（2026-11-05 的 Active LTS，代号 Lithium）。本机用 Node 22 或更新的版本也可以安装。

`astro.config.mjs` 里的 `base` 是 `/moe-lstm`。本地首页在 `/moe-lstm/`。

### npm

```bash
cd site
npm ci
npm run dev
```

浏览器打开 http://127.0.0.1:4321/moe-lstm/

```bash
npm run build
npm run check-dist
npm run preview
```

### pnpm

pnpm 只作为本地的另一种装法。CI 读取 `package-lock.json`。不要提交 `pnpm-lock.yaml`。

```bash
cd site
pnpm install
pnpm dev
```

构建与预览。

```bash
pnpm build
pnpm check-dist
pnpm preview
```

预览地址同样是 http://127.0.0.1:4321/moe-lstm/ 。

## 站点怎么发布

发布用的是官方的 `actions/upload-pages-artifact` 和 `actions/deploy-pages`，工作流在 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)。`deploy` 只在推到 `main` 时运行。pull request 上会构建站点并上传 artifact，不会部署。

站点已经在上面的地址。Source 是 GitHub Actions。下面的步骤是 Source 被改掉之后怎么改回来。

1. 打开仓库的 Settings → Pages。
2. 在 Build and deployment 里，把 Source 设为 GitHub Actions。不要选 Deploy from a branch。
3. 工作流已经在 `main` 上。之后的推送若改到 `site/`、`docs/`、这个工作流或根 `README.md`，就会跑 `pages`。也可以在 Actions 里手动跑 pages（`workflow_dispatch`）。
4. 若部署停在 `github-pages` 环境等待批准，由仓库管理员批准那一次。

`site` 和 `base` 写死为这个仓库的项目 Pages 地址。仓库若改名或换主人，要一起改 `site/astro.config.mjs`。

## 内容从哪来

文案在 `src/i18n/copy.ts`，中英文字段写在一起。首页写下 2026-11-06 的 SPY 日线运行，稀疏 top-1 是主表，稠密是对照。数字在 `public/results/run.json`。行情文件不进仓库。

文档页读取仓库根目录 `docs/` 里的中英 Markdown（环境、数据、训练、引擎、CI），不另起一套文案。

---

# Project brief

`site/` is a small Astro static site. The home page is one real run plus the model layout. Docs are at `/moe-lstm/docs/`. The merge list is at `/moe-lstm/changelog/`. Chinese is the default; English is a switch on the page. Color follows `prefers-color-scheme`, with an explicit light, dark, or system choice.

Live URL:

https://runchengxie.github.io/moe-lstm/

This brief matches main at `3f02207` (the squash of #22, 2026-11-06). The site is published at the URL above. The Pages workflow landed in #7 (`37671ab`). `src/moe_lstm/` landed in #17. The quant-backtest-engine adapter landed in #18. The sparse top-1 gate landed in #20. The home page run is the SPY window from #22.

The Python package is `src/moe_lstm/`. `pyproject.toml`, `uv.lock`, and the smoke workflow stay at the repository root. This workflow builds `site/` only. The build reads the repository `docs/` folder and serves those pages at `/moe-lstm/docs/`, in the same Pages deploy.

## Local preview

CI uses npm and the committed `package-lock.json`. Node is pinned to **26.13.0** in [`.nvmrc`](.nvmrc), the Active LTS (Lithium) on 2026-11-05. Node 22 or newer can install it locally.

`base` in `astro.config.mjs` is `/moe-lstm`, so the local home page is `/moe-lstm/`, not `/`.

### npm

```bash
cd site
npm ci
npm run dev
```

Open http://127.0.0.1:4321/moe-lstm/

```bash
npm run build
npm run check-dist
npm run preview
```

### pnpm

pnpm is a local alternative. CI does not read `pnpm-lock.yaml`; do not commit one.

```bash
cd site
pnpm install
pnpm dev
pnpm build
pnpm check-dist
pnpm preview
```

The preview URL is the same: http://127.0.0.1:4321/moe-lstm/

## Enable GitHub Pages

Deploy uses the official `actions/upload-pages-artifact` and `actions/deploy-pages` actions. The workflow is [`.github/workflows/pages.yml`](../.github/workflows/pages.yml). The `deploy` job runs only on a push to `main`. A pull request builds the site and uploads the artifact, and does not deploy.

The site is already published at the URL above, and Source is GitHub Actions. The steps below put Source back if someone changes it.

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**. Leave “Deploy from a branch” unselected.
3. The workflow is already on `main`. A later push that changes `site/`, `docs/`, this workflow, or the root `README.md` runs `pages`. **workflow_dispatch** on the Actions tab runs it by hand.
4. If a deploy waits for approval on the `github-pages` environment, a repository admin approves that run. The published URL is https://runchengxie.github.io/moe-lstm/ .

`site` and `base` are fixed to this repository’s project Pages URL. If the repository is renamed or moved, change both in `site/astro.config.mjs`.

## Where the words live

Copy is in `src/i18n/copy.ts`, with Chinese and English on the same fields. The home page records the 2026-11-06 SPY daily run. Sparse top-1 is the main table. Dense is the comparison. The numbers live in `public/results/run.json`. The price file stays out of the repository.

The docs routes read the bilingual Markdown in the repository `docs/` folder (setup, data, training, engine, CI). They do not keep a second copy of that text.
