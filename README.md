**English** | [简体中文](README.zh-CN.md)

**Project site:** [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/) — home and docs.

# MoE-LSTM

This is a research script. It asks whether the next session’s close will be up or down, using a mixture-of-experts LSTM (MoE-LSTM). It was written for an index level, with the S&P 500 in mind. It prints metrics and a long-or-flat backtest against buy and hold. The test dates and sigmoid probabilities are written to `oos_probabilities.csv`. It is not a trading system.

Hive Parquet minute bars are the input when you set them. Otherwise the script falls back to a daily CSV. This repo does not include market data. The default remote CSV URL returned HTTP 404 on 2026-11-05, so a CSV run needs a local path.

## Quick start

Checked on Python 3.12. Install [uv](https://docs.astral.sh/uv/) 0.13.7, then from this directory:

```bash
uv sync
```

`uv sync` creates `.venv` and installs the locked dependencies. The fixture below is a small synthetic CSV in this repo, not market data:

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run moe-lstm
```

Parquet is supported with environment variables. When `MOE_DATA_PARQUET` is set, that Hive root is the data source and it wins over `MOE_DATA_CSV`:

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run moe-lstm
```

## What you get

One run trains three models: a hand-picked feature set, a K-Means subset, and a self-organizing-map subset. Each one is an LSTM mixture of experts. The three experts read the same window. They differ by initialization and by the learned router. The default gate is sparse top-1: the winning expert has weight 1 and the other two have weight 0. `MOE_TOP_K=dense` keeps the softmax over all three. These experts are LSTMs, not a Transformer mixture. The script prints class counts and does not resample. It then prints classification metrics and a long-or-flat backtest next to buy and hold.

## More detail

- [Data](docs/data.md) — Parquet layout, how minutes become daily bars, the CSV columns, and `MOE_DATA_PARQUET`, `MOE_SYMBOL`, `MOE_SECURITY`, `MOE_DATA_CSV`
- [Training and backtest](docs/training.md) — window length, the split, features, the label threshold, fees, and the printed metrics
- [Engine backtest](docs/engine.md) — long-or-flat weights, and fills plus the ledger through quant-backtest-engine
- [Setup](docs/setup.md) — uv, why the packages are pinned, Python 3.12
- [CI and the project site](docs/ci.md) — GitHub workflows, the smoke fixture, and GitHub Pages

Those notes are also on the project site: [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/). The Astro app in [`site/`](site/) serves the home page and these docs. On 2026-11-05 the project site returned HTTP 404 because no Pages deploy had run. Preview and publish steps are in [`site/README.md`](site/README.md).
