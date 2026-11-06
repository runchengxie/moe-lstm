[English](ci.md) | 简体中文

# CI 和项目站点

[项目说明](../README.zh-CN.md) · [数据](data.zh-CN.md) · [训练和回测](training.zh-CN.md) · [环境](setup.zh-CN.md)

安装步骤和版本表在 [环境](setup.zh-CN.md)。冒烟用的文件遵循 [数据](data.zh-CN.md) 里的 CSV 约定。

## 单元测试

[`.github/workflows/tests.yml`](../.github/workflows/tests.yml) 在 pull request 上，以及向 `main` 的 push 上，运行下面的 unittest。环境是 `ubuntu-latest` 和 Python 3.12，先执行 `uv sync --frozen`。

```bash
uv run python -m unittest discover -s tests -t . -v
```

加载、标签、切分和回测不会导入 TensorFlow。安装了 TensorFlow 时，`tests/test_model.py` 会构建混合专家并执行 `main(epochs=1)`。未安装时这些测试跳过。

## 冒烟

[`.github/workflows/smoke.yml`](../.github/workflows/smoke.yml) 在同样的事件上运行。它安装同一份锁，对 `src/moe_lstm` 做字节编译，并用 `tests/fixtures/tiny_bars.csv` 训练一个 epoch。

```bash
uv sync --frozen
uv run python -m compileall -q src/moe_lstm
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg uv run moe-lstm
```

`tests/fixtures/tiny_bars.csv` 是 120 行合成序列，列约定和上面的 CSV 一样。它用来确认包装得上、拟合得了、指标印得出来。行情文件留在仓库外面。这条 workflow 给 TensorFlow 安装留了 30 分钟。GitHub 托管 runner 装不上 TensorFlow 时，到能安装的机器上跑这三条命令。`compileall` 只做字节编译。跑完后，每个特征子集各自建一个模型，终端里可能出现 TensorFlow 的 retracing 警告。Agg 后端下，无显示画布那条警告不出现。`MOE_EPOCHS` 和 Agg 后端写在 [训练和回测](training.zh-CN.md)。冒烟命令是控制台脚本 `uv run moe-lstm`。`uv run python -m moe_lstm` 是同一个入口。

## Parquet 加载

[`.github/workflows/parquet-loader.yml`](../.github/workflows/parquet-loader.yml) 在 pull request 上，以及向 `main` 的 push 上运行。它用 uv 只安装 pandas 和 pyarrow，并设置 `PYTHONPATH=src`，这样导入 `moe_lstm.prices` 时旁边没有 TensorFlow。然后执行下面的命令。

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

这个检查会建一棵合成的 Hive 目录并比较日线 OHLCV，不需要 TensorFlow。Hive 目录和聚合规则在 [数据](data.zh-CN.md)。

## 项目站点

[`site/`](../site/) 是一份双语简报。默认中文，页面上可以切到英文。颜色跟着 `prefers-color-scheme`，也可以收成浅色、深色或系统。[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) 只构建这个 Astro 应用。Node.js 26.13.0 写在 `site/.nvmrc`。发布用 `actions/upload-pages-artifact` 和 `actions/deploy-pages`，产物是 `site/dist`。这个工作流不装 Python 依赖。

工作流在 `main` 上成功之后，站点在 [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)。2026-11-05 项目站点返回 HTTP 404。当时还没有 Pages 部署。Pages API 已经把 Source 报成 GitHub Actions，`build_type` 是 `workflow`。

### 打开 GitHub Pages

1. 打开 Settings，进入 Pages。
2. 在 Build and deployment 里把 Source 设为 GitHub Actions。
3. 把工作流合并到 `main`。推送若改到 `site/`、`docs/`、这个工作流或根目录 `README.md`，就会跑 `pages`。`deploy` 只在 `main` 上运行。pull request 会构建站点，发布留在 `main` 的那次推送。
4. 第一次运行若停在 `github-pages` 环境等批准，批准那一次。发布地址是 https://runchengxie.github.io/moe-lstm/ 。

Source 已经是 GitHub Actions 时，第 2 步不用再点。npm 和 pnpm 的本地命令，还有 `/moe-lstm/` 这个 base，写在 [`site/README.md`](../site/README.md)。

```bash
cd site
npm ci
npm run dev
```

打开 http://127.0.0.1:4321/moe-lstm/ 。用 pnpm 时，在 `site/` 里执行 `pnpm install` 然后 `pnpm dev`。持续集成使用 npm 和 `site/package-lock.json`。
