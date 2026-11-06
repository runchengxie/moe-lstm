English | [简体中文](engine.zh-CN.md)

# Engine backtest

[Project README](../README.md) · [Training and backtest](training.md) · [Data](data.md)

`moe_lstm.backtest` prints the in-process result. Prediction `1` is position `+1`. Prediction `0` is position `0`, flat. The engine weight uses the same map.

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) is a separate program. `EngineClient.size` plans share orders from a nonnegative weight. `EngineClient.run_sessions` submits those orders against quotes you pass and returns fills, fees, and a daily ledger.

| Study prediction | In-process position | Engine target weight |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0` | `"0"` |

`sizing_request_for_signal` builds one `sizing_request.v1`. `session_request_for_order` builds one `engine_request.v2` around an order you already have. The example sends one signal you choose and leaves the LSTM untrained.

```bash
uv pip install /path/to/quant-backtest-engine/python
uv run python examples/engine_backtest.py
```

With `QUANT_ENGINE_BINARY` and `QUANT_ENGINE_SHA256` set, the script calls `size` and, when the plan has an order, `run_sessions`. The fields it prints are the engine's JSON. This note leaves those numbers out. The project site leaves its metric cells empty.
