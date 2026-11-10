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
    def test_all_four_new_topics_export_shared_schema(self):
        expected_ids = {
            0: "cluster0_hallucination_invariance_audit_v0",
            6: "cluster6_faithfulness_audit_v0",
            13: "cluster13_revision_history_audit_v0",
            18: "cluster18_singapore_safety_audit_v0",
        }
        for cluster, package_id in expected_ids.items():
            with self.subTest(cluster=cluster), TemporaryDirectory() as temporary:
                topic = ROOT / "drafts" / "track3_four_cluster_v0" / f"cluster{cluster}"
                output = Path(temporary) / "handover"
                manifest = export_topic(topic, output)
                saved = json.loads((output / "research_package.json").read_text())
                package = ResearchPackage.from_dict(saved)
                draft = Draft.from_dict(json.loads((output / "v0.json").read_text()), package)
                self.assertEqual(package.package_id, package_id)
                self.assertEqual(set(p.section for p in draft.paragraphs),
                                 {"abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"})
                self.assertTrue(all(source.url.startswith("https://") for source in package.sources))
                self.assertTrue(all(term.lower() in "\n".join(p.text for p in draft.paragraphs).lower()
                                    for term in package.technical_terms))
                self.assertEqual(manifest["status"], "PROVISIONAL_AUTOMATED_MAPPING")
                self.assertFalse(manifest["production_ready"])
                self.assertEqual(manifest["fact_check_status"], "NOT_RUN")
                facts = load_facts(output / "master_facts.xlsx", package)
                self.assertEqual(len(facts), manifest["fact_check_records"])
                self.assertGreaterEqual(len(facts), len([claim for claim in package.claims if claim.kind == "source"]))
                self.assertEqual(saved["schema_version"], "0.1")

    def test_five_topic_index_resolves_and_preserves_status_boundary(self):
        index = json.loads((ROOT / "drafts" / "track3_five_topic_index.json").read_text())
        self.assertEqual([topic["id"] for topic in index["topics"]],
                         ["cluster7", "cluster0", "cluster6", "cluster13", "cluster18"])
        for topic in index["topics"]:
            for field in ("package", "draft", "manifest"):
                self.assertTrue((ROOT / topic[field]).is_file(), f"Missing {topic['id']} {field}")
            package = ResearchPackage.from_dict(json.loads((ROOT / topic["package"]).read_text()))
            Draft.from_dict(json.loads((ROOT / topic["draft"]).read_text()), package)
            if topic["id"] == "cluster7":
                self.assertEqual(topic["status"], "REVIEWED_HANDOVER")
                self.assertTrue(topic["production_ready"])
            else:
                self.assertEqual(topic["status"], "PROVISIONAL_AUTOMATED_MAPPING")
                self.assertFalse(topic["production_ready"])
                self.assertTrue((ROOT / topic["facts"]).is_file())
                if topic["id"] == "cluster6":
                    self.assertEqual(topic["fact_check_status"], "COMPLETED")
                    self.assertTrue((ROOT / topic["fact_check_summary"]).is_file())
                    self.assertTrue((ROOT / topic["fact_check_results"]).is_file())
                else:
                    self.assertEqual(topic["fact_check_status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
