"""Focused expectation checks are not scientific accuracy measurements."""
from copy import deepcopy
import unittest

from polymer_cards_lib.evaluation import evaluate_run


def evidence(chunk="identity", quote="Polymer P1 was synthesized"):
    return {"chunk_id": chunk, "quote": quote, "evidence_status": "quote_matched"}


def fixture():
    prop = {"entity_id": "p1", "property": "voltage", "value": "3.8", "unit": "V",
            "specimen_id": "salted", "evidence": [evidence("result", "P1 showed 3.8 V")],
            "specimen_evidence": [evidence("preparation", "P1/LiFSI electrolyte was prepared")],
            "conditions": [{"name": "temperature", "value": "room temperature", "evidence": [evidence("test", "at room temperature")]}]}
    card = {"entity_id": "p1", "name": "P1", "identity_kind": "specific_polymer",
            "classification": {"is_polymer": True}, "identity_evidence": [evidence()], "aliases": [],
            "specimens": [{"specimen_id": "salted", "label": "P1/LiFSI electrolyte", "evidence": [evidence("preparation")]},
                          {"specimen_id": "neat", "label": "P1 film", "evidence": [evidence("casting")]}],
            "properties": {"status": "reported", "items": [prop]}}
    run = {"results": [{"paper_id": "paper-a", "cards": [card], "review_queue": [], "discarded_entities": []}]}
    reference = {"reference_version": "test-reference", "identity_expectations": [{"paper_id": "paper-a", "name": "P1"}],
                 "measurement_expectations": [{"claim_id": "voltage", "paper_id": "paper-a", "entity_labels": ["P1"],
                     "value": "3.8", "unit": "V", "specimen_require_any": ["LiFSI"], "specimen_forbid": ["neat"],
                     "condition_value_terms": [["room temperature", "RT"]],
                     "evidence_chunk_ids_required": ["result", "preparation", "test"]}]}
    return run, reference


class PolymerCardEvaluationTests(unittest.TestCase):
    def test_correct_specific_identity_and_sample_match_without_mutating_data(self):
        run, reference = fixture()
        old_run, old_ref = deepcopy(run), deepcopy(reference)
        result = evaluate_run(run, reference)
        self.assertEqual("matched_focused_expectation", result["identities"][0]["status"])
        self.assertEqual("matched_focused_expectation", result["measurements"][0]["status"])
        self.assertEqual(old_run, run)
        self.assertEqual(old_ref, reference)
        self.assertNotIn("accuracy", result)

    def test_wrong_neat_sample_cannot_match_an_electrolyte_measurement(self):
        run, reference = fixture()
        run["results"][0]["cards"][0]["properties"]["items"][0]["specimen_id"] = "neat"
        result = evaluate_run(run, reference)["measurements"][0]
        self.assertEqual("needs_source_review", result["status"])
        self.assertIn("specimen_required_term_missing", result["candidates"][0]["reasons"])

    def test_negated_additive_name_does_not_establish_the_required_form(self):
        for label in ("P1 without LiFSI", "P1 LiFSI-free film"):
            with self.subTest(label=label):
                run, reference = fixture()
                run["results"][0]["cards"][0]["specimens"][0]["label"] = label
                self.assertEqual("needs_source_review", evaluate_run(run, reference)["measurements"][0]["status"])

    def test_family_and_explicit_unknown_scope_cannot_own_a_member_measurement(self):
        for kind in ("polymer_family", None):
            with self.subTest(kind=kind):
                run, reference = fixture()
                run["results"][0]["cards"][0]["identity_kind"] = kind
                result = evaluate_run(run, reference)
                self.assertEqual("needs_source_review", result["identities"][0]["status"])
                self.assertEqual("needs_source_review", result["measurements"][0]["status"])

    def test_identity_needs_an_explicit_quoted_source_label(self):
        run, reference = fixture()
        run["results"][0]["cards"][0]["identity_evidence"] = [evidence(quote="Polymers P2–P7 were prepared")]
        result = evaluate_run(run, reference)
        self.assertEqual("needs_source_review", result["identities"][0]["status"])
        self.assertEqual("needs_source_review", result["measurements"][0]["status"])

    def test_other_paper_or_wrong_parent_does_not_count(self):
        for mutation in ("paper", "parent"):
            with self.subTest(mutation=mutation):
                run, reference = fixture()
                if mutation == "paper":
                    run["results"][0]["paper_id"] = "paper-b"
                else:
                    card = run["results"][0]["cards"][0]
                    card["name"] = "P2"
                    card["identity_evidence"] = [evidence(quote="Polymer P2 was synthesized")]
                self.assertNotEqual("matched_focused_expectation", evaluate_run(run, reference)["measurements"][0]["status"])

    def test_held_measurement_and_identity_are_review_not_retained_success(self):
        run, reference = fixture()
        card = run["results"][0]["cards"].pop()
        run["results"][0]["review_queue"].append({"entity_id": "p1", "name": "P1", "path": "entities[0].classification",
            "reason": "identity_quote_missing", "record": card})
        result = evaluate_run(run, reference)
        self.assertEqual("needs_source_review", result["identities"][0]["status"])
        self.assertTrue(result["identities"][0]["identity_held_for_review"])
        self.assertEqual("needs_source_review", result["measurements"][0]["status"])

    def test_child_fact_reviews_do_not_mark_an_accepted_identity_as_held(self):
        for path in ("entities[0].properties.items[0]", "entities[0].composition.items[0]",
                     "entities[0].specimens[0]", "entities[0].description", "entities[0].aliases[0]"):
            with self.subTest(path=path):
                run, reference = fixture()
                run["results"][0]["review_queue"].append({"entity_id": "p1", "name": "P1", "path": path,
                    "reason": "child_fact_needs_review", "record": {"value": "unresolved"}})
                item = evaluate_run(run, reference)["identities"][0]
                self.assertEqual("matched_focused_expectation", item["status"])
                self.assertFalse(item["identity_held_for_review"])

    def test_whole_entity_review_and_conflicting_identity_remain_visible(self):
        for path in ("entities[1]", "entities[1].classification", "entities[1].identity_evidence"):
            with self.subTest(path=path):
                run, reference = fixture()
                duplicate = deepcopy(run["results"][0]["cards"][0])
                duplicate["entity_id"] = "p1-duplicate"
                run["results"][0]["review_queue"].append({"entity_id": "p1-duplicate", "name": "P1", "path": path,
                    "reason": "identity_needs_review", "record": duplicate})
                self.assertTrue(evaluate_run(run, reference)["identities"][0]["identity_held_for_review"])

    def test_required_conditions_and_definition_cannot_come_from_unrelated_facts(self):
        run, reference = fixture()
        card = run["results"][0]["cards"][0]
        reference["measurement_expectations"][0]["evidence_chunk_ids_required"].append("definition")
        card["unrelated"] = {"evidence": [evidence("definition")]}
        result = evaluate_run(run, reference)["measurements"][0]
        self.assertEqual("needs_source_review", result["status"])
        self.assertIn("required_evidence_chunk_missing:definition", result["candidates"][0]["reasons"])
        card["properties"]["items"][0]["specimen_evidence"].append(evidence("definition"))
        self.assertEqual("matched_focused_expectation", evaluate_run(run, reference)["measurements"][0]["status"])
        card["properties"]["items"][0]["conditions"] = []
        self.assertEqual("needs_source_review", evaluate_run(run, reference)["measurements"][0]["status"])

    def test_percent_unit_notation_matches_without_duplicating_the_unit(self):
        run, reference = fixture()
        prop = run["results"][0]["cards"][0]["properties"]["items"][0]
        prop.update(value="2,000%", unit="%")
        reference["measurement_expectations"][0].update(value="2,000", unit="%")
        self.assertEqual("matched_focused_expectation", evaluate_run(run, reference)["measurements"][0]["status"])
        prop["unit"] = None
        candidate = evaluate_run(run, reference)["measurements"][0]["candidates"][0]
        self.assertEqual([], candidate["reasons"])
        self.assertIn("unit_field_missing_but_unit_in_raw_value", candidate["notes"])

    def test_source_related_value_variant_remains_review_without_number_conversion(self):
        run, reference = fixture()
        prop = run["results"][0]["cards"][0]["properties"]["items"][0]
        prop.update(value="nearly 140 times its original length", unit=None)
        reference["measurement_expectations"][0].update(value="14,000", unit="%")
        result = evaluate_run(run, reference)["measurements"][0]
        self.assertEqual("needs_source_review", result["status"])
        self.assertIn("raw_value_or_unit_not_exact_reference", result["candidates"][0]["reasons"])
        self.assertEqual("source_related_value_variant", result["candidates"][0]["match_kind"])

    def test_qualifiers_and_number_notation_are_not_silently_converted(self):
        run, reference = fixture()
        reference["measurement_expectations"][0]["value"] = "beyond 3.8"
        self.assertNotEqual("matched_focused_expectation", evaluate_run(run, reference)["measurements"][0]["status"])

    def test_empty_reference_has_no_success_rate_and_bad_configs_fail(self):
        run, _ = fixture()
        result = evaluate_run(run, {})
        self.assertEqual([], result["identities"])
        self.assertEqual([], result["measurements"])
        self.assertNotIn("accuracy", result)
        _, reference = fixture()
        for key, value in [("entity_labels", "P1"), ("condition_value_terms", ["room temperature"]),
                           ("evidence_chunk_ids_required", "test"), ("value", {}), ("unit", 1)]:
            with self.subTest(key=key):
                bad = deepcopy(reference)
                bad["measurement_expectations"][0][key] = value
                with self.assertRaises(ValueError):
                    evaluate_run(run, bad)


if __name__ == "__main__":
    unittest.main()
