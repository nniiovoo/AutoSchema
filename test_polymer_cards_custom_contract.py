"""A bounded context review must use and record its actual output contract."""
import hashlib
import json
from types import SimpleNamespace
import unittest

from polymer_cards_lib.llm import _request


class PolymerCustomContractTests(unittest.TestCase):
    def test_review_contract_is_forwarded_and_fingerprinted(self):
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(
                content='{"paper_id":"fixture","edits":[]}', refusal=None))], usage=None)
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        contract = {"type": "json_schema", "json_schema": {"name": "synthetic_context_contract", "strict": True, "schema": schema}}
        parsed, trace = _request(client, "model", "original source data", 1234,
                                 system_prompt="Review context only.", response_format=contract)
        self.assertEqual([], parsed["edits"])
        self.assertEqual(contract, calls[0]["response_format"])
        self.assertEqual("Review context only.", calls[0]["messages"][0]["content"])
        self.assertEqual(1234, calls[0]["max_completion_tokens"])
        self.assertEqual("synthetic_context_contract", trace["extraction_profile"]["schema_name"])
        self.assertEqual(hashlib.sha256(b"Review context only.").hexdigest(), trace["extraction_profile"]["system_prompt_sha256"])
        canonical = json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), trace["extraction_profile"]["schema_sha256"])


if __name__ == "__main__":
    unittest.main()
