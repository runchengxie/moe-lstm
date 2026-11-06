[English](README.md) | 简体中文

项目站点在 [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)，上面有首页和文档。

# MoE-LSTM

本文与英文文档描述同一套行为，事实以英文和代码为准。

这是一份研究脚本。它判断下一根 K 线的收盘相对当根是涨还是跌。模型是混合专家 LSTM（MoE-LSTM）。脚本按指数点位编写，最初针对标普 500。它会打印分类指标，以及做多或空仓的回测和买入持有的对比。测试段的日期和概率写在 `oos_probabilities.csv`。脚本在终端打印指标。

行情文件留在仓库外面。列约定、Parquet 和 CSV 的先后写在 [数据](docs/data.zh-CN.md)。

## 快速开始

在 Python 3.12 上核对过。先安装 [uv](https://docs.astral.sh/uv/) 0.13.7，然后在本目录执行。

```bash
uv sync
```

`uv sync` 创建 `.venv`，装上锁住的依赖。下面的样本是仓库里的一小份合成 CSV。

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run moe-lstm
```

Hive 分钟线用环境变量打开。

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run moe-lstm
```

## 你会看到什么

一次运行训练三个模型。它们是手工特征、K-Means 子集、自组织映射子集。每个模型都是 LSTM 混合专家。三个专家读取同一段窗口，差别来自初始化和学到的路由。默认门控是稀疏 top-1。选中的专家权重为 1，另外两个为 0。`MOE_TOP_K=dense` 保留三个专家的 softmax。专家是 LSTM。门控只读最后一根。脚本打印类别数量，两类的比例保持原样。然后打印分类指标，以及做多或空仓的回测和买入持有的对比。

## 更多说明

- [数据](docs/data.zh-CN.md)，Parquet 目录、分钟线如何收成日线、CSV 列，以及 `MOE_DATA_PARQUET`、`MOE_SYMBOL`、`MOE_SECURITY`、`MOE_DATA_CSV`
- [训练和回测](docs/training.zh-CN.md)，窗口长度、切分、特征、标签阈值、费用和打印的指标
- [引擎回测](docs/engine.zh-CN.md)，做多或空仓的权重，以及 quant-backtest-engine 里的成交和账本
- [环境](docs/setup.zh-CN.md)，uv、为什么钉住这些包、Python 3.12
- [CI 和项目站点](docs/ci.zh-CN.md)，GitHub 工作流、冒烟用的样本、GitHub Pages

这些说明也在项目站点上，地址是 [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/)。[`site/`](site/) 里的 Astro 应用提供首页和这些文档。站点已经发布。预览步骤写在 [`site/README.md`](site/README.md)。
