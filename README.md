English | [简体中文](README.zh-CN.md)

Project site [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/), home and docs.

# MoE-LSTM

The script asks whether the next close-to-close return clears a threshold. The model is a mixture-of-experts LSTM, written for an index level, with the S&P 500 in mind. It prints metrics and a long-or-flat backtest next to buy and hold. The numbers land in the terminal.

Hive minute Parquet is the primary input once `MOE_DATA_PARQUET` is set. When that root is empty, the script reads a daily CSV. Price files stay outside the repository. The default remote CSV URL returned HTTP 404 on 2026-11-05. A CSV run points at a local file.

## Quick start

Checked on Python 3.12. Install [uv](https://docs.astral.sh/uv/) 0.13.7, then from this directory:

```bash
uv sync
```

`uv sync` creates `.venv` and installs the locked dependencies. The fixture below is a small synthetic CSV in this repository. Price files stay outside it.

```bash
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MPLBACKEND=Agg uv run moe-lstm
```

Parquet is selected with environment variables. When `MOE_DATA_PARQUET` is set, that Hive root is the data source and it wins over `MOE_DATA_CSV`.

```bash
MOE_DATA_PARQUET=/path/to/dataset-root MOE_SYMBOL=AAPL MPLBACKEND=Agg uv run moe-lstm
```

## What you get

One run trains three models: a hand-picked feature set, a K-Means subset, and a self-organizing-map subset. Each one is an LSTM mixture of experts. The three experts read the same window. They differ by initialization and by the learned gate. The script prints class counts and does not resample. It then prints classification metrics and a long-or-flat backtest next to buy and hold.

## More detail

- [Data](docs/data.md). Parquet layout, how minutes become daily bars, the CSV columns, `MOE_DATA_PARQUET`, `MOE_SYMBOL`, `MOE_SECURITY`, `MOE_DATA_CSV`.
- [Training and backtest](docs/training.md). Window length, the split, features, the label threshold, fees, and the printed metrics.
- [Engine backtest](docs/engine.md). Long-only weights, and fills plus the ledger through quant-backtest-engine.
- [Setup](docs/setup.md). uv, why the packages are pinned, Python 3.12.
- [CI and the project site](docs/ci.md). GitHub workflows, the smoke fixture, and GitHub Pages.

Those notes are also on the project site: [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/). The Astro app in [`site/`](site/) serves the home page and these docs. On 2026-11-05 the project site returned HTTP 404 because no Pages deploy had run. Preview and publish steps are in [`site/README.md`](site/README.md).
