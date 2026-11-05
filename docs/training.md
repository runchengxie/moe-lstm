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

A test prediction is attached to the row whose label it predicts. Prediction `1` is long (`+1`) and `0` is short (`-1`), using a sigmoid threshold of `0.5`. The position earns that row's `Tomorrow_Change`, the close-to-close return from that session to the next, which is the return the label used. It does not earn `Daily_Return` on that row.

The label on session `t` is `1` when the close-to-close return from `t` to `t+1` is above `0.2%` (`THRESHOLD = 0.002`). A return equal to `0.2%` is `0`.

The default fee is `0.0005` return units per unit of position turnover. The account is flat before the first test bar, so the opening position costs `0.0005`. A flip from long to short changes position by 2 and costs `0.001`. Holding a position costs nothing. Buy and hold is the uncosted cumulative product of the same forward returns.

Total return is final equity minus 1. Max drawdown is the minimum of `equity / running_peak - 1` and is zero or negative. Sharpe ratio is the mean strategy return divided by its sample standard deviation, times `sqrt(252)`. That scaling assumes one bar per trading session. If the median gap between dates is outside 1 to 3 days, the script prints a warning and still reports the same ratio. A constant strategy return has Sharpe `NaN`. If the test labels contain one class, AUC is `NaN` and the other classification scores use `zero_division=0`.

Reported columns are `Model`, `Accuracy`, `Precision`, `Recall`, `F1`, `AUC-ROC`, `Total Return`, `Max Drawdown`, and `Sharpe Ratio` for `Manual`, `KMeans`, and `SOM`.
