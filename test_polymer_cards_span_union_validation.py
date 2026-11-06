"""A qualified observation may be covered by adjacent selected passages."""
from copy import deepcopy
import unittest

from polymer_cards_lib.evidence_spans import build_span_catalog
from polymer_cards_lib.validation import build_cards


class PolymerSpanUnionValidationTests(unittest.TestCase):
    def fixture(self, include_qualifier=True):
        text = "Polymer R1 film was prepared. R1 film reached ca. 456% strain at break."
        doc = {"paper_id": "union-fixture", "chunks": [{"chunk_id": "original", "text": text,
               "source_part": "synthetic", "locator": "Results", "document_sha256": "a" * 64}]}
        catalog = build_span_catalog(doc)
        full = catalog[0]
        qualifier = next(s for s in catalog if s["text"] == "R1 film reached ca.")
        number = next(s for s in catalog if s["text"] == "456% strain at break.")
        ref = lambda s: {"chunk_id": "original", "span_id": s["span_id"]}
        identity = [ref(full)]
        evidence = [ref(qualifier), ref(number)] if include_qualifier else [ref(number)]
        raw = {"paper_id": doc["paper_id"], "entities": [{"entity_id": "r1", "name": "R1",
            "classification": {"is_polymer": True, "reason": "Source calls it a polymer", "evidence": identity},
            "identity_evidence": identity,
            "specimens": [{"specimen_id": "film", "label": "R1 film", "evidence": identity}],
            "properties": {"status": "reported", "items": [{"entity_id": "r1", "property": "strain at break",
                "value": "ca. 456%", "unit": "%", "specimen_id": "film", "specimen_evidence": identity,
                "conditions": [], "evidence": evidence}]}}]}
        return doc, raw

    def test_selected_adjacent_context_supports_full_qualifier_with_explicit_union(self):
        doc, raw = self.fixture()
        before = deepcopy(raw)
        result = build_cards(doc, raw)
        prop = result["cards"][0]["properties"]["items"][0]
        support = next(e for e in prop["evidence"] if e.get("evidence_origin") == "source_span_selection_union")
        self.assertEqual("R1 film reached ca. 456% strain at break.", support["quote"])
        self.assertEqual(2, len(support["span_ids"]))
        self.assertNotIn("span_id", support)
        self.assertEqual(before, raw)

    def test_an_unselected_qualifier_cannot_be_borrowed_from_the_chunk(self):
        doc, raw = self.fixture(include_qualifier=False)
        result = build_cards(doc, raw)
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertIn("property_value_not_in_original_evidence", [q["reason"] for q in result["review_queue"]])


if __name__ == "__main__":
    unittest.main()
