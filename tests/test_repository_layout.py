"""Check moved paths and provenance without collecting data or making model calls."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]


class RepositoryLayoutTests(unittest.TestCase):
    def test_expected_components_and_guides_exist(self):
        for path in (
            "src/research/collect_emnlp.py", "src/research/sample_papers.py",
            "src/research/generate_ai_sections.py", "src/fact_checking/fact_checker.py",
            "src/detection/detector.py", "src/writing/pipeline.py",
            "docs/architecture.md", "docs/evaluation.md", "docs/deployment.md",
            "docs/contributions.md", "docs/research/draft_v0.md",
            "sprint2_demo/ui/app.py", "sprint2_demo/backend/src/writing/pipeline.py",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())

    def test_moved_scripts_resolve_the_repository_root(self):
        for path in ("src/research/collect_emnlp.py", "src/research/sample_papers.py",
                     "src/research/generate_ai_sections.py", "src/fact_checking/fact_checker.py"):
            with self.subTest(path=path):
                file = ROOT / path
                tree = ast.parse(file.read_text(encoding="utf-8"))
                assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                                  and any(isinstance(t, ast.Name) and t.id == "PROJECT_ROOT" for t in node.targets))
                self.assertEqual(ast.unparse(assignment.value), "Path(__file__).resolve().parents[2]")
                self.assertEqual(file.resolve().parents[2], ROOT)
        checker = (ROOT / "src/fact_checking/fact_checker.py").read_text()
        self.assertIn('/ "research"', checker)
        self.assertNotIn('/ "part_a_research_development"', checker)

    def test_compatibility_launchers_do_not_run_on_import(self):
        mapping = {"fact_checker": "fact_checking/fact_checker.py",
                   "generate_ai_sections": "research/generate_ai_sections.py",
                   "sample_papers": "research/sample_papers.py"}
        for name, target in mapping.items():
            with self.subTest(name=name):
                file = ROOT / "src" / (name + ".py")
                spec = importlib.util.spec_from_file_location("compat_" + name, file)
                with patch.object(runpy, "run_path") as launch:
                    spec.loader.exec_module(importlib.util.module_from_spec(spec))
                    launch.assert_not_called()
                original_run = runpy.run_path
                with patch.object(runpy, "run_path") as launch:
                    original_run(str(file), run_name="__main__")
                    launch.assert_called_once_with(str(ROOT / "src" / target), run_name="__main__")

    def test_research_document_contents_match_the_preserved_snapshot(self):
        for name in ("README.md", "claim_evidence_ledger.json", "claim_evidence_table.md",
                     "draft_v0.md", "external_evidence.md", "research_development.md"):
            with self.subTest(name=name):
                current = (ROOT / "docs/research" / name).read_text(encoding="utf-8-sig")
                pinned = (ROOT / "sprint2_demo/inputs/source" / name).read_text(encoding="utf-8-sig")
                self.assertEqual(current, pinned)

    def test_pinned_source_hashes_and_pilot_labels_are_unchanged(self):
        base = ROOT / "sprint2_demo"
        manifest = json.loads((base / "inputs/source_manifest.json").read_text(encoding="utf-8-sig"))
        for record in manifest["files"]:
            with self.subTest(source=record["path"]):
                path = base / "inputs/source" / Path(record["path"]).name
                if not path.exists():
                    # The original manifest also indexes the scope document,
                    # which the demo did not copy into its runtime snapshot.
                    self.assertEqual(record["path"], "docs/part_a_research_development/review_scope.md")
                    path = ROOT / "docs/research/review_scope.md"
                data = path.read_bytes()
                blob = b"blob " + str(len(data)).encode() + b"\0" + data
                self.assertEqual(hashlib.sha1(blob).hexdigest(), record["sha"])
        original = (ROOT / "data/facts/pilot/draft_v0_pilot_verification.csv").read_text(encoding="utf-8-sig")
        pinned = (base / "inputs/source/draft_v0_pilot_verification.csv").read_text(encoding="utf-8-sig")
        self.assertEqual(original, pinned)

    def test_documentation_local_links_resolve(self):
        paths = [ROOT / "README.md", ROOT / "data/README.md", ROOT / "examples/README.md",
                 ROOT / "results/README.md", ROOT / "src/research/README.md",
                 ROOT / "src/fact_checking/README.md", *sorted((ROOT / "docs").rglob("*.md"))]
        for path in paths:
            content = path.read_text(encoding="utf-8-sig")
            for link in re.findall(r"\]\(([^\s)]+)\)", content):
                parsed = urlparse(link)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(document=str(path.relative_to(ROOT)), link=link):
                    self.assertTrue((path.parent / unquote(parsed.path)).exists())

    def test_root_and_demo_keep_their_intended_backend(self):
        command = "import src.writing.pipeline as p; print(p.__file__)"
        root = subprocess.check_output([sys.executable, "-c", command], cwd=ROOT, text=True).strip()
        pinned = subprocess.check_output([sys.executable, "-c", "import handover; " + command],
                                         cwd=ROOT / "sprint2_demo", text=True).strip()
        self.assertEqual(Path(root), ROOT / "src/writing/pipeline.py")
        self.assertEqual(Path(pinned), ROOT / "sprint2_demo/backend/src/writing/pipeline.py")


if __name__ == "__main__":
    unittest.main()
