"""Send one chosen signal through quant-backtest-engine.

This does not train the LSTM. Without QUANT_ENGINE_BINARY and
QUANT_ENGINE_SHA256 it prints the sizing request and stops.

```bash
uv run python examples/engine_backtest.py
```
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from moe_lstm.engine import run_sessions, run_sizing, session_request_for_order, sizing_request_for_signal

_INFORMATION_TS_NS = 1735781399999999999
_OPEN_TS_NS = 1735781400000000000
_VALUATION_TS_NS = 1735781401000000000


def main() -> int:
    signal = int(os.environ.get("MOE_SIGNAL", "1"))
    symbol = os.environ.get("MOE_ENGINE_SYMBOL", "INDEX")
    cash = os.environ.get("MOE_ENGINE_CASH", "10000")
    price = os.environ.get("MOE_ENGINE_PRICE", "100")
    fee_bps = os.environ.get("MOE_ENGINE_FEE_BPS", "10")
    request = sizing_request_for_signal(
        signal,
        symbol=symbol,
        cash=cash,
        fee_bps=fee_bps,
        reference_price=price,
        information_ts_ns=_INFORMATION_TS_NS,
        price_ts_ns=_INFORMATION_TS_NS,
        currency="USD",
    )
    print(json.dumps(request, indent=2))
    binary = os.environ.get("QUANT_ENGINE_BINARY", "").strip()
    digest = os.environ.get("QUANT_ENGINE_SHA256", "").strip()
    if not binary or not digest:
        print(
            "QUANT_ENGINE_BINARY and QUANT_ENGINE_SHA256 are unset. "
            "Printed the sizing request only. No fills were run."
        )
        return 0
    revision = os.environ.get("QUANT_ENGINE_SOURCE_REVISION", "").strip() or None
    plan = run_sizing(Path(binary), digest, request, source_revision=revision)
    print("marked_equity", plan["marked_equity"])
    print("projected_cash", plan["projected_cash"])
    print("orders", len(plan["orders"]))
    if not plan["orders"]:
        print("Engine planned no orders. No session was run.")
        return 0
    order = plan["orders"][0]
    session_date = datetime.fromtimestamp(_VALUATION_TS_NS // 1_000_000_000, UTC).date().isoformat()
    session = session_request_for_order(
        currency="USD",
        initial_cash=cash,
        fee_bps=fee_bps,
        symbol=symbol,
        price_precision=2,
        buy_lot=1,
        enforce_t1=False,
        session_date=session_date,
        information_ts_ns=_INFORMATION_TS_NS,
        open_ts_ns=_OPEN_TS_NS,
        valuation_ts_ns=_VALUATION_TS_NS,
        bid=price,
        ask=price,
        order_id=order["id"],
        side=order["side"],
        quantity=order["quantity"],
    )
    ledger = run_sessions(Path(binary), digest, session, source_revision=revision)
    print("final_cash", ledger["final_cash"])
    print("final_nav", ledger["final_nav"])
    print("total_commission", ledger["total_commission"])
    print("fills", len(ledger["fills"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
