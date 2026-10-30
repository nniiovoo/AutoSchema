"""Regression checks for the live request contract, without a provider call."""
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest

from polymer_cards_lib import prompt
from polymer_cards_lib.llm import ModelRequestError, extract_document
from polymer_cards_lib.validation import build_cards


class PolymerCardContractTests(unittest.TestCase):
    def setUp(self):
        self.document = {"paper_id": "paper", "title": "Fixture", "domains": [], "chunks": []}
        self.request = None

        def create(**kwargs):
            self.request = kwargs
            return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(
                content=json.dumps({"paper_id": "paper", "entities": []}), refusal=None))], usage=None)

        self.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    def test_live_request_enforces_schema_instead_of_json_syntax_only(self):
        _, trace = extract_document(self.client, "configured-model", self.document)
        output = self.request["response_format"]
        self.assertEqual("json_schema", output["type"])
        self.assertTrue(output["json_schema"]["strict"])
        schema = output["json_schema"]["schema"]
        entity = schema["$defs"]["entity"]
        for field in ("monomers", "composition", "synthesis_text", "properties", "applications", "source_tag"):
            self.assertIn(field, entity["required"])
        composition = schema["$defs"]["composition_fact"]
        self.assertIn("basis", composition["required"])
        self.assertEqual(["string", "null"], composition["properties"]["basis"]["type"])
        prop = schema["$defs"]["property_fact"]
        self.assertIn("specimen_id", prop["required"])
        self.assertIn("conditions", prop["required"])
        self.assertEqual(prompt.extraction_profile(), trace["extraction_profile"])

    def test_every_schema_object_is_closed_and_requires_its_declared_keys(self):
        def check(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    self.assertIs(False, value.get("additionalProperties"))
                    self.assertEqual(set(value["properties"]), set(value["required"]))
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
        check(prompt.build_response_format()["json_schema"]["schema"])
        # Callers cannot mutate the next request's shared contract accidentally.
        changed = prompt.build_response_format()
        changed["json_schema"]["schema"]["required"].clear()
        self.assertEqual(["paper_id", "entities"], prompt.build_response_format()["json_schema"]["schema"]["required"])

    def test_worked_example_keeps_matrix_and_electrolyte_ratios_and_values_separate(self):
        document, response = prompt.worked_example()
        before = deepcopy(response)
        result = build_cards(document, response)
        self.assertEqual([], result["review_queue"])
        self.assertEqual(1, len(result["cards"]))
        card = result["cards"][0]
        self.assertEqual(["monomer_feed_molar_ratio", "polymer_salt_mass_ratio"],
                         [item["basis"] for item in card["composition"]["items"]])
        self.assertEqual(["p1-film", "p1-salt-film"],
                         [item["specimen_id"] for item in card["properties"]["items"]])
        self.assertEqual("reported", card["source_tag"]["status"])
        self.assertEqual("author_synthesized", card["source_tag"]["items"][0]["value"])
        self.assertEqual(before, response)
        self.assertIn("SYNTHETIC", prompt.build_system_prompt())

    def test_refusal_and_nonterminal_response_are_not_treated_as_valid_empty_extractions(self):
        for finish, content, refusal in [("stop", "", "Refused"), ("content_filter", "{}", None)]:
            response = SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish,
                message=SimpleNamespace(content=content, refusal=refusal))], usage=None)
            self.client.chat.completions.create = lambda **kwargs: response
            with self.assertRaises(ModelRequestError):
                extract_document(self.client, "model", self.document)


if __name__ == "__main__":
    unittest.main()
