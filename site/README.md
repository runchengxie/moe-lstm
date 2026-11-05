# moe_lstm 项目简报

`site/` 是一个很小的 Astro 静态站，用来公开介绍仓库根目录的研究脚本。页面默认中文，可以切到英文；颜色跟随系统的 `prefers-color-scheme`，也可以改成浅色或深色。

站点地址（在 `main` 上用 GitHub Actions 成功发布之后）：

https://runchengxie.github.io/moe_lstm/

撰写时（2026-11-05）这个地址返回 HTTP 404，因为还没有任何一次 Pages 部署。仓库的 Pages API 当时已经是 `build_type: workflow`（Source 为 GitHub Actions）。

Python 脚本、`pyproject.toml` / `uv.lock` 和 smoke 流程仍在仓库根目录。这个工作流只构建 `site/`。

## 本地预览

CI 使用 npm，并提交了 `package-lock.json`。Node 版本钉在 [`.nvmrc`](.nvmrc) 的 **26.13.0**（2026-11-05 的 Active LTS，代号 Lithium）。本机用 Node 22 或更新的版本也可以安装。

`astro.config.mjs` 里的 `base` 是 `/moe_lstm`，所以本地首页在 `/moe_lstm/`，不在 `/`。

### npm

```bash
cd site
npm ci
npm run dev
```

浏览器打开 http://127.0.0.1:4321/moe_lstm/

```bash
npm run build
npm run check-dist
npm run preview
```

### pnpm

pnpm 只作为本地的另一种装法。CI 不读 `pnpm-lock.yaml`，请不要把那份锁文件提交进来。

```bash
cd site
pnpm install
pnpm dev
```

构建与预览：

```bash
pnpm build
pnpm check-dist
pnpm preview
```

预览地址同样是 http://127.0.0.1:4321/moe_lstm/ 。

## 打开 GitHub Pages

发布用的是官方的 `actions/upload-pages-artifact` 和 `actions/deploy-pages`，工作流在 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)。`deploy` 只在推到 `main` 时运行。pull request 上会构建站点并上传 artifact，不会部署。

1. 打开仓库的 **Settings → Pages**。
2. 在 **Build and deployment** 里，把 **Source** 设为 **GitHub Actions**。不要选 “Deploy from a branch”。
3. 把包含该工作流的提交合并到 `main`。推送若改到 `site/`、这个工作流或根 `README.md`，就会跑 `pages`。也可以在 Actions 里手动跑 **pages**（`workflow_dispatch`）。
4. 第一次部署若停在 `github-pages` 环境等待批准，由仓库管理员批准那一次。成功后站点在 https://runchengxie.github.io/moe_lstm/ 。

2026-11-05 这次查看里，Source 已经是 GitHub Actions，因此第 2 步多半不用再点。需要做的是把本工作流合并进 `main`，等 `pages` 成功。若以后有人把 Source 改回某个分支，再按第 2 步改回来。

`site` 和 `base` 写死为这个仓库的项目 Pages 地址。仓库若改名或换主人，要一起改 `site/astro.config.mjs`。

## 内容从哪来

文案在 `src/i18n/copy.ts`，中英文字段写在一起。页面只描述脚本和撰写时的开放 PR，不记录任何一次回测数字，也不放行情。

---

# Project brief

`site/` is a small Astro static site for the study script at the repository root. Chinese is the default; English is a switch on the page. Color follows `prefers-color-scheme`, with an explicit light, dark, or system choice.

Live URL after a successful GitHub Actions deploy on `main`:

https://runchengxie.github.io/moe_lstm/

On 2026-11-05 that URL returned HTTP 404 because nothing had been published. The Pages API already reported `build_type: workflow` (Source: GitHub Actions).

The Python script, `pyproject.toml` / `uv.lock`, and the smoke workflow stay at the repository root. This workflow builds `site/` only.

## Local preview

CI uses npm and the committed `package-lock.json`. Node is pinned to **26.13.0** in [`.nvmrc`](.nvmrc), the Active LTS (Lithium) on 2026-11-05. Node 22 or newer can install it locally.

`base` in `astro.config.mjs` is `/moe_lstm`, so the local home page is `/moe_lstm/`, not `/`.

### npm

```bash
cd site
npm ci
npm run dev
```

Open http://127.0.0.1:4321/moe_lstm/

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

The preview URL is the same: http://127.0.0.1:4321/moe_lstm/

## Enable GitHub Pages

Deploy uses the official `actions/upload-pages-artifact` and `actions/deploy-pages` actions. The workflow is [`.github/workflows/pages.yml`](../.github/workflows/pages.yml). The `deploy` job runs only on a push to `main`. A pull request builds the site and uploads the artifact, and does not deploy.

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**. Leave “Deploy from a branch” unselected.
3. Merge a commit that contains this workflow into `main`. A push that changes `site/`, this workflow, or the root `README.md` runs `pages`. **workflow_dispatch** on the Actions tab runs it by hand.
4. If the first deploy waits for approval on the `github-pages` environment, a repository admin approves that run. The site is then https://runchengxie.github.io/moe_lstm/ .

On 2026-11-05 the Source was already GitHub Actions, so step 2 is likely already done. Merging this workflow to `main` and waiting for a green `pages` run is what publishes the URL. If Source is later switched back to a branch, set it to GitHub Actions again.

`site` and `base` are fixed to this repository’s project Pages URL. If the repository is renamed or moved, change both in `site/astro.config.mjs`.

## Where the words live

Copy is in `src/i18n/copy.ts`, with Chinese and English on the same fields. The page describes the script and the pull requests that were open at write time. It records no backtest figures and hosts no market data.
