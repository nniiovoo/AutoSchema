"""Meaningful source-link and retention checks for the entity-card workflow."""
from copy import deepcopy
import unittest

from polymer_cards_lib.validation import FIELD_NAMES, build_cards


class PolymerCardValidationTests(unittest.TestCase):
    def setUp(self):
        self.document = {
            "paper_id": "test-paper", "title": "Fixture, not an experimental paper",
            "chunks": [{"chunk_id": "main-1", "source_part": "main", "locator": "Methods", "page": 2,
                        "document_sha256": "a" * 64,
                        "text": "Polymer P1 was synthesized from monomer M1. P1/LiFSI used mass ratio 2:1. "
                                "LiFSI is a lithium salt. PEO polymer was commercially purchased. "
                                "P1/LiFSI conductivity was 6.5 × 10−5 S cm−1 at 30°C and "
                                "6.5 × 10−5 S cm−1 at 60°C. Polymer feed was 1:2.4:1."}],
        }
        self.entity = {
            "entity_id": "P1", "name": "P1", "identity_evidence": self.ev("Polymer P1"),
            "classification": {"is_polymer": True, "reason": "Original source calls it a polymer.",
                               "evidence": self.ev("Polymer P1")},
            "specimens": [{"specimen_id": "salted", "label": "P1/LiFSI", "evidence": self.ev("P1/LiFSI used mass ratio 2:1")}],
            "source_tag": self.group(self.fact("author_synthesized", "P1 was synthesized")),
        }
        self.response = {"paper_id": "test-paper", "entities": [self.entity]}

    def ev(self, quote, **extra):
        return [{"chunk_id": "main-1", "quote": quote, **extra}]

    def fact(self, value, quote, **extra):
        return {"entity_id": "P1", "value": value, "evidence": self.ev(quote), **extra}

    def group(self, *items, status="reported"):
        return {"status": status, "items": list(items)}

    def property(self, temperature=30, value="6.5 × 10−5"):
        return self.fact(value, "P1/LiFSI conductivity was 6.5 × 10−5 S cm−1 at 30°C and 6.5 × 10−5 S cm−1 at 60°C",
                         property="ionic_conductivity", unit="S cm−1", specimen_id="salted",
                         conditions=[{"name": "temperature_C", "value": temperature,
                                      "evidence": self.ev(str(temperature) + "°C")}])

    def run_case(self):
        return build_cards(self.document, self.response)

    def test_low_performance_and_missing_information_do_not_remove_polymer(self):
        self.entity["properties"] = self.group(self.property())
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]))
        card = result["cards"][0]
        self.assertEqual("retained_polymer", card["decision"])
        self.assertEqual("6.5 × 10−5", card["properties"]["items"][0]["value"])
        for field in FIELD_NAMES:
            self.assertIn(field, card)
        self.assertEqual({"status": "not_found_in_provided_text", "items": []}, card["monomers"])
        self.assertEqual("not_performed_by_validator", card["semantic_review_status"])

    def test_commercial_polymer_is_retained_and_salt_can_stay_an_ingredient(self):
        self.entity["composition"] = self.group(self.fact("LiFSI, mass ratio 2:1", "P1/LiFSI used mass ratio 2:1", basis="mass_ratio", specimen_id="salted"))
        peo = {"entity_id": "PEO", "name": "PEO", "identity_evidence": self.ev("PEO polymer"),
               "classification": {"is_polymer": True, "reason": "Described as polymer.", "evidence": self.ev("PEO polymer")},
               "source_tag": self.group({"entity_id": "PEO", "value": "commercially_purchased", "evidence": self.ev("PEO polymer was commercially purchased")})}
        salt = {"entity_id": "salt", "name": "LiFSI", "identity_evidence": self.ev("LiFSI is a lithium salt"),
                "classification": {"is_polymer": False, "reason": "Lithium salt, not polymer.", "evidence": self.ev("LiFSI is a lithium salt")}}
        self.response["entities"] += [peo, salt]
        result = self.run_case()
        self.assertEqual(["P1", "PEO"], [c["entity_id"] for c in result["cards"]])
        self.assertEqual(["salt"], [e["entity_id"] for e in result["discarded_entities"]])
        self.assertIn("LiFSI", result["cards"][0]["composition"]["items"][0]["value"])

    def test_unknown_or_unquoted_classification_is_review_not_discard(self):
        for change in ("unknown", "false_without_evidence", "numeric_boolean", "identity_wrong_name"):
            with self.subTest(change=change):
                e = deepcopy(self.entity)
                if change == "unknown":
                    e["classification"]["is_polymer"] = None
                elif change == "false_without_evidence":
                    e["classification"].update(is_polymer=False, evidence=[])
                elif change == "numeric_boolean":
                    e["classification"]["is_polymer"] = 0
                else:
                    e["name"] = "Nonexistent polymer"
                result = build_cards(self.document, {"paper_id": "test-paper", "entities": [e]})
                self.assertEqual([], result["cards"])
                self.assertEqual([], result["discarded_entities"])
                self.assertEqual(1, result["statistics"]["classification_review_entities"])

    def test_invalid_fact_is_quarantined_without_losing_polymer(self):
        self.entity["monomers"] = self.group(self.fact("invented M2", "M2 was present"))
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]))
        self.assertEqual([], result["cards"][0]["monomers"]["items"])
        self.assertEqual("needs_review", result["cards"][0]["monomers"]["status"])
        self.assertEqual("quote_not_in_original_source", result["review_queue"][0]["reason"])

    def test_wrong_parent_or_specimen_cannot_receive_property(self):
        for mutation in ("parent", "specimen", "unhashable_specimen"):
            with self.subTest(mutation=mutation):
                p = self.property()
                p["entity_id" if mutation == "parent" else "specimen_id"] = ("other" if mutation != "unhashable_specimen" else {})
                self.entity["properties"] = self.group(p)
                result = self.run_case()
                self.assertEqual(1, len(result["cards"]))
                self.assertEqual([], result["cards"][0]["properties"]["items"])
                self.assertTrue(result["review_queue"])

    def test_repeated_value_at_different_temperatures_and_slashes_are_preserved(self):
        self.entity["properties"] = self.group(self.property(30), self.property(60))
        self.entity["composition"] = self.group(self.fact("P1/LiFSI; 2:1", "P1/LiFSI used mass ratio 2:1", basis="mass_ratio", specimen_id="salted"))
        self.entity["synthesis_text"] = self.group(self.fact("A sentence describing the synthesis of P1 from M1.", "Polymer P1 was synthesized from monomer M1"))
        card = self.run_case()["cards"][0]
        self.assertEqual(2, len(card["properties"]["items"]))
        self.assertEqual([30, 60], [p["conditions"][0]["value"] for p in card["properties"]["items"]])
        self.assertEqual("P1/LiFSI; 2:1", card["composition"]["items"][0]["value"])
        self.assertTrue(card["synthesis_text"]["items"][0]["value"].endswith("M1."))

    def test_property_value_unit_and_condition_require_their_own_literal_support(self):
        changes = [("value", "0.000065"), ("unit", "S/cm"), ("condition", 130)]
        for key, val in changes:
            with self.subTest(key=key):
                p = self.property()
                if key == "condition":
                    p["conditions"][0]["value"] = val
                else:
                    p[key] = val
                self.entity["properties"] = self.group(p)
                result = self.run_case()
                self.assertEqual([], result["cards"][0]["properties"]["items"])
                self.assertIn("not_in_original_evidence", result["review_queue"][0]["reason"])

    def test_source_metadata_is_resolved_and_forged_paper_or_page_is_rejected(self):
        result = self.run_case()
        ev = result["cards"][0]["identity_evidence"][0]
        self.assertEqual(2, ev["page"])
        self.assertEqual("Methods", ev["locator"])
        self.assertEqual("a" * 64, ev["document_sha256"])
        for changed in ({"paper_id": "another paper"}, {"page": 100}, {"document_sha256": "b" * 64}):
            with self.subTest(changed=changed):
                self.entity["identity_evidence"] = self.ev("Polymer P1", **changed)
                result = self.run_case()
                self.assertEqual([], result["cards"])
                self.assertTrue(result["review_queue"])

    def test_duplicate_ids_and_malformed_groups_are_visible(self):
        result = build_cards(self.document, {"paper_id": "test-paper", "entities": [self.entity, deepcopy(self.entity)]})
        self.assertEqual([], result["cards"])
        self.assertEqual(2, result["statistics"]["classification_review_entities"])
        self.entity["monomers"] = {"status": [], "items": []}
        self.entity["properties"] = []
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]))
        self.assertEqual("needs_review", result["cards"][0]["monomers"]["status"])
        self.assertEqual("needs_review", result["cards"][0]["properties"]["status"])

    def test_conflicting_source_tags_remain_visible_without_excluding_polymer(self):
        self.entity["source_tag"]["items"].append(self.fact("commercially_purchased", "PEO polymer was commercially purchased"))
        result = self.run_case()
        card = result["cards"][0]
        self.assertEqual("conflicting", card["source_tag"]["status"])
        self.assertEqual(2, len(card["source_tag"]["items"]))
        self.assertIn("not verified", result["validation_scope"])

    def test_whole_input_identity_nonfinite_and_duplicate_source_fail(self):
        with self.assertRaises(ValueError):
            build_cards(self.document, {"paper_id": "wrong", "entities": []})
        bad = deepcopy(self.response)
        bad["entities"][0]["description"] = {"value": float("inf"), "evidence": self.ev("P1")}
        with self.assertRaises(ValueError):
            build_cards(self.document, bad)
        doc = deepcopy(self.document)
        doc["chunks"].append(deepcopy(doc["chunks"][0]))
        with self.assertRaises(ValueError):
            build_cards(doc, self.response)
        doc = deepcopy(self.document)
        doc["chunks"][0]["document_sha256"] = "not-a-source-digest"
        with self.assertRaises(ValueError):
            build_cards(doc, self.response)

    def test_validation_does_not_mutate_input_or_claim_scientific_verification(self):
        self.entity["properties"] = self.group(self.property())
        original_doc, original_response = deepcopy(self.document), deepcopy(self.response)
        result = self.run_case()
        self.assertEqual(original_doc, self.document)
        self.assertEqual(original_response, self.response)
        self.assertEqual("quote_matched", result["cards"][0]["properties"]["items"][0]["evidence_status"])
        self.assertEqual("not_performed_by_validator", result["cards"][0]["properties"]["items"][0]["semantic_review_status"])

    def test_optional_identity_facts_need_not_repeat_parent_and_percent_units_work(self):
        self.entity["aliases"] = [{"value": "P1", "evidence": self.ev("Polymer P1")}]
        self.entity["description"] = {"value": "A synthesized polymer.", "evidence": self.ev("Polymer P1 was synthesized")}
        self.document["chunks"][0]["text"] += " P1/LiFSI recovery was 95% at 30°C."
        self.entity["properties"] = self.group(self.fact("95", "P1/LiFSI recovery was 95% at 30°C",
                    property="recovery", unit="%", specimen_id="salted", conditions=[]))
        card = self.run_case()["cards"][0]
        self.assertEqual(1, len(card["aliases"]))
        self.assertIsNotNone(card["description"])
        self.assertEqual("%", card["properties"]["items"][0]["unit"])

    def test_condition_parent_and_unit_prefix_mismatch_are_quarantined(self):
        prop = self.property()
        prop["conditions"][0]["entity_id"] = "another-polymer"
        self.entity["properties"] = self.group(prop)
        result = self.run_case()
        self.assertEqual("condition_parent_entity_mismatch", result["review_queue"][0]["reason"])
        self.document["chunks"][0]["text"] += " P1/LiFSI was 0.5mS/cm."
        self.entity["properties"] = self.group(self.fact("0.5", "P1/LiFSI was 0.5mS/cm",
                    property="conductivity", unit="S/cm", specimen_id="salted", conditions=[]))
        result = self.run_case()
        self.assertEqual("property_unit_not_in_original_evidence", result["review_queue"][0]["reason"])

    def test_numeric_fragments_cannot_replace_thousands_ranges_or_scientific_values(self):
        cases = [
            ("1", "1,000", "MPa"), ("000", "1,000", "MPa"),
            ("30", "30–60", "°C"), ("60", "30–60", "°C"),
            ("30", "30 – 60", "°C"), ("60", "30 — 60", "°C"),
            ("30", "30°C–60", "°C"), ("60", "30°C – 60", "°C"),
            ("30", "30-60", "°C"), ("60", "30−60", "°C"),
            ("2.4", "2.4 · 10−4", "S cm−1"),
            ("2.4", "2.4 ⋅ 10⁻⁴", "S cm−1"),
            ("2.4", "2.4 ∙ 10⁻⁴", "S cm−1"),
            ("2.4", "2.4 × 10⁻⁴", "S cm−1"),
            ("10", "10⁻⁴", "S cm−1"), ("10", "10⁴", "S cm−1"),
            ("90", "90 ± 3", "MPa"), ("3", "90 ± 3", "MPa"),
            ("90", "90 +/- 3", "MPa"), ("3", "90 +/- 3", "MPa"),
        ]
        for value, measured, unit in cases:
            with self.subTest(value=value, measured=measured):
                quote = "P1/LiFSI measurement was " + measured + unit
                self.document["chunks"][0]["text"] += " " + quote
                self.entity["properties"] = self.group(self.fact(value, quote,
                        property="measurement", unit=unit, specimen_id="salted", conditions=[]))
                result = self.run_case()
                self.assertEqual(1, len(result["cards"]))
                self.assertEqual([], result["cards"][0]["properties"]["items"])
                self.assertEqual("property_value_not_in_original_evidence", result["review_queue"][0]["reason"])

    def test_complete_raw_numbers_ranges_and_uncertainties_are_preserved(self):
        cases = [
            ("1,000", "MPa"), ("30–60", "°C"), ("30 – 60", "°C"),
            ("90 ± 3", "MPa"), ("90 +/- 3", "MPa"),
            ("2.4 · 10−4", "S cm−1"), ("2.4 ⋅ 10⁻⁴", "S cm−1"),
            ("2.4 ∙ 10⁻⁴", "S cm−1"), ("10⁻⁴", "S cm−1"),
            ("0.5", "mS/cm"), ("30", "°C"), ("95", "%"),
        ]
        for value, unit in cases:
            with self.subTest(value=value, unit=unit):
                quote = "P1/LiFSI measurement was " + value + unit
                self.document["chunks"][0]["text"] += " " + quote
                self.entity["properties"] = self.group(self.fact(value, quote,
                        property="measurement", unit=unit, specimen_id="salted", conditions=[]))
                result = self.run_case()
                accepted = result["cards"][0]["properties"]["items"]
                self.assertEqual([value], [item["value"] for item in accepted])

    def test_temperature_condition_cannot_take_a_range_endpoint(self):
        quote = "P1/LiFSI measured across 30–60°C"
        self.document["chunks"][0]["text"] += " " + quote
        prop = self.property()
        prop["conditions"] = [{"name": "temperature_C", "value": 30, "evidence": self.ev(quote)}]
        self.entity["properties"] = self.group(prop)
        result = self.run_case()
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertEqual("condition_value_not_in_original_evidence", result["review_queue"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
