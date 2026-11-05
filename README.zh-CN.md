[English](README.md) | **简体中文**

# MoE-LSTM

面向指数点位的隔日涨跌模型（脚本是为标普 500 编写的）。它构造技术特征，用 K-Means 与自组织映射（self-organizing map）挑选特征子集，训练 LSTM 混合专家（mixture-of-experts）模型，并打印相对买入持有（buy-and-hold）的多空回测。

## 安装

已在 Python 3.12、仅 CPU 的 TensorFlow 安装上检查过。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` 只给出版本下界。2026-11-05 的一次全新解析安装了 TensorFlow 2.21.0、pandas 3.1.1 和 scikit-learn 1.9.1。

## 运行

本仓库不含行情数据。默认 URL（`runchengxie/quant_practice_3` 的 `historical_data.csv`）返回 HTTP 404，因此请把脚本指向本地文件：

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py
```

`MPLBACKEND=Agg` 用来避免无头环境下的 `FigureCanvasAgg` 警告。脚本仍会调用 `plt.show()`。

训练会跑四次（手工特征、K-Means 子集、SOM 子集，然后再跑一次手工特征集），每次最多 50 个 epoch，并使用早停（patience 为 5）。在较小的 CPU 上这需要数分钟，它不是一个打包好的命令行工具。

## CSV 约定

必需列。多余列会被忽略。

| 列 | 规则 |
| --- | --- |
| `Date` | 仅按 `format="%m/%d/%Y"` 解析，例如 `01/13/2020`。ISO 日期会失败。 |
| `Close/Last` | 数值型收盘价。指标、标签和回测都使用这一列。 |
| `Open` | 数值。 |
| `High` | 数值。 |
| `Low` | 数值。 |

价格字段必须已经是数字。`$` 前缀或千分位分隔符会使滚动计算出错。脚本按 `Date` 排序，丢弃指标无法填充的行，并在收盘到收盘收益率高于 `0.2%`（`THRESHOLD = 0.002`）时把下一交易日标为 `1`，否则标为 `0`。

AlgoSeek 美国股票行情条并不是这一 schema。样本要在这里使用之前，需要把每个交易日映射成一行并改写成这些列名，同时把日期写成 `%m/%d/%Y`（交易日日期对应 `Date`，开/高/低/收对应 `Open` / `High` / `Low` / `Close/Last`）。请在单独的文件里完成；本脚本不会重命名供应商列。
