[English](engine.md) | **简体中文**

# 引擎回测

本文与英文文档描述同一套行为，事实以英文和代码为准。

[项目说明](../README.zh-CN.md) · [训练和回测](training.zh-CN.md) · [数据](data.zh-CN.md)

脚本打印的结果来自 `moe_lstm.backtest`。预测 `1` 是仓位 `+1`，预测 `0` 是仓位 `0`（空仓）。引擎权重用的是同一套映射。

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) 是另一个程序。Python 客户端是 `quant_backtest_engine.EngineClient`。`size` 把非负目标权重变成股数计划。`run_sessions` 用你提供的报价提交订单，并返回成交、费用和日度账本。本仓库不另写一套会计。

## 权重

`moe_lstm.signals.long_only_target_weights` 把研究信号映射成引擎的只做多约定：

| 研究预测 | 进程内仓位 | 引擎目标权重 |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0`（空仓） | `"0"` |

权重非负，单标的权重至多为 1。`sizing_request_for_signal` 构造一份 `sizing_request.v1`。参考价必须是十进制字符串，时间不得晚于信息时间。`session_request_for_order` 围绕一笔已经有的订单构造一份 `engine_request.v2`，订单可以来自 `size`。请求里的报价就是传入的字符串，不是本仓库里的行情文件。

## 运行

从引擎仓库的检出安装客户端。可执行文件按那个仓库的说明构建，并用你核对过的 SHA256 钉住。

```bash
uv pip install /path/to/quant-backtest-engine/python
```

示例不训练 LSTM。`MOE_SIGNAL` 是你设的开关，用来走通这条线。默认的现金和价格也是你给的。不设置引擎路径时，脚本只打印 sizing 请求。

```bash
uv run python examples/engine_backtest.py
```

要引擎给出计划，并在计划里有订单时跑成交：

```bash
export QUANT_ENGINE_BINARY=/absolute/path/to/quant-backtest-engine
export QUANT_ENGINE_SHA256=the-lowercase-sha256-of-that-file
uv run python examples/engine_backtest.py
```

`run_sizing` 和 `run_sessions` 调用 `EngineClient.size` 与 `EngineClient.run_sessions`。打印出来的 `marked_equity`、`projected_cash`、`final_cash`、`final_nav`、`total_commission` 和成交笔数是引擎的 JSON。这份说明不抄那些数字，项目站点也不据此编造夏普率。
