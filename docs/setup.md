English | [简体中文](setup.zh-CN.md)

# Setup

[Project README](../README.md) · [Data](data.md) · [Training and backtest](training.md) · [CI and the project site](ci.md)

The check used Python 3.12. Install [uv](https://docs.astral.sh/uv/) 0.13.7, then run this from the repository directory.

```bash
uv sync
```

`uv sync` creates `.venv`, installs the locked dependencies, and installs this project. The import name is `moe_lstm`, in `src/moe_lstm/`. The console command is `moe-lstm`. `python -m moe_lstm` runs the same study. `pyproject.toml` pins the direct packages. `uv.lock` pins the full resolve. `.python-version` names Python 3.12. When that interpreter is missing, uv installs it.

These direct pins installed cleanly on Python 3.12 on 2026-11-05. The Hive loader also pins pyarrow 26.0.1.

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

Keras is pinned on its own. TensorFlow 2.21.0 only asks for `keras>=3.12`. With the pins frozen, a fresh install stays on pandas 3.1.1 and numpy 2.5.4. K-Means sets `n_init` to 10. scikit-learn 1.4 changed the default to `auto`.

How GitHub Actions runs these pins is in [CI and the project site](ci.md). What the script prints after training is in [Training and backtest](training.md).

## Tests

```bash
uv run python -m unittest discover -s tests -t . -v
```

The loading, label, split, and backtest tests use pandas and scikit-learn. When TensorFlow is installed, `tests/test_model.py` builds the mixture and runs `main(epochs=1)`. When TensorFlow is absent, those tests skip.

The Hive aggregation check uses pandas and pyarrow.

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

That check is described with the file layout in [Data](data.md).
