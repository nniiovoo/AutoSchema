"""Preserve source gaps and honest software/reference disagreements in the battery case."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from select_candidates import main
from selection_lib.screening import review_digest


ROOT = Path(__file__).resolve().parent
CASE = ROOT / "examples/task3/battery_electrolytes"


def read(name):
    return json.loads((CASE / name).read_text())


class BatteryCaseTests(unittest.TestCase):
    def test_reference_profile_and_review_revisions_remain_bound(self):
        bundle, reference, evaluation = read("input.json"), read("reference.json"), read("evaluation.json")
        self.assertEqual(read("profile.json"), bundle["profile"])
        for filename, key in [("profile.json", "profile_sha256"), ("reference.json", "reference_sha256"),
                              ("input.json", "input_sha256"), ("reviews.json", "reviews_sha256")]:
            self.assertEqual(hashlib.sha256((CASE / filename).read_bytes()).hexdigest(), evaluation[key])
        self.assertEqual(reference["profile_sha256"], evaluation["profile_sha256"])
        reviews = {r["observation_id"]: r for r in read("reviews.json")}
        references = {r["candidate_id"]: r for r in reference["records"]}
        members = {r["DOI"] for r in read("provenance.json")["records"]}
        self.assertEqual(4, len(members))
        for candidate in bundle["candidates"]:
            self.assertIn(candidate["paper_id"], members)
            self.assertEqual(candidate["sample_id"], references[candidate["candidate_id"]]["sample_id"])
            for observation in candidate["observations"]:
                self.assertEqual(review_digest(observation, bundle["sources"]),
                                 reviews[observation["observation_id"]]["record_digest"])

    def test_actual_replay_retains_the_two_numeric_review_failures(self):
        with tempfile.TemporaryDirectory() as output:
            self.assertEqual(0, main(["--input", str(CASE / "input.json"),
                                     "--profile", str(CASE / "profile.json"),
                                     "--reviews", str(CASE / "reviews.json"), "--out-dir", output]))
            records = json.loads((Path(output) / "selection.json").read_text())
        checks = {c["candidate_id"]: c for c in read("evaluation.json")["comparisons"]}
        matches = 0
        for record in records:
            checked = checks[record["candidate_id"]]
            self.assertEqual(checked["selector_decision"], record["decision"])
            self.assertEqual(checked["reason"], record["criteria"][0]["reason"])
            matches += record["decision"] == checked["reference_decision"]
            self.assertTrue(all(not action["retrieval_executed"] for action in record["followups"]))
        self.assertEqual(3, matches)
        self.assertEqual(2, sum(r["decision"] == "manual_review" for r in records))
        self.assertFalse(any(r["decision"] in {"keep_for_followup", "exclude_for_use"} for r in records))

    def test_target_gaps_preserve_real_non_target_numbers_without_interpolation(self):
        candidates = read("input.json")["candidates"]
        for candidate in candidates[2:]:
            observation = candidate["observations"][0]
            self.assertIsNone(observation["value"])
            self.assertIsNone(observation["value_raw"])
            self.assertTrue(candidate["related_results"])
            self.assertTrue(all(r["selector_evaluates"] is False for r in candidate["related_results"]))
        for candidate in (candidates[2], candidates[4]):
            observation = candidate["observations"][0]
            self.assertEqual(30, observation["conditions"]["measurement_temperature_C"])
            self.assertIn("plotted", observation["missing_reason"])
        self.assertEqual(25, candidates[3]["observations"][0]["conditions"]["measurement_temperature_C"])
        self.assertEqual([25, 35], [r["measurement_temperature_C"] for r in candidates[3]["related_results"][:2]])

    def test_original_notation_and_control_identity_are_not_silently_repaired(self):
        candidates = read("input.json")["candidates"]
        for candidate in candidates[:2]:
            self.assertIn("×", candidate["observations"][0]["value_raw"])
            self.assertIn("cm−1", candidate["observations"][0]["value_raw"])
        eligibility = read("eligibility.json")["cases"]
        controls = [c for c in eligibility if c["electrolyte_role"] == "performance_control"]
        self.assertEqual(["Pei2024-HDI-LiFSI-control"], [c["candidate_id"] for c in controls])
        self.assertTrue(all(c["automatic_eligibility_validation"] is False for c in eligibility))


if __name__ == "__main__":
    unittest.main()
