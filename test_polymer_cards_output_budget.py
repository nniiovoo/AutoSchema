"""Bounded larger responses for full evidence-rich polymer cards."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from extract_polymer_cards import main
from test_polymer_cards_workflow import example


class PolymerOutputBudgetTests(unittest.TestCase):
    def test_explicit_larger_budget_reaches_model_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, _, _, response = example(root)
            output = root / "out"
            with patch("polymer_cards_lib.llm.create_client", return_value=(object(), "model", "openai")), \
                    patch("polymer_cards_lib.llm.extract_document", return_value=(response, {"usage": {}})) as extract, \
                    redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                code = main(["--papers", str(manifest), "--out-dir", str(output), "--max-output-tokens", "48000"])
            self.assertEqual(0, code)
            self.assertEqual(48000, extract.call_args.args[3])
            metadata = json.loads((output / "cards.json").read_text())["run_metadata"]
            self.assertEqual(48000, metadata["max_output_tokens_per_live_request"])

    def test_excessive_budget_is_rejected_before_model_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, _, _, _ = example(root)
            with patch("polymer_cards_lib.llm.create_client", side_effect=AssertionError("Must reject before model access")), \
                    redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                code = main(["--papers", str(manifest), "--out-dir", str(root / "out"), "--max-output-tokens", "48001"])
            self.assertEqual(2, code)
            self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
