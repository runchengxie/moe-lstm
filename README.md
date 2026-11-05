# MoE-LSTM

Daily next-day up/down model for an index level (the script was written for the S&P 500). It builds technical features, picks feature subsets with K-Means and a self-organizing map, trains an LSTM mixture-of-experts, and prints a long/short backtest against buy-and-hold.

## Setup

Checked on Python 3.12 with a CPU-only TensorFlow install.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` pins the set that installed cleanly on Python 3.12 on 2026-11-05:

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

Keras is pinned because TensorFlow 2.21.0 only requires `keras>=3.12`. The other pins are the packages this script imports. Exact versions stop a later pandas 4 (or a newer numpy) from being selected on a fresh install.

## Run

Market data is not in this repo. The default URL (`runchengxie/quant_practice_3` `historical_data.csv`) returns HTTP 404, so point the script at a local file:

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py
```

`MPLBACKEND=Agg` keeps `plt.show()` from opening a window on a machine with no display. Matplotlib still prints `FigureCanvasAgg is non-interactive`; that warning does not stop the script.

Training runs four times (manual features, K-Means subset, SOM subset, then the manual set again), up to 50 epochs each with early stopping (patience 5). On a small CPU this is several minutes, not a packaged CLI.

`MOE_EPOCHS` overrides that epoch count. Unset, it stays 50. A smoke run sets it to `1`. The network, loss, batch size, and early-stopping patience stay as written.

## CSV contract

Required columns. Extra columns are ignored.

| Column | Rule |
| --- | --- |
| `Date` | Parsed with `format="%m/%d/%Y"` only, for example `01/13/2020`. ISO dates fail. |
| `Close/Last` | Numeric close. Indicators, the label, and the backtest all use this column. |
| `Open` | Numeric. |
| `High` | Numeric. |
| `Low` | Numeric. |

Price fields must already be numbers. A `$` prefix or thousands separator will break the rolling calculations. The script sorts by `Date`, drops rows that indicators cannot fill, and labels the next session `1` when close-to-close return is above `0.2%` (`THRESHOLD = 0.002`), otherwise `0`.

AlgoSeek US equity bars are not this schema. Before a sample can be used here, map one row per session onto these names and rewrite the date as `%m/%d/%Y` (session date to `Date`, open/high/low/close to `Open` / `High` / `Low` / `Close/Last`). Do that in a separate file; this script does not rename vendor columns.

## CI

`.github/workflows/smoke.yml` runs on pull requests and on pushes to `main`. On `ubuntu-latest` with Python 3.12 it installs the pinned requirements, byte-compiles `moe_lstm.py`, and trains one epoch on `tests/fixtures/tiny_bars.csv`.

The same three steps locally, from a repo checkout with the venv above activated:

```bash
python -m pip install -r requirements.txt
python -m py_compile moe_lstm.py
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg python moe_lstm.py
```

`tests/fixtures/tiny_bars.csv` is a synthetic 120-row series (alternating up and down days) in the column contract above. It only checks that the script can load, fit, and print metrics. It is not market data, and leaving `MOE_EPOCHS` unset still trains for 50 epochs.

The TensorFlow wheel is large. The workflow allows 30 minutes. A finished run still prints `Pandas4Warning` (`DataFrame` `inplace` is deprecated ahead of pandas 4) and the non-interactive canvas warning. Neither fails the job. If a GitHub-hosted runner cannot install or import TensorFlow, run the three commands above on a machine that can; `py_compile` does not import TensorFlow, and the smoke step does.
