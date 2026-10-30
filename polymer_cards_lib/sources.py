"""Prepare stable source chunks without losing original page/section identity."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from polymer_cards_lib.io import read_json


def _string(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _tag(node):
    return node.tag.rsplit("}", 1)[-1] if isinstance(node.tag, str) else ""


def _children(node, name):
    return [c for c in node if _tag(c) == name]


_SCRIPT_DIGITS = "0123456789"
_SUPERSCRIPT = dict(zip(_SCRIPT_DIGITS, "⁰¹²³⁴⁵⁶⁷⁸⁹"))
_SUPERSCRIPT.update({"+": "⁺", "-": "⁻", "−": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"})
_SUBSCRIPT = dict(zip(_SCRIPT_DIGITS, "₀₁₂₃₄₅₆₇₈₉"))
_SUBSCRIPT.update({"+": "₊", "-": "₋", "−": "₋", "=": "₌", "(": "₍", ")": "₎"})
JATS_TEXT_TRANSFORMATION = "jats_script_notation_v1"


def _inline_content(node):
    """Render XML scripts without silently changing 10**5 into the number 105.

    Digits and script signs use Unicode positions. Other script content retains
    its boundary as ^{...} or _{...}; unsupported characters are never dropped.
    Plain inline markup keeps its text and tails in their original order.
    """
    text = (node.text or "") + "".join(
        _inline_content(child) + (child.tail or "") for child in node
    )
    tag = _tag(node)
    if tag in {"sup", "sub"}:
        mapping = _SUPERSCRIPT if tag == "sup" else _SUBSCRIPT
        if text and all(char in mapping for char in text):
            return "".join(mapping[char] for char in text)
        return ("^{" if tag == "sup" else "_{") + text + "}"
    return text


def _content(node):
    return _inline_content(node).strip()


def _jats_chunks(path):
    root = ET.fromstring(path.read_bytes())
    result = []

    def visit(node, section):
        tag = _tag(node)
        if tag in {"sec", "abstract"}:
            title = next(iter(_children(node, "title")), None)
            heading = _content(title) if title is not None else ("Abstract" if tag == "abstract" else "Untitled section")
            section = section + [heading]
        if tag == "p":
            text = _content(node)
            if text:
                result.append({"text": text, "locator": " / ".join(section or ["Article"]) + f", paragraph {len(result) + 1}"})
            return
        if tag == "table-wrap":
            label = next(iter(_children(node, "label")), None)
            label_text = _content(label) if label is not None else "Table"
            rows = []
            for row in node.iter():
                if _tag(row) == "tr":
                    rows.append(" | ".join(_content(c) for c in row if _tag(c) in {"td", "th"}))
            caption = next(iter(_children(node, "caption")), None)
            text = "\n".join(([ _content(caption)] if caption is not None else []) + rows).strip()
            if text:
                result.append({"text": text, "locator": " / ".join(section + [label_text])})
            return
        if tag in {"ref-list", "references"}:
            return
        for child in node:
            if _tag(child) != "title":
                visit(child, section)

    # Abstracts live in front matter; body contains the experimental evidence.
    for node in root.iter():
        if _tag(node) == "abstract":
            visit(node, [])
    bodies = [n for n in root.iter() if _tag(n) == "body"]
    for body in bodies:
        visit(body, [])
    if not result:
        raise ValueError("XML source contains no readable article paragraphs")
    return result


def _pdf_chunks(path):
    try:
        import fitz
    except ImportError:
        fitz = None
    result = []
    if fitz is not None:
        with fitz.open(path) as document:
            for page_number, page in enumerate(document, 1):
                for block_number, block in enumerate(page.get_text("blocks", sort=True), 1):
                    if len(block) > 6 and block[6] != 0:
                        continue
                    text = block[4].strip()
                    if text:
                        result.append({"text": text, "page": page_number,
                                       "locator": f"PDF page {page_number}, text block {block_number}"})
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF reading requires PyMuPDF or pypdf from requirements.txt") from exc
        for page_number, page in enumerate(PdfReader(path).pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                result.append({"text": text, "page": page_number,
                               "locator": f"PDF page {page_number}"})
    if not result:
        raise ValueError("PDF source has no extracted text; OCR was not performed")
    return result


def _text_chunks(path):
    result, heading = [], "UTF-8 text"
    for part in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        part = part.strip()
        if not part:
            continue
        if part.startswith("#") and "\n" not in part:
            heading = part.lstrip("#").strip()
        else:
            result.append({"text": part, "locator": f"{heading}, text paragraph {len(result) + 1}"})
    if not result:
        raise ValueError("Text source has no readable paragraphs")
    return result


def _read_source(entry, base, paper_id, source_number):
    if not isinstance(entry, dict) or not _string(entry.get("path")):
        raise ValueError("Each source requires a local path")
    path = (base / entry["path"]).resolve()
    data = path.read_bytes()
    digest = _hash(data)
    expected = entry.get("expected_sha256")
    if expected is not None and expected != digest:
        raise ValueError("Source SHA256 does not match the manifest")
    format_name = entry.get("format", path.suffix.lstrip(".")).lower()
    part = entry.get("source_part", "main")
    if not _string(part):
        raise ValueError("Source part must be a nonempty string")
    metadata = {}
    if format_name == "json":
        source = read_json(path)
        if not isinstance(source, dict) or not isinstance(source.get("chunks"), list):
            raise ValueError("JSON source snapshot must contain a chunks list")
        chunks = source["chunks"]
        metadata = {k: source[k] for k in ("license", "attribution", "url", "original_document_sha256") if k in source}
        if "coverage" in source:
            metadata["declared_coverage"] = source["coverage"]
        coverage = "selected_excerpts"
    elif format_name in {"xml", "jats"}:
        chunks, coverage = _jats_chunks(path), "article_xml_body_and_abstract"
        metadata["text_transformations"] = [JATS_TEXT_TRANSFORMATION]
    elif format_name == "pdf":
        chunks, coverage = _pdf_chunks(path), "extracted_pdf_text_not_OCR"
    elif format_name in {"txt", "text"}:
        chunks, coverage = _text_chunks(path), "provided_text"
    else:
        raise ValueError("Unsupported source format; use PDF, JATS XML, UTF-8 text or JSON source excerpts")
    out = []
    for index, chunk in enumerate(chunks, 1):
        if not isinstance(chunk, dict) or not _string(chunk.get("text")) or not _string(chunk.get("locator")):
            raise ValueError("Source chunks require nonempty text and a genuine source locator")
        if "paper_id" in chunk and chunk["paper_id"] != paper_id:
            raise ValueError("Source chunk paper ID differs from its manifest paper")
        if "page" in chunk and (not isinstance(chunk["page"], int) or isinstance(chunk["page"], bool) or chunk["page"] < 1):
            raise ValueError("Source page must be a positive integer when available")
        chunk_id = chunk.get("chunk_id") or "src-" + _hash(f"{paper_id}|{digest}|{source_number}|{index}".encode())[:20]
        if not _string(chunk_id):
            raise ValueError("Chunk ID must be a nonempty string")
        record = {"chunk_id": chunk_id, "paper_id": paper_id, "text": chunk["text"],
                  "source_part": chunk.get("source_part", part), "locator": chunk["locator"],
                  "document_sha256": digest, "source_path": str(path)}
        if "text_transformations" in metadata:
            record["text_transformations"] = list(metadata["text_transformations"])
        if "page" in chunk:
            record["page"] = chunk["page"]
        original = chunk.get("original_document_sha256", metadata.get("original_document_sha256"))
        if original:
            record["original_document_sha256"] = original
            record["original_hash_status"] = "declared_provenance_not_reverified_from_excerpt"
        out.append(record)
    if not out:
        raise ValueError("A source must contain at least one chunk")
    source_file = {"path": str(path), "format": format_name, "source_part": part,
                   "document_sha256": digest, "coverage": coverage, "bytes": len(data), **metadata}
    return out, source_file


def load_documents(manifest_path):
    """Load sources from a paper manifest; all model evidence points to these chunks."""
    manifest_path = Path(manifest_path)
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("papers"), list) or not manifest["papers"]:
        raise ValueError("Manifest must contain a nonempty papers list")
    documents, seen = [], set()
    for paper in manifest["papers"]:
        if not isinstance(paper, dict) or not _string(paper.get("paper_id")) or paper["paper_id"] in seen:
            raise ValueError("Paper IDs must be present and unique")
        seen.add(paper["paper_id"])
        if not isinstance(paper.get("sources"), list) or not paper["sources"]:
            raise ValueError("Every paper needs at least one source")
        domains = paper.get("domains", [])
        if not isinstance(domains, list) or not all(_string(d) for d in domains):
            raise ValueError("Domains must be a list of nonempty strings")
        chunks, files = [], []
        for index, source in enumerate(paper["sources"], 1):
            new_chunks, source_file = _read_source(source, manifest_path.parent, paper["paper_id"], index)
            chunks.extend(new_chunks)
            files.append(source_file)
        ids = [c["chunk_id"] for c in chunks]
        if len(ids) != len(set(ids)):
            raise ValueError("Chunk IDs must be unique within a paper")
        documents.append({"paper_id": paper["paper_id"], "title": paper.get("title", paper["paper_id"]),
                          "domains": domains, "source_files": files, "chunks": chunks})
    return documents
