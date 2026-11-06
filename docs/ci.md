**English** | [简体中文](ci.zh-CN.md)

# CI and the project site

[Project README](../README.md) · [Data](data.md) · [Training and backtest](training.md) · [Setup](setup.md)

Install and the pin table are in [Setup](setup.md). The smoke file uses the CSV contract in [Data](data.md).

## Unit tests

[`.github/workflows/tests.yml`](../.github/workflows/tests.yml) runs the unittest command below on pull requests and on pushes to `main`, on `ubuntu-latest` with Python 3.12, after `uv sync --frozen`.

```bash
uv run python -m unittest discover -s tests -t . -v
```

Loading, labels, the split, and the backtest do not import TensorFlow. `tests/test_model.py` builds the mixture and runs `main(epochs=1)` when TensorFlow is installed, and skips otherwise.

## Smoke

[`.github/workflows/smoke.yml`](../.github/workflows/smoke.yml) runs on those same events. It installs the same lock, byte-compiles `src/moe_lstm`, and trains one epoch on `tests/fixtures/tiny_bars.csv`:

```bash
uv sync --frozen
uv run python -m compileall -q src/moe_lstm
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg uv run moe-lstm
```

`tests/fixtures/tiny_bars.csv` is a synthetic 120-row series in this column contract. It checks that the script can load, fit, and print metrics. It is not market data. The smoke workflow allows 30 minutes for the TensorFlow wheel. If a GitHub-hosted runner cannot install TensorFlow, run the three commands on a machine that can. `compileall` does not import TensorFlow. The smoke command is `uv run moe-lstm`. A finished run can still print TensorFlow retracing warnings, because each feature set builds its own model. It does not print a non-interactive canvas warning. `MOE_EPOCHS` and the Agg backend are described in [Training and backtest](training.md).

## Parquet loader

[`.github/workflows/parquet-loader.yml`](../.github/workflows/parquet-loader.yml) runs on pull requests and on pushes to `main`. It uses uv to install pandas and pyarrow only, then runs:

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

That check builds a synthetic Hive tree and compares the daily OHLCV. It does not need TensorFlow. The Hive layout and the aggregation rules are in [Data](data.md).

## Project site

A bilingual brief lives in [`site/`](../site/). Chinese is the default, with an English switch. Color follows `prefers-color-scheme`, and the page can force light, dark, or system. [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) builds only that Astro app (Node.js 26.13.0 from `site/.nvmrc`) and deploys `site/dist` with `actions/upload-pages-artifact` and `actions/deploy-pages`. It does not install the Python dependencies.

After the workflow has succeeded on `main`, the site is [https://runchengxie.github.io/moe-lstm/](https://runchengxie.github.io/moe-lstm/). On 2026-11-05 the project site returned HTTP 404 because no Pages deploy had run. The Pages API already reported Source as GitHub Actions (`build_type: workflow`).

### Enable GitHub Pages

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from a branch”).
3. Merge the workflow to `main`. Pushes that touch `site/`, `docs/`, the workflow, or the root `README.md` run `pages`. The deploy job itself runs only on `main`. A pull request builds the site and does not publish it.
4. If the first run waits on the `github-pages` environment, approve it once. The published URL is https://runchengxie.github.io/moe-lstm/ .

If Source is already GitHub Actions, step 2 needs no click. Full local commands for npm and pnpm, and the `/moe-lstm/` base path, are in [`site/README.md`](../site/README.md).

```bash
cd site
npm ci
npm run dev
```

Open http://127.0.0.1:4321/moe-lstm/ . With pnpm, from `site/`: `pnpm install` then `pnpm dev`. Continuous integration uses npm and `site/package-lock.json`.
