[English](ci.md) | **简体中文**

# CI 和项目站点

本文与英文文档描述同一套行为，事实以英文和代码为准。

[项目说明](../README.zh-CN.md) · [数据](data.zh-CN.md) · [训练和回测](training.zh-CN.md) · [环境](setup.zh-CN.md)

安装步骤和版本表在 [环境](setup.zh-CN.md)。冒烟用的文件遵循 [数据](data.zh-CN.md) 里的 CSV 约定。

## 单元测试

[`.github/workflows/tests.yml`](../.github/workflows/tests.yml) 在 pull request 上，以及向 `main` 的 push 上，运行下面的 unittest。环境是 `ubuntu-latest` 和 Python 3.12，先执行 `uv sync --frozen`。

```bash
uv run python -m unittest discover -s tests -t . -v
```

加载、标签、切分和回测不会导入 TensorFlow。安装了 TensorFlow 时，`tests/test_model.py` 会构建混合专家并执行 `main(epochs=1)`。未安装时这些测试跳过。

## 冒烟

[`.github/workflows/smoke.yml`](../.github/workflows/smoke.yml) 在同样的事件上运行。它安装同一份锁，对 `moe_lstm.py` 做字节编译，并用 `tests/fixtures/tiny_bars.csv` 训练一个 epoch：

```bash
uv sync --frozen
uv run python -m py_compile moe_lstm.py
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg uv run python moe_lstm.py
```

`tests/fixtures/tiny_bars.csv` 是符合上述列约定的 120 行合成序列，用来确认脚本能加载、拟合并打印指标。它不是真实行情。这条 workflow 给 TensorFlow 安装留了 30 分钟。如果 GitHub 托管 runner 装不上 TensorFlow，就在能安装的机器上跑这三条命令。`py_compile` 不会导入 TensorFlow。跑完后仍可能看到 TensorFlow 的 retracing 警告，因为每个特征子集都会单独建一个模型。不会再出现无显示画布警告。`MOE_EPOCHS` 和 Agg 后端写在 [训练和回测](training.zh-CN.md)。

## Parquet 加载

[`.github/workflows/parquet-loader.yml`](../.github/workflows/parquet-loader.yml) 在 pull request 上，以及向 `main` 的 push 上运行。它用 uv 只安装 pandas 和 pyarrow，然后执行：

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

这个检查会建一棵合成的 Hive 目录并比较日线 OHLCV，不需要 TensorFlow。Hive 目录和聚合规则在 [数据](data.zh-CN.md)。

## 项目站点

[`site/`](../site/) 是一份双语简报。默认中文，可以切到英文。颜色跟随 `prefers-color-scheme`，也可以固定为浅色、深色或系统。[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) 只构建这个 Astro 应用（Node.js 26.13.0，版本写在 `site/.nvmrc`），并用 `actions/upload-pages-artifact` 和 `actions/deploy-pages` 发布 `site/dist`。它不安装 Python 依赖。

工作流在 `main` 上成功之后，站点地址是 [https://runchengxie.github.io/moe_lstm/](https://runchengxie.github.io/moe_lstm/)。2026-11-05 这个地址返回 HTTP 404，因为还没有 Pages 部署。当时 Pages API 已经把 Source 报成 GitHub Actions（`build_type: workflow`）。

### 打开 GitHub Pages

1. 打开 **Settings → Pages**。
2. 在 **Build and deployment** 里把 **Source** 设为 **GitHub Actions**（不要选 “Deploy from a branch”）。
3. 把工作流合并到 `main`。改动 `site/`、这个工作流或根目录 `README.md` 的推送会跑 `pages`。`deploy` 只在 `main` 上运行。pull request 会构建站点，但不会发布。
4. 如果第一次运行停在 `github-pages` 环境等待批准，批准那一次。发布地址是 https://runchengxie.github.io/moe_lstm/ 。

如果 Source 已经是 GitHub Actions，第 2 步不用再点。npm 和 pnpm 的本地命令，以及 `/moe_lstm/` 这个 base，写在 [`site/README.md`](../site/README.md)。

```bash
cd site
npm ci
npm run dev
```

打开 http://127.0.0.1:4321/moe_lstm/ 。用 pnpm 时，在 `site/` 里执行 `pnpm install` 然后 `pnpm dev`。持续集成使用 npm 和 `site/package-lock.json`。
