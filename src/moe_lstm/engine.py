"""Wire requests for quant-backtest-engine.

``size`` plans long-only share orders. ``run_sessions`` applies those orders
to quotes and returns fills and a daily ledger. Prediction 1 is weight ``1``.
Prediction 0 is weight ``0``, the same flat position as ``backtest``.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from moe_lstm.signals import long_only_target_weights

_DECIMAL = re.compile(r"\d+(?:\.\d+)?")
_INTEGER = re.compile(r"\d+")
_CURRENCIES = {"USD": "UTC", "CNY": "Asia/Shanghai"}


def sizing_request_for_signal(
    prediction: int,
    *,
    symbol: str,
    cash: str,
    fee_bps: str,
    reference_price: str,
    information_ts_ns: int,
    price_ts_ns: int,
    held_quantity: str = "0",
    buy_lot: int = 1,
    currency: str = "USD",
) -> dict:
    """One ``sizing_request.v1`` for a single symbol."""
    weight = long_only_target_weights([prediction])[0]
    _currency(currency)
    _token("symbol", symbol)
    _decimal("cash", cash)
    _decimal("fee_bps", fee_bps)
    _decimal("reference_price", reference_price)
    _integer("held_quantity", held_quantity)
    _stamp("information_ts_ns", information_ts_ns)
    _stamp("price_ts_ns", price_ts_ns)
    if price_ts_ns > information_ts_ns:
        raise ValueError("reference price must be known no later than the information time.")
    if not isinstance(buy_lot, int) or isinstance(buy_lot, bool) or buy_lot < 1:
        raise ValueError("buy_lot must be a positive int.")
    return {
        "schema_version": "sizing_request.v1",
        "currency": currency,
        "information_ts_ns": information_ts_ns,
        "cash": cash,
        "fee_bps": fee_bps,
        "assets": [
            {
                "symbol": symbol,
                "held_quantity": held_quantity,
                "reference_price": reference_price,
                "price_ts_ns": price_ts_ns,
                "target_weight": weight,
                "buy_lot": buy_lot,
            }
        ],
    }


def session_request_for_order(
    *,
    currency: str,
    initial_cash: str,
    fee_bps: str,
    symbol: str,
    price_precision: int,
    buy_lot: int,
    enforce_t1: bool,
    session_date: str,
    information_ts_ns: int,
    open_ts_ns: int,
    valuation_ts_ns: int,
    bid: str,
    ask: str,
    order_id: str,
    side: str,
    quantity: str,
    bid_size: str = "1000000",
    ask_size: str = "1000000",
) -> dict:
    """One ``engine_request.v2`` session around a single order."""
    zone = _currency(currency)
    _decimal("initial_cash", initial_cash)
    _decimal("fee_bps", fee_bps)
    _decimal("bid", bid)
    _decimal("ask", ask)
    _decimal("bid_size", bid_size)
    _decimal("ask_size", ask_size)
    _token("symbol", symbol)
    _token("order_id", order_id)
    _integer("quantity", quantity)
    if int(quantity) < 1:
        raise ValueError("quantity must be a positive integer string.")
    if side not in ("buy", "sell"):
        raise ValueError("side must be buy or sell.")
    if not isinstance(enforce_t1, bool):
        raise ValueError("enforce_t1 must be a bool.")
    if not isinstance(price_precision, int) or isinstance(price_precision, bool) or price_precision < 0:
        raise ValueError("price_precision must be a nonnegative int.")
    if not isinstance(buy_lot, int) or isinstance(buy_lot, bool) or buy_lot < 1:
        raise ValueError("buy_lot must be a positive int.")
    _stamp("information_ts_ns", information_ts_ns)
    _stamp("open_ts_ns", open_ts_ns)
    _stamp("valuation_ts_ns", valuation_ts_ns)
    if not (information_ts_ns < open_ts_ns <= valuation_ts_ns):
        raise ValueError("Require information_ts_ns < open_ts_ns <= valuation_ts_ns.")
    expected = datetime.fromtimestamp(valuation_ts_ns // 1_000_000_000, UTC).astimezone(ZoneInfo(zone)).date().isoformat()
    if session_date != expected:
        raise ValueError(
            f"session_date {session_date!r} does not match {zone} date {expected} of valuation_ts_ns."
        )
    quote = {
        "bid": bid,
        "ask": ask,
        "bid_size": bid_size,
        "ask_size": ask_size,
        "tradable": True,
        "limit_up": False,
        "limit_down": False,
        "symbol": symbol,
    }
    return {
        "schema_version": "engine_request.v2",
        "currency": currency,
        "price_basis": "raw",
        "initial_cash": initial_cash,
        "fee_bps": fee_bps,
        "enforce_t1": enforce_t1,
        "instruments": [{"symbol": symbol, "price_precision": price_precision, "buy_lot": buy_lot}],
        "required_capabilities": ["session_ledger"],
        "sessions": [
            {
                "session_date": session_date,
                "open_ts_ns": open_ts_ns,
                "valuation_ts_ns": valuation_ts_ns,
                "quotes": [{**quote, "ts_ns": open_ts_ns}, {**quote, "ts_ns": valuation_ts_ns}],
                "orders": [
                    {
                        "id": order_id,
                        "symbol": symbol,
                        "information_ts_ns": information_ts_ns,
                        "side": side,
                        "quantity": quantity,
                    }
                ],
            }
        ],
    }


def run_sizing(executable, sha256: str, request: dict, *, timeout: float = 30, source_revision: str | None = None) -> dict:
    """Call ``EngineClient.size``. The dict is the engine's plan."""
    return _client(executable, sha256, timeout, source_revision).size(request)


def run_sessions(executable, sha256: str, request: dict, *, timeout: float = 30, source_revision: str | None = None) -> dict:
    """Call ``EngineClient.run_sessions``. Fills and the ledger are the engine's."""
    return _client(executable, sha256, timeout, source_revision).run_sessions(request)


def _client(executable, sha256: str, timeout: float, source_revision: str | None):
    try:
        from quant_backtest_engine import EngineClient
    except ImportError as exc:
        raise SystemExit(
            "quant_backtest_engine is not installed. From a checkout of "
            "https://github.com/runchengxie/quant-backtest-engine run "
            "`uv pip install ./python`."
        ) from exc
    return EngineClient(Path(executable), sha256, timeout=timeout, source_revision=source_revision)


def _currency(currency: str) -> str:
    try:
        return _CURRENCIES[currency]
    except KeyError as exc:
        raise ValueError("currency must be USD or CNY.") from exc


def _token(label: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip() or any(char.isspace() for char in value):
        raise ValueError(f"{label} must be a non-empty token.")


def _decimal(label: str, value: str) -> None:
    if not isinstance(value, str) or _DECIMAL.fullmatch(value) is None:
        raise ValueError(f"{label} must be a nonnegative decimal string.")


def _integer(label: str, value: str) -> None:
    if not isinstance(value, str) or _INTEGER.fullmatch(value) is None:
        raise ValueError(f"{label} must be a nonnegative integer string.")


def _stamp(label: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be an int.")
