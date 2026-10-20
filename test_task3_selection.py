"""Task 3 behavior checks with independently specified synthetic evidence.

These cases exercise screening policy, not scientific extraction accuracy.  A
supported receipt represents an external review of the complete observation;
the engine must not treat an extractor's own 'verified' flag as that review.
"""

from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from select_candidates import main as selection_main
from selection_lib.screening import review_digest, screen_candidate


class Task3SelectionTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            "source-strength": {
                "paper_id": "synthetic-paper",
                "locator": "Results, paragraph 1",
                "text": (
                    "Sample P-A recovered 95% of its pristine tensile strength "
                    "after a partial cut, surface contact, and 60 minutes at 25 C."
                ),
            }
        }
        self.observation = {
            "observation_id": "strength-1",
            "paper_id": "synthetic-paper",
            "sample_id": "P-A",
            "role": "current_work",
            "property": "ultimate_tensile_strength_recovery",
            "value": 95.0,
            "value_raw": "95%",
            "unit": "%",
            "baseline": "pristine",
            "claim_type": "property_test",
            "conditions": {
                "repair_temperature_C": 25,
                "repair_duration_min": 60,
                "damage": "partial_cut",
                "surface_contact": True,
            },
            "evidence": [{
                "source_id": "source-strength",
                "quote": self.sources["source-strength"]["text"],
            }],
        }
        self.candidate = {
            "candidate_id": "candidate-P-A",
            "paper_id": "synthetic-paper",
            "sample_id": "P-A",
            "observations": [self.observation],
            "missing": [],
            "source_coverage": {"main_text": "checked", "supplementary": "checked"},
        }
        self.profile = {
            "profile_id": "illustrative-ambient-repair",
            "application": "Illustrative ambient-repair laboratory specimen",
            "criteria": [{
                "criterion_id": "strength-recovery",
                "property": "ultimate_tensile_strength_recovery",
                "unit": "%",
                "minimum": 90.0,
                "required": True,
                "required_claim_type": "property_test",
                "baseline": "pristine",
                "conditions": {
                    "repair_temperature_C": {"equals": 25},
                    "repair_duration_min": {"maximum": 60},
                    "damage": {"equals": "partial_cut"},
                    "surface_contact": {"equals": True},
                },
            }],
        }

    def receipt(self, observation=None, status="supported"):
        observation = self.observation if observation is None else observation
        return {
            "observation_id": observation["observation_id"],
            "paper_id": observation["paper_id"],
            "sample_id": observation["sample_id"],
            "record_digest": review_digest(observation, self.sources),
            "status": status,
            "reviewer": "Synthetic independent reviewer",
        }

    def screen(self, reviews=None):
        if reviews is None:
            reviews = [self.receipt()]
        return screen_candidate(self.candidate, self.profile, self.sources, reviews)

    def assertDecision(self, expected, result):
        self.assertEqual(expected, result["decision"], json.dumps(result, indent=2))
        self.assertIsInstance(result["criteria"], list)
        self.assertIsInstance(result["followups"], list)
        self.assertEqual("strength-recovery", result["criteria"][0]["criterion_id"])

    def test_supported_comparable_result_kept_for_followup(self):
        self.assertDecision("keep_for_followup", self.screen())

    def test_actual_comparable_failure_excluded_for_this_use(self):
        self.observation["value"] = 84.0
        self.observation["value_raw"] = "84%"
        text = self.sources["source-strength"]["text"].replace("95%", "84%")
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.assertDecision("exclude_for_use", self.screen())

    def test_heated_result_does_not_establish_ambient_performance(self):
        self.observation["conditions"]["repair_temperature_C"] = 90
        text = self.sources["source-strength"]["text"].replace("25 C", "90 C")
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.assertDecision("retrieve_more", self.screen())

    def test_partial_cut_does_not_establish_fully_severed_repair(self):
        self.profile["criteria"][0]["conditions"]["damage"]["equals"] = "fully_severed"
        self.assertDecision("retrieve_more", self.screen())

    def test_missing_critical_property_prevents_keep(self):
        self.candidate["observations"] = []
        self.candidate["missing"] = [{
            "property": "ultimate_tensile_strength_recovery",
            "reason": "not_extracted",
        }]
        self.assertDecision("retrieve_more", self.screen(reviews=[]))

    def test_undefined_threshold_requires_requirement_owner(self):
        del self.profile["criteria"][0]["minimum"]
        self.assertDecision("manual_review", self.screen())

    def test_extractor_verified_flag_cannot_replace_review_receipt(self):
        self.observation["evidence_status"] = "verified"
        self.observation["verified"] = True
        self.assertDecision("manual_review", self.screen(reviews=[]))

    def test_changed_source_invalidates_previous_review(self):
        reviews = [self.receipt()]
        self.sources["source-strength"]["text"] += " Correction: the sample label is under review."
        self.assertDecision("manual_review", self.screen(reviews=reviews))

    def test_changed_observation_value_invalidates_previous_review(self):
        reviews = [self.receipt()]
        self.observation["value"] = 99.0
        self.assertDecision("manual_review", self.screen(reviews=reviews))

    def test_wrong_sample_is_not_comparable_evidence(self):
        self.observation["sample_id"] = "P-B"
        text = self.sources["source-strength"]["text"].replace("P-A", "P-B")
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.assertDecision("manual_review", self.screen())

    def test_exact_quote_with_wrong_metric_is_blocked_by_review(self):
        text = "Sample P-A recovered 89% of its pristine elongation at break."
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.observation["value"] = 89.0
        self.observation["value_raw"] = "89%"
        # The extracted property remains tensile strength; the quote is exact
        # but an independent review rejects that scientific relationship.
        self.assertDecision("manual_review", self.screen([self.receipt(status="unsupported")]))

    def test_proposed_application_does_not_establish_device_test(self):
        self.observation["claim_type"] = "proposed_use"
        self.profile["criteria"][0]["required_claim_type"] = "tested_device"
        self.assertDecision("retrieve_more", self.screen())

    def test_conflicting_comparable_results_require_review(self):
        other = deepcopy(self.observation)
        other["observation_id"] = "strength-2"
        other["value"] = 82.0
        other["value_raw"] = "82%"
        text = self.sources["source-strength"]["text"].replace("95%", "82%")
        self.sources["source-strength-2"] = {
            "paper_id": "synthetic-paper",
            "locator": "Results, paragraph 2",
            "text": text,
        }
        other["evidence"] = [{"source_id": "source-strength-2", "quote": text}]
        self.candidate["observations"].append(other)
        self.assertDecision("manual_review", self.screen([self.receipt(), self.receipt(other)]))

    def test_supplied_uncertainty_crossing_threshold_requires_review(self):
        self.observation["uncertainty"] = {"lower": 85.0, "upper": 97.0, "unit": "%"}
        text = self.sources["source-strength"]["text"] + " The reported interval is 85% to 97%."
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.assertDecision("manual_review", self.screen())

    def test_incompatible_units_do_not_produce_numeric_pass(self):
        self.observation["unit"] = "MPa"
        self.observation["value_raw"] = "95 MPa"
        self.assertDecision("manual_review", self.screen())

    def test_missing_si_preserves_precise_followup_reason(self):
        self.candidate["observations"] = []
        self.candidate["missing"] = [{
            "property": "ultimate_tensile_strength_recovery",
            "reason": "supplementary_information_unavailable",
        }]
        self.candidate["source_coverage"]["supplementary"] = "unavailable"
        result = self.screen(reviews=[])
        self.assertDecision("retrieve_more", result)
        self.assertIn("supplementary_information_unavailable", json.dumps(result["followups"]))

    def test_inclusive_threshold_keeps_exact_boundary(self):
        self.profile["criteria"][0]["minimum"] = 95.0
        self.assertDecision("keep_for_followup", self.screen())

    def test_baseline_mismatch_requires_matching_evidence(self):
        self.profile["criteria"][0]["baseline"] = "uncut_aged_control"
        self.assertDecision("retrieve_more", self.screen())

    def test_omitted_conditions_require_application_owner(self):
        del self.profile["criteria"][0]["conditions"]
        result = self.screen()
        self.assertDecision("manual_review", result)
        self.assertTrue(any(gap["owner"] == "application_owner" for gap in result["followups"]))

    def test_fresh_review_cannot_make_numeric_raw_value_disagreement_pass(self):
        self.observation["value"] = 99.0
        self.profile["criteria"][0]["minimum"] = 98.0
        # The raw value and quoted source both still say 95%.  Even a freshly
        # supplied support receipt cannot make 99 a valid normalized value.
        result = self.screen([self.receipt()])
        self.assertDecision("manual_review", result)

    def test_malformed_missing_reason_object_is_rejected(self):
        self.candidate["missing"] = [{
            "property": "ultimate_tensile_strength_recovery",
            "reason": {"unavailable": True},
        }]
        with self.assertRaises(ValueError):
            self.screen()

    def test_passing_result_retains_null_measurement_followup(self):
        missing = deepcopy(self.observation)
        missing["observation_id"] = "strength-unavailable"
        missing["value"] = None
        missing["value_raw"] = None
        missing["missing_reason"] = "supplementary_information_unavailable"
        text = "A second strength recovery measurement for sample P-A is in the unavailable supplement."
        self.sources["source-unavailable"] = {
            "paper_id": "synthetic-paper",
            "locator": "Main text, supplement reference",
            "text": text,
        }
        missing["evidence"] = [{"source_id": "source-unavailable", "quote": text}]
        self.candidate["observations"].append(missing)
        result = self.screen([self.receipt(), self.receipt(missing)])
        self.assertDecision("keep_for_followup", result)
        self.assertIn("supplementary_information_unavailable", json.dumps(result["followups"]))


    def test_unrepresentable_raw_exponent_requires_review_without_crashing(self):
        raw = "95e9999999999999999999999999%"
        text = "Synthetic source reports " + raw + " for this observation."
        self.observation["value_raw"] = raw
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text
        self.assertDecision("manual_review", self.screen())

    def reported_deviation(self, raw, value, uncertainty):
        self.observation.update(value_raw=raw, value=value)
        if uncertainty is None:
            self.observation.pop("uncertainty", None)
        else:
            self.observation["uncertainty"] = uncertainty
        text = "Synthetic source reports " + raw + " for this observation."
        self.sources["source-strength"]["text"] = text
        self.observation["evidence"][0]["quote"] = text

    def test_reported_deviation_preserves_threshold_crossing(self):
        # Li et al. report this number for fracture-strain recovery, not UTS.
        self.observation["property"] = "fracture_strain_recovery"
        self.profile["criteria"][0]["property"] = "fracture_strain_recovery"
        self.reported_deviation("90 ± 3%", 90, {"lower": 87, "upper": 93, "unit": "%",
                                               "kind": "standard_deviation"})
        result = self.screen()
        self.assertDecision("manual_review", result)
        self.assertEqual("supported_as_reported", result["evidence"]["status"])
        self.assertEqual("uncertainty_crosses_requirement", result["criteria"][0]["reason"])
        self.assertEqual("90 ± 3%", self.observation["value_raw"])
        self.assertEqual("standard_deviation", self.observation["uncertainty"]["kind"])

    def test_reported_deviation_below_threshold_excludes(self):
        self.reported_deviation("68 ± 2%", 68, {"lower": 66, "upper": 70, "unit": "%"})
        result = self.screen()
        self.assertDecision("exclude_for_use", result)
        self.assertEqual("supported_as_reported", result["evidence"]["status"])

    def test_ascii_deviation_with_decimal_and_exponent_notation(self):
        self.reported_deviation("9.0e1 +/- 3e0%", 90,
                                {"lower": 87, "upper": 93, "unit": "%"})
        result = self.screen()
        self.assertEqual("supported_as_reported", result["evidence"]["status"])
        self.assertDecision("manual_review", result)

    def test_reported_deviation_requires_matching_finite_uncertainty(self):
        intervals = [None, {}, {"lower": 87, "unit": "%"},
                     {"lower": 86, "upper": 93, "unit": "%"},
                     {"lower": 87, "upper": 94, "unit": "%"},
                     {"lower": 87, "upper": 93, "unit": "MPa"},
                     {"lower": float("-inf"), "upper": 93, "unit": "%"}]
        for interval in intervals:
            with self.subTest(interval=interval):
                self.reported_deviation("90 ± 3%", 90, interval)
                # Invalid numeric evidence must fail before a review digest is used.
                result = self.screen(reviews=[])
                self.assertDecision("manual_review", result)
                self.assertEqual("raw_deviation_requires_matching_uncertainty",
                                 result["evidence"]["observations"][0]["reason"])

    def test_reported_deviation_rejects_negative_unit_and_value_mismatches(self):
        for raw, value, reason in [
                ("90 ± -3%", 90, "raw_value_format_requires_reviewed_normalization"),
                ("90 +/- -3%", 90, "raw_value_format_requires_reviewed_normalization"),
                ("90 ± 3 MPa", 90, "raw_unit_mismatch"),
                ("90 ± 3%", 91, "numeric_and_raw_value_mismatch")]:
            with self.subTest(raw=raw, value=value):
                self.reported_deviation(raw, value, {"lower": 87, "upper": 93, "unit": "%"})
                result = self.screen()
                self.assertDecision("manual_review", result)
                self.assertEqual(reason, result["evidence"]["observations"][0]["reason"])


class Task3CommandLineTests(unittest.TestCase):
    """Exercise the public CLI with disposable copies of its documented example."""

    example_dir = Path(__file__).resolve().parent / "examples" / "task3"

    def prepare(self, root):
        input_path = root / "input.json"
        review_path = root / "reviews.json"
        input_path.write_bytes((self.example_dir / "input.json").read_bytes())
        review_path.write_bytes((self.example_dir / "reviews.json").read_bytes())
        return input_path, review_path, root / "output"

    def invoke(self, args):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return selection_main(args)

    def test_documented_example_writes_expected_decisions_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path, review_path, output = self.prepare(Path(directory))
            original_input, original_reviews = input_path.read_bytes(), review_path.read_bytes()
            code = self.invoke(["--input", str(input_path), "--reviews", str(review_path),
                                "--out-dir", str(output)])
            self.assertEqual(0, code)
            expected = {"candidate-A": "keep_for_followup", "candidate-B": "exclude_for_use",
                        "candidate-C": "retrieve_more"}
            records = json.loads((output / "selection.json").read_text())
            self.assertEqual(expected, {r["candidate_id"]: r["decision"] for r in records})
            with (output / "selection.csv").open(newline="") as stream:
                csv_records = list(csv.DictReader(stream))
            self.assertEqual(expected, {r["candidate_id"]: r["decision"] for r in csv_records})
            followups = json.loads((output / "followups.json").read_text())
            self.assertTrue(any(g["candidate_id"] == "candidate-C" for g in followups))
            self.assertEqual(original_input, input_path.read_bytes())
            self.assertEqual(original_reviews, review_path.read_bytes())

    def test_cli_without_separate_reviews_requires_manual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path, _, output = self.prepare(Path(directory))
            code = self.invoke(["--input", str(input_path), "--out-dir", str(output)])
            self.assertEqual(0, code)
            records = json.loads((output / "selection.json").read_text())
            self.assertEqual({"candidate-A": "manual_review", "candidate-B": "manual_review",
                              "candidate-C": "manual_review"},
                             {r["candidate_id"]: r["decision"] for r in records})

    def test_invalid_input_writes_no_results_and_preserves_input(self):
        # Test parsing errors and a later malformed candidate so validation
        # cannot silently leave a partial result from earlier valid candidates.
        for invalid_kind in ("duplicate_key", "nan", "malformed_missing"):
            with self.subTest(invalid_kind=invalid_kind), tempfile.TemporaryDirectory() as directory:
                input_path, review_path, output = self.prepare(Path(directory))
                if invalid_kind == "duplicate_key":
                    input_path.write_text('{"candidates": [], "candidates": []}')
                else:
                    bundle = json.loads(input_path.read_text())
                    if invalid_kind == "nan":
                        bundle["candidates"][-1]["observations"][0]["value"] = float("nan")
                    else:
                        bundle["candidates"][-1]["missing"] = [{
                            "property": "creep_strain", "reason": {"unavailable": True},
                        }]
                    input_path.write_text(json.dumps(bundle))
                original_input, original_reviews = input_path.read_bytes(), review_path.read_bytes()
                code = self.invoke(["--input", str(input_path), "--reviews", str(review_path),
                                    "--out-dir", str(output)])
                self.assertEqual(2, code)
                self.assertFalse(output.exists(), "Invalid input must not create output artifacts")
                self.assertEqual(original_input, input_path.read_bytes())
                self.assertEqual(original_reviews, review_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
