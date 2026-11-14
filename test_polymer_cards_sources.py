"""Source-loading regressions for scientific script notation in real JATS XML."""
from contextlib import redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest

from polymer_cards_lib.sources import JATS_TEXT_TRANSFORMATION, load_documents


MML = 'xmlns:mml="http://www.w3.org/1998/Math/MathML"'


def chunk_id(paper_id, digest, source_number, ordinal):
    return "src-" + hashlib.sha256(f"{paper_id}|{digest}|{source_number}|{ordinal}".encode()).hexdigest()[:20]


class SourceFixture(unittest.TestCase):
    def folder(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        return Path(folder.name)

    def load_file(self, name, data, **source):
        root = self.folder()
        (root / name).write_bytes(data)
        manifest = {"papers": [{"paper_id": "test-paper", "sources": [{"path": name, **source}]}]}
        path = root / "papers.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return load_documents(path)[0]

    def load_xml(self, text):
        data = text.encode("utf-8")
        return self.load_file("paper.xml", data, expected_sha256=hashlib.sha256(data).hexdigest()), data

    def texts(self, document):
        return [c["text"] for c in document["chunks"]]


class JATSScriptNotationTests(SourceFixture):
    def test_loader_preserves_scientific_exponents_units_and_formulas(self):
        document, _ = self.load_xml(
            '<article><body><sec><title>Results</title><p>'
            'Mn = 7.3 × 10<sup>5</sup> g mol<sup>−1</sup>; '
            'conductivity 2.4 × 10<sup>-4</sup> S cm<sup>−1</sup>; '
            'Li<sup>+</sup> in CH<sub>2</sub>Cl<sub>2</sub>.'
            '</p></sec></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"],
                         'Mn = 7.3 × 10⁵ g mol⁻¹; conductivity 2.4 × 10⁻⁴ S cm⁻¹; Li⁺ in CH₂Cl₂.')

    def test_unsupported_script_content_has_an_explicit_fallback(self):
        document, _ = self.load_xml(
            '<article><body><p>y = 10<sup>n+δ</sup>; '
            'X<sub>α+β</sub> and 10<sup><italic>5</italic></sup>.</p></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"],
                         'y = 10^{n+δ}; X_{α+β} and 10⁵.')

    def test_transformation_is_declared_without_changing_raw_provenance(self):
        xml = '<article><body><sec><title>Results</title><p>10<sup>5</sup></p></sec></body></article>'
        document, data = self.load_xml(xml)
        digest = hashlib.sha256(data).hexdigest()
        chunk = document["chunks"][0]
        source = document["source_files"][0]
        self.assertEqual(source["document_sha256"], digest)
        self.assertEqual(chunk["document_sha256"], digest)
        self.assertEqual(chunk["locator"], "Results, paragraph 1")
        self.assertEqual(chunk["chunk_id"], chunk_id("test-paper", digest, 1, 1))
        self.assertEqual(source["text_transformations"], chunk["text_transformations"])
        # The JATS text representation changed (MathML, alternatives, nested
        # blocks, figure titles), so newly loaded text declares a new version.
        self.assertEqual(["jats_script_notation_v2"], source["text_transformations"])
        self.assertEqual("jats_script_notation_v2", JATS_TEXT_TRANSFORMATION)

    def test_table_cells_and_captions_preserve_scripts(self):
        document, _ = self.load_xml(
            '<article><body><sec><title>Results</title><table-wrap><label>Table 1</label>'
            '<caption><p>Li<sup>+</sup> transport.</p></caption><table>'
            '<tr><th>Conductivity (S cm<sup>−1</sup>)</th></tr>'
            '<tr><td>2.4 × 10<sup>−4</sup></td></tr>'
            '</table></table-wrap></sec></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"],
                         'Li⁺ transport.\nConductivity (S cm⁻¹)\n2.4 × 10⁻⁴')
        self.assertEqual(document["chunks"][0]["locator"], "Results / Table 1")

    def test_ordinary_inline_text_and_tails_are_unchanged(self):
        document, _ = self.load_xml(
            '<article><body><p>The <italic>polymer</italic> has '
            '<bold>two</bold> forms<xref ref-type="bibr">12</xref>.</p></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"], 'The polymer has two forms12.')

    def test_mathml_scripts_use_the_same_notation_as_plain_markup(self):
        document, _ = self.load_xml(
            f'<article {MML}><body><sec><title>Results</title><p>'
            'Mn = 7.3 × <inline-formula><mml:math><mml:msup><mml:mn>10</mml:mn><mml:mn>5</mml:mn></mml:msup>'
            '</mml:math></inline-formula> g/mol; 2.4 × <inline-formula><mml:math><mml:msup><mml:mn>10</mml:mn>'
            '<mml:mrow><mml:mo>−</mml:mo><mml:mn>4</mml:mn></mml:mrow></mml:msup></mml:math></inline-formula> S/cm; '
            '<mml:math><mml:msubsup><mml:mi>t</mml:mi><mml:mi>Li</mml:mi><mml:mo>+</mml:mo></mml:msubsup></mml:math>; '
            '<mml:math><mml:msub><mml:mi>E</mml:mi><mml:mn>2</mml:mn></mml:msub></mml:math>; '
            '<mml:math>\n  <mml:msup>\n    <mml:mn>10</mml:mn>\n    <mml:mn>3</mml:mn>\n  </mml:msup>\n</mml:math>; '
            'plain 10<sup>5</sup>.</p></sec></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"],
                         'Mn = 7.3 × 10⁵ g/mol; 2.4 × 10⁻⁴ S/cm; t_{Li}⁺; E₂; 10³; plain 10⁵.')

    def test_alternatives_keep_one_representation(self):
        document, _ = self.load_xml(
            f'<article {MML}><body><sec><title>Methods</title>'
            '<p>E is <inline-formula><alternatives><tex-math>\\documentclass[12pt]{minimal}\\begin{document}'
            '$$10^{5}$$\\end{document}</tex-math><mml:math><mml:msup><mml:mn>10</mml:mn><mml:mn>5</mml:mn>'
            '</mml:msup></mml:math><inline-graphic/></alternatives></inline-formula> Pa.</p>'
            '<p>Plain <inline-formula><alternatives><inline-graphic/><tex-math>x^2</tex-math>'
            '<textual-form>x squared</textual-form></alternatives></inline-formula> form.</p>'
            '<p>TeX only <inline-formula><alternatives><tex-math>\\documentclass{minimal}\\usepackage{amsmath}'
            '\\begin{document}$$a+b$$\\end{document}</tex-math><inline-graphic/></alternatives></inline-formula>.</p>'
            '</sec></body></article>'
        )
        self.assertEqual(self.texts(document), ['E is 10⁵ Pa.', 'Plain x squared form.', 'TeX only $$a+b$$.'])
        self.assertNotIn("documentclass", " ".join(self.texts(document)))

    def test_adjacent_scripts_and_citation_scripts_keep_explicit_boundaries(self):
        document, _ = self.load_xml(
            '<article><body><sec><title>Results</title><p>'
            'A: 2.4 S cm<sup>&#8722;1</sup><sup><xref ref-type="bibr" rid="R12">12</xref></sup>. '
            'B: 2.4 S cm<sup>&#8722;112</sup>. C: 10<sup>1-3</sup>; '
            # Different script kinds cannot merge, so E keeps Unicode notation.
            'D: X<sub>2</sub><sub>3</sub>; E: g<sub>S</sub><sup>&#8722;1</sup>; '
            'F: value 25<sup><xref ref-type="bibr">4</xref></sup>; G: 10<sup>5</sup> <sup>6</sup>.'
            '</p></sec></body></article>'
        )
        self.assertEqual(document["chunks"][0]["text"],
                         'A: 2.4 S cm⁻¹^{12}. B: 2.4 S cm⁻¹¹². C: 10¹⁻³; D: X₂_{3}; E: g_{S}⁻¹; '
                         'F: value 25^{4}; G: 10⁵ ⁶.')


class JATSBlockLayoutTests(SourceFixture):
    def test_blocks_nested_in_a_paragraph_stay_in_that_chunk_on_their_own_lines(self):
        document, data = self.load_xml(
            f'<article {MML}><body><sec><title>Results</title>'
            '<p>Values are listed below.<table-wrap><label>Table 1</label><caption><title>Moduli.</title>'
            '<p>Measured at 25 C.</p></caption><table><tr><th>Sample</th><th>E (MPa)</th></tr>'
            '<tr><td>1.5</td><td>20</td></tr></table><table-wrap-foot><fn><p>Dry films.</p></fn></table-wrap-foot>'
            '</table-wrap></p>'
            '<p>Structures are shown<sup><xref ref-type="bibr">42</xref>–<xref ref-type="bibr">45</xref></sup>.'
            '<fig id="F1"><label>Fig. 1</label><caption><title>Schematic illustration.</title>'
            '<p><bold>a</bold> Chemical structures.</p><p><bold>b</bold> Bonds.</p></caption><graphic/></fig></p>'
            '<p>The binding energy was computed by<disp-formula id="E1"><alternatives><tex-math>\\documentclass{minimal}'
            '\\begin{document}$$E$$\\end{document}</tex-math><mml:math><mml:msub><mml:mi>E</mml:mi><mml:mi>b</mml:mi>'
            '</mml:msub></mml:math></alternatives></disp-formula>where E is energy.</p>'
            '<p>Steps: <list><list-item><p>Mix.</p></list-item><list-item><p>Cast.</p></list-item></list> Done.</p>'
            '</sec></body></article>'
        )
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual(self.texts(document), [
            'Values are listed below.\nTable 1 Moduli. Measured at 25 C.\nSample | E (MPa)\n1.5 | 20\nDry films.',
            'Structures are shown^{42–45}.\nFig. 1 Schematic illustration. a Chemical structures. b Bonds.',
            'The binding energy was computed by\nE_{b}\nwhere E is energy.',
            'Steps:\nMix.\nCast.\nDone.',
        ])
        self.assertEqual([c["locator"] for c in document["chunks"]],
                         [f"Results, paragraph {n}" for n in range(1, 5)])
        self.assertEqual([c["chunk_id"] for c in document["chunks"]],
                         [chunk_id("test-paper", digest, 1, n) for n in range(1, 5)])

    def test_section_level_figure_titles_and_formulas_become_new_chunks_without_shifting_ids(self):
        document, data = self.load_xml(
            '<article><front><article-meta><abstract><p>Abstract text.</p></abstract></article-meta></front><body>'
            '<sec><title>Results</title><p>See Fig. 2b.</p>'
            '<fig id="F2"><label>Fig. 2</label><caption><title>Mechanical properties of P3 elastomer.</title>'
            '<p>b Stress-strain curves at 50 mm/min.</p></caption><graphic/></fig>'
            '<fig id="F3"><label>Figure 3</label><caption><p>Untitled caption.</p></caption></fig>'
            '<table-wrap><label>Table 1</label><caption><title>Conductivity.</title><p>Ion transport data.</p></caption>'
            '<table><tr><td>PEO</td><td>2.4 × 10<sup>−4</sup> <sup>a</sup></td></tr></table>'
            '<table-wrap-foot><fn><p><sup>a</sup> Measured at 60 °C under argon.</p></fn></table-wrap-foot></table-wrap></sec>'
            '<sec><title>Methods</title><p>Healing efficiency was defined as</p>'
            '<disp-formula id="E1"><label>(1)</label>η = ε<sub>healed</sub>/ε<sub>original</sub> × 100%</disp-formula>'
            '<disp-formula id="E2">a = b</disp-formula>'
            '<p>where the strains are at break.</p></sec></body></article>'
        )
        digest = hashlib.sha256(data).hexdigest()
        expected = [
            ("Abstract, paragraph 1", "Abstract text.", 1),
            ("Results, paragraph 2", "See Fig. 2b.", 2),
            ("Results / Fig. 2", "Fig. 2 Mechanical properties of P3 elastomer.", "2.1"),
            ("Results, paragraph 3", "b Stress-strain curves at 50 mm/min.", 3),
            ("Results / Figure 3", "Figure 3", "3.1"),
            ("Results, paragraph 4", "Untitled caption.", 4),
            ("Results / Table 1",
             "Conductivity. Ion transport data.\nPEO | 2.4 × 10⁻⁴ ^{a}\n^{a} Measured at 60 °C under argon.", 5),
            ("Methods, paragraph 6", "Healing efficiency was defined as", 6),
            ("Methods / Equation (1)", "η = ε_{healed}/ε_{original} × 100% (1)", "6.1"),
            ("Methods / Equation", "a = b", "6.2"),
            ("Methods, paragraph 7", "where the strains are at break.", 7),
        ]
        self.assertEqual([(c["locator"], c["text"]) for c in document["chunks"]],
                         [(locator, text) for locator, text, _ in expected])
        self.assertEqual([c["chunk_id"] for c in document["chunks"]],
                         [chunk_id("test-paper", digest, 1, ordinal) for _, _, ordinal in expected])
        for chunk in document["chunks"]:
            self.assertFalse(any(key.startswith("_") or "ordinal" in key for key in chunk), chunk)


class TextSourceTests(SourceFixture):
    def test_only_markdown_heading_syntax_is_a_heading(self):
        data = (b"# Results\n\nThe neat P3 film was tested.\n\n#2 film reached 1.2e-4 S/cm at 30 C.\n\n"
                b"All films were stored under argon.\n\n## Methods\n\n#hashtag line\n")
        document = self.load_file("paper.txt", data, format="text")
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual([(c["locator"], c["text"]) for c in document["chunks"]], [
            ("Results, text paragraph 1", "The neat P3 film was tested."),
            ("Results, text paragraph 2", "#2 film reached 1.2e-4 S/cm at 30 C."),
            ("Results, text paragraph 3", "All films were stored under argon."),
            ("Methods, text paragraph 4", "#hashtag line"),
        ])
        # Chunks that were already produced keep their IDs; formerly swallowed
        # one-line paragraphs get IDs that cannot collide with them.
        self.assertEqual([c["chunk_id"] for c in document["chunks"]],
                         [chunk_id("test-paper", digest, 1, n) for n in (1, "1.1", 2, "2.1")])


class JSONSnapshotTests(SourceFixture):
    def snapshot(self, **extra):
        return {"chunks": [{"chunk_id": "c1", "text": "10⁵ g mol⁻¹", "locator": "Results, paragraph 1"},
                           {"chunk_id": "c2", "text": "Plain", "locator": "Results, paragraph 2",
                            "text_transformations": ["manual_excerpt_v1"]}], **extra}

    def test_declared_text_transformations_are_carried_to_source_and_chunks(self):
        data = json.dumps(self.snapshot(text_transformations=["jats_script_notation_v1"])).encode()
        document = self.load_file("excerpts.json", data)
        self.assertEqual(["jats_script_notation_v1"], document["source_files"][0]["text_transformations"])
        self.assertEqual(["jats_script_notation_v1"], document["chunks"][0]["text_transformations"])
        self.assertEqual(["manual_excerpt_v1"], document["chunks"][1]["text_transformations"])

    def test_snapshot_without_declarations_is_unchanged(self):
        data = json.dumps({"chunks": [{"chunk_id": "c1", "text": "Plain", "locator": "Results, paragraph 1"}]}).encode()
        document = self.load_file("excerpts.json", data)
        self.assertNotIn("text_transformations", document["source_files"][0])
        self.assertNotIn("text_transformations", document["chunks"][0])

    def test_malformed_transformation_declarations_are_rejected(self):
        for value in ("jats_script_notation_v1", [""], [1], None):
            with self.subTest(top_level=value), self.assertRaisesRegex(ValueError, "text_transformations"):
                self.load_file("excerpts.json", json.dumps(self.snapshot(text_transformations=value)).encode())
        bad = self.snapshot()
        bad["chunks"][0]["text_transformations"] = [" "]
        with self.assertRaisesRegex(ValueError, "text_transformations"):
            self.load_file("excerpts.json", json.dumps(bad).encode())

    def test_snapshot_cannot_choose_internal_ordinals(self):
        data = json.dumps({"chunks": [{"text": "Plain", "locator": "Results, paragraph 1", "_ordinal": "9.9"}]}).encode()
        document = self.load_file("excerpts.json", data)
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual(chunk_id("test-paper", digest, 1, 1), document["chunks"][0]["chunk_id"])
        self.assertNotIn("_ordinal", document["chunks"][0])


class ManifestAndUnreadableSourceTests(SourceFixture):
    def test_expected_sha256_is_hex_validated_and_case_insensitive(self):
        data = b"Paragraph one.\n"
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual("Paragraph one.", self.load_file("a.txt", data, expected_sha256=digest.upper())["chunks"][0]["text"])
        for value in ("xyz", digest[:-1], 12, digest + "0"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "expected_sha256"):
                self.load_file("a.txt", data, expected_sha256=value)
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.load_file("a.txt", data, expected_sha256="0" * 64)

    def test_format_must_be_a_nonempty_string_when_present(self):
        for value in (None, "", 3):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "format"):
                self.load_file("a.txt", b"Paragraph one.\n", format=value)
        self.assertEqual("text", self.load_file("a.txt", b"Paragraph one.\n", format=" TEXT ")["source_files"][0]["format"])

    def test_unparseable_xml_is_a_value_error(self):
        with self.assertRaisesRegex(ValueError, r"paper\.xml.*XML"):
            self.load_file("paper.xml", b"<article><body><p>1&ndash;2</p></body></article>")

    def test_unreadable_pdf_is_a_value_error(self):
        with self.assertRaisesRegex(ValueError, r"paper\.pdf"):
            self.load_file("paper.pdf", b"%PDF-1.7 truncated garbage")

    def test_cli_reports_unparseable_xml_as_input_error(self):
        from extract_polymer_cards import main
        root = self.folder()
        (root / "paper.xml").write_bytes(b"<article><body><p>1&ndash;2</p></body></article>")
        (root / "papers.json").write_text(json.dumps({"papers": [{"paper_id": "p", "sources": [{"path": "paper.xml"}]}]}))
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["--papers", str(root / "papers.json"), "--records", str(root / "records.json"),
                         "--out-dir", str(root / "out")])
        self.assertEqual(2, code)
        self.assertIn("paper.xml", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


REAL_SOURCES = Path("/Volumes/Seagate/research /polymer-screening/sources/polymer-cards-2026-10-28/full-papers.json")
FROZEN_REFERENCES = [Path(__file__).resolve().parent / "examples/polymer_cards" / name for name in (
    "identity_reference_2026-10-30.json", "condition_reference_2026-11-06/reference.json",
    "checked_pei_2026-10-30/evaluation-cases.json")]


@unittest.skipUnless(REAL_SOURCES.exists(), "original JATS sources are not available on this machine")
class RealPaperChunkIdentityTests(unittest.TestCase):
    def test_frozen_reference_chunk_ids_still_resolve_and_paragraph_numbers_are_unchanged(self):
        documents = load_documents(REAL_SOURCES)
        chunks = {c["chunk_id"]: c for d in documents for c in d["chunks"]}
        pinned = set()
        for path in FROZEN_REFERENCES:
            pinned |= set(re.findall(r'"(src-[0-9a-f]{20})"', path.read_text(encoding="utf-8")))
        self.assertEqual(19, len(pinned))
        self.assertLessEqual(pinned, set(chunks))
        for document in documents:
            numbers = [int(m.group(1)) for c in document["chunks"]
                       for m in [re.search(r", paragraph (\d+)$", c["locator"])] if m]
            self.assertEqual(list(range(1, len(numbers) + 1)), numbers)
            self.assertTrue(all(c["text_transformations"] == [JATS_TEXT_TRANSFORMATION] for c in document["chunks"]))
            self.assertFalse(any("documentclass" in c["text"] for c in document["chunks"]))


if __name__ == "__main__":
    unittest.main()
