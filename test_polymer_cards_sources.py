"""Source-loading regressions for scientific script notation in real JATS XML."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from polymer_cards_lib.sources import load_documents


class JATSScriptNotationTests(unittest.TestCase):
    def load_xml(self, text):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        data = text.encode("utf-8")
        (root / "paper.xml").write_bytes(data)
        manifest = {"papers": [{"paper_id": "test-paper", "sources": [{
            "path": "paper.xml", "expected_sha256": hashlib.sha256(data).hexdigest()
        }]}]}
        path = root / "papers.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return load_documents(path)[0], data

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
        self.assertEqual(chunk["chunk_id"], "src-" + hashlib.sha256(
            f"test-paper|{digest}|1|1".encode()).hexdigest()[:20])
        self.assertEqual(source["text_transformations"], chunk["text_transformations"])
        self.assertIn("jats_script_notation_v1", source["text_transformations"])

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


if __name__ == "__main__":
    unittest.main()
