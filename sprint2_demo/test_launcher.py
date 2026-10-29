from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import start_live


class LauncherTests(unittest.TestCase):
    def setUp(self):
        parent = start_live.run_live.ROOT / ".test-work"
        parent.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_waiting_launcher_keeps_key_out_of_files_and_console(self):
        output = StringIO()
        worker = SimpleNamespace(pid=12345, wait=Mock(return_value=0))
        with patch.object(start_live.run_live, "ROOT", self.root), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-not-a-real-secret"}), \
                patch.object(start_live.subprocess, "Popen", return_value=worker) as spawn, \
                redirect_stdout(output):
            self.assertEqual(start_live.main(), 0)
            kwargs = spawn.call_args.kwargs
            self.assertIn("--calibrate-first", spawn.call_args.args[0])
            self.assertEqual(kwargs["stdin"], start_live.subprocess.DEVNULL)
            if os.name == "nt":
                self.assertNotEqual(kwargs["creationflags"], 0)
                self.assertFalse(kwargs["start_new_session"])
            else:
                self.assertEqual(kwargs["creationflags"], 0)
                self.assertTrue(kwargs["start_new_session"])
            self.assertEqual(kwargs["env"].get("OPENAI_API_KEY"), None)
            worker.wait.assert_called_once_with()
        record = json.loads((self.root / "verification/active_worker.json").read_text(encoding="utf-8"))
        self.assertEqual(record["pid"], 12345)
        self.assertFalse(record["key_saved_to_file"])
        self.assertEqual(record["status"], "COMPLETED")
        self.assertIn("Keep this window open", output.getvalue())
        self.assertNotIn("You can close this window", output.getvalue())
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn("fixture-not-a-real-secret", path.read_text(encoding="utf-8"))
        self.assertNotIn("fixture-not-a-real-secret", output.getvalue())

    def test_existing_lock_prevents_second_worker(self):
        (self.root / "pilot_spend.lock").write_text("12345", encoding="ascii")
        with patch.object(start_live.run_live, "ROOT", self.root), \
                patch.object(start_live.subprocess, "Popen") as spawn, redirect_stdout(StringIO()):
            self.assertEqual(start_live.main(), 2)
            spawn.assert_not_called()

    def test_non_ascii_key_is_rejected_before_a_worker_starts(self):
        with patch.object(start_live.run_live, "ROOT", self.root), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-key-\u201c"}), \
                patch.object(start_live.subprocess, "Popen") as spawn, redirect_stdout(StringIO()):
            self.assertEqual(start_live.main(), 2)
            spawn.assert_not_called()

    def test_worker_failure_is_recorded_and_not_retried(self):
        worker = SimpleNamespace(pid=12345, wait=Mock(return_value=2))
        with patch.object(start_live.run_live, "ROOT", self.root), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-not-a-real-secret"}), \
                patch.object(start_live.subprocess, "Popen", return_value=worker) as spawn, \
                redirect_stdout(StringIO()):
            self.assertEqual(start_live.main(), 2)
            spawn.assert_called_once()
        record = json.loads((self.root / "verification/active_worker.json").read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "STOPPED")
        self.assertEqual(record["exit_code"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
