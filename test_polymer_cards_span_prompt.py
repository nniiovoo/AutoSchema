"""Live span selection prevents rewritten quotations and exposes method links."""
from copy import deepcopy
import json
import unittest

from polymer_cards_lib import prompt


class PolymerSpanPromptTests(unittest.TestCase):
    def test_live_evidence_requires_source_span_ids_instead_of_model_quotations(self):
        output = prompt.build_response_format()["json_schema"]
        self.assertEqual("polymer_cards_strict_v4", output["name"])
        evidence = output["schema"]["$defs"]["evidence"]
        self.assertEqual({"chunk_id", "span_id"}, set(evidence["properties"]))
        self.assertNotIn("quote", evidence["properties"])

    def test_fresh_payload_supplies_original_chunks_catalog_and_same_method_neighbors(self):
        document = {"paper_id": "synthetic", "title": "Synthetic protocols", "domains": [], "chunks": [
            {"chunk_id": "mechanical", "text": "Polymer Z film tensile tests used a crosshead speed of 7 mm min−1.",
             "locator": "Methods / Film testing, paragraph 2", "source_part": "main", "document_sha256": "a" * 64},
            {"chunk_id": "healing", "text": "After healing, the films were tested following the same procedure.",
             "locator": "Methods / Film testing, paragraph 3", "source_part": "main", "document_sha256": "a" * 64},
            {"chunk_id": "other", "text": "The reaction was stirred.",
             "locator": "Methods / Synthesis, paragraph 4", "source_part": "main", "document_sha256": "a" * 64},
        ]}
        before = deepcopy(document)
        payload = json.loads(prompt.build_user_prompt(document).split("\n", 1)[1])
        self.assertEqual(document["chunks"], payload["chunks"])
        self.assertTrue(payload["source_span_catalog"])
        for span in payload["source_span_catalog"]:
            source = next(c["text"] for c in document["chunks"] if c["chunk_id"] == span["chunk_id"])
            self.assertEqual(source[span["start"]:span["end"]], span["text"])
        link = next(c for c in payload["method_cross_reference_index"] if c["chunk_id"] == "healing")
        self.assertIn("mechanical", link["adjacent_method_chunk_ids"])
        self.assertNotIn("other", link["adjacent_method_chunk_ids"])
        self.assertEqual(before, document)
        self.assertNotIn("previous_response", payload)
        self.assertNotIn("reference_answers", payload)

    def test_system_example_selects_synthetic_catalog_spans_and_keeps_legacy_fixture(self):
        text = prompt.build_system_prompt()
        example = json.loads(text.rsplit("\n", 1)[1])
        catalog = {(c["chunk_id"], c["span_id"]): c for c in example["source_span_catalog"]}
        refs = []

        def walk(value):
            if isinstance(value, dict):
                if "chunk_id" in value and ("quote" in value or "span_id" in value):
                    refs.append(value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(example["response"])
        self.assertTrue(refs)
        for ref in refs:
            self.assertEqual({"chunk_id", "span_id"}, set(ref))
            self.assertIn((ref["chunk_id"], ref["span_id"]), catalog)
        self.assertIn("SYNTHETIC", text)
        self.assertIn("post-healing", text)
        self.assertIn("identity_evidence", text)
        self.assertIn("quote", prompt.worked_example()[1]["entities"][0]["identity_evidence"][0])

    def test_revision_name_lookup_offers_catalog_ids_without_replacing_proposals(self):
        from polymer_cards_lib.repair import build_revision_context
        from test_polymer_cards_repair import fixture
        document, previous = fixture()
        before = deepcopy(previous)
        context = build_revision_context(document, previous)
        candidates = context["candidate_source_contexts"][0]["source_names"][0]["candidate_chunks"]
        self.assertTrue(candidates[0]["candidate_span_ids"])
        self.assertEqual(before, context["previous_response"])
        self.assertEqual(before, previous)


if __name__ == "__main__":
    unittest.main()
