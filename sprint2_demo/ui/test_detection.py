"""Offline integration checks for the detector branch's fifth UI step."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
import detection_view as dv

APP = Path(__file__).with_name("app.py")


class DetectionInterfaceTests(unittest.TestCase):
    def test_detector_step_reads_saved_outputs_without_model_calls(self):
        with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "0"}), \
             patch("src.writing.providers.OpenAIJSON.generate", side_effect=AssertionError("No model calls")):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            app.session_state["stage"] = "Detect"
            app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Make it read human" in h.value for h in app.header))
        self.assertGreaterEqual(len(app.tabs), 4)
        self.assertIn("A clichéd, LLM-style paragraph", app.selectbox(key="det_preset").options)
        self.assertIn("det_dl_final", [b.key for b in app.download_button])
        self.assertIn("det_dl_first", [b.key for b in app.download_button])
        self.assertFalse(any("No rewriting-loop results" in item.value for item in app.info))

    def test_pasted_text_is_scored_locally_and_empty_text_is_not_a_fake_zero(self):
        with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "0"}), \
             patch("src.writing.providers.OpenAIJSON.generate", side_effect=AssertionError("No model calls")):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            app.session_state["stage"] = "Detect"
            app.run()
            app.selectbox(key="det_preset").set_value("Paste your own text").run()
            self.assertTrue(any("15+ words" in x.value for x in app.info))
            field = next(x for x in app.text_area if x.label.startswith("Text to score"))
            field.set_value(dv.CLICHE).run()
        self.assertFalse(app.exception)
        result = dv.analysis(dv.CLICHE)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertGreater(result["hedges"], 0)
        self.assertFalse(any("15+ words" in x.value for x in app.info))

    def test_detector_files_and_recorded_rounds_remain_available(self):
        self.assertTrue((dv.RESULTS / "detector_model.json").is_file())
        loop = dv.loop_data()
        self.assertIsNotNone(loop)
        self.assertGreater(loop["rounds"], 0)
        paper = dv.full_paper_data()
        self.assertIsNotNone(paper)
        self.assertTrue(paper["final_md"])
        self.assertTrue(paper["first_md"])
        self.assertGreater(len(paper["revised"]), 0)


if __name__ == "__main__":
    unittest.main()
