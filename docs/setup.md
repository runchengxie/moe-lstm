**English** | [简体中文](setup.zh-CN.md)

# Setup

[Project README](../README.md) · [Data](data.md) · [Training and backtest](training.md) · [CI and the project site](ci.md)

Checked on Python 3.12. Install [uv](https://docs.astral.sh/uv/) 0.13.7, then from this directory:

```bash
uv sync
```

`uv sync` creates `.venv`, installs the locked dependencies, and installs this project. The import name is `moe_lstm` in `src/moe_lstm/`. The console command is `moe-lstm`. `python -m moe_lstm` runs the same study. `pyproject.toml` pins the direct packages. `uv.lock` pins the full resolve. `.python-version` requests Python 3.12, and uv installs that interpreter when it is missing.

The direct pins are the set that installed cleanly on Python 3.12 on 2026-11-05, plus pyarrow 26.0.1 for the Hive loader:

| Package | Pin |
| --- | --- |
| tensorflow | 2.21.0 |
| keras | 3.15.1 |
| pandas | 3.1.1 |
| numpy | 2.5.4 |
| scikit-learn | 1.9.1 |
| minisom | 2.3.6 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| pyarrow | 26.0.1 |

Keras is pinned because TensorFlow 2.21.0 only requires `keras>=3.12`. Exact pins keep a later pandas 4 or a newer numpy from being selected on a fresh install. K-Means sets `n_init=10` because scikit-learn 1.4 changed the default to `auto`.

How those pins are exercised in GitHub Actions is in [CI and the project site](ci.md). What the script prints after it trains is in [Training and backtest](training.md).

## Tests

```bash
uv run python -m unittest discover -s tests -t . -v
```

Loading, labels, the split, and the backtest do not import TensorFlow. `tests/test_model.py` builds the mixture and runs `main(epochs=1)` when TensorFlow is installed, and skips otherwise.

The Hive aggregation check does not need TensorFlow:

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

That check is described with the file layout in [Data](data.md).
