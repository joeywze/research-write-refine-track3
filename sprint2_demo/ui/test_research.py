"""Keep displayed findings tied to their original claim and support records."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import core
import research


class ResearchRecordTests(unittest.TestCase):
    def setUp(self):
        self.data = core.open_run(core.DEFAULT_RUN)

    def test_original_pilot_counts_and_passage_links(self):
        context = research.prepared_context(self.data)
        self.assertEqual(research.pilot_counts(context), (7, 3, 4))
        first = context["pilot_findings"][0]
        self.assertEqual(first["finding_id"], "D001")
        self.assertEqual(first["evidence"][0]["evidence_id"], "E001")
        self.assertEqual(first["evidence"][0]["passage_url"], "https://aclanthology.org/2025.findings-emnlp.587.pdf#page=3")

    def test_changed_labels_or_links_are_rejected(self):
        original = core.load(research.CONTEXT)
        for field, value in (("status", "SUPPORTED"), ("claim", "A rewritten finding")):
            modified = deepcopy(original)
            modified["pilot_findings"][1][field] = value
            with self.subTest(field=field), patch.object(core, "load", return_value=modified):
                with self.assertRaises(ValueError): research.prepared_context(self.data)

    def test_context_from_another_package_is_rejected(self):
        context = core.load(research.CONTEXT)
        context["package_hash"] = "different"
        with patch.object(core, "load", return_value=context):
            with self.assertRaises(ValueError): research.prepared_context(self.data)


if __name__ == "__main__":
    unittest.main()
