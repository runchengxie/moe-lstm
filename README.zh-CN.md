# MoE-LSTM

英文说明：[README.md](README.md)。本文与英文文档描述同一套行为，事实以英文和代码为准。

这是一个日频模型，用来判断指数下一根 K 线的收盘相对当根收盘是否上涨。脚本最初按标普 500 编写。它计算技术指标，用 K-Means 和自组织映射挑选特征子集，对每个子集训练一个 LSTM 混合专家，并打印多空回测与买入持有的对比。

三个 LSTM 专家读取同一段窗口，差别来自初始化和学到的门控权重。脚本只打印类别数量，不做重采样。

## 环境

在 Python 3.12 上核对过。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` 锁定 2026-11-05 在 Python 3.12 上能干净安装的版本：

| 包 | 版本 |
| --- | --- |
| tensorflow | 2.21.0 |
| keras | 3.15.1 |
| pandas | 3.1.1 |
| numpy | 2.5.4 |
| scikit-learn | 1.9.1 |
| minisom | 2.3.6 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |

Keras 单独锁定，是因为 TensorFlow 2.21.0 只要求 `keras>=3.12`。精确版本避免以后一次全新安装选到 pandas 4 或更新的 numpy。K-Means 显式使用 `n_init=10`，因为 scikit-learn 1.4 把默认值改成了 `auto`。

## 运行

仓库里没有行情。默认地址是 `runchengxie/quant_practice_3` 的 `historical_data.csv`。2026-11-05 访问该地址返回 HTTP 404，所以要指向本地文件：

```bash
export MOE_DATA_CSV=/path/to/bars.csv
export MPLBACKEND=Agg
python moe_lstm.py
```

没有命令行参数。数据只看环境变量 `MOE_DATA_CSV`。未设置时读取 `DEFAULT_DATA_URL`。该变量可以是本地路径，也可以是 `pandas.read_csv` 能打开的 URL。

使用 Agg 后端时，脚本把图画出后关闭，不调用 `plt.show()`，因此不会出现无显示画布警告。只有交互式后端才会调用 `plt.show()`。

一次运行训练三个模型：手工特征、K-Means 子集、SOM 子集。每个模型的批大小是 16，早停耐心为 5。`MOE_EPOCHS` 用来改 epoch 数。未设置时每个模型训练 50 个 epoch。网络、损失、批大小和耐心不变。在较小的 CPU 上，50 个 epoch 通常要几分钟。特征选择的随机种子是固定的，LSTM 训练不能逐位复现。在 Python 里调用 `moe_lstm.main(epochs=1)` 是同一种覆盖。显式传入的参数优先于 `MOE_EPOCHS`。

## 测试

```bash
python -m unittest discover -s tests -t . -v
```

加载、标签、切分和回测不会导入 TensorFlow。安装了 TensorFlow 时，`tests/test_model.py` 会构建混合专家并执行 `main(epochs=1)`。未安装时这些测试跳过。

## CI

`.github/workflows/tests.yml` 在 pull request 上，以及向 `main` 的 push 上，运行上面的 unittest。环境是 `ubuntu-latest` 和 Python 3.12，先安装锁定的依赖。

`.github/workflows/smoke.yml` 在同样的事件上运行。它安装同一套版本，对 `moe_lstm.py` 做字节编译，并用 `tests/fixtures/tiny_bars.csv` 训练一个 epoch：

```bash
python -m pip install -r requirements.txt
python -m py_compile moe_lstm.py
MOE_DATA_CSV=tests/fixtures/tiny_bars.csv MOE_EPOCHS=1 MPLBACKEND=Agg python moe_lstm.py
```

`tests/fixtures/tiny_bars.csv` 是符合上述列约定的 120 行合成序列，用来确认脚本能加载、拟合并打印指标。它不是真实行情。这条 workflow 给 TensorFlow 安装留了 30 分钟。如果 GitHub 托管 runner 装不上 TensorFlow，就在能安装的机器上跑这三条命令。`py_compile` 不会导入 TensorFlow。跑完后仍可能看到 TensorFlow 的 retracing 警告，因为每个特征子集都会单独建一个模型。不会再出现无显示画布警告。

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

交易日 `t` 的标签：从 `t` 到 `t+1` 的收盘收益率高于 `0.2%`（`THRESHOLD = 0.002`）时为 `1`，否则为 `0`。恰好等于 `0.2%` 时为 `0`。

AlgoSeek 的美股 bar 不是这个表结构。请在单独的文件里把每个交易日映射成这些列名，并把日期写成 `%m/%d/%Y`（交易日写成 `Date`，开、高、低、收写成 `Open`、`High`、`Low`、`Close/Last`）。本脚本不会重命名供应商列名。

## 样本、缩放和回测

`LOOKBACK = 5`。去掉暖机行之后，窗口数是 `n_rows - 5`。前 80% 的窗口是训练段，后 20% 是测试段，按时间切分。训练段的最后 20% 用作早停验证，至少留一个验证窗口。

`MinMaxScaler` 只在拟合窗口用到的特征行上拟合。K-Means（`N_CLUSTERS = 5`，`random_state=42`，`n_init=10`）和 3×3 的 SOM（`sigma=0.5`，学习率 `0.5`，100 次迭代，`random_seed=42`）只看这一段缩放后的数据。每个模型再对自己的特征子集做同一切片上的缩放。相关热力图只用于查看，仍然使用全样本。

手工特征按这个顺序：

`Close/Last`、`MA5`、`MA10`、`EMA5`、`EMA10`、`RSI`、`BB_upper`、`BB_lower`、`MACD`、`Signal_line`、`Daily_Return`、`Volatility`、`Open`、`High`、`Low`。

RSI 是 14 日简单平均。一段里既没有上涨也没有下跌时取 50，没有下跌时取 100。布林带用 20 日均值和 2 倍标准差（pandas 的样本标准差）。MACD 是 12/26 EMA 之差，信号线是 9 日 EMA。K-Means 和 SOM 选出的列取决于拟合切片。

测试集预测对到它所预测的那一行标签上。预测 `1` 做多（`+1`），`0` 做空（`-1`），sigmoid 阈值是 `0.5`。仓位赚取该行的 `Tomorrow_Change`，也就是当根收盘到下一根收盘的收益率，和标签用的是同一个收益。它不赚取该行的 `Daily_Return`，因为那个收益在当根收盘时已经实现。

默认费用是每单位换手 `0.0005` 的收益率。第一根测试 K 线之前视为空仓，所以开仓成本是 `0.0005`。从多头翻到空头，仓位变化为 2，成本是 `0.001`。仓位不变时不收费。买入持有是同一组向前收益的累计乘积，不扣费用。

总收益是期末净值减 1。最大回撤是 `净值 / 累计峰值 - 1` 的最小值，为零或负数。夏普率是策略收益的均值除以样本标准差，再乘以 `sqrt(252)`。这个年化假设每根 K 线对应一个交易日。如果日期间隔的中位数不在 1 到 3 天之内，脚本会打印警告，夏普率的算法不变。策略收益为常数时，夏普率是 `NaN`。测试标签只有一个类别时，AUC 是 `NaN`，其余分类指标使用 `zero_division=0`。

输出列是 `Model`、`Accuracy`、`Precision`、`Recall`、`F1`、`AUC-ROC`、`Total Return`、`Max Drawdown`、`Sharpe Ratio`，模型名为 `Manual`、`KMeans`、`SOM`。
