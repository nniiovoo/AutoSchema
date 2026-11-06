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

    def test_live_schema_requires_evidence_linked_property_conflicts(self):
        output = prompt.build_response_format()["json_schema"]
        self.assertEqual("polymer_cards_strict_v3", output["name"])
        defs = output["schema"]["$defs"]
        self.assertIn("conflicts", defs["properties_group"]["required"])
        conflict = defs["property_conflict"]
        self.assertEqual({"property", "description", "specimen_ids", "evidence"}, set(conflict["required"]))
        self.assertEqual("array", conflict["properties"]["specimen_ids"]["type"])
        self.assertNotIn("conflicts", defs["composition_group"]["properties"])
        _, response = prompt.worked_example()
        self.assertEqual([], response["entities"][0]["properties"]["conflicts"])

    def test_conflict_instructions_require_known_specimens_without_resolving_their_relation(self):
        document, response = prompt.worked_example()
        entity = response["entities"][0]
        entity["properties"]["conflicts"] = [{
            "property": "breaking strength", "description": "The correspondence remains unresolved.",
            "specimen_ids": [], "evidence": entity["properties"]["items"][0]["evidence"],
        }]
        result = build_cards(document, response)
        self.assertIn("conflict_specimen_ids_missing_or_invalid", [r["reason"] for r in result["review_queue"]])
        self.assertNotIn("may be empty", prompt.SYSTEM_PROMPT)
        self.assertIn("at least one", prompt.SYSTEM_PROMPT)
        self.assertIn("never invent a specimen ID", prompt.SYSTEM_PROMPT)
        self.assertIn("relationship is uncertain in description", prompt.SYSTEM_PROMPT)

    def test_fresh_request_indexes_source_methods_without_replacing_source_chunks(self):
        document = {"paper_id": "synthetic", "title": "Synthetic example", "domains": [], "chunks": [
            {"chunk_id": "intro", "text": "P1 is a polymer.", "locator": "Introduction", "source_part": "main"},
            {"chunk_id": "protocol", "text": "P1 film tensile tests used a crosshead speed of 7 mm min−1.",
             "locator": "Methods / Characterization", "source_part": "main"},
            {"chunk_id": "result", "text": "P1 film has strength 12 MPa.", "locator": "Results", "source_part": "main"},
        ]}
        before = deepcopy(document)
        extract_document(self.client, "configured-model", document)
        user = self.request["messages"][1]["content"]
        payload = json.loads(user.split("\n", 1)[1])
        self.assertEqual(document["chunks"], payload["chunks"])
        entries = payload["method_context_index"]
        self.assertIn("protocol", [entry["chunk_id"] for entry in entries])
        self.assertNotIn("intro", [entry["chunk_id"] for entry in entries])
        self.assertEqual(before, document)
        self.assertTrue(all(set(entry) <= {"chunk_id", "locator", "protocol_terms"} for entry in entries))
        self.assertIn("not evidence that", payload["method_context_index_scope"])
        self.assertNotIn("reference", payload)
        self.assertNotIn("previous_response", payload)

    def test_synthetic_example_attaches_testing_methods_to_results_separately(self):
        document, response = prompt.worked_example()
        properties = response["entities"][0]["properties"]["items"]
        self.assertIn("example-testing-methods", [c["chunk_id"] for c in document["chunks"]])
        for prop in properties:
            conditions = prop["conditions"]
            self.assertGreaterEqual(len(conditions), 2)
            self.assertTrue(any(any(e["chunk_id"] == "example-testing-methods" for e in c["evidence"])
                                for c in conditions))

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
