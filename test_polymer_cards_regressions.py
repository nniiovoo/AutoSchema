"""Regression checks for defects found in the first real-paper pilot."""
from copy import deepcopy
import unittest

from polymer_cards_lib.validation import build_cards


def fixture(measurement="P1/LiFSI had Mw/Mn = 1.77.", value="1.77"):
    text = ("Polymer P1 was synthesized. P1 film was cast. "
            "P1/LiFSI electrolyte was prepared at a mass ratio of 2:1. " + measurement)
    ev = lambda quote: [{"chunk_id": "c", "quote": quote}]
    document = {"paper_id": "regression", "chunks": [{"chunk_id": "c", "text": text,
                "source_part": "main", "locator": "Methods and Results", "document_sha256": "a" * 64}]}
    entity = {"entity_id": "p1", "name": "P1", "identity_evidence": ev("Polymer P1"),
              "classification": {"is_polymer": True, "reason": "Source calls it a polymer.", "evidence": ev("Polymer P1")},
              "specimens": [{"specimen_id": "salted", "label": "P1/LiFSI", "evidence": ev("P1/LiFSI electrolyte was prepared")},
                            {"specimen_id": "neat", "label": "P1", "evidence": ev("P1 film was cast")}],
              "properties": {"status": "reported", "items": [{"entity_id": "p1", "property": "measurement",
                    "value": value, "unit": None, "specimen_id": "salted", "conditions": [], "evidence": ev(measurement)}]}}
    return document, {"paper_id": document["paper_id"], "entities": [entity]}


class PolymerPilotRegressionTests(unittest.TestCase):
    def test_sentence_final_decimal_is_kept_but_decimal_fragments_are_not(self):
        for value, measurement, accepted in [
            ("1.77", "P1/LiFSI had Mw/Mn = 1.77.", True),
            ("1", "P1/LiFSI had Mw/Mn = 1.77.", False),
            ("1.77", "P1/LiFSI had Mw/Mn = 1.77.5.", False),
            ("1.77", "P1/LiFSI had Mw/Mn = 1.77, with no units.", True),
        ]:
            with self.subTest(value=value, measurement=measurement):
                doc, raw = fixture(measurement, value)
                result = build_cards(doc, raw)
                self.assertEqual(accepted, bool(result["cards"][0]["properties"]["items"]))

    def test_ratio_and_fraction_denominators_are_not_new_scalar_measurements(self):
        for text in ("2:1", "2 : 1", "2/1", "2 / 1"):
            for value in ("1", "2"):
                with self.subTest(text=text, value=value):
                    doc, raw = fixture("P1/LiFSI measurement was " + text + " units", value)
                    self.assertEqual([], build_cards(doc, raw)["cards"][0]["properties"]["items"])

    def test_braced_and_unicode_exponents_cannot_supply_partial_values(self):
        cases = [("5", "7.3 × 10^{5}", False), ("-4", "2.4 × 10^{-4}", False),
                 ("10^{5}", "7.3 × 10^{5}", False), ("10⁵", "7.3 × 10⁵", False),
                 ("7.3 × 10^{5}", "7.3 × 10^{5}", True), ("10⁵", "10⁵", True)]
        for value, measured, accepted in cases:
            with self.subTest(value=value, measured=measured):
                doc, raw = fixture("P1/LiFSI measurement was " + measured + " units", value)
                self.assertEqual(accepted, bool(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_qualified_numeric_values_cannot_stop_before_a_decimal(self):
        for value, measured, accepted in [("beyond 5", "beyond 5.9", False),
                ("<1", "<1.7", False), ("approximately 1", "approximately 1.77", False),
                ("beyond 5.9", "beyond 5.9", True), ("<1.7", "<1.7", True)]:
            with self.subTest(value=value, measured=measured):
                doc, raw = fixture("P1/LiFSI measurement was " + measured + " units", value)
                self.assertEqual(accepted, bool(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_numeric_qualifiers_cannot_be_lost(self):
        for measured in ("beyond 5.0", ">5.0", "at least 5.0", "approximately 5.0"):
            for value, accepted in (("5.0", False), (measured, True)):
                with self.subTest(value=value, measured=measured):
                    doc, raw = fixture("P1/LiFSI measurement was " + measured + " V", value)
                    self.assertEqual(accepted, bool(build_cards(doc, raw)["cards"][0]["properties"]["items"]))

    def test_optional_unknown_specimen_scope_is_not_invented(self):
        doc, raw = fixture()
        e = raw["entities"][0]
        e["composition"] = {"status": "reported", "items": [{"entity_id": "p1", "value": "2:1", "basis": "mass_ratio",
            "specimen_id": None, "evidence": [{"chunk_id": "c", "quote": "mass ratio of 2:1"}]}]}
        e["synthesis_text"] = {"status": "reported", "items": [{"entity_id": "p1", "value": "P1 was synthesized.",
            "specimen_id": None, "evidence": [{"chunk_id": "c", "quote": "Polymer P1 was synthesized."}]}]}
        c = build_cards(doc, raw)["cards"][0]
        self.assertEqual(1, len(c["composition"]["items"]))
        self.assertNotIn("specimen_id", c["composition"]["items"][0])
        self.assertEqual(1, len(c["synthesis_text"]["items"]))
        e["properties"]["items"][0]["specimen_id"] = None
        self.assertEqual([], build_cards(doc, raw)["cards"][0]["properties"]["items"])

    def test_molecular_weight_only_is_not_accepted_as_a_composition_recipe(self):
        doc, raw = fixture()
        for value in ("M_{w} = 4,600 g mol⁻¹", "Mw = 4,600 g mol⁻¹"):
            with self.subTest(value=value):
                doc["chunks"][0]["text"] += " " + value
                raw["entities"][0]["composition"] = {"status": "reported", "items": [{"entity_id": "p1",
                    "value": value, "basis": "component_amounts", "specimen_id": None,
                    "evidence": [{"chunk_id": "c", "quote": value}]}]}
                result = build_cards(doc, raw)
                self.assertEqual([], result["cards"][0]["composition"]["items"])
                self.assertIn("composition_contains_molecular_weight_only", [q["reason"] for q in result["review_queue"]])
        value = "Mw = 4,600 g mol⁻¹; polymer:salt mass ratio 2:1"
        doc["chunks"][0]["text"] += " " + value
        raw["entities"][0]["composition"]["items"][0].update(value=value, evidence=[{"chunk_id": "c", "quote": value}])
        self.assertEqual(1, len(build_cards(doc, raw)["cards"][0]["composition"]["items"]))

    def test_requested_sample_link_evidence_must_be_original_and_nonempty(self):
        for refs, accepted in [([], False), ([{"chunk_id": "c", "quote": "invented preparation"}], False),
                              ([{"chunk_id": "c", "quote": "P1/LiFSI electrolyte was prepared"}], True)]:
            with self.subTest(refs=refs):
                doc, raw = fixture()
                raw["entities"][0]["properties"]["items"][0]["specimen_evidence"] = refs
                result = build_cards(doc, raw)
                self.assertEqual(accepted, bool(result["cards"][0]["properties"]["items"]))
                if accepted:
                    self.assertEqual("quote_matched", result["cards"][0]["properties"]["items"][0]["specimen_evidence"][0]["evidence_status"])

    def test_source_transformations_are_propagated_and_cannot_be_spoofed(self):
        doc, raw = fixture()
        doc["chunks"][0]["text_transformations"] = ["jats_script_notation_v1"]
        ev = build_cards(doc, raw)["cards"][0]["identity_evidence"][0]
        self.assertEqual(["jats_script_notation_v1"], ev["text_transformations"])
        raw["entities"][0]["identity_evidence"][0]["text_transformations"] = []
        self.assertEqual([], build_cards(doc, raw)["cards"])

    def test_shared_specimen_labels_warn_without_merging_or_dropping_cards(self):
        doc, raw = fixture()
        doc["chunks"][0]["text"] += " Polymer P2 was synthesized."
        second = deepcopy(raw["entities"][0])
        second.update(entity_id="p2", name="P2", identity_evidence=[{"chunk_id": "c", "quote": "Polymer P2"}],
                      classification={"is_polymer": True, "reason": "Polymer in source", "evidence": [{"chunk_id": "c", "quote": "Polymer P2"}]})
        second["properties"] = {"status": "not_found_in_provided_text", "items": []}
        raw["entities"].append(second)
        result = build_cards(doc, raw)
        self.assertEqual(2, len(result["cards"]))
        warnings = [w for w in result["attribution_warnings"] if w["reason"] == "specimen_label_shared_between_polymer_records"]
        self.assertEqual({"P1", "P1/LiFSI"}, {w["specimen_label"] for w in warnings})
        self.assertEqual(["p1", "p2"], warnings[0]["related_entity_ids"])
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))
        # The same label in a separate paper has no cross-paper effect.
        self.assertFalse(build_cards(doc, {"paper_id": doc["paper_id"], "entities": raw["entities"][:1]})["attribution_warnings"])

    def test_neat_versus_additive_ambiguity_is_flagged_without_automatic_relink(self):
        doc, raw = fixture("P1 showed a stability window of 3.8 V.", "3.8")
        prop = raw["entities"][0]["properties"]["items"][0]
        prop.update(specimen_id="neat", unit="V")
        result = build_cards(doc, raw)
        self.assertEqual("neat", result["cards"][0]["properties"]["items"][0]["specimen_id"])
        self.assertIn("specimen_form_ambiguous", [w["reason"] for w in result["attribution_warnings"]])
        doc, raw = fixture("The neat P1 film had a strength of 5 MPa.", "5")
        raw["entities"][0]["properties"]["items"][0].update(specimen_id="neat", unit="MPa")
        self.assertFalse(build_cards(doc, raw)["attribution_warnings"])
        doc, raw = fixture("Unlike the neat P2 control, P1 showed a stability window of 3.8 V.", "3.8")
        raw["entities"][0]["properties"]["items"][0].update(specimen_id="neat", unit="V")
        self.assertIn("specimen_form_ambiguous", [w["reason"] for w in build_cards(doc, raw)["attribution_warnings"]])


if __name__ == "__main__":
    unittest.main()
