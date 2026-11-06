**English** | [简体中文](training.zh-CN.md)

# Training and backtest

[Project README](../README.md) · [Data](data.md) · [Setup](setup.md) · [CI and the project site](ci.md)

Column names and how a file becomes daily bars are in [Data](data.md).

## Display and epochs

With the Agg backend the script draws the figures and closes them, so `plt.show()` is not called and the headless canvas warning is not raised. An interactive backend still calls `plt.show()`.

Training fits three models (manual features, the K-Means subset, and the SOM subset). Each run uses batch size 16 and early stopping with patience 5. `MOE_EPOCHS` overrides the epoch count. Unset, each run uses 50 epochs. The network, loss, batch size, and patience do not change. On a small CPU a 50-epoch run is several minutes. Feature selection uses fixed seeds. LSTM training is not bitwise reproducible. From Python, `moe_lstm.main(epochs=1)` is the same override. An explicit argument wins over `MOE_EPOCHS`.

## Sample, scaling, and backtest

`LOOKBACK = 5`. The number of windows is `n_rows - 5` after warmup. The first 80% of windows are the training block and the last 20% are the test block. The split is chronological. The last 20% of the training block is the early-stopping validation set, with at least one validation window.

`MinMaxScaler` is fit on the feature rows that belong to the fit windows. K-Means (`N_CLUSTERS = 5`, `random_state=42`, `n_init=10`) and the 3 by 3 SOM (`sigma=0.5`, learning rate `0.5`, 100 iterations, `random_seed=42`) see only that scaled slice. Each model scales its own feature subset on the same slice. The correlation heatmap is descriptive and still uses the full sample.

Manual features, in order:

`Close/Last`, `MA5`, `MA10`, `EMA5`, `EMA10`, `RSI`, `BB_upper`, `BB_lower`, `MACD`, `Signal_line`, `Daily_Return`, `Volatility`, `Open`, `High`, `Low`.

RSI is a 14-session simple average. A window with no gain and no loss is 50. A window with no losses is 100. Bollinger bands use the 20-session mean and a 2-standard-deviation band (pandas sample standard deviation). MACD is the 12/26 EMA difference and a 9-session signal. K-Means and SOM subsets depend on the fit slice.

A test prediction sits on the row whose label it predicts. Prediction `1` is long (`+1`). Prediction `0` is flat (`0`). The sigmoid cutoff is `0.5`. Class `0` is every forward return that did not clear the threshold, small gains included, and the position stays flat. While long, the position earns that row's `Tomorrow_Change`. `Daily_Return` on the same row is already finished at that close.

The label on session `t` is `1` when the close-to-close return from `t` to `t+1` is above `0.2%` (`THRESHOLD = 0.002`). A return equal to `0.2%` is `0`. A lower return is `0` too.

With `LOOKBACK = 5`, window `i` holds feature rows `i` through `i+4`. The label is row `i+5`. Those five rows are known at the close of row `i+4`. The labeled return starts at the close of row `i+5` and ends at the close of row `i+6`. The window does not include those two closes. The backtest fills at the close of the label row and earns that next-session return. Early stopping uses later windows of the same shape. `MinMaxScaler`, K-Means, and the SOM see only the feature rows of the fit windows. Those rows stop on the last bar of the last fit window, the bar before that window's label row.

The run writes `oos_probabilities.csv`, or the path in `MOE_OOS_CSV`. Columns are `Date`, `Model`, `Probability`, and `Prediction` for the test windows of Manual, KMeans, and SOM. `Probability` is the sigmoid score. `Prediction` is 1 when that score is above `0.5`.

The default fee is `0.0005` return units per unit of position turnover. The account is flat before the first test bar, so opening a long costs `0.0005`. Leaving a long for flat costs `0.0005` once. Staying flat earns nothing and pays nothing. Buy and hold is the uncosted cumulative product of the same forward returns.

Total return is final equity minus 1. Equity starts at 1 before the first bar. Max drawdown uses a running peak that is at least that 1, then later equity highs. Two consecutive `-10%` days from a long position, with no fee, finish at `0.81` and the max drawdown is `-19%`. A fee on a zero forward return is a drawdown from 1. Sharpe ratio is the mean strategy return divided by its sample standard deviation, times `sqrt(252)`. That scaling assumes one bar per trading session. If the median gap between dates is outside 1 to 3 days, the script prints a warning and still reports the same ratio. A constant strategy return has Sharpe `NaN`. If the test labels contain one class, AUC is `NaN` and the other classification scores use `zero_division=0`. The confusion-matrix axes read "Not above" and "Above".

Reported columns are `Model`, `Accuracy`, `Precision`, `Recall`, `F1`, `AUC-ROC`, `Total Return`, `Max Drawdown`, and `Sharpe Ratio` for `Manual`, `KMeans`, and `SOM`.

Fills and the ledger for quant-backtest-engine are a separate path. How to run it is in [Engine backtest](engine.md).
