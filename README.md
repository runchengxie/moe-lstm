# MoE-LSTM

中文说明：[README.zh-CN.md](README.zh-CN.md).

Daily next-session up/down model for an index level. The script was written for the S&P 500. It builds technical features, picks feature subsets with K-Means and a self-organizing map, trains an LSTM mixture of experts on each subset, and prints a long/short backtest against buy and hold.

The three LSTM experts read the same window. They differ by initialization and by the learned gate. The script prints class counts and does not resample.

## Setup

Checked on Python 3.12.

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

Keras is pinned because TensorFlow 2.21.0 only requires `keras>=3.12`. Exact pins keep a later pandas 4 or a newer numpy from being selected on a fresh install. K-Means sets `n_init=10` because scikit-learn 1.4 changed the default to `auto`.

## Run

Market data is not in this repo. The default URL is `runchengxie/quant_practice_3` `historical_data.csv`. On 2026-11-05 that URL returned HTTP 404, so point the script at a local file:

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py
```

There is no argument parser. `MOE_DATA_CSV` is the only data setting. When it is unset, the script reads `DEFAULT_DATA_URL`. `MOE_DATA_CSV` may be a local path or any URL `pandas.read_csv` can open.

With the Agg backend the script draws the figures and closes them, so `plt.show()` is not called and the headless canvas warning is not raised. An interactive backend still calls `plt.show()`.

Training fits three models (manual features, the K-Means subset, and the SOM subset). Each run uses batch size 16 and early stopping with patience 5. `MOE_EPOCHS` overrides the epoch count. Unset, each run uses 50 epochs. The network, loss, batch size, and patience do not change. On a small CPU a 50-epoch run is several minutes. Feature selection uses fixed seeds. LSTM training is not bitwise reproducible. From Python, `moe_lstm.main(epochs=1)` is the same override. An explicit argument wins over `MOE_EPOCHS`.

## Tests

```bash
python -m unittest discover -s tests -t . -v
```

Loading, labels, the split, and the backtest do not import TensorFlow. `tests/test_model.py` builds the mixture and runs `main(epochs=1)` when TensorFlow is installed, and skips otherwise.

## CI

`.github/workflows/tests.yml` runs the unittest command above on pull requests and on pushes to `main`, on `ubuntu-latest` with Python 3.12, after installing the pinned requirements.

`.github/workflows/smoke.yml` runs on those same events. It installs the same pins, byte-compiles `moe_lstm.py`, and trains one epoch on `tests/fixtures/tiny_bars.csv`:

```bash
python -m pip install -r requirements.txt
python -m py_compile moe_lstm.py
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg python moe_lstm.py
```

`tests/fixtures/tiny_bars.csv` is a synthetic 120-row series in this column contract. It checks that the script can load, fit, and print metrics. It is not market data. The smoke workflow allows 30 minutes for the TensorFlow wheel. If a GitHub-hosted runner cannot install TensorFlow, run the three commands on a machine that can. `py_compile` does not import TensorFlow. A finished run can still print TensorFlow retracing warnings, because each feature set builds its own model. It does not print a non-interactive canvas warning.

## CSV contract

Required columns. Extra columns stay in the preview print and are not features. Missing values in extra columns do not drop sessions.

| Column | Rule |
| --- | --- |
| `Date` | Parsed with `format="%m/%d/%Y"`, for example `01/13/2020` or `1/13/2020`. ISO dates such as `2020-01-13` fail. Values must be unique. The preview and the model both use date order. |
| `Close/Last` | Finite and positive. Indicators, the label, and the backtest use this column. |
| `Open` | Finite number. Used as a feature. |
| `High` | Finite number. Used as a feature. |
| `Low` | Finite number. Used as a feature. |

Price fields must already be numbers. A `$` prefix or a thousands separator is rejected. The script then drops the leading rows that the 20-session rolling indicators cannot fill, and drops the last row because the next close is unknown. A file needs at least 28 sessions before the fit, validation, and test windows can all be non-empty.

The label on session `t` is `1` when the close-to-close return from `t` to `t+1` is above `0.2%` (`THRESHOLD = 0.002`). A return equal to `0.2%` is `0`.

AlgoSeek US equity bars are not this schema. Map one row per session onto these names in a separate file and write the date as `%m/%d/%Y` (session date to `Date`, open, high, low, and close to `Open`, `High`, `Low`, and `Close/Last`). This script does not rename vendor columns.

## Sample, scaling, and backtest

`LOOKBACK = 5`. The number of windows is `n_rows - 5` after warmup. The first 80% of windows are the training block and the last 20% are the test block. The split is chronological. The last 20% of the training block is the early-stopping validation set, with at least one validation window.

`MinMaxScaler` is fit on the feature rows that belong to the fit windows. K-Means (`N_CLUSTERS = 5`, `random_state=42`, `n_init=10`) and the 3 by 3 SOM (`sigma=0.5`, learning rate `0.5`, 100 iterations, `random_seed=42`) see only that scaled slice. Each model scales its own feature subset on the same slice. The correlation heatmap is descriptive and still uses the full sample.

Manual features, in order:

`Close/Last`, `MA5`, `MA10`, `EMA5`, `EMA10`, `RSI`, `BB_upper`, `BB_lower`, `MACD`, `Signal_line`, `Daily_Return`, `Volatility`, `Open`, `High`, `Low`.

RSI is a 14-session simple average. A window with no gain and no loss is 50. A window with no losses is 100. Bollinger bands use the 20-session mean and a 2-standard-deviation band (pandas sample standard deviation). MACD is the 12/26 EMA difference and a 9-session signal. K-Means and SOM subsets depend on the fit slice.

A test prediction is attached to the row whose label it predicts. Prediction `1` is long (`+1`) and `0` is short (`-1`), using a sigmoid threshold of `0.5`. The position earns that row's `Tomorrow_Change`, the close-to-close return from that session to the next, which is the return the label used. It does not earn `Daily_Return` on that row.

The default fee is `0.0005` return units per unit of position turnover. The account is flat before the first test bar, so the opening position costs `0.0005`. A flip from long to short changes position by 2 and costs `0.001`. Holding a position costs nothing. Buy and hold is the uncosted cumulative product of the same forward returns.

Total return is final equity minus 1. Max drawdown is the minimum of `equity / running_peak - 1` and is zero or negative. Sharpe ratio is the mean strategy return divided by its sample standard deviation, times `sqrt(252)`. That scaling assumes one bar per trading session. If the median gap between dates is outside 1 to 3 days, the script prints a warning and still reports the same ratio. A constant strategy return has Sharpe `NaN`. If the test labels contain one class, AUC is `NaN` and the other classification scores use `zero_division=0`.

Reported columns are `Model`, `Accuracy`, `Precision`, `Recall`, `F1`, `AUC-ROC`, `Total Return`, `Max Drawdown`, and `Sharpe Ratio` for `Manual`, `KMeans`, and `SOM`.
