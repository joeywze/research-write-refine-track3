"""Check calibration controls with scripted verdicts, without paid calls."""
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
from io import StringIO
import unittest

from citation_calibration import development_cases, matches_expectation, run_calibration
from handover import ROOT
from run_live import prepare
from src.writing.contracts import digest
from src.writing.preservation import PreservationResult, deterministic, reference_comparisons
from src.writing.storage import RunStore
from test_citation_policy import RecordedVerdict


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package, cls.original, _ = prepare()
        cls.cases = development_cases(cls.package, cls.original)

    def test_cases_isolate_changes_beyond_fixed_content_counts(self):
        expected = [[], ["P002", "P007", "P008"], ["P001"], ["P002"], ["P006"]]
        self.assertEqual(len({digest(c["candidate"]) for c in self.cases}), 5)
        for case, changed in zip(self.cases, expected):
            self.assertEqual(deterministic(self.package, case["candidate"], (self.original,)).status, "PASS")
            self.assertEqual(reference_comparisons(case["candidate"], (self.original,))[0]["changed_paragraph_ids"], changed)

    def test_unrelated_failure_and_check_error_do_not_count_as_detection(self):
        case = self.cases[3]
        unrelated = PreservationResult("CITATION_MISMATCH", ("fixture",), {"paragraphs": [
            {"paragraph_id": "P010", "status": "CITATION_MISMATCH"}]})
        self.assertFalse(matches_expectation(case, unrelated))
        self.assertFalse(matches_expectation(case, PreservationResult("CHECK_ERROR", ("fixture",))))

    def run_fixture(self, factory):
        parent = ROOT / ".test-work"
        parent.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=parent) as temp, redirect_stdout(StringIO()):
            store = RunStore(Path(temp) / "calibration")
            return run_calibration(self.package, self.original, factory, store)

    def test_accepting_every_case_blocks_the_writing_run(self):
        calls = []

        def factory(stage):
            calls.append(stage)
            return RecordedVerdict(self.original)

        report = self.run_fixture(factory)
        self.assertEqual(len(calls), 5)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual([c["matches_development_expectation"] for c in report["cases"]], [True, True, True, False, False])

    def test_format_failure_stops_further_paid_cases(self):
        calls = []

        class Malformed:
            model = "offline-malformed-fixture"
            test_only = True

            def generate(self, *args):
                return {}

        def factory(stage):
            calls.append(stage)
            return Malformed()

        report = self.run_fixture(factory)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(calls), 1)
        self.assertEqual(report["cases"][0]["result"]["status"], "CHECK_ERROR")


if __name__ == "__main__":
    unittest.main()
