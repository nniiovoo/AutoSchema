"""Source-grounded revision checks; these tests never call a provider."""
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest

from polymer_cards_lib import llm, prompt


def fixture():
    texts = [
        ("range", "Results", "Polymers P1–P7 were prepared."),
        ("method", "Methods / Polymer synthesis", "A typical polymerization procedure for P3 was used. The purified P3 sample had Mw/Mn = 1.77."),
        ("film", "Methods / Film preparation", "A P3 film was cast from solution."),
        ("decoy", "Results", "Polymer P30 was a different material."),
    ]
    document = {"paper_id": "paper", "title": "Fixture, not a real paper", "domains": [],
                "chunks": [{"chunk_id": key, "text": text, "locator": locator, "source_part": "main",
                            "document_sha256": "a" * 64, "source_path": "/private/not-for-model"}
                           for key, locator, text in texts]}
    ev = [{"chunk_id": "range", "quote": texts[0][2]}]
    previous = {"paper_id": "paper", "entities": [{"entity_id": "p3", "name": "P3",
        "identity_evidence": deepcopy(ev),
        "classification": {"is_polymer": True, "reason": "Prior model proposal", "evidence": deepcopy(ev)},
        "aliases": [{"value": "P3", "evidence": deepcopy(ev)}]}]}
    return document, previous


class PolymerCardRepairTests(unittest.TestCase):
    def test_v2_schema_requires_explicit_nullable_identity_scope(self):
        output = prompt.build_response_format()["json_schema"]
        self.assertEqual("polymer_cards_strict_v2", output["name"])
        entity = output["schema"]["$defs"]["entity"]
        self.assertIn("identity_kind", entity["required"])
        self.assertEqual(["specific_polymer", "polymer_family", None], entity["properties"]["identity_kind"]["enum"])
        self.assertEqual("specific_polymer", prompt.worked_example()[1]["entities"][0]["identity_kind"])

    def test_revision_context_retrieves_exact_names_without_expanding_ranges(self):
        from polymer_cards_lib.repair import build_revision_context
        document, previous = fixture()
        context = build_revision_context(document, previous)
        self.assertIn("entity_name_not_in_original_evidence", [i["reason"] for i in context["validation_feedback"]["validation_issues"]])
        candidates = context["candidate_source_contexts"][0]["source_names"][0]["candidate_chunks"]
        self.assertEqual("method", candidates[0]["chunk_id"])
        self.assertEqual({"method", "film"}, {c["chunk_id"] for c in candidates})
        self.assertIn("not chemical proof", context["candidate_context_limit"])
        self.assertNotIn("source_path", json.dumps(context))

    def test_revision_inputs_are_not_mutated_or_replaced_with_inferred_answers(self):
        from polymer_cards_lib.repair import build_revision_context
        document, previous = fixture()
        before = deepcopy((document, previous))
        context = build_revision_context(document, previous)
        self.assertEqual(before, (document, previous))
        self.assertEqual(previous, context["previous_response"])
        self.assertEqual("range", context["previous_response"]["entities"][0]["identity_evidence"][0]["chunk_id"])
        context["previous_response"]["entities"].clear()
        self.assertEqual(1, len(previous["entities"]))

    def test_stale_paper_or_invalid_prior_records_fail_before_provider_call(self):
        document, previous = fixture()
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=lambda **kwargs: self.fail("Invalid inputs must not call a provider"))))
        for bad in ({"paper_id": "other", "entities": []}, {"paper_id": "paper", "entities": None}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                llm.revise_document(client, "model", document, bad)

    def test_revision_request_has_full_sources_proposals_feedback_and_one_strict_call(self):
        document, previous = fixture()
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(
                content=json.dumps({"paper_id": "paper", "entities": []}), refusal=None))], usage=None)
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        result, trace = llm.revise_document(client, "model", document, previous, 1234)
        self.assertEqual(1, len(calls))
        self.assertEqual("json_schema", calls[0]["response_format"]["type"])
        self.assertEqual(1234, calls[0]["max_completion_tokens"])
        user = calls[0]["messages"][1]["content"]
        for value in ("previous_response", "validation_feedback", "candidate_source_contexts", "P30", "purified P3"):
            self.assertIn(value, user)
        self.assertIn("untrusted proposals", user)
        self.assertNotIn("/private/not-for-model", user)
        self.assertNotIn("checked_pei", user)
        self.assertEqual("source_grounded_model_revision", trace["request_mode"])
        self.assertEqual(64, len(trace["previous_response_sha256"]))
        self.assertEqual(64, len(trace["request_prompt_sha256"]))
        self.assertEqual({"paper_id": "paper", "entities": []}, result)

    def test_revision_retains_safe_model_failure_handling(self):
        document, previous = fixture()
        class ProviderError(Exception):
            status_code = 401
        def fail(**kwargs):
            raise ProviderError("credential-containing provider message")
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
        with self.assertRaises(llm.ModelRequestError) as error:
            llm.revise_document(client, "model", document, previous)
        self.assertIn("HTTP 401", str(error.exception))
        self.assertNotIn("credential-containing", str(error.exception))


if __name__ == "__main__":
    unittest.main()
