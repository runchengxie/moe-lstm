[English](training.md) | 简体中文

# 训练和回测

本文与英文文档描述同一套行为，事实以英文和代码为准。

[项目说明](../README.zh-CN.md) · [数据](data.zh-CN.md) · [环境](setup.zh-CN.md) · [CI 和项目站点](ci.zh-CN.md)

列名，以及文件如何变成日线，写在 [数据](data.zh-CN.md)。

## 显示和 epoch

使用 Agg 后端时，脚本把图画出后关闭，不调用 `plt.show()`，因此不会出现无显示画布警告。只有交互式后端才会调用 `plt.show()`。

一次运行训练三个模型。它们是手工特征、K-Means 子集、SOM 子集。每个模型的批大小是 16，早停耐心为 5。`MOE_EPOCHS` 用来改 epoch 数。未设置时每个模型训练 50 个 epoch。批大小和耐心不变。任务损失是 binary crossentropy。门控写在下一节。在较小的 CPU 上，50 个 epoch 通常要几分钟。特征选择的随机种子是固定的，LSTM 训练不能逐位复现。在 Python 里调用 `moe_lstm.main(epochs=1)` 是同一种覆盖。显式传入的参数优先于 `MOE_EPOCHS`。

## 门控

每个模型有三个 LSTM 专家。第 `i` 个专家是 `LSTM(64, return_sequences=True)`，名字是 `LSTM_Expert_i`，然后展平。三个专家读同一段窗口，差别来自初始化和学到的路由。专家是 LSTM。门控只读最后一根。

路由是名为 `Gating_Network` 的 dense softmax，宽度是专家个数 3。

研究脚本的默认门控是稀疏 top-1（`TOP_K = 1`）。选中的专家留下，另外两个权重正好是 0。留下的路由概率会重新归一，使它们的和为 1。top-1 时这个权重就是 1。加权求和用的是这些权重。然后 sigmoid 把和映射成概率，阈值仍是 0.5。

`MOE_TOP_K` 用来改保留的个数。`2` 留两个专家，并把这两个路由概率重新归一。`dense`、`all` 或 `none` 保留全部 softmax 权重。在 Python 里，`build_moe_model(..., top_k=None)` 是稠密路径，`top_k=2` 是留两个专家。`train_and_predict_moe(..., top_k=None)` 对其中一次训练做同样的选择。显式传入的参数优先于 `MOE_TOP_K`。`top_k` 只能是 1 或 2。其他值会报错。专家仍是 LSTM。门控只读最后一根。

稀疏路径上，训练额外加一项 Switch 式的负载均衡。`P` 是每个专家的平均路由概率。`f` 是 top-k 包含该专家的窗口占比。这一项是 `n_experts * sum(f_i * P_i)`，再乘以 `AUX_LOSS_WEIGHT = 0.01`。它用 `add_loss` 挂上，所以模型仍然只有一个 sigmoid 输出，`predict` 仍是回测用的概率。`MOE_AUX_LOSS=0` 关掉这一项。稠密路径不加它。稠密路径再配一个正的辅助系数会报错。

设置了 `MOE_RESULTS_DIR` 时，运行还会写出 `metrics.csv`（打印的那张表）、`equity.csv`（Manual、KMeans、SOM，以及不扣费用的买入持有）、`buy_and_hold.csv`，以及图 `close.png`、`correlation.png`、`confusion.png`、`equity.png`、`daily_returns.png`。打印的表仍然只有 Manual、KMeans、SOM。那个买入持有文件的费用是 0。买入持有没有单独训练。

## 样本、缩放和回测

`LOOKBACK = 5`。去掉暖机行之后，窗口数是 `n_rows - 5`。前 80% 的窗口是训练段，后 20% 是测试段，按时间切分。训练段的最后 20% 用作早停验证，至少留一个验证窗口。

`MinMaxScaler` 只在拟合窗口用到的特征行上拟合。K-Means（`N_CLUSTERS = 5`，`random_state=42`，`n_init=10`）和 3×3 的 SOM（`sigma=0.5`，学习率 `0.5`，100 次迭代，`random_seed=42`）只看这一段缩放后的数据。每个模型再对自己的特征子集做同一切片上的缩放。相关热力图只用于查看，仍然使用全样本。

手工特征按这个顺序。

`Close/Last`、`MA5`、`MA10`、`EMA5`、`EMA10`、`RSI`、`BB_upper`、`BB_lower`、`MACD`、`Signal_line`、`Daily_Return`、`Volatility`、`Open`、`High`、`Low`。

RSI 是 14 日简单平均。一段里既没有上涨也没有下跌时取 50，没有下跌时取 100。布林带用 20 日均值和 2 倍标准差（pandas 的样本标准差）。MACD 是 12/26 EMA 之差，信号线是 9 日 EMA。K-Means 和 SOM 选出的列取决于拟合切片。

测试集预测落在它所预测的那一行标签上。预测 `1` 做多（`+1`）。预测 `0` 空仓（`0`）。sigmoid 阈值是 `0.5`。类别 `0` 是没有超过阈值的向前收益，里面有小涨。仓位记成空仓。持有多头时，仓位赚取该行的 `Tomorrow_Change`，也就是当根收盘到下一根收盘的收益，和标签用的是同一段。该行的 `Daily_Return` 在当根收盘时已经实现。

交易日 `t` 的标签，从 `t` 到 `t+1` 的收盘收益高于 0.2%（`THRESHOLD = 0.002`）时记 `1`。等于 0.2% 时记 `0`。更低的收益也记 `0`。

`LOOKBACK = 5` 时，窗口 `i` 使用特征行 `i` 到 `i+4`。标签是第 `i+5` 行。这五行在第 `i+4` 行收盘时已经知道。标签对应的收益从第 `i+5` 行收盘开始，到第 `i+6` 行收盘结束。窗口不含这两个收盘。回测在标签行的收盘价成交，赚取下一根的这段收益。早停用更后面、形状相同的窗口。`MinMaxScaler`、K-Means 和 SOM 只看到拟合窗口的特征行。这些行停在最后一个拟合窗口的最后一根，也就是该窗口标签行的前一根。

每次运行写出 `oos_probabilities.csv`，路径可用 `MOE_OOS_CSV` 改。列是测试窗口的 `Date`、`Model`、`Probability`、`Prediction`，三个模型都在同一张表里。`Probability` 是 sigmoid 分数。分数高于 `0.5` 时 `Prediction` 为 1。

默认费用是每单位换手 `0.0005` 的收益率。第一根测试 K 线之前账户是空仓，净值是 1，所以开多仓成本是 `0.0005`。从多头回到空仓同样收一次 `0.0005`。一直空仓不赚收益，也不付费用。买入持有是同一组向前收益的累计乘积，不扣费用。

总收益是期末净值减 1。最大回撤的累计峰值至少是起始的 1，之后再取更高的净值。多头连续两根 `-10%`，不扣费用，期末净值是 `0.81`，最大回撤是 `-19%`。向前收益为 0 时，开仓费用本身也是相对 1 的回撤。夏普率是策略收益的均值除以样本标准差，再乘以 `sqrt(252)`。这个年化假设每根 K 线对应一个交易日。如果日期间隔的中位数不在 1 到 3 天之内，脚本会打印警告，夏普率的算法不变。策略收益为常数时，夏普率是 `NaN`。测试标签只有一个类别时，AUC 是 `NaN`，其余分类指标使用 `zero_division=0`。混淆矩阵的轴写成 Not above 和 Above。

输出列是 `Model`、`Accuracy`、`Precision`、`Recall`、`F1`、`AUC-ROC`、`Total Return`、`Max Drawdown`、`Sharpe Ratio`，模型名为 `Manual`、`KMeans`、`SOM`。

quant-backtest-engine 的成交和账本是另一条路径。运行方式写在 [引擎回测](engine.zh-CN.md)。
