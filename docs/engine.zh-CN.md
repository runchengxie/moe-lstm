[English](engine.md) | 简体中文

# 引擎回测

[项目说明](../README.zh-CN.md) · [训练和回测](training.zh-CN.md) · [数据](data.zh-CN.md)

`moe_lstm.backtest` 打印进程里的结果。预测 `1` 是仓位 `+1`。预测 `0` 是仓位 `0`，空仓。引擎权重用同一套映射。

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) 是另一个程序。`EngineClient.size` 把非负权重收成股数计划。`EngineClient.run_sessions` 按你给的报价提交这些订单，再返回成交、费用和日度账本。

| 研究预测 | 进程内仓位 | 引擎目标权重 |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0` | `"0"` |

`sizing_request_for_signal` 造一份 `sizing_request.v1`。`session_request_for_order` 围着一笔已有的订单造一份 `engine_request.v2`。示例送出一个你选定的信号，LSTM 留着不训练。

```bash
uv pip install /path/to/quant-backtest-engine/python
uv run python examples/engine_backtest.py
```

设了 `QUANT_ENGINE_BINARY` 和 `QUANT_ENGINE_SHA256` 之后，脚本调用 `size`。计划里有订单时再调用 `run_sessions`。打印出来的字段是引擎的 JSON。这份说明把那些数字留在引擎那边。项目站点记下了一次研究脚本自己的回测，不印这份引擎账本。
