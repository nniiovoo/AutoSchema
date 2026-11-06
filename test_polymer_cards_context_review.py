"""An anchored model context proposal cannot rewrite immutable extraction facts."""
from copy import deepcopy
import json
import unittest

from polymer_cards_lib.context_review import (
    apply_context_proposals, build_context_review_prompt,
    property_anchor_sha256, response_format,
)
from polymer_cards_lib.evidence_spans import build_span_catalog
from polymer_cards_lib.prompt import worked_example


def fixture():
    document, previous = worked_example()
    catalog = build_span_catalog(document)
    full = {span["chunk_id"]: span for span in catalog
            if span["start"] == 0 and span["end"] == len(next(
                c["text"] for c in document["chunks"] if c["chunk_id"] == span["chunk_id"]))}
    ev = lambda key: [{"chunk_id": key, "span_id": full[key]["span_id"]}]
    prop = previous["entities"][0]["properties"]["items"][0]
    edit = {"entity_id": "p1", "property_index": 0,
            "anchor_sha256": property_anchor_sha256("p1", 0, prop),
            "specimen_id": "p1-film", "specimen_evidence": ev("example-film"),
            "conditions": [{"name": "crosshead speed", "value": "7 mm min−1",
                            "evidence": ev("example-testing-methods")}],
            "evidence": ev("example-film"), "reason": "Use the supported mechanical protocol."}
    return document, previous, edit


class PolymerContextReviewTests(unittest.TestCase):
    def test_valid_context_edit_preserves_values_units_names_order_and_inputs(self):
        document, previous, edit = fixture()
        before = deepcopy(previous)
        proposals = {"paper_id": document["paper_id"], "edits": [edit]}
        composed, audit = apply_context_proposals(document, previous, proposals)
        self.assertEqual(before, previous)
        actual = composed["entities"][0]["properties"]["items"][0]
        old = before["entities"][0]["properties"]["items"][0]
        for key in ("entity_id", "property", "value", "unit"):
            self.assertEqual(old[key], actual[key])
        self.assertEqual(edit["conditions"], actual["conditions"])
        self.assertTrue(audit["immutable_fields_preserved"])
        self.assertEqual(1, audit["applied_edits"])

    def test_immutable_field_attempt_wrong_anchor_foreign_id_and_unknown_sample_are_held(self):
        for kind in ("value", "anchor", "span", "sample", "index", "bool_index"):
            with self.subTest(kind=kind):
                document, previous, edit = fixture()
                if kind == "value": edit["value"] = "999"
                elif kind == "anchor": edit["anchor_sha256"] = "0" * 64
                elif kind == "span": edit["evidence"][0]["span_id"] = "spn-foreign"
                elif kind == "sample": edit["specimen_id"] = "unknown"
                elif kind == "index": edit["property_index"] = 99
                else: edit["property_index"] = False
                composed, audit = apply_context_proposals(document, previous,
                    {"paper_id": document["paper_id"], "edits": [edit]})
                self.assertEqual(previous, composed)
                self.assertEqual(0, audit["applied_edits"])
                self.assertEqual(1, len(audit["held_edits"]))

    def test_duplicate_edits_hold_both_instead_of_first_or_last_wins(self):
        document, previous, edit = fixture()
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit, deepcopy(edit)]})
        self.assertEqual(previous, composed)
        self.assertEqual(0, audit["applied_edits"])
        self.assertEqual(2, len(audit["held_edits"]))

    def test_context_with_real_span_but_new_unsupported_condition_is_held_whole(self):
        document, previous, edit = fixture()
        edit["conditions"][0]["value"] = "999 °C"
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit]})
        self.assertEqual(previous, composed)
        self.assertEqual(0, audit["applied_edits"])
        self.assertIn("condition_value_not_in_original_evidence", audit["held_edits"][0]["new_validation_reasons"])

    def test_existing_held_fact_can_gain_context_without_changing_its_bad_claim(self):
        document, previous, edit = fixture()
        prop = previous["entities"][0]["properties"]["items"][0]
        prop["value"] = "999"
        edit["anchor_sha256"] = property_anchor_sha256("p1", 0, prop)
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit]})
        self.assertEqual("999", composed["entities"][0]["properties"]["items"][0]["value"])
        self.assertEqual(1, audit["applied_edits"])
        self.assertEqual("applied_with_validation_review", audit["edit_results"][0]["status"])
        self.assertIn("property_value_not_in_original_evidence", audit["edit_results"][0]["validation_reasons"])

    def test_wrong_paper_and_nonfinite_json_do_not_change_the_base(self):
        document, previous, edit = fixture()
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": "foreign", "edits": [edit]})
        self.assertEqual(previous, composed)
        self.assertEqual(0, audit["applied_edits"])
        edit["reason"] = float("nan")
        with self.assertRaises(ValueError):
            apply_context_proposals(document, previous, {"paper_id": document["paper_id"], "edits": [edit]})

    def test_a_rejected_edit_never_partially_changes_the_other_target(self):
        document, previous, edit = fixture()
        bad = deepcopy(edit)
        bad["property_index"] = 1
        target = previous["entities"][0]["properties"]["items"][1]
        bad["anchor_sha256"] = property_anchor_sha256("p1", 1, target)
        bad["conditions"][0]["evidence"][0]["chunk_id"] = "foreign"
        before = deepcopy(target)
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit, bad]})
        self.assertEqual(1, audit["applied_edits"])
        self.assertEqual(1, len(audit["held_edits"]))
        self.assertEqual(before, composed["entities"][0]["properties"]["items"][1])

    def test_nonobject_base_group_fails_without_mutation(self):
        document, previous, _ = fixture()
        previous["entities"][0]["properties"] = None
        before = deepcopy(previous)
        with self.assertRaises(ValueError):
            apply_context_proposals(document, previous, {"paper_id": document["paper_id"], "edits": []})
        self.assertEqual(before, previous)

    def test_prompt_contains_only_sources_and_current_untrusted_targets_and_schema_is_closed(self):
        document, previous, _ = fixture()
        before = deepcopy(previous)
        text = build_context_review_prompt(document, previous)
        self.assertIn("untrusted", text)
        self.assertIn("anchor_sha256", text)
        self.assertIn("post-healing", text)
        self.assertIn("source_span_catalog", text)
        self.assertNotIn("checked_pei", text)
        self.assertEqual(before, previous)
        schema = response_format()["json_schema"]["schema"]
        self.assertEqual({"paper_id", "edits"}, set(schema["required"]))
        edit = schema["$defs"]["edit"]
        self.assertNotIn("value", edit["properties"])
        self.assertNotIn("unit", edit["properties"])
        self.assertNotIn("name", edit["properties"])
        self.assertIs(False, edit["additionalProperties"])

    def test_optional_audit_focus_is_anchored_unverified_and_never_changes_records(self):
        document, previous, _ = fixture()
        before = deepcopy(previous)
        focus = [{"entity_id": "p1", "property_index": 0,
                  "reason": "Check whether the measurement protocol is fully attributed."}]
        original_focus = deepcopy(focus)
        text = build_context_review_prompt(document, previous, review_focus=focus)
        payload = json.loads(text.split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[1])
        entry = payload["source_audit_focus"][0]
        self.assertEqual("unverified_source_audit_hypothesis", entry["status"])
        self.assertEqual(property_anchor_sha256("p1", 0, previous["entities"][0]["properties"]["items"][0]), entry["anchor_sha256"])
        self.assertEqual({"entity_id", "property_index", "reason", "anchor_sha256", "status"}, set(entry))
        self.assertNotIn("expected_value", entry)
        self.assertIn("not an answer", payload["source_audit_focus_scope"])
        self.assertEqual(before, previous)
        self.assertEqual(original_focus, focus)

    def test_focus_rejects_answer_fields_unknown_targets_and_duplicate_targets(self):
        for bad in [
            [{"entity_id": "p1", "property_index": 0, "reason": "Check context", "expected_value": "999"}],
            [{"entity_id": "foreign", "property_index": 0, "reason": "Check context"}],
            [{"entity_id": "p1", "property_index": 99, "reason": "Check context"}],
            [{"entity_id": "p1", "property_index": False, "reason": "Check context"}],
            [{"entity_id": "p1", "property_index": 0, "reason": "Check context"}] * 2,
        ]:
            with self.subTest(focus=bad):
                document, previous, _ = fixture()
                with self.assertRaises(ValueError):
                    build_context_review_prompt(document, previous, review_focus=bad)

    def test_strict_focus_filters_targets_without_renumbering_or_hiding_sources(self):
        document, previous, _ = fixture()
        focus = [{"entity_id": "p1", "property_index": 1, "reason": "Check the measurement context."}]
        text = build_context_review_prompt(document, previous, review_focus=focus, strict_focus=True)
        payload = json.loads(text.split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[1])
        entity = payload["untrusted_review_targets"][0]
        self.assertEqual([1], [p["property_index"] for p in entity["properties"]])
        self.assertEqual(previous["entities"][0]["specimens"], entity["specimens"])
        source = json.loads(text.split("\nORIGINAL SOURCE DATA\n", 1)[1]
                            .split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[0])
        self.assertEqual(len(document["chunks"]), len(source["chunks"]))
        self.assertNotIn("Extract the polymer records from", text)
        self.assertEqual("specified_targets_only", payload["strict_context_scope"]["mode"])
        self.assertIn("verbatim", payload["strict_context_scope"]["conditions_policy"])

    def test_strict_focus_holds_an_unrequested_valid_edit_and_default_remains_compatible(self):
        document, previous, edit = fixture()
        focus = [{"entity_id": "p1", "property_index": 1, "reason": "Check the other target."}]
        proposals = {"paper_id": document["paper_id"], "edits": [edit]}
        composed, audit = apply_context_proposals(document, previous, proposals,
                                                review_focus=focus, strict_focus=True)
        self.assertEqual(previous, composed)
        self.assertEqual(0, audit["applied_edits"])
        self.assertEqual("context_target_outside_strict_focus", audit["held_edits"][0]["reason"])
        plain, plain_audit = apply_context_proposals(document, previous, proposals)
        legacy, legacy_audit = apply_context_proposals(document, previous, proposals,
                                                     review_focus=focus, strict_focus=False)
        self.assertEqual(plain, legacy)
        self.assertEqual(plain_audit, legacy_audit)
        self.assertNotIn("strict_context_scope", plain_audit)


if __name__ == "__main__":
    unittest.main()
