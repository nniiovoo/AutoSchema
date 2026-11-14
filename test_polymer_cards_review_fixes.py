"""Regressions for a code review of the polymer-card library (2026-11-14).

MathML scripts and strict-focus warnings were fixed independently on the
branch; these tests keep them covered alongside the floats-group and
whole-name evaluation fixes.
"""
from copy import deepcopy
import json
import tempfile
import unittest
from pathlib import Path

from polymer_cards_lib.context_review import build_context_review_prompt
from polymer_cards_lib.evaluation import evaluate_run
from polymer_cards_lib.prompt import worked_example
from polymer_cards_lib.sources import _jats_chunks
from polymer_cards_lib.validation import build_cards

MATHML = """<article xmlns:mml="http://www.w3.org/1998/Math/MathML"><body><sec><title>Results</title>
<p>The modulus was 3<mml:math><mml:mo>×</mml:mo><mml:msup><mml:mn>10</mml:mn><mml:mn>5</mml:mn></mml:msup></mml:math> Pa.</p>
<p>Mn = 7.3 × <mml:math><mml:msubsup><mml:mi>X</mml:mi><mml:mn>2</mml:mn><mml:mi>n</mml:mi></mml:msubsup></mml:math>.</p>
</sec></body></article>"""

TABLES = """<article><body><sec><title>Results</title>
<p>Table 1 lists the data.<table-wrap id="t1"><label>Table 1</label><caption><p>Conductivity</p></caption><table><tr><th>Sample</th><th>σ (S/cm)</th></tr><tr><td>P1</td><td>2.4</td></tr><tr><td>P2</td><td>10</td></tr></table></table-wrap></p>
</sec></body>
<floats-group><table-wrap id="t2"><label>Table 2</label><table><tr><td>P3</td><td>5.5</td></tr></table></table-wrap></floats-group></article>"""


def _chunks(xml):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "paper.xml"
        path.write_text(xml, encoding="utf-8")
        return _jats_chunks(path)


class JatsMathAndTablesTests(unittest.TestCase):
    def test_mathml_exponents_keep_their_position(self):
        texts = [c["text"] for c in _chunks(MATHML)]
        self.assertIn("The modulus was 3×10⁵ Pa.", texts)
        self.assertNotIn("3×105", " ".join(texts))
        self.assertIn("X₂^{n}", texts[1])

    def test_nested_and_floating_tables_keep_cell_boundaries(self):
        chunks = _chunks(TABLES)
        texts = [c["text"] for c in chunks]
        joined = "\n".join(texts)
        self.assertIn("P1 | 2.4", joined)            # nested table: cells stay separate
        self.assertNotIn("P12.4", joined)
        floats = [c for c in chunks if "P3 | 5.5" in c["text"]]
        self.assertEqual(1, len(floats))              # <floats-group> tables are read
        self.assertTrue(floats[0]["locator"].endswith("Table 2"))
        self.assertTrue(chunks[0]["text"].startswith("Table 1 lists the data."))


def _ev(chunk, quote):
    return {"chunk_id": chunk, "quote": quote, "evidence_status": "quote_matched"}


class EvaluationLabelTests(unittest.TestCase):
    def test_longer_hyphenated_name_is_not_the_shorter_polymer(self):
        prop = {"entity_id": "bhds", "property": "electrochemical stability window", "value": "4.1", "unit": "V",
                "specimen_id": "bhds-salt", "conditions": [],
                "evidence": [_ev("r", "PTMG-HDI-BHDS/LiFSI is stable up to 4.1 V")]}
        card = {"entity_id": "bhds", "name": "PTMG-HDI-BHDS", "identity_kind": "specific_polymer",
                "classification": {"is_polymer": True},
                "identity_evidence": [_ev("id", "PTMG-HDI-BHDS was synthesized")], "aliases": [],
                "specimens": [{"specimen_id": "bhds-salt", "label": "PTMG-HDI-BHDS/LiFSI",
                               "evidence": [_ev("prep", "PTMG-HDI-BHDS/LiFSI")]}],
                "properties": {"status": "reported", "items": [prop]}}
        run = {"results": [{"paper_id": "pei", "cards": [card], "review_queue": [], "discarded_entities": []}]}
        ref = {"identity_expectations": [{"paper_id": "pei", "name": "PTMG-HDI"}],
               "measurement_expectations": [{"claim_id": "pei-hdi-voltage", "paper_id": "pei",
                                             "entity_labels": ["PTMG-HDI"], "value": "4.1", "unit": "V",
                                             "specimen_require_any": ["LiFSI"],
                                             "specimen_forbid": ["neat", "salt-free", "without salt"]}]}
        out = evaluate_run(run, ref)
        self.assertNotEqual("matched", out["identities"][0]["status"])
        self.assertNotEqual("matched_focused_expectation", out["measurements"][0]["status"])
        self.assertIn("parent_identity_does_not_match", out["measurements"][0]["candidates"][0]["reasons"])


class StrictFocusWarningTests(unittest.TestCase):
    def test_strict_focus_keeps_warnings_for_its_targets(self):
        document, previous = worked_example()
        warnings = build_cards(document, previous)["attribution_warnings"]
        self.assertTrue(warnings)
        focus = [{"entity_id": warnings[0]["entity_id"],
                  "property_index": int(warnings[0]["path"].split("[")[1].rstrip("]")),
                  "reason": "Check the tested specimen form."}]
        text = build_context_review_prompt(document, previous, review_focus=focus, strict_focus=True)
        payload = json.loads(text.split("\nUNTRUSTED CONTEXT-REVIEW TARGETS\n", 1)[1])
        kept = payload["validation_feedback"]["attribution_warnings"]
        self.assertEqual([(w["entity_id"], w["path"]) for w in warnings[:1]],
                         [(w["entity_id"], w["path"]) for w in kept])


class SameConditionValueTests(unittest.TestCase):
    """The conflict key compares whitespace-normalized text, like quote matching."""

    def properties(self, document, response):
        result = build_cards(document, response)
        return (result["cards"][0]["properties"]["status"],
                {issue["reason"] for issue in result["validation_issues"]})

    def test_value_restated_with_other_spacing_is_not_a_conflict(self):
        document, response = worked_example()
        items = response["entities"][0]["properties"]["items"]
        restated = deepcopy(items[1])
        restated["value"] = "1.0  \u00d7\u00a010\u22124"
        items.append(restated)
        status, reasons = self.properties(document, response)
        self.assertEqual("reported", status)
        self.assertNotIn("multiple_property_values_for_same_stated_conditions", reasons)

    def test_condition_spacing_does_not_hide_a_real_conflict(self):
        document, response = worked_example()
        second = " A second P1 film had breaking strength 14 MPa at 25\u00b0C."
        next(c for c in document["chunks"] if c["chunk_id"] == "example-film")["text"] += second
        items = response["entities"][0]["properties"]["items"]
        other = deepcopy(items[0])
        other["value"] = "14"
        other["evidence"] = [{"chunk_id": "example-film", "quote": second.strip()}]
        other["conditions"][1]["value"] = "7  mm\u00a0min\u22121"
        items.append(other)
        status, reasons = self.properties(document, response)
        self.assertEqual("conflicting", status)
        self.assertIn("multiple_property_values_for_same_stated_conditions", reasons)


if __name__ == "__main__":
    unittest.main()
