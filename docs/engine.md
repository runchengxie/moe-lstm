**English** | [简体中文](engine.zh-CN.md)

# Engine backtest

[Project README](../README.md) · [Training and backtest](training.md) · [Data](data.md)

The printed result comes from `moe_lstm.backtest`. Prediction `1` is position `+1` and prediction `0` is position `0` (flat). The engine weight uses the same map.

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) is a separate program. Its Python client is `quant_backtest_engine.EngineClient`. `size` turns a nonnegative target weight into a share plan. `run_sessions` submits orders against quotes you supply and returns fills, fees, and a daily ledger. This repository does not reimplement that accounting.

## Weights

`moe_lstm.signals.long_only_target_weights` maps a study signal onto the engine's long-only contract:

| Study prediction | In-process position | Engine target weight |
| --- | --- | --- |
| `1` | `+1` | `"1"` |
| `0` | `0` (flat) | `"0"` |

Weights are nonnegative and the single-symbol weight is at most one. `sizing_request_for_signal` builds one `sizing_request.v1`. The reference price has to be a decimal string timestamped no later than the information time. `session_request_for_order` builds one `engine_request.v2` session around an order you already have, including an order returned by `size`. Quotes in that request are the strings you pass. They are not loaded from a vendor file in this repo.

## Run

Install the client from a checkout of the engine repository. Build the executable the way that repository documents, and pin it with the SHA256 you verified.

```bash
uv pip install /path/to/quant-backtest-engine/python
```

The example does not train the LSTM. `MOE_SIGNAL` is a switch you set so the wire path can be exercised. The default cash and price are also yours. Unset, the script only prints the sizing request.

```bash
uv run python examples/engine_backtest.py
```

To ask the engine for a plan, and for fills when that plan has an order:

```bash
export QUANT_ENGINE_BINARY=/absolute/path/to/quant-backtest-engine
export QUANT_ENGINE_SHA256=the-lowercase-sha256-of-that-file
uv run python examples/engine_backtest.py
```

`run_sizing` and `run_sessions` call `EngineClient.size` and `EngineClient.run_sessions`. What they print (`marked_equity`, `projected_cash`, `final_cash`, `final_nav`, `total_commission`, fill count) is the engine's JSON. This page does not copy those numbers, and the project site does not invent a Sharpe ratio from them.
