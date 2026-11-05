**English** | [简体中文](README.zh-CN.md)

# MoE-LSTM

Daily next-day up/down model for an index level (the script was written for the S&P 500). It builds technical features, picks feature subsets with K-Means and a self-organizing map, trains an LSTM mixture-of-experts, and prints a long/short backtest against buy-and-hold.

## Setup

Checked on Python 3.12 with a CPU-only TensorFlow install.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` is lower bounds only. A fresh resolve on 2026-11-05 installed TensorFlow 2.21.0, pandas 3.1.1, and scikit-learn 1.9.1.

## Run

Market data is not in this repo. The default URL (`runchengxie/quant_practice_3` `historical_data.csv`) returns HTTP 404, so point the script at a local file:

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py
```

`MPLBACKEND=Agg` avoids a headless `FigureCanvasAgg` warning. The script still calls `plt.show()`.

Training runs four times (manual features, K-Means subset, SOM subset, then the manual set again), up to 50 epochs each with early stopping (patience 5). On a small CPU this is several minutes, not a packaged CLI.

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
