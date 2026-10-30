"""Sample-attribution regressions; fixtures are synthetic, not paper results."""
from copy import deepcopy
import json
import unittest

from polymer_cards_lib.validation import build_cards


def fixture():
    parts = {
        "identity": "Polymer P1 was synthesized.",
        "neat": "A P1 film was cast after solvent evaporation.",
        "salted": "P1/LiFSI electrolyte was prepared by adding LiFSI to P1.",
        "comparison": "The electrolyte labelled P1 showed 3.8 V, compared with 4.2 V for P2.",
        "transform": "P1 solutions were mixed with LiFSI to obtain P1/LiFSI electrolyte.",
        "neat-comparison": "The neat P1 film had strength 5 MPa, compared with P1/LiFSI at 4 MPa.",
        "both-forms": "The neat P1 film was compared with the P1/LiFSI electrolyte.",
        "other-name": "P10/LiFSI electrolyte was prepared.",
    }
    doc = {"paper_id": "fixture", "chunks": [{"chunk_id": k, "text": v, "source_part": "synthetic",
            "locator": k, "document_sha256": "a" * 64} for k, v in parts.items()]}
    ev = lambda k: [{"chunk_id": k, "quote": parts[k]}]
    entity = {"entity_id": "p1", "name": "P1", "identity_evidence": ev("identity"),
              "classification": {"is_polymer": True, "reason": "The source names a polymer.", "evidence": ev("identity")},
              "specimens": [{"specimen_id": "neat", "label": "P1", "evidence": ev("neat")},
                            {"specimen_id": "salted", "label": "P1/LiFSI", "evidence": ev("salted")}],
              "properties": {"status": "reported", "items": [{"entity_id": "p1", "property": "voltage",
                    "value": "3.8", "unit": "V", "specimen_id": "neat", "specimen_evidence": ev("salted"),
                    "conditions": [], "evidence": ev("comparison")}]} }
    return doc, {"paper_id": "fixture", "entities": [entity]}, ev


class PolymerSampleLinkTests(unittest.TestCase):
    def test_additive_preparation_cannot_support_a_bare_sample_link(self):
        for sample_quote in ("salted", "transform"):
            with self.subTest(sample_quote=sample_quote):
                doc, raw, ev = fixture()
                raw["entities"][0]["properties"]["items"][0]["specimen_evidence"] = ev(sample_quote)
                result = build_cards(doc, raw)
                self.assertEqual(1, len(result["cards"]))
                self.assertEqual([], result["cards"][0]["properties"]["items"])
                self.assertIn("property_sample_evidence_names_alternate_form", [q["reason"] for q in result["review_queue"]])
                # The validator must hold the old link, never invent a replacement.
                self.assertEqual("neat", result["review_queue"][0]["record"]["specimen_id"])

    def test_additive_form_cannot_be_hidden_by_omitting_a_sibling_specimen(self):
        for operator in ("/", "+", " with "):
            with self.subTest(operator=operator):
                doc, raw, _ = fixture()
                quote = "P1" + operator + "LiFSI electrolyte was prepared."
                doc["chunks"].append({"chunk_id": "omitted-form", "text": quote, "source_part": "synthetic",
                    "locator": "Preparation", "document_sha256": "a" * 64})
                e = raw["entities"][0]
                e["specimens"] = e["specimens"][:1]
                e["properties"]["items"][0]["specimen_evidence"] = [{"chunk_id": "omitted-form", "quote": quote}]
                result = build_cards(doc, raw)
                self.assertEqual([], result["cards"][0]["properties"]["items"])
                self.assertIn("property_sample_evidence_names_alternate_form", [q["reason"] for q in result["review_queue"]])

    def test_slash_inside_the_full_chosen_polymer_name_is_preserved(self):
        doc, raw, _ = fixture()
        doc, raw = json.loads(json.dumps([doc, raw]).replace("P1", "A/B"))
        e = raw["entities"][0]
        e["specimens"] = e["specimens"][:1]
        prop = e["properties"]["items"][0]
        prop["specimen_evidence"] = deepcopy(e["specimens"][0]["evidence"])
        result = build_cards(doc, raw)
        self.assertEqual("A/B", result["cards"][0]["name"])
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))

    def test_unit_slash_is_not_treated_as_an_additive_component(self):
        doc, raw, _ = fixture()
        doc, raw = json.loads(json.dumps([doc, raw]).replace("P1", "S"))
        quote = "The S film conductivity was 5 S/cm."
        doc["chunks"].append({"chunk_id": "units", "text": quote, "source_part": "synthetic",
            "locator": "Measurement", "document_sha256": "a" * 64})
        e = raw["entities"][0]
        e["specimens"] = e["specimens"][:1]
        e["properties"]["items"][0].update(property="conductivity", value="5", unit="S/cm",
            evidence=[{"chunk_id": "units", "quote": quote}], specimen_evidence=[{"chunk_id": "units", "quote": quote}])
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_source_named_lowercase_component_needs_a_material_form_context(self):
        doc, raw, _ = fixture()
        quote = "P1/silica composite film was prepared."
        doc["chunks"].append({"chunk_id": "composite", "text": quote, "source_part": "synthetic",
            "locator": "Preparation", "document_sha256": "a" * 64})
        e = raw["entities"][0]
        e["specimens"] = e["specimens"][:1]
        e["properties"]["items"][0]["specimen_evidence"] = [{"chunk_id": "composite", "quote": quote}]
        self.assertEqual([], build_cards(doc, raw)["cards"][0]["properties"]["items"])

    def test_result_comparison_does_not_reject_separate_neat_preparation(self):
        doc, raw, ev = fixture()
        prop = raw["entities"][0]["properties"]["items"][0]
        prop.update(property="strength", value="5", unit="MPa", evidence=ev("neat-comparison"), specimen_evidence=ev("neat"))
        card = build_cards(doc, raw)["cards"][0]
        self.assertEqual("neat", card["properties"]["items"][0]["specimen_id"])

    def test_explicit_neat_link_can_coexist_with_an_alternate_form(self):
        doc, raw, ev = fixture()
        prop = raw["entities"][0]["properties"]["items"][0]
        prop.update(property="strength", value="5", unit="MPa", evidence=ev("neat-comparison"), specimen_evidence=ev("both-forms"))
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_correct_additive_specimen_is_preserved_with_shorthand_results(self):
        doc, raw, ev = fixture()
        raw["entities"][0]["properties"]["items"][0]["specimen_id"] = "salted"
        result = build_cards(doc, raw)
        self.assertEqual("salted", result["cards"][0]["properties"]["items"][0]["specimen_id"])

    def test_name_boundaries_and_other_samples_do_not_create_a_false_mismatch(self):
        doc, raw, ev = fixture()
        raw["entities"][0]["properties"]["items"][0]["specimen_evidence"] = ev("other-name")
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_legacy_missing_extra_link_field_keeps_compatibility(self):
        doc, raw, _ = fixture()
        del raw["entities"][0]["properties"]["items"][0]["specimen_evidence"]
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_explicit_family_cannot_own_a_member_numeric_measurement(self):
        doc, raw, ev = fixture()
        raw["entities"][0]["identity_kind"] = "polymer_family"
        result = build_cards(doc, raw)
        self.assertEqual(1, len(result["cards"]))
        self.assertEqual("polymer_family", result["cards"][0]["identity_kind"])
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertIn("family_measurement_requires_specific_polymer", [q["reason"] for q in result["review_queue"]])

    def test_declared_specific_scope_is_preserved_and_invalid_scope_is_review(self):
        for kind, retained in [("specific_polymer", True), (None, True), ("invented_scope", False), ({}, False)]:
            with self.subTest(kind=kind):
                doc, raw, ev = fixture()
                raw["entities"][0]["identity_kind"] = kind
                raw["entities"][0]["properties"]["items"][0]["specimen_id"] = "salted"
                result = build_cards(doc, raw)
                self.assertEqual(retained, bool(result["cards"]))
                if retained:
                    self.assertEqual(kind, result["cards"][0]["identity_kind"])
                else:
                    self.assertEqual([], result["discarded_entities"])
                    self.assertIn("identity_kind_invalid", [q["reason"] for q in result["review_queue"]])

    def test_nonpolymer_cannot_simultaneously_declare_polymer_scope(self):
        doc, raw, _ = fixture()
        raw["entities"][0]["identity_kind"] = "polymer_family"
        raw["entities"][0]["classification"]["is_polymer"] = False
        result = build_cards(doc, raw)
        self.assertEqual([], result["cards"])
        self.assertEqual([], result["discarded_entities"])
        self.assertIn("nonpolymer_identity_kind_conflict", [q["reason"] for q in result["review_queue"]])

    def test_explicit_unknown_polymer_scope_does_not_bypass_numeric_family_guard(self):
        doc, raw, _ = fixture()
        raw["entities"][0]["identity_kind"] = None
        raw["entities"][0]["properties"]["items"][0]["specimen_id"] = "salted"
        result = build_cards(doc, raw)
        self.assertEqual(1, len(result["cards"]))
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertIn("measurement_polymer_scope_unresolved", [q["reason"] for q in result["review_queue"]])

    def test_member_digits_do_not_turn_a_qualitative_family_statement_into_a_number(self):
        doc, raw, _ = fixture()
        quote = "The family response was lower than P3."
        doc["chunks"].append({"chunk_id": "qualitative", "text": quote, "source_part": "synthetic",
            "locator": "qualitative", "document_sha256": "a" * 64})
        e = raw["entities"][0]
        e["identity_kind"] = "polymer_family"
        e["properties"]["items"][0].update(value="lower than P3", unit=None, specimen_id="salted",
            evidence=[{"chunk_id": "qualitative", "quote": quote}])
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_scope_and_link_checks_do_not_mutate_inputs(self):
        doc, raw, ev = fixture()
        before_doc, before_raw = deepcopy(doc), deepcopy(raw)
        build_cards(doc, raw)
        self.assertEqual(before_doc, doc)
        self.assertEqual(before_raw, raw)


if __name__ == "__main__":
    unittest.main()
