import json
import os
import subprocess
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

from moe_lstm.engine import session_request_for_order, sizing_request_for_signal

ROOT = Path(__file__).resolve().parents[1]
INFORMATION = 1735781399999999999
OPEN = 1735781400000000000
VALUATION = 1735781401000000000
SESSION = datetime.fromtimestamp(VALUATION // 1_000_000_000, UTC).date().isoformat()


def _order_request(**overrides):
    fields = dict(
        currency="USD",
        initial_cash="10000",
        fee_bps="10",
        symbol="INDEX",
        price_precision=2,
        buy_lot=1,
        enforce_t1=False,
        session_date=SESSION,
        information_ts_ns=INFORMATION,
        open_ts_ns=OPEN,
        valuation_ts_ns=VALUATION,
        bid="100",
        ask="100",
        order_id="signal-1",
        side="buy",
        quantity="10",
    )
    fields.update(overrides)
    return session_request_for_order(**fields)


class EngineAdapterTests(unittest.TestCase):
    def test_long_and_short_signals_become_long_only_weights(self):
        long = sizing_request_for_signal(
            1,
            symbol="INDEX",
            cash="10000",
            fee_bps="10",
            reference_price="100",
            information_ts_ns=INFORMATION,
            price_ts_ns=INFORMATION,
        )
        short = sizing_request_for_signal(
            0,
            symbol="INDEX",
            cash="10000",
            fee_bps="10",
            reference_price="100",
            information_ts_ns=INFORMATION,
            price_ts_ns=INFORMATION,
        )
        self.assertEqual(long["schema_version"], "sizing_request.v1")
        self.assertEqual(long["assets"][0]["target_weight"], "1")
        self.assertEqual(short["assets"][0]["target_weight"], "0")
        self.assertLessEqual(sum(float(asset["target_weight"]) for asset in long["assets"]), 1)

    def test_a_future_reference_price_is_rejected(self):
        with self.assertRaises(ValueError):
            sizing_request_for_signal(
                1,
                symbol="INDEX",
                cash="10000",
                fee_bps="10",
                reference_price="100",
                information_ts_ns=INFORMATION,
                price_ts_ns=INFORMATION + 1,
            )

    def test_session_request_keeps_the_order_inside_the_session(self):
        request = _order_request()
        self.assertEqual(request["schema_version"], "engine_request.v2")
        self.assertEqual(request["price_basis"], "raw")
        self.assertEqual(request["required_capabilities"], ["session_ledger"])
        session = request["sessions"][0]
        order = session["orders"][0]
        self.assertLess(order["information_ts_ns"], session["open_ts_ns"])
        self.assertLessEqual(session["open_ts_ns"], session["valuation_ts_ns"])
        self.assertEqual(
            [quote["ts_ns"] for quote in session["quotes"]],
            [session["open_ts_ns"], session["valuation_ts_ns"]],
        )
        self.assertEqual(session["session_date"], SESSION)

    def test_session_date_must_match_the_valuation_zone(self):
        with self.assertRaises(ValueError):
            _order_request(session_date="1999-01-01")

    def test_example_without_a_binary_prints_the_request_and_no_ledger(self):
        env = os.environ.copy()
        env.pop("QUANT_ENGINE_BINARY", None)
        env.pop("QUANT_ENGINE_SHA256", None)
        env["MOE_SIGNAL"] = "0"
        env["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [sys.executable, str(ROOT / "examples" / "engine_backtest.py")],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("No fills were run.", completed.stdout)
        self.assertNotIn("final_nav", completed.stdout)
        payload = json.loads(completed.stdout.split("QUANT_ENGINE_BINARY", 1)[0])
        self.assertEqual(payload["assets"][0]["target_weight"], "0")
