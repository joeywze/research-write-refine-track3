"""Check paired uploads, content protection and saved input identity."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from handover import ROOT, render
from project_io import decode, read_input, save_input, validate_upload
from run_live import prepare
from src.writing.contracts import digest


class ProjectInputTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".test-work").mkdir(exist_ok=True)
        base = ROOT / "inputs/converted"
        self.package = (base / "research_package.json").read_bytes()
        self.draft = (base / "v0.json").read_bytes()

    def test_valid_pair_keeps_every_block_and_citation_and_locks_tables(self):
        package, draft, manifest = validate_upload(self.package, self.draft)
        self.assertEqual(len(draft.paragraphs), 39)
        self.assertEqual(sum(b["locked"] for b in manifest["blocks"]), 4)
        text = render(draft, manifest)
        self.assertIn("References", text)
        self.assertIn(package.title, text)
        for block in manifest["blocks"]:
            self.assertEqual(block["converted_text"], next(p.text for p in draft.paragraphs if p.paragraph_id == block["paragraph_id"]))

    def test_wrong_package_missing_section_and_unknown_claim_are_rejected(self):
        original = json.loads(self.draft)
        cases = []
        wrong = deepcopy(original); wrong["package_id"] = "different_project"; cases.append(wrong)
        missing = deepcopy(original); missing["paragraphs"] = [p for p in missing["paragraphs"] if p["section"] != "conclusion"]; cases.append(missing)
        claim = deepcopy(original); claim["paragraphs"][0]["claim_ids"] = ["UnknownClaim"]; cases.append(claim)
        citation = deepcopy(original); citation["paragraphs"][1]["text"] += " [[UnrecognisedSource]]"; cases.append(citation)
        for value in cases:
            with self.subTest(value=value["package_id"]), self.assertRaises(ValueError):
                validate_upload(self.package, json.dumps(value).encode())

    def test_invalid_json_duplicates_unsafe_links_and_size_are_rejected(self):
        for data in (b'{"x": 1, "x": 2}', b'{"x": NaN}', b'bad json', b'\xff', b' ' * 1_000_001):
            with self.subTest(data=data[:20]), self.assertRaises(ValueError): decode(data)
        package = json.loads(self.package)
        for url in ("javascript:alert(1)", "file:///private", "https://name:password@example.com/paper"):
            package["sources"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_upload(json.dumps(package).encode(), self.draft)

    def test_saved_upload_is_revalidated_and_used_by_the_runner(self):
        package, draft, manifest = validate_upload(self.package, self.draft)
        with TemporaryDirectory(dir=ROOT / ".test-work") as temp:
            folder = Path(temp) / "checked"
            save_input(folder, package, draft, manifest)
            got_package, got_draft, got_manifest = prepare(folder)
            self.assertEqual(digest(got_package), digest(package))
            self.assertEqual(digest(got_draft), digest(draft))
            self.assertEqual(got_manifest, manifest)
            changed = json.loads((folder / "v0.json").read_text())
            changed["paragraphs"][0]["text"] += " A later edit."
            (folder / "v0.json").write_text(json.dumps(changed))
            with self.assertRaises(ValueError): read_input(folder)


if __name__ == "__main__":
    (ROOT / ".test-work").mkdir(exist_ok=True)
    unittest.main()
