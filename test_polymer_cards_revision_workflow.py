"""Public CLI checks for explicit source-grounded revision of saved proposals."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from extract_polymer_cards import main
from polymer_cards_lib.sources import load_documents
from test_polymer_cards_workflow import dump, example


class PolymerCardRevisionWorkflowTests(unittest.TestCase):
    def setup_files(self, root):
        manifest, records, source, response = example(root)
        sources = root / "prior-sources.json"
        dump(sources, {"documents": load_documents(manifest)})
        return manifest, records, sources, response

    def invoke(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(arguments)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_revision_uses_model_and_prior_proposals_without_modifying_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, records, sources, response = self.setup_files(root)
            before = {p: p.read_bytes() for p in [manifest, records, sources]}
            revised = deepcopy(response)
            revised["entities"][0]["identity_kind"] = "specific_polymer"
            output = root / "revision"
            with patch("polymer_cards_lib.llm.create_client", return_value=(object(), "configured-model", "openai")), \
                    patch("polymer_cards_lib.llm.revise_document", create=True,
                          return_value=(revised, {"usage": {}, "request_kind": "source_grounded_revision"})) as revise, \
                    patch("polymer_cards_lib.llm.extract_document", side_effect=AssertionError("Revision must be labeled separately from fresh extraction")):
                code, _, error = self.invoke(["--papers", str(manifest), "--repair-records", str(records),
                    "--repair-sources", str(sources), "--out-dir", str(output)])
            self.assertEqual(0, code, error)
            self.assertEqual(1, revise.call_count)
            self.assertEqual(response, revise.call_args.args[3])
            saved = json.loads((output / "cards.json").read_text())
            self.assertEqual("live_model_revision", saved["run_metadata"]["mode"])
            self.assertEqual(1, saved["run_metadata"]["model_calls"])
            self.assertTrue(saved["run_metadata"]["run_complete"])
            self.assertIn("repair_input_records_sha256", saved["run_metadata"])
            self.assertIn("repair_input_sources_sha256", saved["run_metadata"])
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_revision_rejects_stale_sources_and_wrong_papers_before_model_access(self):
        for issue in ("source_text", "source_paper", "response_paper", "duplicate_source", "missing_snapshot"):
            with self.subTest(issue=issue), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest, records, sources, response = self.setup_files(root)
                data = json.loads(sources.read_text())
                if issue == "source_text":
                    data["documents"][0]["chunks"][0]["text"] += " changed"
                elif issue == "source_paper":
                    data["documents"][0]["paper_id"] = "different-paper"
                elif issue == "response_paper":
                    response["paper_id"] = "different-paper"
                    dump(records, {"responses": [response]})
                elif issue == "duplicate_source":
                    data["documents"].append(deepcopy(data["documents"][0]))
                dump(sources, data)
                args = ["--papers", str(manifest), "--repair-records", str(records), "--out-dir", str(root / "out")]
                if issue != "missing_snapshot":
                    args += ["--repair-sources", str(sources)]
                with patch("polymer_cards_lib.llm.create_client", side_effect=AssertionError("Reject stale revision before client access")):
                    code, _, _ = self.invoke(args)
                self.assertEqual(2, code)
                self.assertFalse((root / "out" / "cards.json").exists())

    def test_revision_cannot_overwrite_its_prior_records_or_source_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, records, sources, response = self.setup_files(root)
            protected = root / "raw-responses.json"
            records.rename(protected)
            before = protected.read_bytes()
            with patch("polymer_cards_lib.llm.create_client", side_effect=AssertionError("No access before overwrite check")):
                code, _, _ = self.invoke(["--papers", str(manifest), "--repair-records", str(protected),
                    "--repair-sources", str(sources), "--out-dir", str(root)])
            self.assertEqual(2, code)
            self.assertEqual(before, protected.read_bytes())


if __name__ == "__main__":
    unittest.main()
