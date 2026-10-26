"""Exercise the real user journey without paid requests."""
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch, Mock

from streamlit.testing.v1 import AppTest
import core
import jobs
import launch
from contextlib import redirect_stdout
from io import StringIO

APP = Path(__file__).with_name("app.py")


class InterfaceTests(unittest.TestCase):
    def app(self):
        with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "0"}):
            app = AppTest.from_file(str(APP), default_timeout=20).run()
        self.assertFalse(app.exception)
        return app

    def test_research_to_draft_to_refinement_to_results(self):
        app = self.app()
        self.assertIn("Research Write Refine", [e.value for e in app.title])
        self.assertTrue(any("approval is pending" in e.value for e in app.warning))
        app.button(key="to_draft").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["stage"], "Draft")
        self.assertIn("Evaluation Plan", "\n".join(e.value for e in app.markdown))
        app.selectbox(key="draft_section").set_value("conclusion").run()
        self.assertFalse(app.exception)
        app.button(key="to_refine").click().run()
        self.assertEqual(app.session_state["stage"], "Refine")
        self.assertFalse(app.exception)
        comparison = app.dataframe[0].value
        self.assertEqual(comparison["Before refinement"].tolist(), [0, 2])
        self.assertEqual(comparison["After refinement"].tolist(), [0, 0])
        self.assertTrue(app.button(key="start_live").disabled)
        self.assertTrue(any("Introduction · Paragraph 1" in e.value for e in app.subheader))
        next(b for b in app.button if b.label == "Continue to results").click().run()
        self.assertEqual(app.session_state["stage"], "Results")
        self.assertFalse(app.exception)
        rows = app.dataframe[0].value
        self.assertEqual(rows["Review points flagged by the LLM"].tolist(), [2, 2, 0])
        self.assertEqual(len(app.download_button), 2)

    def test_upload_choice_does_not_show_the_examples_results(self):
        app = self.app()
        app.radio(key="_project_choice").set_value("Upload your research project").run()
        self.assertFalse(app.exception)
        self.assertTrue(app.button(key="check_upload").disabled)
        self.assertTrue(any("matching draft" in e.value for e in app.info))
        self.assertFalse(app.dataframe)

    def test_uploaded_project_survives_navigation_and_has_no_invented_llm_score(self):
        app = self.app()
        base = core.ROOT / "inputs/converted"
        app.session_state["uploaded_project"] = core.uploaded_project((base / "research_package.json").read_bytes(), (base / "v0.json").read_bytes())
        app.session_state["project_mode"] = "Upload your research project"
        app.run()
        app.button(key="to_draft").click().run()
        app.button(key="to_refine").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["project_mode"], "Upload your research project")
        rows = app.dataframe[0].value
        self.assertEqual(rows.loc[0, "Before refinement"], 0)
        self.assertTrue(rows["After refinement"].isna().all())
        self.assertFalse(app.expander)
        next(b for b in app.button if b.label == "Continue to results").click().run()
        self.assertTrue(any("has not been refined" in e.value for e in app.info))
        self.assertFalse(app.download_button)

    def test_topic_generation_is_clearly_planned_and_cannot_start_a_job(self):
        app = self.app()
        with patch.object(jobs, "start_live") as start:
            app.radio(key="_project_choice").set_value("Start from a research topic (planned)").run()
            self.assertFalse(app.exception)
            self.assertTrue(any("are planned" in e.value for e in app.info))
            self.assertFalse(app.dataframe)
            start.assert_not_called()

    def test_uploaded_job_uses_its_checked_input_directory(self):
        base = core.ROOT / "inputs/converted"
        project = core.uploaded_project((base / "research_package.json").read_bytes(), (base / "v0.json").read_bytes())
        folder = core.ROOT / ".test-work"
        folder.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=folder) as temp:
            root = Path(temp)
            with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "1", "OPENAI_API_KEY": "not-a-real-key"}), \
                 patch.object(jobs, "ROOT", root), patch.object(jobs, "JOB_DIR", root / "jobs"), \
                 patch.object(jobs, "LOCK", root / "ui.lock"), patch.object(jobs.subprocess, "Popen", return_value=Mock(pid=1234)) as spawn, \
                 patch.object(jobs.threading, "Thread"):
                job_id = jobs.start_live("127.0.0.1", project)
                command = spawn.call_args.args[0]
                self.assertIn("--input-dir", command)
                input_dir = Path(command[command.index("--input-dir") + 1])
                from project_io import read_input
                package, draft, manifest = read_input(input_dir)
                self.assertEqual(core.digest(package), core.digest(project["package"]))
                self.assertEqual(core.digest(draft), core.digest(project["drafts"]["v0_input"]))
                self.assertEqual(manifest["input_origin"], "uploaded")
                self.assertEqual(jobs.job_status(job_id)["project_name"], project["name"])

    def test_safety_button_runs_the_gate_retains_input_and_never_calls_api(self):
        app = self.app()
        app.session_state["stage"] = "Results"
        app.run()
        with patch("src.writing.providers.OpenAIJSON.generate", side_effect=AssertionError("No API calls allowed")):
            app.button(key="run_safety").click().run()
        self.assertFalse(app.exception)
        safety = app.session_state["safety_" + core.DEFAULT_RUN]
        self.assertTrue(safety["rejected"])
        self.assertEqual(safety["api_calls"], 0)
        self.assertEqual(safety["accepted_hash"], safety["retained_hash"])
        self.assertIn("numbers changed", safety["reason"])

    def test_earlier_unsuccessful_run_has_no_invented_accepted_change(self):
        app = self.app()
        app.selectbox(key="run_id").set_value("live-20261025T142355415015Z").run()
        app.session_state["stage"] = "Results"
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("No guided revision was accepted" in e.value for e in app.info))
        self.assertEqual(app.dataframe[0].value["Review points flagged by the LLM"].tolist(), [3, 3, 3])

    def test_whole_paper_download_content_matches_the_saved_accepted_file(self):
        data = core.open_run(core.DEFAULT_RUN)
        generated = core.paper(data, "guided_final").encode("utf-8")
        original = (data["path"] / "guided_final_with_layout.md").read_bytes()
        self.assertEqual(hashlib.sha256(generated).hexdigest(), hashlib.sha256(original).hexdigest())

    def test_untrusted_paths_and_job_ids_are_rejected(self):
        for name in ("../pilot_spend.json", "..", str(core.ROOT)):
            with self.subTest(name=name), self.assertRaises(ValueError): core.run_path(name)
        with self.assertRaises(ValueError): jobs.job_status("../secrets")

    def test_a_remote_or_unconfigured_server_cannot_launch_paid_jobs(self):
        with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "1", "OPENAI_API_KEY": "not-a-real-key"}):
            self.assertFalse(jobs.live_allowed("0.0.0.0"))
            with patch.object(jobs.subprocess, "Popen") as spawn:
                with self.assertRaises(ValueError): jobs.start_live("0.0.0.0")
                spawn.assert_not_called()

    def test_live_adapter_starts_existing_runner_once_and_blocks_duplicate(self):
        folder = core.ROOT / ".test-work"
        folder.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=folder) as temp:
            root = Path(temp)
            jobs_dir, lock = root / "jobs", root / "ui.lock"
            process = Mock(pid=1234)
            with patch.dict(os.environ, {"TRACK3_LOCAL_LIVE": "1", "OPENAI_API_KEY": "not-a-real-key"}), \
                 patch.object(jobs, "ROOT", root), patch.object(jobs, "JOB_DIR", jobs_dir), \
                 patch.object(jobs, "LOCK", lock), patch.object(jobs.subprocess, "Popen", return_value=process) as spawn, \
                 patch.object(jobs.threading, "Thread"):
                job_id = jobs.start_live("127.0.0.1")
                self.assertIn("--execute", spawn.call_args.args[0])
                self.assertIn("--allow-provisional", spawn.call_args.args[0])
                self.assertNotIn("not-a-real-key", json.dumps(json.loads((jobs_dir / (job_id + ".json")).read_text())))
                with self.assertRaises(ValueError): jobs.start_live("127.0.0.1")
                spawn.assert_called_once()

    def test_recorded_launcher_strips_an_ambient_key_and_never_prompts(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "not-a-real-key"}), patch.object(launch, "getpass") as prompt, \
             patch.object(launch.subprocess, "call", return_value=0) as run, redirect_stdout(StringIO()):
            self.assertEqual(launch.main([]), 0)
            prompt.assert_not_called()
            self.assertNotIn("OPENAI_API_KEY", run.call_args.kwargs["env"])
            self.assertEqual(run.call_args.kwargs["env"]["TRACK3_LOCAL_LIVE"], "0")

    def test_live_launcher_forwards_the_key_only_to_child_environment(self):
        captured, console = {}, StringIO()

        def child(command, **kwargs):
            captured.update(command=command, env=kwargs["env"].copy())
            return 0

        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}), patch.object(launch, "getpass", return_value="not-a-real-key"), \
             patch.object(launch.subprocess, "call", side_effect=child), redirect_stdout(console):
            self.assertEqual(launch.main(["--live", "--port", "8502"]), 0)
        self.assertEqual(captured["env"]["OPENAI_API_KEY"], "not-a-real-key")
        self.assertEqual(captured["env"]["TRACK3_LOCAL_LIVE"], "1")
        self.assertIn("--server.port=8502", captured["command"])
        self.assertNotIn("not-a-real-key", console.getvalue())

    def test_open_completed_run_refreshes_the_whole_page_and_selects_its_result(self):
        app = self.app()
        app.session_state["stage"] = "Refine"
        app.session_state["job_id"] = "0" * 32
        target = "live-20261025T142355415015Z"
        with patch.object(jobs, "progress", return_value={"status": "COMPLETED", "run_name": target, "stage_markers": []}):
            app.run()
            app.button(key="open_live").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["stage"], "Results")
        self.assertEqual(app.session_state["run_id"], target)
        self.assertEqual(app.dataframe[0].value["Review points flagged by the LLM"].tolist(), [3, 3, 3])


if __name__ == "__main__":
    unittest.main()
