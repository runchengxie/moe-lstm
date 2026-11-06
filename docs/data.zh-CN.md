[English](data.md) | 简体中文

# 数据

本文与英文文档描述同一套行为，事实以英文和代码为准。

[项目说明](../README.zh-CN.md) · [训练和回测](training.zh-CN.md) · [环境](setup.zh-CN.md) · [CI 和项目站点](ci.zh-CN.md)

主输入是 Hive 分钟线。未设置 Parquet 根目录时，回退到日频 CSV。真实行情不放进本仓库。

## 环境变量

没有命令行参数。

| 变量 | 作用 |
| --- | --- |
| `MOE_DATA_PARQUET` | Hive 数据集根目录。设置之后，数据来自这个根目录，并且优先于 `MOE_DATA_CSV`。路径可以是数据集根目录，也可以直接是 `parquet/` 目录。 |
| `MOE_SYMBOL` | Ticker（`symbol=`）。 |
| `MOE_SECURITY` | 同一个 ticker 有多个 `security=` 哈希时再设置。只有一个哈希时会自动选中。 |
| `MOE_DATA_CSV` | 本地路径，或 `pandas.read_csv` 能打开的 URL。只在未设置 `MOE_DATA_PARQUET` 时使用。这个也未设置时，脚本读取 `DEFAULT_DATA_URL`。 |

默认地址是 `runchengxie/quant_practice_3` 的 `historical_data.csv`。2026-11-05 访问该地址返回 HTTP 404，2026-11-06 再查仍是 404。用 CSV 时要指向本地文件。

## Parquet 分钟线

把 `MOE_DATA_PARQUET` 设为处理后的美股逐笔报价分钟线数据集根目录，目录形如下面这样。

```text
parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet
```

`MOE_SYMBOL` 是 ticker（`symbol=`）。同一个 ticker 有多个 `security=` 哈希时再设置 `MOE_SECURITY`。只有一个哈希时会自动选中。脚本读取每个 `year=` 文件，保留 `AuditSession == regular` 的行，并丢掉成交价为空的分钟（没有成交）。其余分钟按 `TimeBarStart` 排序（文件里只有成交时间时用 `FirstTradeTime`），再按日历日聚成一行。

| 分钟字段 | 日线列 |
| --- | --- |
| 当天第一笔 `FirstTradePrice` | `Open` |
| `HighTradePrice` 的最大值 | `High` |
| `LowTradePrice` 的最小值 | `Low` |
| 当天最后一笔 `LastTradePrice` | `Close/Last` |
| `Volume` 之和 | `Volume` |

文件里的 `Date` 是 `YYYYMMDD`。聚合后是 datetime。`Volume` 留在表上，不作为模型特征。指标、标签和回测与解析后的 CSV 走同一段代码。

```bash
export MOE_DATA_PARQUET=/path/to/dataset-root
export MOE_SYMBOL=AAPL
# export MOE_SECURITY=your-hash   # 同一 ticker 有多个 security 时才需要
export MPLBACKEND=Agg
uv run moe-lstm
```

`MOE_DATA_PARQUET` 也可以直接指向 `parquet/` 目录。

```bash
uv run python -m unittest tests.test_hive_daily_bars
```

这个检查会建一棵合成的 Hive 目录并比较日线 OHLCV，不需要 TensorFlow。`.github/workflows/parquet-loader.yml` 在 pull request 上，以及向 `main` 的 push 上运行它，并用 uv 只安装 pandas 和 pyarrow。这条工作流也列在 [CI 和项目站点](ci.zh-CN.md)。下面的 CSV 约定只用于 `MOE_DATA_CSV`。

## CSV 约定

必填列如下。其余列只出现在开头的预览里，不作为特征。额外列中的空值不会删除行情行。

| 列 | 规则 |
| --- | --- |
| `Date` | 只用 `format="%m/%d/%Y"` 解析，例如 `01/13/2020` 或 `1/13/2020`。`2020-01-13` 这种 ISO 日期会失败。日期必须唯一。预览和模型都按日期顺序。 |
| `Close/Last` | 有限且为正。指标、标签和回测都用这一列。 |
| `Open` | 有限数值。作为特征。 |
| `High` | 有限数值。作为特征。 |
| `Low` | 有限数值。作为特征。 |

价格必须已经是数字。带 `$` 或千分位分隔符会被拒绝。随后脚本丢掉 20 日滚动指标填不满的前导行，并丢掉最后一行，因为下一根收盘未知。文件至少要有 28 根 K 线，拟合、验证和测试窗口才能同时非空。

交易日 `t` 的标签看从 `t` 到 `t+1` 的收盘收益率。高于 `0.2%`（`THRESHOLD = 0.002`）时为 `1`，否则为 `0`。恰好等于 `0.2%` 时为 `0`。切分和回测里怎么用这个标签，写在 [训练和回测](training.zh-CN.md)。

AlgoSeek 美股 bar 用另一套列名。在单独的文件里，把每个交易日写成这五列，日期用 `%m/%d/%Y`。交易日写成 `Date`，开、高、低、收写成 `Open`、`High`、`Low`、`Close/Last`。脚本留下供应商原来的列名。

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
uv run moe-lstm
```
