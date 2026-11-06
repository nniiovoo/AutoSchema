"""Readable provenance distinguishes source retrieval from model quotation."""
import unittest

from polymer_cards_lib.render import render_html, render_markdown
from polymer_cards_lib.validation import build_cards
from test_polymer_cards_span_validation import document, response


class PolymerSpanRenderTests(unittest.TestCase):
    def test_selected_source_passage_and_original_offsets_are_visible(self):
        doc = document()
        result = build_cards(doc, response(doc))
        evidence = result["cards"][0]["properties"]["items"][0]["evidence"][0]
        for view in (render_html([result], [doc], {}), render_markdown([result], [doc], {})):
            self.assertIn("Selected source passage retrieved exactly", view)
            self.assertIn(evidence["span_id"], view.replace("\\-", "-"))
            self.assertIn("Source characters", view)
            self.assertIn("M_{w}/M_{n}", view)


if __name__ == "__main__":
    unittest.main()
