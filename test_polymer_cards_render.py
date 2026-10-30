"""Readability, source linkage and safe rendering for polymer-card outputs."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from polymer_cards_lib.render import render_html, render_markdown, write_outputs


def example(paper_id="paper-a", title="Example polymer paper", locator="Methods A"):
    document = {
        "paper_id": paper_id, "title": title, "url": "https://example.org/paper",
        "chunks": [{"chunk_id": "same-id", "source_part": "main", "locator": locator,
                    "page": 2, "text": "Polymer P was prepared. Conductivity 0.00024 S/cm at30 C.",
                    "document_sha256": "abc123"}],
    }
    evidence = [{"chunk_id": "same-id", "quote": "Polymer P was prepared.", "evidence_status": "quote_matched"}]
    card = {
        "entity_id": "P", "name": "Polymer P", "identity_evidence": copy.deepcopy(evidence),
        "classification": {"is_polymer": True, "reason": "Polymer stated in source", "evidence": copy.deepcopy(evidence)},
        "specimens": [{"specimen_id": "salted", "label": "P/LiFSI 2:1 film", "evidence": copy.deepcopy(evidence)}],
        "source_tag": {"status": "reported", "items": [{"entity_id": "P", "value": "author_synthesized", "evidence": copy.deepcopy(evidence)}]},
    }
    result = {"paper_id": paper_id, "cards": [card], "discarded_entities": [{"name": "LiFSI", "reason": "Salt"}],
              "review_queue": [], "validation_issues": [], "statistics": {"retained": 1}}
    return document, result, evidence


class PolymerCardRenderTests(unittest.TestCase):
    def test_partial_run_is_prominent_but_success_and_legacy_runs_are_not_partial(self):
        document, result, _ = example()
        metadata = {"run_complete": False, "papers_completed": 1, "papers_requested": 3,
                    "failed_paper_id": "paper-b"}
        page = render_html([result], [document], metadata)
        markdown = render_markdown([result], [document], metadata)
        for view in (page, markdown):
            self.assertIn("Partial run", view)
            self.assertIn("completed 1 of 3 requested papers", view)
            self.assertIn("drafts and still need review", view)
        self.assertIn("paper-b", page)
        self.assertIn(r"paper\-b", markdown)
        self.assertIn('class="partial-run"', page)
        self.assertIn("**Partial run**", markdown)
        for complete in ({"run_complete": True, "papers_completed": 3, "papers_requested": 3}, {}):
            self.assertNotIn('class="partial-run"', render_html([result], [document], complete))
            self.assertNotIn("**Partial run**", render_markdown([result], [document], complete))

    def test_all_six_groups_visible_even_when_information_is_missing(self):
        document, result, _ = example()
        page = render_html([result], [document], {"mode": "curated_replay"})
        for label in ("Monomers", "Composition", "Synthesis text", "Properties", "Applications", "Source tag"):
            self.assertIn("<h3>" + label + "</h3>", page)
        self.assertIn("Not found in the supplied text", page)
        self.assertIn("Synthesized by the authors", page)
        self.assertIn("Original quote matched to source", page)
        self.assertIn("page 2", page)
        self.assertIn("Methods A", page)
        self.assertIn("abc123", page)
        self.assertIn("A matched quotation does not by itself verify the scientific interpretation.", page)

    def test_html_escapes_names_facts_quotes_metadata_and_rejects_script_urls(self):
        document, result, evidence = example(title='<script>alert("title")</script>')
        document["url"] = "javascript:alert(1)"
        document["chunks"][0]["locator"] = '<img src=x onerror="bad()">'
        result["cards"][0]["name"] = '<script>alert("name")</script>'
        bad = '<img src=x onerror="bad()">'
        result["cards"][0]["description"] = {"value": bad, "evidence": [{"chunk_id": "same-id", "quote": bad}]}
        result["review_queue"] = [{"record": bad}]
        page = render_html([result], [document], {})
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img ", page)
        self.assertNotIn('href="javascript:', page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&lt;img", page)

    def test_same_chunk_id_in_different_papers_resolves_to_its_own_source(self):
        doc_a, result_a, _ = example(locator="Only paper A method")
        doc_b, result_b, _ = example("paper-b", "Second source", "Only paper B method")
        page = render_html([result_a, result_b], [doc_a, doc_b], {})
        first, second = page.split('<section class="paper">')[1:]
        self.assertIn("Only paper A method", first)
        self.assertNotIn("Only paper B method", first)
        self.assertIn("Only paper B method", second)
        self.assertNotIn("Only paper A method", second)

    def test_repeated_values_keep_separate_specimens_conditions_and_evidence(self):
        document, result, evidence = example()
        result["cards"][0]["properties"] = {"status": "reported", "items": [
            {"entity_id": "P", "property": "ionic conductivity", "value": "0.00024", "unit": "S/cm",
             "specimen_id": "salted", "conditions": [{"name": "temperature", "value": t, "evidence": copy.deepcopy(evidence)}],
             "evidence": copy.deepcopy(evidence)} for t in [25, 30]
        ]}
        page = render_html([result], [document], {})
        self.assertEqual(2, page.count("ionic conductivity: 0.00024 S/cm"))
        self.assertIn("25", page)
        self.assertIn("30", page)
        self.assertIn("P/LiFSI 2:1 film", page)

    def test_script_conversion_is_declared_beside_the_evidence_in_both_views(self):
        document, result, _ = example()
        document["chunks"][0]["text_transformations"] = ["jats_script_notation_v1"]
        page = render_html([result], [document], {})
        markdown = render_markdown([result], [document], {})
        for view in (page, markdown):
            self.assertIn("preserved superscripts/subscripts", view)
            self.assertIn("converted source text", view)
        self.assertNotIn("Original quote matched to source", page)

    def test_transformation_labels_come_from_source_chunks_not_model_claims(self):
        document, result, _ = example()
        result["cards"][0]["identity_evidence"][0]["text_transformations"] = ["jats_script_notation_v1"]
        page = render_html([result], [document], {})
        markdown = render_markdown([result], [document], {})
        self.assertIn("Original quote matched to source", page)
        for view in (page, markdown):
            self.assertNotIn("preserved superscripts/subscripts", view)

    def test_sample_link_evidence_remains_separate_from_measurement_evidence(self):
        document, result, evidence = example()
        document["chunks"].append({"chunk_id": "sample-link", "source_part": "main",
                                   "locator": "Electrolyte preparation", "document_sha256": "abc123",
                                   "text": "P/LiFSI was cast as a film."})
        result["cards"][0]["properties"] = {"status": "reported", "items": [{
            "entity_id": "P", "property": "ionic conductivity", "value": "0.00024", "unit": "S/cm",
            "specimen_id": "salted", "conditions": [], "evidence": copy.deepcopy(evidence),
            "specimen_evidence": [{"chunk_id": "sample-link", "quote": "P/LiFSI was cast as a film.",
                                   "evidence_status": "quote_matched"}],
        }]}
        page = render_html([result], [document], {})
        markdown = render_markdown([result], [document], {})
        self.assertIn("<summary>Sample-link evidence (1 source passage)</summary>", page)
        for view in (page, markdown):
            self.assertIn("Sample-link evidence", view)
            self.assertIn("P/LiFSI was cast as a film.", view)
            self.assertIn("Electrolyte preparation", view)

    def test_empty_sample_link_evidence_is_shown_as_missing(self):
        document, result, evidence = example()
        result["cards"][0]["properties"] = {"status": "reported", "items": [{
            "entity_id": "P", "property": "ionic conductivity", "value": "0.00024", "unit": "S/cm",
            "specimen_id": "salted", "conditions": [], "evidence": copy.deepcopy(evidence),
            "specimen_evidence": [],
        }]}
        for view in (render_html([result], [document], {}), render_markdown([result], [document], {})):
            self.assertIn("Sample-link evidence: not attached", view)

    def test_attribution_warnings_are_visible_and_safely_escaped(self):
        document, result, _ = example()
        result["cards"][0]["attribution_warnings"] = [{
            "reason": "specimen_label_matches_other_material", "specimen_label": '<img src=x onerror="bad()">',
            "related_entity_ids": ["P2", "<script>bad()</script>"],
        }]
        page = render_html([result], [document], {})
        markdown = render_markdown([result], [document], {})
        for view in (page, markdown):
            self.assertIn("Sample/material link needs review", view)
            self.assertIn("P2", view)
            self.assertIn("&lt;img", view)
            self.assertNotIn("<img ", view)
            self.assertNotIn("<script>", view)
        self.assertIn("specimen label matches other material", page)

    def test_output_files_preserve_machine_records_and_separate_audit(self):
        document, result, evidence = example()
        result["cards"][0]["aliases"] = [{"value": "Poly-P", "evidence": copy.deepcopy(evidence)}]
        result["cards"][0]["role"] = {"value": "control", "evidence": copy.deepcopy(evidence)}
        original = copy.deepcopy(result)
        with tempfile.TemporaryDirectory() as temporary:
            paths = write_outputs([result], [document], temporary, {"mode": "curated_replay"})
            self.assertEqual({"cards.json", "cards.jsonl", "cards.html", "cards.md", "audit.json", "sources.json"}, set(paths))
            saved = json.loads(Path(paths["cards.json"]).read_text())
            self.assertEqual([original], saved["results"])
            cards = [json.loads(line) for line in Path(paths["cards.jsonl"]).read_text().splitlines()]
            self.assertEqual("paper-a", cards[0]["paper_id"])
            audit = json.loads(Path(paths["audit.json"]).read_text())
            self.assertEqual(1, audit["counts"]["retained_cards"])
            self.assertEqual(1, audit["counts"]["discarded_entities"])
            self.assertEqual(0, audit["counts"]["attribution_warnings"])
            self.assertEqual([], audit["papers"][0]["attribution_warnings"])
            self.assertEqual([document], json.loads(Path(paths["sources.json"]).read_text())["documents"])
            markdown = Path(paths["cards.md"]).read_text()
            self.assertIn("Poly-P", Path(paths["cards.html"]).read_text())
            self.assertIn("control", markdown)
            self.assertIn("Original evidence", markdown)
            self.assertIn("```text", markdown)
        self.assertEqual(original, result)

    def test_paper_audits_preserve_unique_attribution_warnings_and_counts(self):
        document, result, _ = example()
        warning = {"reason": "specimen_label_shared_between_polymer_records", "specimen_label": "P film",
                   "related_entity_ids": ["P", "P2"], "detail": "Check exact material identity."}
        result["attribution_warnings"] = [warning]
        result["cards"][0]["attribution_warnings"] = [copy.deepcopy(warning)]
        second = copy.deepcopy(result["cards"][0])
        second["entity_id"] = "P2"
        result["cards"].append(second)
        with tempfile.TemporaryDirectory() as temporary:
            paths = write_outputs([result], [document], temporary, {})
            audit = json.loads(Path(paths["audit.json"]).read_text())
            self.assertEqual(1, audit["counts"]["attribution_warnings"])
            self.assertEqual([warning], audit["papers"][0]["attribution_warnings"])
            for filename in ("cards.html", "cards.md"):
                view = Path(paths[filename]).read_text()
                self.assertIn('"attribution_warnings"' if filename.endswith(".md") else "&quot;attribution_warnings&quot;", view)
                self.assertIn("Check exact material identity.", view)

    def test_invalid_nonfinite_json_does_not_create_partial_outputs(self):
        document, result, _ = example()
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "result"
            with self.assertRaises(ValueError):
                write_outputs([result], [document], out, {"bad": float("nan")})
            self.assertFalse(out.exists())

    def test_all_targets_are_preflighted_before_previous_run_is_replaced(self):
        document, result, _ = example()
        for invalid_kind in ("directory", "symlink"):
            with self.subTest(kind=invalid_kind), tempfile.TemporaryDirectory() as temporary:
                out = Path(temporary)
                old = out / "cards.json"
                old.write_bytes(b"old run\n")
                other = out / "unrelated.txt"
                other.write_text("leave me")
                invalid = out / "cards.jsonl"
                if invalid_kind == "directory":
                    invalid.mkdir()
                else:
                    invalid.symlink_to(other)
                with self.assertRaises(ValueError):
                    write_outputs([result], [document], out, {})
                self.assertEqual(b"old run\n", old.read_bytes())
                self.assertEqual("leave me", other.read_text())
                self.assertFalse((out / "cards.html").exists())
                self.assertFalse(any(p.name.startswith(".polymer-cards-") for p in out.iterdir()))

    def test_late_commit_error_rolls_back_existing_and_new_files(self):
        document, result, _ = example()
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            (out / "cards.json").write_bytes(b"previous cards")
            (out / "raw-responses.json").write_bytes(b"previous responses")
            (out / "unrelated.txt").write_text("unchanged")
            real_replace = os.replace
            failed = False

            def fail_raw_response_once(source, target):
                nonlocal failed
                if Path(target).name == "raw-responses.json" and not failed:
                    failed = True
                    raise OSError("simulated late disk error")
                return real_replace(source, target)

            with patch("polymer_cards_lib.render.os.replace", side_effect=fail_raw_response_once):
                with self.assertRaises(OSError):
                    write_outputs([result], [document], out, {}, {"raw-responses.json": {"responses": []}})
            self.assertTrue(failed)
            self.assertEqual(b"previous cards", (out / "cards.json").read_bytes())
            self.assertEqual(b"previous responses", (out / "raw-responses.json").read_bytes())
            self.assertEqual("unchanged", (out / "unrelated.txt").read_text())
            self.assertEqual({"cards.json", "raw-responses.json", "unrelated.txt"}, {p.name for p in out.iterdir()})

    def test_additional_json_outputs_join_run_and_reject_unsafe_names(self):
        document, result, _ = example()
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "result"
            raw = {"responses": [{"paper_id": "paper-a", "entities": []}]}
            paths = write_outputs([result], [document], out, {}, {"raw-responses.json": raw})
            self.assertEqual(raw, json.loads(Path(paths["raw-responses.json"]).read_text()))
        for bad_name in ("../elsewhere.json", "/tmp/elsewhere.json", "subdir/result.json", "subdir\\result.json", "cards.json", ".."):
            with self.subTest(name=bad_name), tempfile.TemporaryDirectory() as temporary:
                out = Path(temporary) / "result"
                with self.assertRaises(ValueError):
                    write_outputs([result], [document], out, {}, {bad_name: {}})
                self.assertFalse(out.exists())

    def test_staging_cleanup_tolerates_disappeared_entries_but_propagates_other_errors(self):
        document, result, _ = example()
        real_rmtree = shutil.rmtree
        for error_type in (FileNotFoundError, PermissionError):
            with self.subTest(error=error_type.__name__), tempfile.TemporaryDirectory() as temporary:
                out = Path(temporary) / "result"

                def cleanup_with_race(staging, *, onerror=None):
                    self.assertTrue(callable(onerror))
                    error = error_type("simulated staging cleanup race")
                    onerror(os.unlink, str(Path(staging) / "._new"), (error_type, error, None))
                    real_rmtree(staging, onerror=onerror)

                with patch("polymer_cards_lib.render.shutil.rmtree", side_effect=cleanup_with_race):
                    if error_type is PermissionError:
                        with self.assertRaises(PermissionError):
                            write_outputs([result], [document], out, {})
                    else:
                        paths = write_outputs([result], [document], out, {})
                        self.assertTrue(all(Path(p).is_file() for p in paths.values()))
                        self.assertFalse(any(p.name.startswith(".polymer-cards-") for p in out.iterdir()))


if __name__ == "__main__":
    unittest.main()
