"""Offline integration and source-integrity checks for uploaded research projects."""
from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest

import fitz
import openpyxl

from research_package_automation.research_package_builder import (
    build_research_package, generate_and_check, read_pdfs,
)
from research_package_automation.evidence_checker import check_draft, load_facts
from research_package_automation.support.contracts import Draft, ResearchPackage, SECTIONS
from research_package_automation.support.storage import RunStore

QUOTE = "The classifier achieved 90 percent accuracy on this dataset."


class ScriptedProvider:
    """Synthetic responses, for testing wiring only; no model performance claims."""
    model = "offline-test"
    test_only = True

    def __init__(self):
        self.tasks = []
        self.bad_quote = False
        self.bad_evidence_id = False
        self.status = "SUPPORTED"
        self.empty_extraction = False

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        self.tasks.append(task)
        if task == "extract_evidence":
            if self.empty_extraction:
                return {"facts": []}
            fact = {"claim": QUOTE, "quote": "Invented quote" if self.bad_quote else QUOTE}
            return {"facts": [fact, fact]}
        if task == "research_direction":
            return {"title": "Test proposal", "research_question": "Does accuracy transfer?",
                    "gap": "Transfer needs study in these selected papers.",
                    "contribution": "A proposed transfer evaluation.",
                    "methodology": "We will evaluate another dataset.",
                    "technical_terms": ["accuracy"], "limitations": [], "unknowns": ["Dataset selection"]}
        if task == "draft_v0":
            package = payload["package"]
            sid = package["sources"][0]["source_id"]
            return {"schema_version": "0.1", "package_id": package["package_id"],
                    "paragraphs": [{"paragraph_id": f"D{i}", "section": section,
                                    "text": f"{QUOTE} [[{sid}]] We will evaluate another dataset.",
                                    "claim_ids": [c["claim_id"] for c in package["claims"]]}
                                   for i, section in enumerate(SECTIONS)]}
        if task == "extract_draft_claims":
            return {"statements": [{"text": QUOTE, "kind": "factual"},
                                   {"text": "We will evaluate another dataset.", "kind": "proposal"}]}
        if task == "verify_draft_claim":
            return {"status": self.status, "reason": "Synthetic test judgment.",
                    "evidence_ids": ["UNKNOWN" if self.bad_evidence_id else payload["evidence"][0]["evidence_id"]]}
        raise AssertionError(task)


class ResearchPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pdf = self.root / "study.pdf"
        with fitz.open() as document:
            page = document.new_page()
            page.insert_text((72, 72), QUOTE)
            document.save(self.pdf)
        self.provider = ScriptedProvider()

    def build(self):
        self.store = RunStore(self.root / "build")
        self.package = build_research_package("accuracy transfer", read_pdfs([self.pdf]), self.provider, self.store)
        return self.package

    def test_pdf_to_package_workbook_draft_and_fresh_verdicts(self):
        package = self.build()
        self.assertEqual(ResearchPackage.from_dict(asdict(package)), package)
        self.assertEqual(len(package.evidence), 1)  # Duplicate extraction removed.
        facts_path = self.store.directory / "master_facts.xlsx"
        facts = load_facts(facts_path, package)
        self.assertEqual(facts[0]["verification"], "UNREVIEWED")
        self.assertEqual(facts[0]["page"], "1")
        draft_store = RunStore(self.root / "draft")
        draft, results = generate_and_check(package, facts_path, self.provider, self.provider, draft_store)
        self.assertEqual(Draft.from_dict(asdict(draft), package), draft)
        self.assertEqual(results["counts"]["SUPPORTED"], 6)
        self.assertEqual(results["factual_claim_count"], 6)
        self.assertEqual(self.provider.tasks.count("verify_draft_claim"), 6)
        self.assertTrue((self.store.directory / "build_manifest.json").is_file())
        self.assertTrue((draft_store.directory / "draft_manifest.json").is_file())
        self.assertEqual(load_facts(facts_path, package)[0]["verification"], "UNREVIEWED")
        self.provider.status = "CONTRADICTED"
        fresh = check_draft(draft, package, facts_path, self.provider)
        self.assertEqual(fresh["counts"]["CONTRADICTED"], 6)

    def test_hallucinated_quote_cannot_create_completed_package(self):
        self.provider.bad_quote = True
        with self.assertRaisesRegex(ValueError, "No relevant evidence"):
            self.build()
        self.assertFalse((self.store.directory / "build_manifest.json").exists())
        self.assertFalse((self.store.directory / "master_facts.xlsx").exists())

    def test_no_relevant_evidence_stops_before_synthesis(self):
        self.provider.empty_extraction = True
        with self.assertRaisesRegex(ValueError, "No relevant evidence"):
            self.build()
        self.assertNotIn("research_direction", self.provider.tasks)

    def test_scanned_pdf_requires_ocr(self):
        path = self.root / "scan.pdf"
        with fitz.open() as document:
            document.new_page()
            document.save(path)
        with self.assertRaisesRegex(ValueError, "OCR"):
            read_pdfs([path])

    def test_duplicate_pdf_uploaded_once(self):
        self.assertEqual(len(read_pdfs([self.pdf, self.pdf])), 1)

    def test_mismatched_workbook_is_rejected_before_model_calls(self):
        package = self.build()
        path = self.store.directory / "master_facts.xlsx"
        workbook = openpyxl.load_workbook(path)
        workbook["Master"]["E2"] = "Replaced passage"
        workbook.save(path)
        with self.assertRaisesRegex(ValueError, "differs"):
            load_facts(path, package)

    def test_unknown_judgment_evidence_is_rejected(self):
        package = self.build()
        store = RunStore(self.root / "draft")
        self.provider.bad_evidence_id = True
        with self.assertRaisesRegex(ValueError, "outside retrieved"):
            generate_and_check(package, self.store.directory / "master_facts.xlsx", self.provider, self.provider, store)
        self.assertFalse((store.directory / "draft_manifest.json").exists())

    def test_uncited_factual_claim_has_insufficient_evidence(self):
        package = self.build()
        response = self.provider.generate("draft_v0", "", {"package": asdict(package)}, {}, 1)
        # A proposal paragraph can still contain an unsupported factual addition.
        response["paragraphs"][0]["text"] = QUOTE + " We will evaluate another dataset."
        response["paragraphs"][0]["claim_ids"] = ["C_PROPOSAL"]
        draft = Draft.from_dict(response, package)
        results = check_draft(draft, package, self.store.directory / "master_facts.xlsx", self.provider)
        self.assertEqual(results["counts"]["INSUFFICIENT_EVIDENCE"], 1)

    def test_excel_source_titles_are_literal_text(self):
        papers = read_pdfs([self.pdf])
        papers[0]["title"] = "=1+1"
        store = RunStore(self.root / "literal")
        build_research_package("accuracy", papers, self.provider, store)
        book = openpyxl.load_workbook(store.directory / "master_facts.xlsx")
        self.assertEqual(book["Master"]["C2"].value, "=1+1")
        self.assertEqual(book["Master"]["C2"].data_type, "s")

    def test_retries_use_new_directories(self):
        self.build()
        with self.assertRaises(FileExistsError):
            RunStore(self.root / "build")


if __name__ == "__main__":
    unittest.main()
