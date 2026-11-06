"""Regression cases for explicit units and unresolved source-context conflicts.

The source is synthetic: none of these values are reference answers supplied
to the extraction model. These tests exercise the real card validator.
"""
from copy import deepcopy
import unittest

from polymer_cards_lib.validation import build_cards


class PolymerCardConditionsConflictTests(unittest.TestCase):
    def setUp(self):
        texts = {
            "identity": "Polymer Z was synthesized. Z membrane was tested.",
            "methods": "The Z membrane used for electrochemical testing had a thickness of 12 μm.",
            "results": "The Z membrane in the impedance results had a thickness of about 15 μm.",
            "recovery": "The Z membrane recovery was 93% ± 3% after 2 h at room temperature.",
            "dispersity": "The Z membrane material had dispersity 1.77.",
        }
        self.document = {"paper_id": "synthetic-context-paper", "title": "Synthetic test only",
                         "chunks": [{"chunk_id": key, "text": text, "source_part": "main",
                                     "locator": key, "document_sha256": "a" * 64}
                                    for key, text in texts.items()]}
        self.texts = texts
        self.entity = {
            "entity_id": "z", "name": "Z", "identity_kind": "specific_polymer",
            "identity_evidence": self.ev("identity"),
            "classification": {"is_polymer": True, "reason": "The source explicitly calls Z a polymer.",
                               "evidence": self.ev("identity")},
            "specimens": [
                {"specimen_id": "z-methods", "label": "Z membrane used for electrochemical testing",
                 "evidence": self.ev("methods")},
                {"specimen_id": "z-results", "label": "Z membrane in the impedance results",
                 "evidence": self.ev("results")},
            ],
        }
        self.response = {"paper_id": self.document["paper_id"], "entities": [self.entity]}

    def ev(self, key):
        return [{"chunk_id": key, "quote": self.texts[key]}]

    def prop(self, key, value, unit, specimen_id="z-methods", property="thickness"):
        return {"entity_id": "z", "property": property, "value": value, "unit": unit,
                "specimen_id": specimen_id, "specimen_evidence": self.ev(key),
                "conditions": [], "evidence": self.ev(key)}

    def conflict(self):
        return {"property": "thickness",
                "description": "Methods and Results report different membrane thicknesses; specimen equivalence is unresolved.",
                "specimen_ids": ["z-methods", "z-results"],
                "evidence": self.ev("methods") + self.ev("results")}

    def run_case(self):
        return build_cards(self.document, self.response)

    def thickness_group(self):
        self.entity["properties"] = {
            "status": "reported", "items": [self.prop("methods", "12", "μm"),
                self.prop("results", "about 15", "μm", "z-results")],
            "conflicts": [self.conflict()]}

    def test_source_qualified_thickness_conflict_survives_different_specimens(self):
        self.thickness_group()
        before = deepcopy(self.response)
        result = self.run_case()
        group = result["cards"][0]["properties"]
        self.assertEqual("conflicting", group["status"])
        self.assertEqual(["12", "about 15"], [p["value"] for p in group["items"]])
        self.assertEqual(["z-methods", "z-results"], group["conflicts"][0]["specimen_ids"])
        self.assertEqual("quote_matched", group["conflicts"][0]["evidence"][0]["evidence_status"])
        self.assertEqual(before, self.response)

    def test_percent_in_raw_value_requires_an_explicit_unit_field(self):
        self.entity["properties"] = {"status": "reported", "items": [
            self.prop("recovery", "93% ± 3%", None, property="recovery")], "conflicts": []}
        result = self.run_case()
        self.assertEqual(1, len(result["cards"]))
        self.assertEqual([], result["cards"][0]["properties"]["items"])
        self.assertIn("property_unit_field_missing_for_explicit_percent",
                      [q["reason"] for q in result["review_queue"]])
        self.assertIsNone(result["review_queue"][0]["record"]["unit"])

    def test_explicit_percent_and_dimensionless_values_remain_valid(self):
        self.entity["properties"] = {"status": "reported", "items": [
            self.prop("recovery", "93% ± 3%", "%", property="recovery"),
            self.prop("dispersity", "1.77", None, property="dispersity")], "conflicts": []}
        result = self.run_case()
        self.assertEqual(["%", None], [p["unit"] for p in result["cards"][0]["properties"]["items"]])
        self.assertEqual([], result["review_queue"])

    def test_unknown_or_foreign_specimen_conflict_is_held_without_losing_facts(self):
        self.thickness_group()
        self.entity["properties"]["conflicts"][0]["specimen_ids"].append("other-entity-sample")
        result = self.run_case()
        group = result["cards"][0]["properties"]
        self.assertEqual(2, len(group["items"]))
        self.assertEqual([], group["conflicts"])
        self.assertEqual("needs_review", group["status"])
        self.assertIn("conflict_specimen_not_linked_to_polymer", [q["reason"] for q in result["review_queue"]])

    def test_unquoted_conflict_does_not_disappear_or_erase_valid_observations(self):
        self.thickness_group()
        self.entity["properties"]["conflicts"][0]["evidence"][1]["quote"] = "The thickness is resolved to 20 μm."
        result = self.run_case()
        self.assertEqual(2, len(result["cards"][0]["properties"]["items"]))
        self.assertEqual([], result["cards"][0]["properties"]["conflicts"])
        held = result["review_queue"][0]
        self.assertIn(".conflicts[0]", held["path"])
        self.assertEqual("quote_not_in_original_source", held["reason"])

    def test_legacy_group_without_conflicts_is_still_accepted(self):
        self.entity["properties"] = {"status": "reported", "items": [self.prop("methods", "12", "μm")]}
        result = self.run_case()
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))
        self.assertEqual([], result["review_queue"])

    def test_empty_numerical_conditions_are_visible_without_inventing_a_protocol(self):
        self.entity["properties"] = {"status": "reported", "items": [self.prop("methods", "12", "μm")]}
        item = self.run_case()["cards"][0]["properties"]["items"][0]
        self.assertEqual("not_captured", item["conditions_review_status"])
        self.assertEqual([], item["conditions"])

    def test_attached_conditions_still_need_scientific_review(self):
        item = self.prop("recovery", "93% ± 3%", "%", property="recovery")
        item["conditions"] = [{"name": "healing time", "value": "2 h", "evidence": self.ev("recovery")}]
        self.entity["properties"] = {"status": "reported", "items": [item], "conflicts": []}
        checked = self.run_case()["cards"][0]["properties"]["items"][0]
        self.assertEqual("captured_not_scientifically_verified", checked["conditions_review_status"])

    def test_invalid_conflict_shapes_are_held_and_do_not_destroy_the_parent(self):
        for mutation in (None, {}, "conflict", {**self.conflict(), "specimen_ids": []},
                         {**self.conflict(), "specimen_ids": ["z-methods", "z-methods"]},
                         {**self.conflict(), "specimen_ids": [["z-methods"]]},
                         {**self.conflict(), "unvalidated_extra": "20 μm"},
                         {**self.conflict(), "description": ""}):
            with self.subTest(mutation=mutation):
                self.thickness_group()
                self.entity["properties"]["conflicts"] = [mutation]
                result = self.run_case()
                self.assertEqual(1, len(result["cards"]))
                self.assertEqual(2, len(result["cards"][0]["properties"]["items"]))
                self.assertEqual([], result["cards"][0]["properties"]["conflicts"])
                self.assertTrue(result["review_queue"])

    def test_nonlist_conflicts_are_held_without_changing_valid_values(self):
        self.thickness_group()
        self.entity["properties"]["conflicts"] = "there is a conflict"
        result = self.run_case()
        self.assertEqual(["12", "about 15"],
                         [p["value"] for p in result["cards"][0]["properties"]["items"]])
        self.assertEqual("invalid_property_conflicts_list", result["review_queue"][0]["reason"])

    def test_a_conflict_can_refer_to_one_unresolved_specimen_without_inventing_another(self):
        self.thickness_group()
        self.entity["properties"]["conflicts"][0]["specimen_ids"] = ["z-methods"]
        group = self.run_case()["cards"][0]["properties"]
        self.assertEqual("conflicting", group["status"])
        self.assertEqual(["z-methods"], group["conflicts"][0]["specimen_ids"])

    def test_valid_and_invalid_conflict_notes_are_kept_distinct(self):
        self.thickness_group()
        bad = self.conflict()
        bad["specimen_ids"] = ["foreign"]
        self.entity["properties"]["conflicts"].append(bad)
        result = self.run_case()
        group = result["cards"][0]["properties"]
        self.assertEqual("conflicting", group["status"])
        self.assertEqual(1, len(group["conflicts"]))
        self.assertEqual(1, group["invalid_conflicts_count"])
        self.assertEqual(1, len(result["review_queue"]))

    def test_explicit_empty_conflicts_do_not_invent_a_thickness_problem(self):
        self.entity["properties"] = {"status": "reported", "items": [self.prop("methods", "12", "μm")],
                                     "conflicts": []}
        group = self.run_case()["cards"][0]["properties"]
        self.assertEqual("reported", group["status"])
        self.assertEqual([], group["conflicts"])


if __name__ == "__main__":
    unittest.main()
