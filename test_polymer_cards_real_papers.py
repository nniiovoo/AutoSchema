"""Replay selected primary-paper facts; do not call this model extraction accuracy."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from extract_polymer_cards import main
from polymer_cards_lib.sources import load_documents
from polymer_cards_lib.validation import FIELD_NAMES


CASE = Path(__file__).resolve().parent / "examples/polymer_cards"


class RealPolymerCardTests(unittest.TestCase):
    def test_reference_and_source_revisions_are_frozen_and_domains_both_covered(self):
        provenance = json.loads((CASE / "provenance.json").read_text())
        self.assertEqual(provenance["reference_sha256"], hashlib.sha256((CASE / "reference.json").read_bytes()).hexdigest())
        self.assertEqual(provenance["curated_responses_sha256"], hashlib.sha256((CASE / "curated-responses.json").read_bytes()).hexdigest())
        documents = load_documents(CASE / "papers.json")
        self.assertEqual(3, len(documents))
        self.assertEqual({"disulfide", "batteries"}, {domain for d in documents for domain in d["domains"]})
        self.assertTrue(any(d["domains"] == ["disulfide"] for d in documents))
        self.assertTrue(all(s["coverage"] == "selected_excerpts" for d in documents for s in d["source_files"]))

    def test_actual_cli_replay_preserves_selected_identities_and_scientific_assignments(self):
        reference = json.loads((CASE / "reference.json").read_text())
        with tempfile.TemporaryDirectory() as output, redirect_stdout(io.StringIO()):
            self.assertEqual(0, main(["--papers", str(CASE / "papers.json"),
                                     "--records", str(CASE / "curated-responses.json"), "--out-dir", output]))
            data = json.loads((Path(output) / "cards.json").read_text())
            html = (Path(output) / "cards.html").read_text()
            audit = json.loads((Path(output) / "audit.json").read_text())
        self.assertEqual("curated_record_replay", data["run_metadata"]["mode"])
        self.assertEqual(0, data["run_metadata"]["model_calls"])
        self.assertEqual(8, audit["counts"]["retained_cards"])
        self.assertEqual(4, audit["counts"]["discarded_entities"])
        cards = {}
        for result in data["results"]:
            paper_id = result["paper_id"]
            self.assertEqual(set(reference["expected_retained"][paper_id]), {c["entity_id"] for c in result["cards"]})
            self.assertEqual(set(reference["expected_discarded"][paper_id]), {c["entity_id"] for c in result["discarded_entities"]})
            self.assertEqual([], result["validation_issues"])
            for card in result["cards"]:
                self.assertTrue(set(FIELD_NAMES) <= set(card))
                self.assertEqual("retained_polymer", card["decision"])
                cards[card["entity_id"]] = card
        for expected in reference["fact_expectations"]:
            group = cards[expected["entity_id"]][expected["field"]]
            if "expected_status" in expected:
                self.assertEqual(expected["expected_status"], group["status"])
                continue
            matches = [item for item in group["items"] if item["value"] == expected["value"]]
            self.assertTrue(matches, expected)
            item = matches[0]
            for key in ("property", "unit", "specimen_id"):
                if key in expected:
                    self.assertEqual(expected[key], item[key])
            if "temperature" in expected:
                self.assertIn(expected["temperature"], [c["value"] for c in item["conditions"]])
            for field in expected.get("missing_fields", []):
                self.assertEqual("not_found_in_provided_text", cards[expected["entity_id"]][field]["status"])
        self.assertEqual("commercially_purchased", cards["pei-peo"]["source_tag"]["items"][0]["value"])
        self.assertEqual("author_synthesized", cards["pei-bhds"]["source_tag"]["items"][0]["value"])
        self.assertIn("6.5 × 10−5", cards["pei-hdi"]["properties"]["items"][0]["value"])
        self.assertIn("LiFSI", " ".join(i["value"] for i in cards["pei-bhds"]["composition"]["items"]))
        self.assertIn("Original evidence", html)
        self.assertIn("Not found in the supplied text", html)


if __name__ == "__main__":
    unittest.main()
