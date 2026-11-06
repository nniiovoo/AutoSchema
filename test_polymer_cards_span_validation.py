"""Adversarial source-span integration checks through the real card validator."""
from copy import deepcopy
import unittest

from polymer_cards_lib.evidence_spans import build_span_catalog, resolve_span
from polymer_cards_lib.validation import build_cards


def document():
    chunks = [
        ("identity", "Polymer Q1 was synthesized from block B1."),
        ("preparation", "Purified Q1 was isolated with CH₂Cl₂ and tested by GPC using THF as eluent."),
        ("results", "For purified Q1, M_{n} = 63 KDa, M_{w} = 112 KDa and M_{w}/M_{n} = 1.77."),
        ("protocol", "Q1 films were tested at 10 mm min⁻¹."),
    ]
    return {"paper_id": "span-fixture", "title": "Synthetic source-span fixture", "chunks": [
        {"chunk_id": key, "text": text, "source_part": "main", "locator": key,
         "document_sha256": "a" * 64} for key, text in chunks]}


def span_ref(doc, chunk_id):
    text = next(chunk["text"] for chunk in doc["chunks"] if chunk["chunk_id"] == chunk_id)
    span = next(span for span in build_span_catalog(doc)
                if span["chunk_id"] == chunk_id and span["start"] == 0 and span["end"] == len(text))
    return {"chunk_id": chunk_id, "span_id": span["span_id"]}


def response(doc):
    ref = lambda chunk: [span_ref(doc, chunk)]
    prop = {"entity_id": "q1", "property": "GPC dispersity", "value": "1.77", "unit": None,
            "specimen_id": "q1-gpc", "specimen_evidence": ref("preparation"),
            "conditions": [{"name": "method", "value": "GPC", "evidence": ref("preparation")},
                           {"name": "eluent", "value": "THF", "evidence": ref("preparation")}],
            "evidence": ref("results")}
    entity = {
        "entity_id": "q1", "name": "Q1", "identity_kind": "specific_polymer",
        "identity_evidence": ref("identity"),
        "classification": {"is_polymer": True, "reason": "Source explicitly identifies a polymer.",
                           "evidence": ref("identity")},
        "specimens": [{"specimen_id": "q1-gpc", "label": "purified Q1 sample", "evidence": ref("preparation")}],
        "properties": {"status": "reported", "items": [prop], "conflicts": []},
        "source_tag": {"status": "reported", "items": [{"entity_id": "q1", "value": "author_synthesized",
                                                        "evidence": ref("identity")}]}}
    return {"paper_id": doc["paper_id"], "entities": [entity]}


def legacy_response(doc, proposal):
    result = deepcopy(proposal)

    def visit(value):
        if isinstance(value, dict):
            if set(value) == {"chunk_id", "span_id"}:
                exact = resolve_span(doc, value["chunk_id"], value["span_id"])
                return {"chunk_id": value["chunk_id"], "quote": exact["quote"]}
            return {key: visit(child) for key, child in value.items()}
        if isinstance(value, list):
            return [visit(child) for child in value]
        return value

    return visit(result)


class PolymerCardSpanValidationTests(unittest.TestCase):
    def setUp(self):
        self.doc = document()
        self.proposal = response(self.doc)

    @property
    def prop(self):
        return self.proposal["entities"][0]["properties"]["items"][0]

    def run_case(self):
        return build_cards(self.doc, self.proposal)

    def assert_property_held(self):
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]), result["review_queue"])
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertTrue(result["review_queue"])
        return result

    def test_selected_spans_resolve_exact_source_and_provenance_without_mutation(self):
        original_doc, original_proposal = deepcopy(self.doc), deepcopy(self.proposal)
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]), result["review_queue"])
        card = result["cards"][0]
        prop = card["properties"]["items"][0]
        original = next(chunk["text"] for chunk in self.doc["chunks"] if chunk["chunk_id"] == "results")
        evidence = prop["evidence"][0]
        self.assertEqual(original, evidence["quote"])
        self.assertIn("M_{w}/M_{n}", evidence["quote"])
        self.assertEqual("source_span_selection", evidence["evidence_origin"])
        self.assertEqual("source-spans-v1", evidence["catalog_version"])
        self.assertEqual("quote_matched", evidence["evidence_status"])
        self.assertEqual(0, evidence["source_start"])
        self.assertEqual(len(original), evidence["source_end"])
        self.assertEqual(self.prop["evidence"][0]["span_id"], evidence["span_id"])
        self.assertIn("CH₂Cl₂", prop["specimen_evidence"][0]["quote"])
        self.assertEqual(original_doc, self.doc)
        self.assertEqual(original_proposal, self.proposal)

    def test_unknown_cross_chunk_and_malformed_span_ids_hold_fact_not_polymer(self):
        original = deepcopy(self.prop["evidence"][0])
        cases = [
            {"chunk_id": "results", "span_id": "unknown-span"},
            {**original, "chunk_id": "preparation"},
            {"chunk_id": "unavailable", "span_id": original["span_id"]},
            {**original, "span_id": None}, {**original, "span_id": []},
            {**original, "span_id": True},
        ]
        for reference in cases:
            with self.subTest(reference=reference):
                self.prop["evidence"] = [reference]
                self.assert_property_held()

    def test_stale_text_or_source_digest_invalidates_selected_identity(self):
        for kind in ("text", "digest"):
            with self.subTest(kind=kind):
                self.doc = document()
                self.proposal = response(self.doc)
                if kind == "text":
                    self.doc["chunks"][0]["text"] += " New source revision."
                else:
                    self.doc["chunks"][0]["document_sha256"] = "b" * 64
                result = self.run_case()
                self.assertEqual([], result["cards"])
                self.assertEqual(1, result["statistics"]["classification_review_entities"])

    def test_reference_from_another_paper_cannot_be_reused_even_with_same_chunk_id(self):
        other = deepcopy(self.doc)
        other["paper_id"] = "a-different-paper"
        self.prop["evidence"] = [span_ref(other, "results")]
        self.assert_property_held()

    def test_span_reference_cannot_supply_quote_offsets_or_source_metadata(self):
        original = deepcopy(self.prop["evidence"][0])
        for extra in ({"quote": "1.77"}, {"quote": self.doc["chunks"][2]["text"]},
                      {"source_start": 0}, {"source_end": 99}, {"start": 0, "end": 99},
                      {"page": 999}, {"document_sha256": "b" * 64},
                      {"evidence_origin": "source_span_selection"}):
            with self.subTest(extra=extra):
                self.prop["evidence"] = [{**original, **extra}]
                self.assert_property_held()

    def test_legacy_quotes_stay_strict_and_can_coexist_with_span_refs(self):
        legacy = legacy_response(self.doc, self.proposal)
        result = build_cards(self.doc, legacy)
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))
        legacy["entities"][0]["properties"]["items"][0]["evidence"][0]["quote"] = (
            self.doc["chunks"][2]["text"].replace("M_{n}", "Mn").replace("M_{w}", "Mw"))
        result = build_cards(self.doc, legacy)
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertTrue(any(q["reason"] == "quote_not_in_original_source" for q in result["review_queue"]))
        mixed = legacy_response(self.doc, self.proposal)
        mixed["entities"][0]["properties"]["items"][0]["evidence"].append(deepcopy(self.prop["evidence"][0]))
        result = build_cards(self.doc, mixed)
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))
        self.assertEqual(2, len(result["cards"][0]["properties"]["items"][0]["evidence"]))

    def test_valid_span_does_not_fill_missing_values_conditions_or_sample_links(self):
        for kind in ("wrong_value", "wrong_parent", "unknown_sample", "missing_sample"):
            with self.subTest(kind=kind):
                self.proposal = response(self.doc)
                if kind == "wrong_value":
                    self.prop["value"] = "9.99"
                elif kind == "wrong_parent":
                    self.prop["entity_id"] = "other-polymer"
                elif kind == "unknown_sample":
                    self.prop["specimen_id"] = "another-sample"
                else:
                    self.prop["specimen_id"] = None
                self.assert_property_held()
        self.proposal = response(self.doc)
        self.prop["conditions"] = []
        self.prop["specimen_evidence"].append(span_ref(self.doc, "protocol"))
        accepted = self.run_case()["cards"][0]["properties"]["items"][0]
        self.assertEqual([], accepted["conditions"])
        self.assertEqual("not_captured", accepted["conditions_review_status"])
        self.assertEqual("1.77", accepted["value"])
        self.assertIsNone(accepted["unit"])

    def test_source_span_does_not_reassign_salted_measurement_to_neat_film(self):
        for key, text in [
            ("neat", "A Q1 film was prepared without salt."),
            ("salt", "Q1/LiFSI electrolyte was prepared by adding LiFSI."),
            ("conductivity", "Q1/LiFSI conductivity was 2.4 × 10⁻⁴ S cm⁻¹ at 30°C."),
        ]:
            self.doc["chunks"].append({"chunk_id": key, "text": text, "source_part": "main",
                                        "locator": key, "document_sha256": "a" * 64})
        self.proposal = response(self.doc)
        entity = self.proposal["entities"][0]
        entity["specimens"] = [
            {"specimen_id": "neat", "label": "Q1 film", "evidence": [span_ref(self.doc, "neat")]},
            {"specimen_id": "salted", "label": "Q1/LiFSI electrolyte", "evidence": [span_ref(self.doc, "salt")]},
        ]
        entity["properties"]["items"] = [{"entity_id": "q1", "property": "ionic conductivity",
            "value": "2.4 × 10⁻⁴", "unit": "S cm⁻¹", "specimen_id": "neat",
            "specimen_evidence": [span_ref(self.doc, "salt")], "conditions": [],
            "evidence": [span_ref(self.doc, "conductivity")]}]
        original = deepcopy(self.proposal)
        held = self.assert_property_held()
        self.assertTrue(any(q["reason"] == "property_sample_evidence_names_alternate_form"
                            for q in held["review_queue"]))
        self.assertEqual(original, self.proposal)
        self.assertEqual({"neat", "salted"}, {s["specimen_id"] for s in held["cards"][0]["specimens"]})


if __name__ == "__main__":
    unittest.main()
