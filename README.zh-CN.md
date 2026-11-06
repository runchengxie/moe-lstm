[English](README.md) | 简体中文

项目站点在 [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)，首页和文档都在上面。

# MoE-LSTM

脚本判断下一根收盘到收盘的收益有没有超过阈值。模型是混合专家 LSTM，按指数点位写，最初对着标普 500。它打印分类指标，再打印做多或空仓的回测，旁边是买入持有。数字打在终端里。

Hive 分钟 Parquet 是主输入，设上 `MOE_DATA_PARQUET` 之后就走这条。根目录空着时，脚本读日频 CSV。行情文件留在仓库外面。脚本自带的远程 CSV 在 2026-11-05 返回 HTTP 404。用 CSV 时指向本地文件。

## 快速开始

在 Python 3.12 上核对过。先安装 [uv](https://docs.astral.sh/uv/) 0.13.7，然后在本目录执行：

```bash
uv sync
```

`uv sync` 创建 `.venv`，装上锁住的依赖。下面的样本是仓库里的一小份合成 CSV。行情文件留在仓库外面。

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run moe-lstm
```

Parquet 用环境变量打开。设置了 `MOE_DATA_PARQUET` 时，那个 Hive 根目录就是数据来源，并且优先于 `MOE_DATA_CSV`：

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run moe-lstm
```

## 你会看到什么

一次运行训练三个模型，手工特征、K-Means 子集、自组织映射子集。每个模型都是 LSTM 混合专家。三个专家读同一段窗口。差别来自初始化和学到的门控。脚本打印类别数量，类别保持原样。然后打印分类指标，再打印做多或空仓的回测，旁边是买入持有。

## 更多说明

- [数据](docs/data.zh-CN.md)。Parquet 目录，分钟线如何收成日线，CSV 列，`MOE_DATA_PARQUET`、`MOE_SYMBOL`、`MOE_SECURITY`、`MOE_DATA_CSV`。
- [训练和回测](docs/training.zh-CN.md)。窗口长度，切分，特征，标签阈值，费用，打印的指标。
- [引擎回测](docs/engine.zh-CN.md)。只做多的权重，以及 quant-backtest-engine 里的成交和账本。
- [环境](docs/setup.zh-CN.md)。uv，这些包为什么钉住，Python 3.12。
- [CI 和项目站点](docs/ci.zh-CN.md)。GitHub 工作流，冒烟样本，GitHub Pages。

这些说明也在项目站点上：[https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)。[`site/`](site/) 里的 Astro 应用同时提供首页和这些文档。2026-11-05 项目站点返回 HTTP 404，因为还没有 Pages 部署。预览和发布步骤写在 [`site/README.md`](site/README.md)。
