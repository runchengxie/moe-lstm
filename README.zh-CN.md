[English](README.md) | **简体中文**

**项目站点：** [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/) — 首页和文档。

# MoE-LSTM

本文与英文文档描述同一套行为，事实以英文和代码为准。

这是一份研究脚本，用来判断下一根 K 线的收盘相对当根是涨还是跌，模型是混合专家 LSTM（MoE-LSTM）。脚本按指数点位编写，最初针对标普 500。它会打印分类指标，以及多空回测和买入持有的对比。它不是交易系统。

设置了 Hive Parquet 分钟线时，那就是主输入。否则回退到日频 CSV。仓库里没有行情。脚本自带的远程 CSV 地址在 2026-11-05 返回 HTTP 404，所以用 CSV 时必须给出本地路径。

## 快速开始

在 Python 3.12 上核对过。先安装 [uv](https://docs.astral.sh/uv/) 0.13.7，然后在本目录执行：

```bash
uv sync
```

`uv sync` 会创建 `.venv` 并安装锁定的依赖。下面的样本是仓库里的一小份合成 CSV，不是行情：

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run moe-lstm
```

Parquet 用环境变量打开。设置了 `MOE_DATA_PARQUET` 时，那个 Hive 根目录就是数据来源，并且优先于 `MOE_DATA_CSV`：

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run moe-lstm
```

## 你会看到什么

一次运行训练三个模型：手工特征、K-Means 子集、自组织映射子集。每个模型都是 LSTM 混合专家。三个专家读取同一段窗口，差别来自初始化和学到的门控。脚本只打印类别数量，不做重采样。然后打印分类指标，以及多空回测和买入持有的对比。

## 更多说明

- [数据](docs/data.zh-CN.md) — Parquet 目录、分钟线如何收成日线、CSV 列，以及 `MOE_DATA_PARQUET`、`MOE_SYMBOL`、`MOE_SECURITY`、`MOE_DATA_CSV`
- [训练和回测](docs/training.zh-CN.md) — 窗口长度、切分、特征、标签阈值、费用和打印的指标
- [引擎回测](docs/engine.zh-CN.md) — 只做多权重，以及通过 quant-backtest-engine 的成交和账本
- [环境](docs/setup.zh-CN.md) — uv、为什么钉住这些包、Python 3.12
- [CI 和项目站点](docs/ci.zh-CN.md) — GitHub 工作流、冒烟用的样本、GitHub Pages

这些说明也在项目站点上：[https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)。[`site/`](site/) 里的 Astro 应用同时提供首页和这些文档。2026-11-05 项目站点返回 HTTP 404，因为还没有 Pages 部署。预览和发布步骤写在 [`site/README.md`](site/README.md)。
