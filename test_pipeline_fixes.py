"""Regression tests for the AutoSchema pipeline fixes on the bench branch.

No network or LLM calls: searches, downloads and the chat client are stubbed.
"""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import expand_round
import iterative_expand
from expand_lib.domain_args import get_spec
from expand_lib.searches import openalex_abstract, strip_jats
from expand_lib.utils import record_key
from extract_lib.schema_loader import load_schema
from prompt_lib import llm_client
from prompt_lib.llm_client import LLMCallError
from prompt_lib.snapshot import TRUNCATION_MARK, compact_snapshot

VALID_PDF = b"%PDF-1.4\n" + b"0" * 3000 + b"\n%%EOF\n"
HTML_PAGE = b"<html><body>" + b"landing page " * 300 + b"</body></html>"


def _fake_openai_module():
    mod = types.ModuleType("openai")

    class APIError(Exception):
        pass

    class RateLimitError(APIError):
        pass

    class APIConnectionError(APIError):
        pass

    class APITimeoutError(APIError):
        pass

    mod.APIError = APIError
    mod.RateLimitError = RateLimitError
    mod.APIConnectionError = APIConnectionError
    mod.APITimeoutError = APITimeoutError
    return mod


class LLMChatFailureTest(unittest.TestCase):
    def _run_with_client(self, create):
        fake = _fake_openai_module()
        client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))
        cfg = llm_client.LLMConfig()
        with mock.patch.dict(sys.modules, {"openai": fake}), \
                mock.patch.object(llm_client, "get_config", return_value=cfg), \
                mock.patch.object(llm_client, "get_chat_client", return_value=client), \
                mock.patch.object(llm_client.time, "sleep"):
            return fake, llm_client.llm_chat([{"role": "user", "content": "x"}])

    def test_api_errors_raise_instead_of_fake_empty_json(self):
        fake = _fake_openai_module()

        def create(**_):
            raise fake.APIConnectionError("down")

        with mock.patch.dict(sys.modules, {"openai": fake}), \
                mock.patch.object(llm_client, "get_config", return_value=llm_client.LLMConfig()), \
                mock.patch.object(llm_client, "get_chat_client", return_value=types.SimpleNamespace(
                    chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))), \
                mock.patch.object(llm_client.time, "sleep"):
            with self.assertRaises(LLMCallError):
                llm_client.llm_chat([{"role": "user", "content": "x"}])

    def test_unexpected_errors_raise(self):
        def create(**_):
            raise ValueError("bad request shape")

        with self.assertRaises(LLMCallError):
            self._run_with_client(create)

    def test_success_returns_content(self):
        def create(**_):
            msg = types.SimpleNamespace(content='{"queries": [1]}')
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])

        _fake, out = self._run_with_client(create)
        self.assertEqual(out, '{"queries": [1]}')


class SnapshotTest(unittest.TestCase):
    def test_every_seed_keeps_a_share_of_the_budget(self):
        seeds = [{"title": f"seed {i}", "notes": "x" * 5000, "empty": None, "blank": ""}
                 for i in range(5)]
        snap = compact_snapshot(seeds, budget=8000)
        self.assertLessEqual(len(snap), 8000)
        lines = snap.split("\n")
        self.assertEqual(len(lines), 5)
        for i, line in enumerate(lines):
            self.assertIn(f"seed {i}", line)
            self.assertTrue(line.endswith(TRUNCATION_MARK))
        self.assertNotIn('"empty"', snap)
        self.assertNotIn('"blank"', snap)

    def test_short_snapshots_are_left_whole(self):
        seeds = [{"title": "a"}, {"title": "b", "x": [1, None, ""]}]
        snap = compact_snapshot(seeds, budget=8000)
        self.assertEqual([json.loads(l) for l in snap.split("\n")],
                         [{"title": "a"}, {"title": "b", "x": [1]}])


class RecordKeyTest(unittest.TestCase):
    def test_arxiv_versions_share_one_key(self):
        a = {"id": "2401.12345v1", "title": "T"}
        b = {"id": "http://arxiv.org/abs/2401.12345v3", "title": "T (rev)"}
        self.assertEqual(record_key(a), record_key(b))
        self.assertEqual(record_key({"id": "cond-mat/0101001v2"}),
                         record_key({"id": "cond-mat/0101001"}))

    def test_doi_and_other_ids_unchanged(self):
        self.assertEqual(record_key({"doi": "10.1000/ABC", "id": "x"}), "10.1000/abc")
        self.assertEqual(record_key({"id": "https://openalex.org/W123"}),
                         "https://openalex.org/w123")
        self.assertEqual(record_key({"title": "  A   Title "}), "a title")

    def test_orchestrator_and_retrieval_agree(self):
        recs = [{"id": "2401.12345v2"}, {"doi": "10.1/X"}, {"title": "Some  Paper"}, {}]
        for r in recs:
            self.assertEqual(iterative_expand._record_key(r), expand_round.get_record_key(r))


class RetrievalLoopTest(unittest.TestCase):
    """run_one_round_search_and_download with stubbed searches and downloads."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.queries = [{"query_nl": f"query {i}", "query_bool": f"q{i}"} for i in range(10)]
        (self.root / "queries.json").write_text(json.dumps(self.queries))
        self.spec = get_spec("chem").resolve("cof")

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _search(src, query, per_source, **_):
        qi = query.split("query ")[-1].split()[0] if "query " in query else query
        return [{"source": src, "id": f"{src}-{qi}-{r}", "title": f"{src} {qi} {r}",
                 "pdf_url": f"https://example.org/{src}/{qi}/{r}.pdf", "domain_score": 0}
                for r in range(per_source)]

    def _run(self, exclude=None, html_for=()):
        def fake_download(url, dest):
            dest.write_bytes(HTML_PAGE if any(h in url for h in html_for) else VALID_PDF)
            return True

        with mock.patch.object(expand_round, "_run_search", side_effect=self._search), \
                mock.patch.object(expand_round, "download_pdf", side_effect=fake_download):
            return expand_round.run_one_round_search_and_download(
                queries_path=self.root / "queries.json",
                round_dir=self.root / "round",
                domain_spec=self.spec,
                sources=("openalex", "nature"),
                results_per_source=5,
                exclude_keys=exclude,
            )

    def test_every_query_runs_and_contributes(self):
        res = self._run()
        stats = json.loads(Path(res["retrieval_stats_path"]).read_text())
        self.assertEqual(stats["queries_run"], 10)
        self.assertTrue(all(q["new_candidates"] > 0 for q in stats["per_query"]))
        rows = [json.loads(l) for l in Path(res["search_results_path"]).read_text().splitlines()]
        self.assertTrue(rows)
        for row in rows:
            self.assertIn("found_by", row)
            self.assertIn(row["found_by"][0]["source"], ("openalex", "nature"))

    def test_html_pages_do_not_use_up_download_slots(self):
        # Every openalex URL returns an HTML landing page; nature URLs are PDFs.
        res = self._run(html_for=("/openalex/",))
        names = [p.name for p in res["selected_pdf_paths"]]
        self.assertEqual(len(names), 10)                 # target_per_round = 5 * 2
        downloads = res["download_dir"]
        for p in downloads.glob("*.pdf"):
            self.assertTrue(p.read_bytes().startswith(b"%PDF-"), p.name)

    def test_excluded_keys_are_skipped(self):
        exclude = {record_key({"id": f"openalex-{i}-0"}) for i in range(10)}
        res = self._run(exclude=exclude)
        stats = json.loads(Path(res["retrieval_stats_path"]).read_text())
        self.assertEqual(sum(q["excluded"] for q in stats["per_query"]), 10)
        rows = [json.loads(l) for l in Path(res["search_results_path"]).read_text().splitlines()]
        self.assertFalse({record_key(r) for r in rows} & exclude)


class SchemaLoaderTest(unittest.TestCase):
    def _load(self, fields):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "final_schema.json"
            p.write_text(json.dumps(fields))
            return load_schema(p)

    def test_phase1_schema_keys_are_mapped(self):
        f = self._load([{
            "name": "solvent_system",
            "description": "solvents used in synthesis",
            "examples": ["mesitylene/dioxane"],
            "evidence_examples": ["in mesitylene/dioxane (1:1) at 120 C"],
            "merged_from": ["reaction_solvent"],
            "support_count": 4,
        }])[0]
        self.assertEqual(f.evidence_snippets, ["in mesitylene/dioxane (1:1) at 120 C"])
        self.assertEqual(f.member_field_names, ["reaction_solvent"])
        self.assertTrue(f.is_multi_valued())
        self.assertIn("reaction solvent", f.all_search_terms())

    def test_explicit_value_type_and_phase2_keys_win(self):
        f = self._load([{
            "name": "bet_area", "value_type": "string",
            "evidence_snippets": ["S_BET = 1200 m2/g"], "evidence_examples": ["ignored"],
            "member_field_names": ["surface_area"], "aliases": ["SBET"],
        }])[0]
        self.assertFalse(f.is_multi_valued())
        self.assertEqual(f.evidence_snippets, ["S_BET = 1200 m2/g"])
        self.assertEqual(f.member_field_names, ["surface_area"])
        self.assertEqual(f.aliases, ["SBET"])


class AbstractTest(unittest.TestCase):
    def test_openalex_inverted_index(self):
        idx = {"Porous": [0], "frameworks": [1, 4], "are": [2], "crystalline": [3]}
        self.assertEqual(openalex_abstract(idx), "Porous frameworks are crystalline frameworks")
        self.assertIsNone(openalex_abstract(None))
        self.assertIsNone(openalex_abstract({}))

    def test_crossref_jats(self):
        self.assertEqual(strip_jats("<jats:p>COF <jats:italic>films</jats:italic>.</jats:p>"),
                         "COF films .")
        self.assertIsNone(strip_jats(None))


class FieldProposalFailureTest(unittest.TestCase):
    def setUp(self):
        from schema_lib.domain import SCHEMA_DOMAINS
        self.spec = SCHEMA_DOMAINS["chem"]
        self.papers = [{"source_file": "a.pdf", "text": "A"}, {"source_file": "b.pdf", "text": "B"}]

    def test_failed_paper_is_marked_not_silently_empty(self):
        from schema_lib import fields

        replies = iter([LLMCallError("timeout"),
                        json.dumps({"fields": [{"name": "solvent", "description": "d"}]})])

        def fake_chat(*_a, **_k):
            r = next(replies)
            if isinstance(r, Exception):
                raise r
            return r

        with mock.patch.object(fields, "llm_chat", side_effect=fake_chat):
            out = fields.propose_candidate_fields_per_paper(self.papers, self.spec, "COFs", 5)
        self.assertIn("error", out[0])
        self.assertEqual(out[0]["fields"], [])
        self.assertNotIn("error", out[1])
        self.assertEqual(out[1]["fields"][0]["name"], "solvent")

    def test_all_papers_failing_raises(self):
        from schema_lib import fields

        with mock.patch.object(fields, "llm_chat", side_effect=LLMCallError("down")):
            with self.assertRaises(LLMCallError):
                fields.propose_candidate_fields_per_paper(self.papers, self.spec, "COFs", 5)


if __name__ == "__main__":
    unittest.main()
