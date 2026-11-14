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
# v1 rendered <sup>/<sub> only. v2 also renders MathML scripts, keeps one
# representation of <alternatives>, lays out blocks nested in paragraphs on
# their own lines, and adds figure titles, display formulas and table footers.
# Saved runs that declare v1 remain bound to their own v1 source snapshots.
JATS_TEXT_TRANSFORMATION = "jats_script_notation_v2"

_SCRIPT_MARKERS = {"sup": "^", "sub": "_"}
# Script kind each element ends with; same-kind neighbours would merge.
_SCRIPT_ENDINGS = {"sup": "^", "sub": "_", "msup": "^", "msub": "_", "msubsup": "^"}
_MATH_TOKENS = {"mi", "mn", "mo"}
_MATH_SKIPPED = {"annotation", "annotation-xml"}
_ALTERNATIVE_MEDIA = {"tex-math", "graphic", "inline-graphic", "media", "math"}
_BLOCKS = {"fig", "table-wrap", "disp-formula", "list"}


def _script(text, marker, explicit=False):
    mapping = _SUPERSCRIPT if marker == "^" else _SUBSCRIPT
    if not explicit and text and all(char in mapping for char in text):
        return "".join(mapping[char] for char in text)
    return marker + "{" + text + "}"


def _math_content(node):
    """Render MathML; whitespace between MathML elements carries no content."""
    tag = _tag(node)
    if tag in _MATH_SKIPPED:
        return ""
    if tag in _MATH_TOKENS:
        return "".join(node.itertext()).strip()
    if tag == "semantics":
        return _math_content(node[0]) if len(node) else ""
    parts = [_math_content(child) for child in node]
    if tag in {"msup", "msub"} and len(parts) == 2:
        return parts[0] + _script(parts[1], "^" if tag == "msup" else "_")
    if tag == "msubsup" and len(parts) == 3:
        return parts[0] + _script(parts[1], "_") + _script(parts[2], "^")
    if not len(node):
        return node.text or ""
    return "".join(parts)


def _alternatives_content(node):
    """Keep one representation: MathML, else a textual form, else TeX math."""
    children = list(node)
    for child in children:
        if _tag(child) == "math":
            return _math_content(child)
    for child in children:
        if _tag(child) not in _ALTERNATIVE_MEDIA:
            text = _content(child)
            if text:
                return text
    for child in children:
        if _tag(child) == "tex-math":
            tex = "".join(child.itertext())
            body = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", tex, flags=re.S)
            return (body.group(1) if body else tex).strip()
    return ""


def _inline_content(node, explicit=False, spaced=frozenset(), skip=frozenset()):
    """Render XML scripts without silently changing 10**5 into the number 105.

    Digits and script signs use Unicode positions. Other script content retains
    its boundary as ^{...} or _{...}; unsupported characters are never dropped.
    A script that directly follows a script of the same kind, or that wraps a
    citation <xref>, keeps the explicit boundary so cm⁻¹ plus citation 12
    cannot read as cm⁻¹¹². Plain inline markup keeps its text and tails in
    their original order. Nested blocks (figures, tables, formulas, lists) go
    on their own lines; children named in ``spaced`` are separated by a space.
    """
    tag = _tag(node)
    if tag in {"math", "msup", "msub", "msubsup"}:
        return _math_content(node)
    if tag == "alternatives":
        return _alternatives_content(node)
    text, gap, previous = node.text or "", None, None

    def emit(value):
        nonlocal text, gap
        if gap is None:
            text += value
        elif value.strip():
            text, gap = text + gap + value.lstrip(), None

    for child in node:
        child_tag = _tag(child)
        tail = child.tail or ""
        if child_tag in skip:
            pass
        elif child_tag in _BLOCKS or child_tag in spaced:
            piece = _content(child)
            if piece:
                own = "\n" if child_tag in _BLOCKS else " "
                separator = "\n" if "\n" in (own, gap) else " "
                text = text.rstrip()
                text, gap = (text + separator if text else "") + piece, own
                tail = tail.lstrip()
        else:
            merges = (previous is not None and not previous.tail and child_tag in _SCRIPT_MARKERS
                      and _SCRIPT_ENDINGS.get(_tag(previous)) == _SCRIPT_MARKERS[child_tag])
            emit(_inline_content(child, explicit=merges))
        emit(tail)
        previous = child
    if tag in _SCRIPT_MARKERS:
        cites = any(_tag(d) == "xref" for d in node.iter() if d is not node)
        return _script(text, _SCRIPT_MARKERS[tag], explicit or cites)
    return text


# Paragraph-level children of captions, footnotes, figures and list items.
_PARAGRAPHS = frozenset({"p", "title", "label", "caption", "fn", "attrib", "permissions", "list-item"})
_CONTAINERS = {"caption", "fn", "list-item", "fig"}


def _first(node, name):
    child = next(iter(_children(node, name)), None) if node is not None else None
    return _content(child) if child is not None else ""


def _note_lines(node):
    lines = [(node.text or "").strip()]
    for child in node:
        lines.extend(_note_lines(child) if _tag(child) in {"fn-group", "table-wrap-foot"} else [_content(child)])
        lines.append((child.tail or "").strip())
    return [line for line in lines if line]


def _table_text(node, label=True):
    """Caption line, then rows as " | " cells, then table footnotes."""
    caption = " ".join(part for part in ((_first(node, "label") if label else ""), _first(node, "caption")) if part)
    rows = [" | ".join(_content(c) for c in row if _tag(c) in {"td", "th"})
            for row in node.iter() if _tag(row) == "tr"]
    notes = [line for foot in _children(node, "table-wrap-foot") for line in _note_lines(foot)]
    return "\n".join([caption] + rows + notes).strip()


def _formula_text(node):
    body = _inline_content(node, skip={"label"}).strip()
    return " ".join(part for part in (body, _first(node, "label")) if part)


def _list_text(node):
    return "\n".join(line for line in (_content(child) for child in node) if line)


def _content(node):
    tag = _tag(node)
    if tag in _CONTAINERS:
        return _inline_content(node, spaced=_PARAGRAPHS).strip()
    if tag == "table-wrap":
        return _table_text(node)
    if tag == "disp-formula":
        return _formula_text(node)
    if tag == "list":
        return _list_text(node)
    return _inline_content(node).strip()


def _jats_chunks(path):
    try:
        root = ET.fromstring(path.read_bytes())
    except ET.ParseError as exc:
        raise ValueError(f"XML source {path.name} is not well-formed XML ({exc}); "
                         "DTD-defined entities such as &ndash; are not resolved") from exc
    result = []
    # Chunk IDs hash an ordinal. Paragraphs and tables (the chunks produced
    # before figure titles and display formulas were read) keep consecutive
    # integers, so their IDs and "paragraph N" locators never shift; newer
    # chunk kinds get "N.k" after the preceding integer and cannot collide.
    count, extra = 0, 0

    def add(text, locator, new_kind=False):
        nonlocal count, extra
        if new_kind:
            extra += 1
            ordinal = f"{count}.{extra}"
        else:
            count, extra = count + 1, 0
            ordinal = count
        result.append({"text": text, "locator": locator, "_ordinal": ordinal})

    def visit(node, section):
        tag = _tag(node)
        heading_node = None
        if tag in {"sec", "abstract"}:
            heading_node = next(iter(_children(node, "title")), None)
            heading = _content(heading_node) if heading_node is not None else ("Abstract" if tag == "abstract" else "Untitled section")
            section = section + [heading]
        if tag == "p":
            text = _content(node)
            if text:
                add(text, " / ".join(section or ["Article"]) + f", paragraph {count + 1}")
            return
        if tag == "table-wrap":
            label = next(iter(_children(node, "label")), None)
            label = _content(label) if label is not None else "Table"
            text = _table_text(node, label=False)
            if text:
                add(text, " / ".join(section + [label]))
            return
        if tag == "disp-formula":
            text, label = _formula_text(node), _first(node, "label")
            if text:
                add(text, " / ".join(section + ["Equation" + (" " + label if label else "")]), new_kind=True)
            return
        if tag == "fig":
            label = _first(node, "label")
            caption = next(iter(_children(node, "caption")), None)
            title = _first(caption, "title")
            heading = " ".join(part for part in (label, title) if part)
            if heading:
                add(heading, " / ".join(section + [label or "Figure"]), new_kind=True)
        if tag in {"ref-list", "references"}:
            return
        for child in node:
            if child is not heading_node:
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
        try:
            with fitz.open(path) as document:
                for page_number, page in enumerate(document, 1):
                    for block_number, block in enumerate(page.get_text("blocks", sort=True), 1):
                        if len(block) > 6 and block[6] != 0:
                            continue
                        text = block[4].strip()
                        if text:
                            result.append({"text": text, "page": page_number,
                                           "locator": f"PDF page {page_number}, text block {block_number}"})
        except Exception as exc:  # PyMuPDF raises several unrelated types for damaged files
            raise ValueError(f"PDF source {path.name} could not be read by PyMuPDF: {exc}") from exc
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF reading requires PyMuPDF or pypdf from requirements.txt") from exc
        try:
            for page_number, page in enumerate(PdfReader(path).pages, 1):
                text = (page.extract_text() or "").strip()
                if text:
                    result.append({"text": text, "page": page_number,
                                   "locator": f"PDF page {page_number}"})
        except Exception as exc:  # pypdf raises several unrelated types for damaged files
            raise ValueError(f"PDF source {path.name} could not be read by pypdf: {exc}") from exc
    if not result:
        raise ValueError("PDF source has no extracted text; OCR was not performed")
    return result


_MARKDOWN_HEADING = re.compile(r"#{1,6}\s+\S")


def _text_chunks(path):
    result, heading, count, extra = [], "UTF-8 text", 0, 0
    for part in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        part = part.strip()
        if not part:
            continue
        one_line = "\n" not in part
        if one_line and _MARKDOWN_HEADING.match(part):
            heading = part.lstrip("#").strip()
            continue
        # One-line paragraphs starting with "#" used to be swallowed as
        # headings. Now kept, they take "N.k" ordinals so the IDs of the
        # paragraphs that were already loaded do not shift.
        if one_line and part.startswith("#"):
            extra += 1
            ordinal = f"{count}.{extra}"
        else:
            count, extra = count + 1, 0
            ordinal = count
        result.append({"text": part, "locator": f"{heading}, text paragraph {len(result) + 1}", "_ordinal": ordinal})
    if not result:
        raise ValueError("Text source has no readable paragraphs")
    return result


def _transformations(value):
    if not isinstance(value, list) or not all(_string(item) for item in value):
        raise ValueError("Declared text_transformations must be a list of nonempty strings")
    return list(value)


def _read_source(entry, base, paper_id, source_number):
    if not isinstance(entry, dict) or not _string(entry.get("path")):
        raise ValueError("Each source requires a local path")
    expected = entry.get("expected_sha256")
    if expected is not None and (not isinstance(expected, str)
                                 or not re.fullmatch(r"[0-9a-fA-F]{64}", expected.strip())):
        raise ValueError("Source expected_sha256 must be a 64-character hexadecimal SHA256 digest")
    if "format" in entry and not _string(entry["format"]):
        raise ValueError("Source format must be a nonempty string when given")
    path = (base / entry["path"]).resolve()
    data = path.read_bytes()
    digest = _hash(data)
    if expected is not None and expected.strip().lower() != digest:
        raise ValueError("Source SHA256 does not match the manifest")
    format_name = entry["format"].strip().lower() if "format" in entry else path.suffix.lstrip(".").lower()
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
        if "text_transformations" in source:
            declared = _transformations(source["text_transformations"])
            if declared:
                metadata["text_transformations"] = declared
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
        # Loader-generated chunks carry an internal ordinal (see _jats_chunks);
        # user-supplied JSON excerpts cannot choose one.
        ordinal = index if format_name == "json" else chunk.get("_ordinal", index)
        chunk_id = chunk.get("chunk_id") or "src-" + _hash(f"{paper_id}|{digest}|{source_number}|{ordinal}".encode())[:20]
        if not _string(chunk_id):
            raise ValueError("Chunk ID must be a nonempty string")
        record = {"chunk_id": chunk_id, "paper_id": paper_id, "text": chunk["text"],
                  "source_part": chunk.get("source_part", part), "locator": chunk["locator"],
                  "document_sha256": digest, "source_path": str(path)}
        transformations = metadata.get("text_transformations")
        if format_name == "json" and "text_transformations" in chunk:
            transformations = _transformations(chunk["text_transformations"])
        if transformations:
            record["text_transformations"] = list(transformations)
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
