English | [简体中文](engine.zh-CN.md)

# Engine backtest

[Project README](../README.md) · [Training and backtest](training.md) · [Data](data.md)

The printed result comes from `moe_lstm.backtest`. Prediction `1` is position `+1`. Prediction `0` is position `0`, flat. The engine weight uses the same map.

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) is a separate program. Its Python client is `quant_backtest_engine.EngineClient`. `size` turns a nonnegative target weight into a share plan. `run_sessions` submits the orders you pass, against the quotes you pass, and returns fills, fees, and a daily ledger. The accounting stays in that program.

## Weights

`moe_lstm.signals.long_only_target_weights` maps a study signal onto the engine's long-only contract:

| Study prediction | In-process position | Engine target weight |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0` (flat) | `"0"` |

Weights are nonnegative. One symbol's weight is at most one. `sizing_request_for_signal` builds one `sizing_request.v1`. The reference price is a decimal string, and its timestamp is at or before the information time. `session_request_for_order` builds one `engine_request.v2` session around an order you already have. That order can be one `size` returned. The quotes in the request are the strings you pass. This repository ships no vendor quote file for them.

## Run

Install the client from a checkout of the engine repository. Build the executable the way that repository documents, and pin it with the SHA256 you verified.

```bash
uv pip install /path/to/quant-backtest-engine/python
```

The example sends one signal you choose. It leaves the LSTM untrained. `MOE_SIGNAL` is that switch. The default cash and price are the strings in the example. With the engine path unset, the script prints the sizing request and stops.

```bash
uv run python examples/engine_backtest.py
```

Ask the engine for a plan. When that plan has an order, run the fills.

```bash
export QUANT_ENGINE_BINARY=/absolute/path/to/quant-backtest-engine
export QUANT_ENGINE_SHA256=the-lowercase-sha256-of-that-file
uv run python examples/engine_backtest.py
```

`run_sizing` and `run_sessions` call `EngineClient.size` and `EngineClient.run_sessions`. The fields they print, `marked_equity`, `projected_cash`, `final_cash`, `final_nav`, `total_commission`, and the fill count, are the engine's JSON. This note leaves those numbers out. The project site leaves its metric cells empty.
