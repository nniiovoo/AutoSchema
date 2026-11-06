"""Unresolved source discrepancies must survive the readable card view."""
import copy
import unittest

from polymer_cards_lib.render import render_html, render_markdown
from test_polymer_cards_render import example


class PolymerCardConflictRenderTests(unittest.TestCase):
    def test_conflicting_source_reports_and_both_evidence_spans_remain_visible(self):
        document, result, evidence = example()
        document["chunks"].append({"chunk_id": "results", "locator": "Results B",
                                   "source_part": "main", "text": "Thickness about 17 μm."})
        card = result["cards"][0]
        card["properties"] = {"status": "conflicting", "items": [], "conflicts": [{
            "property": "membrane thickness", "description": "Methods and Results differ; sample equivalence is unresolved.",
            "specimen_ids": ["salted"], "evidence": [*copy.deepcopy(evidence),
                {"chunk_id": "results", "quote": "Thickness about 17 μm.", "evidence_status": "quote_matched"}]}]}
        before = copy.deepcopy(result)
        for view in (render_html([result], [document], {}), render_markdown([result], [document], {})):
            self.assertIn("Unresolved source discrepancy", view)
            self.assertIn("sample equivalence is unresolved", view)
            self.assertIn("Methods A", view)
            self.assertIn("Results B", view)
            self.assertIn("Thickness about 17 μm.", view)
            self.assertIn("P/LiFSI 2:1 film", view)
        self.assertEqual(before, result)

    def test_conflict_notes_are_escaped_and_missing_context_is_visible(self):
        document, result, evidence = example()
        card = result["cards"][0]
        card["properties"] = {"status": "conflicting", "items": [{
            "entity_id": "P", "property": "conductivity", "value": "0.00024", "unit": None,
            "specimen_id": "salted", "conditions": [], "evidence": copy.deepcopy(evidence)}],
            "conflicts": [{"property": "<script>bad()</script>", "description": '<img src=x onerror="bad()">',
                           "specimen_ids": ["salted"], "evidence": copy.deepcopy(evidence)}]}
        for view in (render_html([result], [document], {}), render_markdown([result], [document], {})):
            self.assertNotIn("<script>", view)
            self.assertNotIn("<img ", view)
            self.assertIn("&lt;script&gt;", view)
            self.assertIn("Test conditions: none captured", view)
            self.assertIn("Unit: not specified or dimensionless", view)


if __name__ == "__main__":
    unittest.main()
