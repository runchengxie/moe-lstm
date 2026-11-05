**English** | [简体中文](README.zh-CN.md)

# MoE-LSTM

This is a research script. It asks whether the next session’s close will be up or down, using a mixture-of-experts LSTM (MoE-LSTM). It was written for an index level, with the S&P 500 in mind. It prints metrics and a long/short backtest against buy and hold. It is not a trading system.

Hive Parquet minute bars are the input when you set them. Otherwise the script falls back to a daily CSV. This repo does not include market data. The default remote CSV URL returned HTTP 404 on 2026-11-05, so a CSV run needs a local path.

## Quick start

Checked on Python 3.12. Install [uv](https://docs.astral.sh/uv/) 0.13.7, then from this directory:

```bash
uv sync
```

`uv sync` creates `.venv` and installs the locked dependencies. The fixture below is a small synthetic CSV in this repo, not market data:

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run python moe_lstm.py
```

Parquet is supported with environment variables. When `MOE_DATA_PARQUET` is set, that Hive root is the data source and it wins over `MOE_DATA_CSV`:

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run python moe_lstm.py
```

## What you get

One run trains three models: a hand-picked feature set, a K-Means subset, and a self-organizing-map subset. Each one is an LSTM mixture of experts. The three experts read the same window. They differ by initialization and by the learned gate. The script prints class counts and does not resample. It then prints classification metrics and a long/short backtest next to buy and hold.

## More detail

- [Data](docs/data.md) — Parquet layout, how minutes become daily bars, the CSV columns, and `MOE_DATA_PARQUET`, `MOE_SYMBOL`, `MOE_SECURITY`, `MOE_DATA_CSV`
- [Training and backtest](docs/training.md) — window length, the split, features, the label threshold, fees, and the printed metrics
- [Setup](docs/setup.md) — uv, why the packages are pinned, Python 3.12
- [CI and the project site](docs/ci.md) — GitHub workflows, the smoke fixture, and GitHub Pages

The project site is [https://runchengxie.github.io/moe_lstm/](https://runchengxie.github.io/moe_lstm/). The page source is [`site/`](site/). On 2026-11-05 that URL returned HTTP 404 because no Pages deploy had run. Preview and publish steps are in [`site/README.md`](site/README.md).
