from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from run_live import ROOT, DollarGuard, GuardedProvider, WRITER, CHECKER, SafeResponses
from src.writing.providers import BudgetExceeded, TokenBudget
from src.writing.storage import RunStore


class BudgetTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".test-work"
        parent.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_expensive_call_is_blocked_before_reservation(self):
        guard = DollarGuard(self.root / "spend.json", Decimal("0.01"))
        with self.assertRaises(BudgetExceeded):
            guard.reserve("critic", CHECKER, "review", {}, {}, 32000)
        self.assertEqual(guard.charged, 0)
        self.assertFalse(guard.path.exists())

    def test_unknown_usage_reservation_survives_restart(self):
        guard = DollarGuard(self.root / "spend.json")
        index = guard.reserve("check", CHECKER, "review", {}, {}, 1000)
        held = guard.charged
        guard.settle(index, None)
        restored = DollarGuard(guard.path)
        self.assertEqual(restored.charged, held)
        self.assertGreater(held, 0)

    def test_reported_usage_replaces_full_output_reservation(self):
        guard = DollarGuard(self.root / "spend.json")
        index = guard.reserve("check", CHECKER, "review", {}, {}, 1000)
        guard.settle(index, {"input_tokens": 100, "output_tokens": 50})
        self.assertEqual(guard.charged, Decimal("0.001"))

    def test_unsent_call_is_not_charged(self):
        guard = DollarGuard(self.root / "spend.json")
        index = guard.reserve("write", WRITER, "write", {}, {}, 1000)
        guard.settle(index, None, not_sent=True)
        self.assertEqual(guard.charged, 0)

    def test_unpriced_model_cannot_make_a_reservation(self):
        guard = DollarGuard(self.root / "spend.json")
        with self.assertRaises(ValueError):
            guard.reserve("write", "unpriced", "write", {}, {}, 1000)
        self.assertEqual(guard.charged, 0)

    def test_provider_uses_recorded_tokens_without_a_real_api_call(self):
        response = SimpleNamespace(status="completed", output_text='{"edits":[]}', model=WRITER,
                                   usage=SimpleNamespace(input_tokens=100, output_tokens=50))
        client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kwargs: response))
        store = RunStore(self.root / "run")
        guard = DollarGuard(self.root / "spend.json")
        provider = GuardedProvider(WRITER, TokenBudget(), store, client=client, stage="test", dollar_guard=guard)
        self.assertEqual(provider.generate("write", "write", {}, {}, 1000), {"edits": []})
        self.assertEqual(guard.charged, Decimal("0.0003"))

    def test_request_error_does_not_copy_key_text_into_logs(self):
        def failing(**kwargs):
            raise ValueError("credential-like confidential value")
        responses = SafeResponses(SimpleNamespace(create=failing))
        with self.assertRaises(RuntimeError) as caught:
            responses.create()
        self.assertNotIn("confidential", str(caught.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
