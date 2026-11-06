**English** | [简体中文](data.zh-CN.md)

# Data

[Project README](../README.md) · [Training and backtest](training.md) · [Setup](setup.md) · [CI and the project site](ci.md)

Hive minute bars are the primary input. A daily CSV is the fallback when the Parquet root is not set. Market data is not in this repo.

## Environment variables

There is no argument parser.

| Variable | Role |
| --- | --- |
| `MOE_DATA_PARQUET` | Hive dataset root. When it is set, that root is the data source and it wins over `MOE_DATA_CSV`. The path may be the dataset root or the `parquet/` directory itself. |
| `MOE_SYMBOL` | Ticker (`symbol=`). |
| `MOE_SECURITY` | Set when that ticker has more than one `security=` hash. If there is only one hash, it is selected for you. |
| `MOE_DATA_CSV` | Local path or any URL `pandas.read_csv` can open. Used when `MOE_DATA_PARQUET` is unset. When this is also unset, the script reads `DEFAULT_DATA_URL`. |

The default URL is `runchengxie/quant_practice_3` `historical_data.csv`. On 2026-11-05 that URL returned HTTP 404, and it still did on 2026-11-06, so point the script at a local file for CSV.

## Parquet minute bars

Set `MOE_DATA_PARQUET` to the dataset root that contains the processed US-equities trade-and-quote minute-bar release:

```text
parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet
```

`MOE_SYMBOL` is the ticker (`symbol=`). Set `MOE_SECURITY` when that ticker has more than one `security=` hash. If there is only one hash, it is selected for you. The script reads every `year=` file, keeps rows with `AuditSession == regular`, and drops minutes whose trade prices are blank (no trades). Remaining minutes are ordered by `TimeBarStart` (`FirstTradeTime` if that is the only clock) and rolled up to one row per calendar date.

| Minute field | Daily column |
| --- | --- |
| first `FirstTradePrice` of the day | `Open` |
| max `HighTradePrice` | `High` |
| min `LowTradePrice` | `Low` |
| last `LastTradePrice` of the day | `Close/Last` |
| sum of `Volume` | `Volume` |

`Date` in the file is `YYYYMMDD`. After aggregation it is a datetime. `Volume` stays on the frame and is not a model feature. Indicators, the label, and the backtest then use the same code as a parsed CSV.

```bash
export MOE_DATA_PARQUET=/path/to/dataset-root
export MOE_SYMBOL=AAPL
# export MOE_SECURITY=your-hash   # only when several securities share the ticker
export MPLBACKEND=Agg
uv run moe-lstm
```

The loader also accepts `MOE_DATA_PARQUET` pointed at the `parquet/` directory itself. Real market files stay outside this repo. When `MOE_DATA_PARQUET` is set it wins over `MOE_DATA_CSV`.

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

That check builds a synthetic Hive tree and compares the daily OHLCV. It does not need TensorFlow. [`.github/workflows/parquet-loader.yml`](../.github/workflows/parquet-loader.yml) runs it on pull requests and on pushes to `main`, using uv to install pandas and pyarrow only. That workflow is also listed in [CI and the project site](ci.md). The CSV contract below applies only to `MOE_DATA_CSV`.

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

The label on session `t` is `1` when the close-to-close return from `t` to `t+1` is above `0.2%` (`THRESHOLD = 0.002`). A return equal to `0.2%` is `0`. How that label is used in the split and the backtest is in [Training and backtest](training.md).

AlgoSeek US equity bars are not this schema. Map one row per session onto these names in a separate file and write the date as `%m/%d/%Y` (session date to `Date`, open, high, low, and close to `Open`, `High`, `Low`, and `Close/Last`). This script does not rename vendor columns.

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
uv run moe-lstm
```
