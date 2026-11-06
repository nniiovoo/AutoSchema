"""Source selection preserves scientific text without asking a model to copy it."""
from copy import deepcopy
import unittest

from polymer_cards_lib.evidence_spans import (
    CATALOG_VERSION, build_span_catalog, combine_adjacent_spans, resolve_span,
)


def document(text="P3 was not salted. GPC gives M_{n} = 63 KDa and M_{w}/M_{n} = 1.77.", paper="paper-a"):
    return {"paper_id": paper, "chunks": [{"chunk_id": "source-one", "text": text,
             "source_part": "main", "locator": "Methods", "document_sha256": "a" * 64}]}


def full_span(doc):
    chunk = doc["chunks"][0]
    return next(s for s in build_span_catalog(doc)
                if s["chunk_id"] == chunk["chunk_id"] and s["start"] == 0 and s["end"] == len(chunk["text"]))


class EvidenceSpanSelectionTests(unittest.TestCase):
    def test_full_and_child_spans_are_exact_source_slices_and_cover_each_chunk(self):
        doc = document("P3 film was prepared. Conductivity is 1.77 S cm⁻¹.\n\nP4 was not tested.")
        doc["chunks"].append({**deepcopy(doc["chunks"][0]), "chunk_id": "source-two", "text": "Short statement"})
        spans = build_span_catalog(doc)
        self.assertEqual(len(spans), len({s["span_id"] for s in spans}))
        self.assertEqual(len(spans), len({(s["chunk_id"], s["start"], s["end"]) for s in spans}))
        self.assertGreater(len(spans), len(doc["chunks"]))
        for chunk in doc["chunks"]:
            candidates = [s for s in spans if s["chunk_id"] == chunk["chunk_id"]]
            self.assertTrue(any(s["start"] == 0 and s["end"] == len(chunk["text"]) for s in candidates))
            for span in candidates:
                self.assertEqual(chunk["text"][span["start"]:span["end"]], span["text"])

    def test_selection_retains_negation_chemical_scripts_exponents_and_uncertainty(self):
        text = "P3 was not salted. CH₂Cl₂, N₂ and M_{w}/M_{n} = 1.77; 93% ± 3%; 10⁻⁵ differs from 10−5."
        doc = document(text)
        span = full_span(doc)
        ref = resolve_span(doc, span["chunk_id"], span["span_id"])
        self.assertEqual(text, ref["quote"])
        self.assertEqual("source_span_selection", ref["evidence_origin"])
        self.assertEqual(CATALOG_VERSION, ref["catalog_version"])
        self.assertEqual((0, len(text)), (ref["source_start"], ref["source_end"]))

    def test_offsets_count_original_unicode_codepoints_and_preserve_whitespace(self):
        text = "  α 🧪 e\u0301 sample.\n\tCH₂Cl₂ remains unchanged.  "
        doc = document(text)
        full = full_span(doc)
        self.assertEqual(text, resolve_span(doc, full["chunk_id"], full["span_id"])["quote"])
        child = next(s for s in build_span_catalog(doc) if s["text"] == "CH₂Cl₂ remains unchanged.")
        self.assertEqual(text.index("CH₂Cl₂"), child["start"])
        ref = resolve_span(doc, child["chunk_id"], child["span_id"])
        self.assertEqual(child["text"], text[ref["source_start"]:ref["source_end"]])

    def test_catalog_is_deterministic_and_does_not_mutate_source_documents(self):
        doc = document()
        before = deepcopy(doc)
        self.assertEqual(build_span_catalog(doc), build_span_catalog(deepcopy(doc)))
        self.assertEqual(before, doc)

    def test_changed_source_text_invalidates_a_previous_selection(self):
        doc = document()
        span = full_span(doc)
        changed = deepcopy(doc)
        changed["chunks"][0]["text"] = changed["chunks"][0]["text"].replace("not salted", "salted")
        with self.assertRaises(ValueError):
            resolve_span(changed, span["chunk_id"], span["span_id"])
        with self.assertRaises(ValueError):
            resolve_span(changed, span["chunk_id"], span["span_id"], catalog=build_span_catalog(doc))

    def test_changed_original_file_hash_invalidates_selection_even_with_same_text(self):
        doc = document()
        span = full_span(doc)
        changed = deepcopy(doc)
        changed["chunks"][0]["document_sha256"] = "b" * 64
        with self.assertRaises(ValueError):
            resolve_span(changed, span["chunk_id"], span["span_id"])

    def test_same_text_and_chunk_id_in_another_paper_cannot_reuse_selection(self):
        doc = document()
        span = full_span(doc)
        changed = deepcopy(doc)
        changed["paper_id"] = "paper-b"
        with self.assertRaises(ValueError):
            resolve_span(changed, span["chunk_id"], span["span_id"])

    def test_a_chunk_cannot_claim_another_paper_inside_the_catalogue(self):
        doc = document()
        doc["chunks"][0]["paper_id"] = "different-paper"
        with self.assertRaises(ValueError):
            build_span_catalog(doc)

    def test_same_text_in_another_chunk_cannot_reuse_selection(self):
        doc = document()
        doc["chunks"].append({**deepcopy(doc["chunks"][0]), "chunk_id": "other-source"})
        span = full_span(doc)
        with self.assertRaises(ValueError):
            resolve_span(doc, "other-source", span["span_id"])

    def test_unknown_selection_is_not_retrieved_by_fuzzy_matching_or_id_shape(self):
        doc = document()
        for chunk, span in [("missing", full_span(doc)["span_id"]), ("source-one", "spn-" + "0" * 32),
                            ("source-one", "1.77"), ("source-one", None), ("source-one", 2)]:
            with self.subTest(chunk=chunk, span=span), self.assertRaises(ValueError):
                resolve_span(doc, chunk, span)

    def test_prebuilt_catalog_is_supported_and_tampering_cannot_change_the_source_quote(self):
        doc = document()
        spans = build_span_catalog(doc)
        span = full_span(doc)
        expected = resolve_span(doc, span["chunk_id"], span["span_id"])
        self.assertEqual(expected, resolve_span(doc, span["chunk_id"], span["span_id"], catalog=spans))
        for key, value in [("text", "P3 was salted."), ("start", 1), ("end", 3),
                           ("chunk_id", "other-source"), ("span_id", "forged")]:
            modified = deepcopy(spans)
            target = next(s for s in modified if s["span_id"] == span["span_id"])
            target[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                resolve_span(doc, span["chunk_id"], span["span_id"], catalog=modified)
        duplicate = deepcopy(spans) + [deepcopy(span)]
        with self.assertRaises(ValueError):
            resolve_span(doc, span["chunk_id"], span["span_id"], catalog=duplicate)

    def test_returned_objects_do_not_mutate_an_internal_catalog_cache(self):
        doc = document()
        span = full_span(doc)
        first = build_span_catalog(doc)
        first[0]["text"] = "Changed"
        selected = resolve_span(doc, span["chunk_id"], span["span_id"])
        selected["quote"] = "Changed again"
        self.assertEqual(doc["chunks"][0]["text"], build_span_catalog(doc)[0]["text"])
        self.assertEqual(doc["chunks"][0]["text"], resolve_span(doc, span["chunk_id"], span["span_id"])["quote"])

    def test_decimal_values_are_not_split_at_the_decimal_point(self):
        doc = document("Dispersity is 1.77. Conductivity is 0.00024 S/cm.")
        texts = [s["text"] for s in build_span_catalog(doc)]
        self.assertIn("Dispersity is 1.77.", texts)
        self.assertIn("Conductivity is 0.00024 S/cm.", texts)
        self.assertNotIn("Dispersity is 1.", texts)

    def test_empty_catalog_and_duplicate_source_ids_are_explicit(self):
        self.assertEqual([], build_span_catalog({"paper_id": "empty", "chunks": []}))
        with self.assertRaises(ValueError):
            resolve_span({"paper_id": "empty", "chunks": []}, "missing", "missing")
        doc = document()
        doc["chunks"].append(deepcopy(doc["chunks"][0]))
        with self.assertRaises(ValueError):
            build_span_catalog(doc)


class AdjacentSourceSpanSupportTests(unittest.TestCase):
    def reference(self, doc, text, *, chunk_id="source-one"):
        span = next(s for s in build_span_catalog(doc) if s["chunk_id"] == chunk_id and s["text"] == text)
        return {"chunk_id": chunk_id, **resolve_span(doc, chunk_id, span["span_id"])}

    def test_adjacent_abbreviation_and_value_have_exact_union_support_without_raw_edits(self):
        doc = document("The strain was ca. 456%, with uncertainty retained.")
        refs = [self.reference(doc, "The strain was ca."),
                self.reference(doc, "456%, with uncertainty retained.")]
        before_doc, before_refs = deepcopy(doc), deepcopy(refs)
        support = combine_adjacent_spans(doc, refs)
        self.assertEqual(1, len(support))
        union = support[0]
        self.assertEqual(doc["chunks"][0]["text"], union["quote"])
        self.assertEqual("source_span_selection_union", union["evidence_origin"])
        self.assertEqual([r["span_id"] for r in refs], union["span_ids"])
        self.assertNotIn("span_id", union)
        self.assertEqual((0, len(union["quote"])), (union["source_start"], union["source_end"]))
        self.assertEqual(before_doc, doc)
        self.assertEqual(before_refs, refs)

    def test_original_whitespace_and_source_order_are_preserved(self):
        doc = document("ca.\n\t\n456%.")
        refs = [self.reference(doc, "456%."), self.reference(doc, "ca.")]
        union = combine_adjacent_spans(doc, refs)[0]
        self.assertEqual("ca.\n\t\n456%.", union["quote"])
        self.assertEqual(list(reversed([r["span_id"] for r in refs])), union["span_ids"])

    def test_unselected_words_negation_salts_signs_or_exponents_are_never_bridged(self):
        for left, omitted, right in [("ca.", "not", "456%."), ("P1", "LiFSI", "film"),
                                     ("10", "−", "5"), ("10", "⁻⁵", "S/cm"), ("value", "≥", "4")]:
            with self.subTest(omitted=omitted):
                doc = document(left + "\n\n" + omitted + "\n\n" + right)
                refs = [self.reference(doc, left), self.reference(doc, right)]
                self.assertEqual([], combine_adjacent_spans(doc, refs))

    def test_selected_negation_and_numeric_notation_are_not_normalized(self):
        text = "No salt.\n\nValue = −1.77 × 10⁻⁵ S cm⁻¹."
        doc = document(text)
        refs = [self.reference(doc, "No salt."), self.reference(doc, "Value = −1.77 × 10⁻⁵ S cm⁻¹.")]
        union = combine_adjacent_spans(doc, refs)[0]
        self.assertEqual(text, union["quote"])
        self.assertIn("No salt", union["quote"])
        self.assertIn("−1.77 × 10⁻⁵", union["quote"])

    def test_existing_covering_span_prevents_redundant_union(self):
        doc = document("The strain was ca. 456%.")
        full = full_span(doc)
        refs = [{"chunk_id": full["chunk_id"], **resolve_span(doc, full["chunk_id"], full["span_id"])},
                self.reference(doc, "The strain was ca."), self.reference(doc, "456%.")]
        self.assertEqual([], combine_adjacent_spans(doc, refs))

    def test_duplicate_selection_is_not_two_distinct_spans(self):
        doc = document("The strain was ca. 456%.")
        ref = self.reference(doc, "The strain was ca.")
        self.assertEqual([], combine_adjacent_spans(doc, [ref, deepcopy(ref)]))

    def test_valid_references_from_different_chunks_do_not_form_a_union(self):
        doc = document("ca.")
        doc["chunks"].append({**deepcopy(doc["chunks"][0]), "chunk_id": "other", "text": "456%."})
        refs = [self.reference(doc, "ca."), self.reference(doc, "456%.", chunk_id="other")]
        self.assertEqual([], combine_adjacent_spans(doc, refs))

    def test_foreign_stale_or_modified_resolved_references_do_not_get_fallback_support(self):
        doc = document("The strain was ca. 456%.")
        original = [self.reference(doc, "The strain was ca."), self.reference(doc, "456%.")]
        for key, value in [("quote", "456% altered."), ("source_start", 0), ("source_end", True),
                           ("paper_id", "other-paper"), ("document_sha256", "b" * 64),
                           ("catalog_version", "unknown-version"), ("span_id", "unknown-id")]:
            refs = deepcopy(original)
            refs[1][key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                combine_adjacent_spans(doc, refs)
        foreign = deepcopy(doc)
        foreign["paper_id"] = "other-paper"
        with self.assertRaises(ValueError):
            combine_adjacent_spans(doc, [original[0], self.reference(foreign, "456%.")])
        stale = deepcopy(doc)
        stale["chunks"][0]["text"] += " A revised source."
        with self.assertRaises(ValueError):
            combine_adjacent_spans(stale, original)

    def test_legacy_quotations_are_not_promoted_to_selected_source_unions(self):
        doc = document("The strain was ca. 456%.")
        refs = [{"chunk_id": "source-one", "quote": "The strain was ca."},
                {"chunk_id": "source-one", "quote": "456%."}]
        self.assertEqual([], combine_adjacent_spans(doc, refs))
        refs[0] = self.reference(doc, "The strain was ca.")
        self.assertEqual([], combine_adjacent_spans(doc, refs))

    def test_union_metadata_is_authoritative_and_does_not_alias_source_lists(self):
        doc = document("The strain was ca. 456%.")
        doc["chunks"][0]["text_transformations"] = ["jats_script_notation_v1"]
        refs = [self.reference(doc, "The strain was ca."), self.reference(doc, "456%.")]
        union = combine_adjacent_spans(doc, refs, catalog=build_span_catalog(doc))[0]
        self.assertEqual(doc["paper_id"], union["paper_id"])
        self.assertEqual("a" * 64, union["document_sha256"])
        self.assertEqual("quote_matched", union["evidence_status"])
        union["text_transformations"].append("changed")
        self.assertEqual(["jats_script_notation_v1"], doc["chunks"][0]["text_transformations"])


if __name__ == "__main__":
    unittest.main()
