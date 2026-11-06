"""Deterministic evidence choices tied to exact, unchanged source characters.

The catalogue is source navigation, not scientific attribution. A model selects
an ID; the server retrieves its original span instead of accepting a retyped
quotation. Full chunks remain available when a sentence boundary is unhelpful.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import re


CATALOG_VERSION = "source-spans-v1"
_ENTRY_KEYS = {"span_id", "chunk_id", "start", "end", "text"}


def _source_chunks(document):
    if not isinstance(document, dict):
        raise ValueError("Source span catalogue needs a document")
    paper_id = document.get("paper_id")
    chunks = document.get("chunks")
    if not isinstance(paper_id, str) or not paper_id.strip() or not isinstance(chunks, list):
        raise ValueError("Source span catalogue needs a paper identity and chunks list")
    by_id = {}
    for chunk in chunks:
        if not isinstance(chunk, dict):
            raise ValueError("Source span chunks must be objects")
        chunk_id, text = chunk.get("chunk_id"), chunk.get("text")
        source_hash = chunk.get("document_sha256", "")
        if (not isinstance(chunk_id, str) or not chunk_id.strip()
                or not isinstance(text, str) or not text.strip()
                or not isinstance(source_hash, str)):
            raise ValueError("Source span chunks need nonempty identity/text and a textual source hash")
        if chunk_id in by_id:
            raise ValueError("Source span chunk identities must be unique")
        if "paper_id" in chunk and chunk["paper_id"] != paper_id:
            raise ValueError("Source span chunk belongs to another paper")
        by_id[chunk_id] = chunk
    return paper_id, by_id


def _ranges(text):
    """Return exact full/paragraph/sentence ranges, with no text rewriting.

    These lexical boundaries can split an abbreviation. They never change a
    decimal or a source character, and the complete chunk is always selectable.
    Multiple choices may be attached when the relevant context spans sentences.
    """
    ranges, seen = [(0, len(text))], {(0, len(text))}

    def add(start, end):
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        pair = (start, end)
        if start < end and pair not in seen:
            ranges.append(pair)
            seen.add(pair)

    paragraphs, start = [], 0
    for boundary in re.finditer(r"(?:\r?\n[ \t]*){2,}", text):
        paragraphs.append((start, boundary.start()))
        start = boundary.end()
    paragraphs.append((start, len(text)))
    for start, end in paragraphs:
        add(start, end)
        sentence_start = start
        for boundary in re.finditer(r"[.!?](?=\s+\S)", text[start:end]):
            sentence_end = start + boundary.end()
            add(sentence_start, sentence_end)
            sentence_start = sentence_end
        add(sentence_start, end)
    return ranges


@lru_cache(maxsize=256)
def _chunk_entries(paper_id, chunk_id, source_hash, text):
    """Cache immutable entries, not caller-mutable dictionaries."""
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    entries, ids = [], set()
    for start, end in _ranges(text):
        binding = {"catalog_version": CATALOG_VERSION, "paper_id": paper_id,
                   "chunk_id": chunk_id, "document_sha256": source_hash,
                   "text_sha256": text_hash, "start": start, "end": end}
        encoded = json.dumps(binding, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        span_id = "spn-" + hashlib.sha256(encoded).hexdigest()[:32]
        if span_id in ids:
            raise ValueError("Source span identities collided")
        ids.add(span_id)
        entries.append((span_id, start, end, text[start:end]))
    return tuple(entries)


def _entries_for(paper_id, chunk):
    return _chunk_entries(paper_id, chunk["chunk_id"], chunk.get("document_sha256", ""), chunk["text"])


def _entry(chunk_id, values):
    span_id, start, end, text = values
    return {"span_id": span_id, "chunk_id": chunk_id, "start": start, "end": end, "text": text}


def build_span_catalog(document):
    """Return exact source choices; IDs bind paper, chunk, source and offsets.

    Offsets count Python Unicode codepoints in the unchanged chunk, not UTF-8
    bytes or UTF-16 code units. Empty chunk lists are useful for prompt mocks;
    the scientific source loader separately requires actual source coverage.
    """
    paper_id, chunks = _source_chunks(document)
    return [_entry(chunk_id, values) for chunk_id, chunk in chunks.items()
            for values in _entries_for(paper_id, chunk)]


def resolve_span(document, chunk_id, span_id, *, catalog=None):
    """Retrieve one catalogue member without fuzzy matching or trusting offsets.

    A supplied catalogue is only a prebuilt lookup. The selected entry must
    equal the deterministic entry for the current document, including exact
    text and typed offsets; changing cached dictionaries cannot create evidence.
    """
    paper_id, chunks = _source_chunks(document)
    if (not isinstance(chunk_id, str) or chunk_id not in chunks
            or not isinstance(span_id, str) or not span_id):
        raise ValueError("Unknown source span selection")
    chunk = chunks[chunk_id]
    values = next((v for v in _entries_for(paper_id, chunk) if v[0] == span_id), None)
    if values is None:
        raise ValueError("Source span does not belong to the current paper and chunk")
    expected = _entry(chunk_id, values)
    if catalog is not None:
        if (not isinstance(catalog, (list, tuple))
                or not all(isinstance(item, dict) for item in catalog)):
            raise ValueError("Prebuilt source span catalogue must contain entries")
        matches = [item for item in catalog if item.get("span_id") == span_id]
        if len(matches) != 1:
            raise ValueError("Source span selection must occur exactly once in the catalogue")
        selected = matches[0]
        if (set(selected) != _ENTRY_KEYS
                or any(not isinstance(selected.get(k), int) or isinstance(selected.get(k), bool)
                       for k in ("start", "end"))
                or selected != expected):
            raise ValueError("Prebuilt source span entry differs from the current source")
    start, end = expected["start"], expected["end"]
    quote = chunk["text"][start:end]
    if quote != expected["text"]:
        raise ValueError("Source span text no longer matches its offsets")
    return {"quote": quote, "span_id": span_id, "source_start": start, "source_end": end,
            "evidence_origin": "source_span_selection", "catalog_version": CATALOG_VERSION}


def combine_adjacent_spans(document, resolved_refs, *, catalog=None):
    """Return exact support unions of adjacent, already selected source ranges.

    Only server-resolved selections can contribute. Each original ID, quote,
    offset and supplied source identity is checked again. A union may bridge
    whitespace, never unselected words, numbers, punctuation or chemical signs.
    It is labelled as derived support rather than inventing a catalogue ID or
    replacing the model's original selections. Legacy quotations are untouched.
    """
    paper_id, chunks = _source_chunks(document)
    if not isinstance(resolved_refs, list):
        raise ValueError("Source span support needs a list of resolved references")
    groups = {}
    authoritative = ("source_part", "locator", "document_sha256", "page", "text_transformations")
    allowed = {"chunk_id", "quote", "span_id", "source_start", "source_end", "evidence_origin",
               "catalog_version", "paper_id", "evidence_status", *authoritative}
    for ref in resolved_refs:
        if not isinstance(ref, dict):
            raise ValueError("Source span support references must be objects")
        if ref.get("evidence_origin") != "source_span_selection":
            if "span_id" in ref:
                raise ValueError("Selected source span provenance is missing or inconsistent")
            continue
        if set(ref) - allowed:
            raise ValueError("Selected source span has unsupported provenance fields")
        chunk_id = ref.get("chunk_id")
        expected = resolve_span(document, chunk_id, ref.get("span_id"), catalog=catalog)
        if (any(not isinstance(ref.get(key), int) or isinstance(ref.get(key), bool)
                for key in ("source_start", "source_end"))
                or any(ref.get(key) != value for key, value in expected.items())):
            raise ValueError("Resolved source span differs from its original catalogue selection")
        chunk = chunks[chunk_id]
        if "paper_id" in ref and ref["paper_id"] != paper_id:
            raise ValueError("Selected source span belongs to another paper")
        if any(key in ref and ref[key] != chunk.get(key) for key in authoritative):
            raise ValueError("Selected source span metadata differs from the document")
        if "evidence_status" in ref and ref["evidence_status"] != "quote_matched":
            raise ValueError("Selected source span does not have a matched source status")
        groups.setdefault(chunk_id, {})[expected["span_id"]] = expected

    unions = []

    def emit(chunk_id, selected):
        if len(selected) < 2:
            return
        start = min(ref["source_start"] for ref in selected)
        end = max(ref["source_end"] for ref in selected)
        # A selected covering span already supplies the entire exact passage.
        if any(ref["source_start"] <= start and ref["source_end"] >= end for ref in selected):
            return
        chunk = chunks[chunk_id]
        support = {"chunk_id": chunk_id, "paper_id": paper_id,
                   "quote": chunk["text"][start:end], "source_start": start, "source_end": end,
                   "span_ids": [ref["span_id"] for ref in selected],
                   "evidence_origin": "source_span_selection_union", "catalog_version": CATALOG_VERSION,
                   "evidence_status": "quote_matched"}
        for key in authoritative:
            if key in chunk:
                support[key] = deepcopy(chunk[key])
        unions.append(support)

    for chunk_id, chunk in chunks.items():
        selected = sorted(groups.get(chunk_id, {}).values(),
                          key=lambda ref: (ref["source_start"], ref["source_end"], ref["span_id"]))
        connected, end = [], None
        for ref in selected:
            start = ref["source_start"]
            gap = chunk["text"][end:start] if end is not None and start > end else ""
            if connected and start > end and not gap.isspace():
                emit(chunk_id, connected)
                connected = []
            connected.append(ref)
            end = max(item["source_end"] for item in connected)
        emit(chunk_id, connected)
    return unions
