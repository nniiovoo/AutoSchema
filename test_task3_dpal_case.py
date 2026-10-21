"""Replay checked DPAL experiments; report reference disagreements honestly."""
import json
from pathlib import Path
import tempfile
import unittest

from select_candidates import main
from selection_lib.screening import review_digest, screen_candidate


CASE = Path(__file__).resolve().parent / "examples/task3/dpal_experiments"


class DPALExperimentalCaseTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((CASE / "input.json").read_text())
        self.reviews = json.loads((CASE / "reviews.json").read_text())
        self.reference = json.loads((CASE / "reference.json").read_text())
        self.evaluation = json.loads((CASE / "evaluation.json").read_text())

    def test_source_reviews_and_dpal_membership_remain_bound(self):
        provenance = json.loads((CASE / "provenance.json").read_text())
        members = {r["doi_in_snapshot"] for r in provenance["records"]}
        self.assertEqual(3, len(members))
        receipts = {r["observation_id"]: r for r in self.reviews}
        for candidate in self.bundle["candidates"]:
            self.assertIn(candidate["paper_id"], members)
            for observation in candidate["observations"]:
                self.assertEqual(
                    review_digest(observation, self.bundle["sources"]),
                    receipts[observation["observation_id"]]["record_digest"],
                )
        self.assertEqual(
            {c["candidate_id"] for c in self.bundle["candidates"]},
            {c["candidate_id"] for c in self.reference["cases"]},
        )

    def test_real_case_replay_preserves_reference_disagreements(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(0, main([
                "--input", str(CASE / "input.json"),
                "--reviews", str(CASE / "reviews.json"),
                "--out-dir", directory,
            ]))
            rows = json.loads((Path(directory) / "selection.json").read_text())
        references = {c["candidate_id"]: c for c in self.reference["cases"]}
        checked = {c["candidate_id"]: c for c in self.evaluation["comparisons"]}
        matches = criterion_matches = 0
        for row in rows:
            expected = references[row["candidate_id"]]
            recorded = checked[row["candidate_id"]]
            self.assertEqual(recorded["selector_decision"], row["decision"])
            matches += row["decision"] == expected["decision"]
            criteria = {c["criterion_id"]: c for c in recorded["criteria"]}
            for criterion in row["criteria"]:
                cid = criterion["criterion_id"]
                self.assertEqual(criteria[cid]["reason"], criterion["reason"])
                self.assertEqual(criteria[cid]["selector_decision"], criterion["decision"])
                criterion_matches += criterion["decision"] == expected["criteria"][cid]
        self.assertEqual(2, matches)
        self.assertEqual(6, criterion_matches)
        self.assertEqual(matches, self.evaluation["summary"]["candidate_decision_matches"])
        self.assertEqual(criterion_matches, self.evaluation["summary"]["criterion_decision_matches"])

    def test_real_table_and_comma_require_review_and_keep_needs_receipts(self):
        states = {}
        for candidate in self.bundle["candidates"]:
            row = screen_candidate(candidate, self.bundle["profile"], self.bundle["sources"], self.reviews)
            states[candidate["candidate_id"]] = row
        self.assertEqual("raw_unit_mismatch", states["Balkenende2016-chainstopper1.5"]["criteria"][0]["reason"])
        self.assertEqual("numeric_and_raw_value_mismatch", states["Wang2020-RHP1"]["criteria"][0]["reason"])
        self.assertEqual("manual_review", states["Balkenende2016-chainstopper1.5"]["decision"])
        self.assertEqual("manual_review", states["Wang2020-RHP1"]["decision"])
        neat = self.bundle["candidates"][0]
        row = screen_candidate(neat, self.bundle["profile"], self.bundle["sources"], [])
        self.assertEqual("manual_review", row["decision"])


if __name__ == "__main__":
    unittest.main()
