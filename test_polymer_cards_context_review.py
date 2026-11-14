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


ANNEALED_60 = "After annealing at approx. 60°C, the P1 film had breaking strength 15 MPa."
ANNEALED_80 = "After annealing at 80°C, it had breaking strength 18 MPa."
# The catalogue splits ANNEALED_60 after "approx."; this sentence span holds the 15 MPa value.
VALUE_15 = "60°C, the P1 film had breaking strength 15 MPa."


def span(document, chunk_id, text=None):
    """Select one exact catalogue span; the complete chunk when text is omitted."""
    if text is None:
        text = next(c["text"] for c in document["chunks"] if c["chunk_id"] == chunk_id)
    return [{"chunk_id": chunk_id, "span_id": next(s["span_id"] for s in build_span_catalog(document)
                                                   if s["chunk_id"] == chunk_id and s["text"] == text)}]


def annealed_fixture():
    """The worked example plus two annealed strengths of the same P1 film (items 2 and 3)."""
    document, previous, _ = fixture()
    chunk = deepcopy(next(c for c in document["chunks"] if c["chunk_id"] == "example-film"))
    chunk.update(chunk_id="example-annealed", locator="example-annealed", text=ANNEALED_60 + " " + ANNEALED_80)
    document["chunks"].append(chunk)
    quote = lambda chunk_id, text: [{"chunk_id": chunk_id, "quote": text}]
    for value, temperature, sentence in (("15", "approx. 60°C", ANNEALED_60), ("18", "80°C", ANNEALED_80)):
        previous["entities"][0]["properties"]["items"].append({
            "entity_id": "p1", "value": value, "property": "breaking strength", "unit": "MPa",
            "specimen_id": "p1-film",
            "specimen_evidence": quote("example-film", "A P1 film was cast after solvent evaporation."),
            "conditions": [{"name": "annealing temperature", "value": temperature,
                            "evidence": quote("example-annealed", sentence)}],
            "evidence": quote("example-annealed", sentence)})
    return document, previous


def as_cast_conditions_edit(document, previous, index, sentence):
    """Give an annealed value the as-cast item 0 stated conditions, each with valid evidence."""
    prop = previous["entities"][0]["properties"]["items"][index]
    return {"entity_id": "p1", "property_index": index,
            "anchor_sha256": property_anchor_sha256("p1", index, prop),
            "specimen_id": "p1-film", "specimen_evidence": span(document, "example-film"),
            "conditions": [{"name": "temperature", "value": "25°C", "evidence": span(document, "example-film")},
                           {"name": "crosshead speed", "value": "7 mm min−1",
                            "evidence": span(document, "example-testing-methods")}],
            "evidence": span(document, "example-annealed", sentence), "reason": "Use the tensile protocol."}


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

    def test_unsupported_specimen_link_can_be_removed_as_the_prompt_instructs(self):
        document, previous, edit = fixture()
        self.assertEqual("p1-film", previous["entities"][0]["properties"]["items"][0]["specimen_id"])
        edit.update(specimen_id=None, specimen_evidence=[],
                    reason="The source does not establish which form was tested.")
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit]})
        self.assertEqual(1, audit["applied_edits"])
        self.assertEqual("applied_with_validation_review", audit["edit_results"][0]["status"])
        self.assertIsNone(composed["entities"][0]["properties"]["items"][0]["specimen_id"])
        self.assertIn("fact_specimen_not_linked_to_polymer",
                      {issue["reason"] for issue in audit["validation_issues"]})

    def test_unlinking_does_not_excuse_other_new_problems(self):
        document, previous, edit = fixture()
        edit.update(specimen_id=None, specimen_evidence=[])
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

    def test_held_fact_cannot_gain_unsupported_context_hidden_behind_its_first_issue(self):
        # Validation stops at a fact's first failed check, so the value and
        # condition checks of an unlinked measurement never reach its reasons.
        expected = {"value": ["property_unit_not_in_original_evidence", "property_value_not_in_original_evidence"],
                    "condition": ["condition_value_not_in_original_evidence"]}
        for kind in ("value", "condition", "supported"):
            with self.subTest(kind=kind):
                document, previous, edit = fixture()
                prop = previous["entities"][0]["properties"]["items"][0]
                prop["specimen_id"], prop["specimen_evidence"] = None, []
                edit.update(specimen_id=None, specimen_evidence=[])
                if kind == "value":
                    edit["evidence"] = span(document, "example-method")
                elif kind == "condition":
                    edit["conditions"][0]["value"] = "999 °C"
                composed, audit = apply_context_proposals(document, previous,
                    {"paper_id": document["paper_id"], "edits": [edit]})
                if kind == "supported":
                    self.assertEqual(1, audit["applied_edits"])
                    self.assertEqual(["fact_specimen_not_linked_to_polymer"],
                                     audit["edit_results"][0]["validation_reasons"])
                    continue
                self.assertEqual(previous, composed)
                self.assertEqual(0, audit["applied_edits"])
                self.assertEqual("context_edit_introduces_new_validation_issue", audit["held_edits"][0]["reason"])
                self.assertEqual(expected[kind], audit["held_edits"][0]["new_validation_reasons"])

    def test_family_held_measurement_cannot_gain_link_evidence_naming_another_form(self):
        for kind in ("alternate", "supported"):
            with self.subTest(kind=kind):
                document, previous, edit = fixture()
                previous["entities"][0]["identity_kind"] = "polymer_family"
                if kind == "alternate":
                    edit["specimen_evidence"] = span(document, "example-salt")
                composed, audit = apply_context_proposals(document, previous,
                    {"paper_id": document["paper_id"], "edits": [edit]})
                if kind == "supported":
                    self.assertEqual(1, audit["applied_edits"])
                    self.assertEqual(["family_measurement_requires_specific_polymer"],
                                     audit["edit_results"][0]["validation_reasons"])
                    continue
                self.assertEqual(previous, composed)
                self.assertEqual(["property_sample_evidence_names_alternate_form"],
                                 audit["held_edits"][0]["new_validation_reasons"])

    def test_held_fact_condition_may_rely_on_adjacent_selected_spans_but_not_on_one_alone(self):
        for kind in ("adjacent", "one_span"):
            with self.subTest(kind=kind):
                document, previous = annealed_fixture()
                prop = previous["entities"][0]["properties"]["items"][2]
                prop["specimen_id"], prop["specimen_evidence"] = None, []
                second = span(document, "example-annealed", VALUE_15)
                condition_evidence = second if kind == "one_span" else (
                    span(document, "example-annealed", "After annealing at approx.") + second)
                edit = {"entity_id": "p1", "property_index": 2,
                        "anchor_sha256": property_anchor_sha256("p1", 2, prop),
                        "specimen_id": None, "specimen_evidence": [],
                        "conditions": [{"name": "annealing temperature", "value": "approx. 60°C",
                                        "evidence": condition_evidence}],
                        "evidence": deepcopy(second), "reason": "Select the annealing passage."}
                composed, audit = apply_context_proposals(document, previous,
                    {"paper_id": document["paper_id"], "edits": [edit]})
                if kind == "adjacent":
                    self.assertEqual(1, audit["applied_edits"])
                    self.assertEqual(["fact_specimen_not_linked_to_polymer"],
                                     audit["edit_results"][0]["validation_reasons"])
                else:
                    self.assertEqual(previous, composed)
                    self.assertEqual(["condition_value_not_in_original_evidence"],
                                     audit["held_edits"][0]["new_validation_reasons"])

    def test_edit_giving_two_values_the_same_stated_conditions_is_held(self):
        for base in ("reported", "conflict_note", "existing_pair"):
            with self.subTest(base=base):
                document, previous = annealed_fixture()
                group = previous["entities"][0]["properties"]
                index, sentence = 2, VALUE_15
                if base == "conflict_note":
                    group["conflicts"] = [{"property": "breaking strength", "specimen_ids": ["p1-film"],
                                           "description": "Annealed and as-cast strengths differ.",
                                           "evidence": [{"chunk_id": "example-annealed", "quote": ANNEALED_60}]}]
                elif base == "existing_pair":
                    group["items"][2]["conditions"] = deepcopy(group["items"][0]["conditions"])
                    index, sentence = 3, ANNEALED_80
                edit = as_cast_conditions_edit(document, previous, index, sentence)
                composed, audit = apply_context_proposals(document, previous,
                    {"paper_id": document["paper_id"], "edits": [edit]})
                self.assertEqual(previous, composed)
                self.assertEqual(0, audit["applied_edits"])
                held = audit["held_edits"][0]
                self.assertEqual("context_edit_introduces_new_validation_issue", held["reason"])
                self.assertIn("multiple_property_values_for_same_stated_conditions", held["new_validation_reasons"])
                if base == "reported":
                    self.assertIn("properties_group_status_changed_to_conflicting", held["new_validation_reasons"])

    def test_edit_separating_values_with_supported_conditions_is_applied(self):
        document, previous = annealed_fixture()
        items = previous["entities"][0]["properties"]["items"]
        items[2]["conditions"] = deepcopy(items[0]["conditions"])
        edit = as_cast_conditions_edit(document, previous, 2, VALUE_15)
        edit["conditions"] = [{"name": "annealing temperature", "value": "approx. 60°C",
                               "evidence": span(document, "example-annealed")}]
        composed, audit = apply_context_proposals(document, previous,
            {"paper_id": document["paper_id"], "edits": [edit]})
        self.assertEqual(1, audit["applied_edits"])
        self.assertEqual("applied_context_source_linked", audit["edit_results"][0]["status"])
        self.assertIn("multiple_property_values_for_same_stated_conditions",
                      {issue["reason"] for issue in audit["base_validation_issues"]})
        self.assertEqual([], audit["validation_issues"])

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

    def test_strict_focus_keeps_attribution_warnings_for_focused_properties_only(self):
        document, previous, _ = fixture()

        def warnings(records, index):
            focus = [{"entity_id": "p1", "property_index": index, "reason": "Check the sample form."}]
            text = build_context_review_prompt(document, records, review_focus=focus, strict_focus=True)
            payload = json.loads(text.split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[1])
            return payload["validation_feedback"]["attribution_warnings"]

        focused = warnings(previous, 0)
        self.assertEqual(["specimen_form_ambiguous"], [w["reason"] for w in focused])
        self.assertEqual(0, focused[0]["property_index"])
        self.assertEqual([], warnings(previous, 1))
        # A quarantined item is left out of the validated card, so warning paths
        # count card positions while focus targets count original response positions.
        shifted = deepcopy(previous)
        shifted["entities"][0]["properties"]["items"].insert(0, {"value": None})
        self.assertEqual([], warnings(shifted, 0))
        moved = warnings(shifted, 1)
        self.assertEqual(["breaking strength"], [w["property"] for w in moved])
        self.assertEqual(1, moved[0]["property_index"])
        self.assertEqual([], warnings(shifted, 2))

    def test_strict_focus_keeps_shared_label_warnings_that_name_a_focused_record(self):
        document, previous, _ = fixture()
        twin = json.loads(json.dumps(previous["entities"][0]).replace('"p1"', '"p2"'))
        previous["entities"].append(twin)
        focus = [{"entity_id": "p1", "property_index": 1, "reason": "Check the sample identity."}]
        text = build_context_review_prompt(document, previous, review_focus=focus, strict_focus=True)
        kept = json.loads(text.split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[1])[
            "validation_feedback"]["attribution_warnings"]
        self.assertTrue(kept)
        self.assertEqual({"specimen_label_shared_between_polymer_records"}, {w["reason"] for w in kept})
        self.assertTrue(all("p1" in w["related_entity_ids"] for w in kept))


if __name__ == "__main__":
    unittest.main()
