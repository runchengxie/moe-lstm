[English](engine.md) | 简体中文

# 引擎回测

[项目说明](../README.zh-CN.md) · [训练和回测](training.zh-CN.md) · [数据](data.zh-CN.md)

脚本打印的结果来自 `moe_lstm.backtest`。预测 `1` 是仓位 `+1`。预测 `0` 是仓位 `0`，空仓。引擎权重用同一套映射。

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) 是另一个程序。Python 客户端是 `quant_backtest_engine.EngineClient`。`size` 把非负目标权重收成股数计划。`run_sessions` 按你给的报价提交你给的订单，再返回成交、费用和日度账本。账记在那个程序里。

## 权重

`moe_lstm.signals.long_only_target_weights` 把研究信号映射成引擎的只做多约定：

| 研究预测 | 进程内仓位 | 引擎目标权重 |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0`（空仓） | `"0"` |

权重是非负的。一个标的的权重最多是 1。`sizing_request_for_signal` 造一份 `sizing_request.v1`。参考价是十进制字符串，时间戳早于或等于信息时间。`session_request_for_order` 围着一笔已经有的订单造一份 `engine_request.v2`。这笔订单可以是 `size` 返回的。请求里的报价就是传进去的字符串。仓库里没有配套的供应商报价文件。

## 运行

从引擎仓库的检出安装客户端。可执行文件按那个仓库的说明构建，并用你核对过的 SHA256 钉住。

```bash
uv pip install /path/to/quant-backtest-engine/python
```

示例送出一个你选定的信号。LSTM 留着不训练。`MOE_SIGNAL` 就是这个开关。默认现金和价格是示例里的字符串。引擎路径空着时，脚本打印 sizing 请求后停下。

```bash
uv run python examples/engine_backtest.py
```

要引擎给出计划，计划里有订单时再跑成交。

```bash
export QUANT_ENGINE_BINARY=/absolute/path/to/quant-backtest-engine
export QUANT_ENGINE_SHA256=the-lowercase-sha256-of-that-file
uv run python examples/engine_backtest.py
```

`run_sizing` 和 `run_sessions` 调用 `EngineClient.size` 和 `EngineClient.run_sessions`。打印出来的 `marked_equity`、`projected_cash`、`final_cash`、`final_nav`、`total_commission` 和成交笔数是引擎的 JSON。这份说明把那些数字留在引擎那边。项目站点的指标格子空着。
