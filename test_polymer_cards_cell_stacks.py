"""An explicitly described cell stack is not an additive preparation."""
from copy import deepcopy
import json
import unittest

from polymer_cards_lib.validation import build_cards
from test_polymer_cards_sample_links import fixture


class PolymerCellStackTests(unittest.TestCase):
    def run_link(self, quote, *, label="P1", sibling=False):
        document, raw, _ = fixture()
        if label != "P1":
            document, raw = json.loads(json.dumps([document, raw]).replace("P1", label))
        document["chunks"].append({"chunk_id": "cell", "text": quote, "source_part": "synthetic",
                                   "locator": "Electrochemical tests", "document_sha256": "a" * 64})
        entity = raw["entities"][0]
        entity["specimens"] = entity["specimens"][:1]
        entity["specimens"][0]["label"] = label
        if sibling:
            entity["specimens"].append({"specimen_id": "cell-looking", "label": label + "/Li",
                                         "evidence": [{"chunk_id": "cell", "quote": quote}]})
        prop = entity["properties"]["items"][0]
        prop["specimen_evidence"] = [{"chunk_id": "cell", "quote": quote}]
        before = deepcopy(raw)
        result = build_cards(document, raw)
        self.assertEqual(before, raw)
        return result

    def test_explicit_central_membrane_in_electrode_stack_is_not_an_additive(self):
        for quote in ("An asymmetric cell stainless steel (SS)/P1/Li was used.",
                      "An electrochemical cell SS/P1/Li was assembled.",
                      "The SS/P1/Li asymmetric cell was used."):
            for sibling in (False, True):
                with self.subTest(quote=quote, sibling=sibling):
                    result = self.run_link(quote, sibling=sibling)
                    self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))

    def test_cell_word_does_not_hide_an_additive_or_another_preparation(self):
        for quote in ("A cell used P1/LiFSI electrolyte.",
                      "An asymmetric cell SS/P1/LiFSI was assembled.",
                      "An asymmetric cell SS/P1/Li-TFSI electrolyte was prepared.",
                      "An asymmetric cell SS/P1/Li–TFSI electrolyte was prepared.",
                      "An asymmetric cell SS/P1/Li.TFSI electrolyte was prepared.",
                      "An asymmetric cell SS/P1/Li was assembled. P1/LiFSI electrolyte was prepared.",
                      "P1/Li mixture was prepared; a cell was later tested."):
            with self.subTest(quote=quote):
                result = self.run_link(quote)
                self.assertEqual([], result["cards"][0]["properties"]["items"])

    def test_slashes_inside_full_selected_form_are_preserved(self):
        result = self.run_link("An asymmetric cell SS/A/B/Li was assembled.", label="A/B")
        self.assertEqual(1, len(result["cards"][0]["properties"]["items"]))


if __name__ == "__main__":
    unittest.main()
