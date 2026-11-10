"""Integration tests for exporting reviewed topic folders to Half 2."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from research_package_automation.export_reviewed_topic import export_topic


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sprint2_demo"))
from project_io import validate_upload  # noqa: E402


class ReviewedTopicExportTests(unittest.TestCase):
    def test_cluster6_exports_and_passes_half2_upload_validation(self):
        topic = ROOT / "drafts" / "track3_four_cluster_v0" / "cluster6"
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "handover"
            manifest = export_topic(topic, output)
            package, draft, handover = validate_upload(
                (output / "research_package.json").read_bytes(),
                (output / "v0.json").read_bytes(),
            )
            self.assertEqual(package.package_id, "cluster6_faithfulness_audit_v0")
            self.assertEqual(set(p.section for p in draft.paragraphs),
                             {"abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"})
            self.assertTrue(all(source.url.startswith("https://") for source in package.sources))
            self.assertEqual(set(package.technical_terms), {"neutral rewrite", "answer re-injection"})
            self.assertFalse(manifest["production_ready"])
            self.assertEqual(handover["input_origin"], "uploaded")
            saved = json.loads((output / "research_package.json").read_text())
            self.assertEqual(saved["schema_version"], "0.1")


if __name__ == "__main__":
    unittest.main()
