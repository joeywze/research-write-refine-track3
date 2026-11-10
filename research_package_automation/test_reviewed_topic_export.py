"""Integration tests for exporting reviewed topic folders to Half 2."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_package_automation.export_reviewed_topic import export_topic
from research_package_automation.evidence_checker import load_facts
from research_package_automation.support.contracts import Draft, ResearchPackage


ROOT = Path(__file__).resolve().parents[1]


class ReviewedTopicExportTests(unittest.TestCase):
    def test_cluster6_exports_shared_package_and_draft_schema(self):
        topic = ROOT / "drafts" / "track3_four_cluster_v0" / "cluster6"
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "handover"
            manifest = export_topic(topic, output)
            saved = json.loads((output / "research_package.json").read_text())
            package = ResearchPackage.from_dict(saved)
            draft = Draft.from_dict(json.loads((output / "v0.json").read_text()), package)
            self.assertEqual(package.package_id, "cluster6_faithfulness_audit_v0")
            self.assertEqual(set(p.section for p in draft.paragraphs),
                             {"abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"})
            self.assertTrue(all(source.url.startswith("https://") for source in package.sources))
            self.assertEqual(set(package.technical_terms), {"neutral rewrite", "answer re-injection"})
            self.assertFalse(manifest["production_ready"])
            facts = load_facts(output / "master_facts.xlsx", package)
            self.assertEqual(len(facts), manifest["fact_check_records"])
            self.assertGreater(len(facts), len([claim for claim in package.claims if claim.kind == "source"]))
            self.assertEqual(saved["schema_version"], "0.1")


if __name__ == "__main__":
    unittest.main()
