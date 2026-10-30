"""Write readable polymer cards without flattening their source relationships.

The renderer does not classify materials or certify scientific statements. It
keeps the validator's decisions and displays the evidence attached to each fact.
"""
from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from typing import Any, Dict, Iterable, List
from urllib.parse import urlsplit


FIELD_LABELS = {
    "monomers": "Monomers",
    "composition": "Composition",
    "synthesis_text": "Synthesis text",
    "properties": "Properties",
    "applications": "Applications",
    "source_tag": "Source tag",
}
STATUS_LABELS = {
    "reported": "Reported in the supplied text",
    "not_found_in_provided_text": "Not found in the supplied text",
    "needs_review": "Needs review",
    "conflicting": "Conflicting information — needs review",
}
SOURCE_TAG_LABELS = {
    "author_synthesized": "Synthesized by the authors",
    "commercially_purchased": "Commercially purchased",
}


def _display(value: Any) -> str:
    if value is None:
        return "Not specified"
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    return str(value)


def _h(value: Any) -> str:
    return html.escape(_display(value), quote=True)


def _paragraph(value: Any) -> str:
    return _h(value).replace("\n", "<br>\n")


def _safe_url(value: Any) -> str | None:
    if not isinstance(value, str) or any(ord(c) < 32 for c in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def _documents_by_id(documents: Iterable[Dict]) -> Dict[str, Dict]:
    return {doc["paper_id"]: doc for doc in documents}


def _resolve_evidence(evidence: Any, document: Dict) -> List[Dict]:
    chunks = {chunk["chunk_id"]: chunk for chunk in document.get("chunks", [])}
    resolved = []
    for reference in evidence if isinstance(evidence, list) else []:
        if not isinstance(reference, dict):
            continue
        ref = dict(reference)
        chunk = chunks.get(ref.get("chunk_id"))
        # Location metadata comes from the source document where available,
        # not from a model's claimed source location.
        if chunk is not None:
            for key in ("source_part", "locator", "page", "document_sha256"):
                if key in chunk:
                    ref[key] = chunk[key]
            # Conversion metadata, like a locator, is supplied by the source
            # loader. A model cannot declare that the source used a transform.
            ref.pop("text_transformations", None)
            if chunk.get("text_transformations"):
                ref["text_transformations"] = list(chunk["text_transformations"])
            ref["paper_id"] = document.get("paper_id")
        ref["source_reference_resolved"] = chunk is not None
        resolved.append(ref)
    return resolved


def _location(reference: Dict) -> str:
    pieces = []
    if reference.get("source_part"):
        pieces.append(str(reference["source_part"]))
    if reference.get("page") is not None:
        pieces.append("page " + str(reference["page"]))
    if reference.get("locator"):
        pieces.append(str(reference["locator"]))
    pieces.append("chunk " + str(reference.get("chunk_id", "not specified")))
    return " · ".join(pieces)


def _transformation_note(reference: Dict) -> str:
    transformations = reference.get("text_transformations", [])
    if not isinstance(transformations, list) or not transformations:
        return ""
    notes = []
    if "jats_script_notation_v1" in transformations:
        notes.append("Source XML converted with preserved superscripts/subscripts (jats_script_notation_v1).")
    other = [str(item) for item in transformations if item != "jats_script_notation_v1"]
    if other:
        notes.append("Declared source-text transformations: " + ", ".join(other) + ".")
    return " ".join(notes)


def _evidence_status(reference: Dict) -> str:
    converted = bool(_transformation_note(reference))
    if reference.get("evidence_status") == "quote_matched":
        status = "Quote matched to converted source text" if converted else "Original quote matched to source"
    else:
        status = "Evidence reference to converted source text" if converted else "Original evidence reference"
    if not reference["source_reference_resolved"]:
        status += "; source chunk is unavailable in this view"
    return status


def _evidence_html(evidence: Any, document: Dict, label: str = "Original evidence") -> str:
    refs = _resolve_evidence(evidence, document)
    if not refs:
        return '<p class="missing">' + _h(label) + ': not attached — needs review.</p>'
    entries = []
    for ref in refs:
        status = _evidence_status(ref)
        conversion = _transformation_note(ref)
        digest = ("<p class=\"source-id\">Source SHA-256: " + _h(ref["document_sha256"]) + "</p>"
                  if ref.get("document_sha256") else "")
        entries.append(
            "<li><p class=\"location\">" + _h(_location(ref)) + "</p>"
            + '<blockquote class="quote">' + _paragraph(ref.get("quote", "")) + "</blockquote>"
            + '<p class="source-id">' + _h(status) + "</p>"
            + ('<p class="source-id">' + _h(conversion) + '</p>' if conversion else '')
            + digest + "</li>"
        )
    return ('<details class="evidence"><summary>' + _h(label) + ' (' + str(len(refs))
            + " source passage" + ("s" if len(refs) != 1 else "") + ")</summary><ol>"
            + "".join(entries) + "</ol></details>")


def _specimen_label(card: Dict, specimen_id: Any) -> str:
    for specimen in card.get("specimens", []):
        if specimen.get("specimen_id") == specimen_id:
            return str(specimen.get("label") or specimen_id)
    return str(specimen_id)


def _fact_html(fact: Dict, document: Dict, card: Dict, group: str = "") -> str:
    value = fact.get("value")
    if group == "source_tag":
        value = SOURCE_TAG_LABELS.get(value, value) if isinstance(value, str) else value
    if group == "properties":
        text = _h(fact.get("property", "Property")) + ": " + _paragraph(value)
        unit = fact.get("unit")
        if unit and str(unit) not in _display(value):
            text += " " + _h(unit)
    else:
        text = _paragraph(value)
    metadata = []
    if fact.get("specimen_id"):
        metadata.append("Tested/prepared specimen: " + _specimen_label(card, fact["specimen_id"]))
    if fact.get("basis"):
        metadata.append("Basis: " + _display(fact["basis"]))
    if fact.get("claim_type"):
        metadata.append("Application statement: " + str(fact["claim_type"]).replace("_", " "))
    if fact.get("role"):
        metadata.append("Ingredient role: " + _display(fact["role"]).replace("_", " "))
    detail = "".join('<p class="fact-detail">' + _h(item) + "</p>" for item in metadata)
    conditions = []
    for condition in fact.get("conditions", []):
        conditions.append('<li><span class="condition-name">' + _h(condition.get("name", "Condition"))
                          + ":</span> " + _paragraph(condition.get("value"))
                          + _evidence_html(condition.get("evidence"), document) + "</li>")
    if conditions:
        detail += '<p class="condition-heading">Test conditions</p><ul>' + "".join(conditions) + "</ul>"
    if "specimen_evidence" in fact:
        detail += _evidence_html(fact["specimen_evidence"], document, "Sample-link evidence")
    return '<li class="fact"><p>' + text + "</p>" + detail + _evidence_html(fact.get("evidence"), document) + "</li>"


def _attribution_warning_text(warning: Dict) -> str:
    parts = []
    if warning.get("reason"):
        parts.append(str(warning["reason"]).replace("_", " "))
    if warning.get("specimen_label") or warning.get("specimen_id"):
        parts.append("Sample: " + _display(warning.get("specimen_label") or warning["specimen_id"]))
    if warning.get("related_entity_ids"):
        parts.append("Related material records: " + _display(warning["related_entity_ids"]))
    for key in ("detail", "details"):
        if warning.get(key):
            parts.append(_display(warning[key]))
    return "; ".join(parts) or "The material/sample relationship needs source review."


def _record_type(card: Dict) -> str:
    if "identity_kind" not in card:
        return ""
    kind = card["identity_kind"]
    labels = {"specific_polymer": "Specific polymer", "polymer_family": "Polymer family"}
    label = labels.get(kind, "Scope unresolved") if isinstance(kind, str) else "Scope unresolved"
    return "Declared record type: " + label


def _card_html(card: Dict, document: Dict, number: int) -> str:
    name = card.get("name", "Unnamed polymer")
    content = ['<article class="polymer-card" id="card-' + str(number) + '">', "<h2>" + _h(name) + "</h2>",
               '<p class="identity">Polymer record · ' + _h(document.get("paper_id")) + "</p>",
               _evidence_html(card.get("identity_evidence"), document)]
    if _record_type(card):
        content.append('<p class="identity">' + _h(_record_type(card)) + '</p>')
    warnings = card.get("attribution_warnings", [])
    if warnings:
        content.append('<aside class="attribution-warning"><strong>Sample/material link needs review</strong><ul>'
                       + "".join("<li>" + _h(_attribution_warning_text(warning)) + "</li>"
                                 for warning in warnings if isinstance(warning, dict)) + "</ul></aside>")
    classification = card.get("classification", {})
    if classification:
        content.append("<h3>Polymer identification</h3><p>" + _paragraph(classification.get("reason", "No reason supplied")) + "</p>"
                       + _evidence_html(classification.get("evidence"), document))
    for key, label in (("description", "Description"), ("role", "Role in this paper")):
        if isinstance(card.get(key), dict):
            content.append("<h3>" + label + "</h3><ul class=\"facts\">"
                           + _fact_html(card[key], document, card) + "</ul>")
    aliases = card.get("aliases", [])
    if aliases:
        content.append('<h3>Aliases reported in the source</h3><ul class="facts">'
                       + "".join(_fact_html(f, document, card) for f in aliases) + "</ul>")
    for key, label in FIELD_LABELS.items():
        group = card.get(key, {})
        status = group.get("status", "not_found_in_provided_text")
        content.append('<section class="card-group"><h3>' + label + '</h3><p class="group-status">'
                       + _h(STATUS_LABELS.get(status, status)) + "</p>")
        items = group.get("items", [])
        if items:
            content.append('<ul class="facts">' + "".join(_fact_html(f, document, card, key) for f in items) + "</ul>")
        if group.get("invalid_items_count"):
            content.append('<p class="missing">Additional extracted facts need review; see the audit below.</p>')
        content.append("</section>")
    specimens = card.get("specimens", [])
    if specimens:
        content.append('<h3>Linked formulations and specimens</h3><ul class="facts">')
        for specimen in specimens:
            content.append('<li class="fact"><p>' + _h(specimen.get("label", specimen.get("specimen_id")))
                           + "</p>" + _evidence_html(specimen.get("evidence"), document) + "</li>")
        content.append("</ul>")
    content.append("</article>")
    return "\n".join(content)


def _partial_run_message(run_metadata: Dict, completed_fallback: int) -> str:
    completed = run_metadata.get("papers_completed", completed_fallback)
    requested = run_metadata.get("papers_requested")
    message = ("Extraction completed " + _display(completed) + " of " + _display(requested)
               + " requested papers. These cards are drafts and still need review.")
    if run_metadata.get("failed_paper_id"):
        message += " Stopped at paper: " + _display(run_metadata["failed_paper_id"]) + "."
    return message


def render_html(results: List[Dict], documents: List[Dict], run_metadata: Dict) -> str:
    by_id = _documents_by_id(documents)
    sections = []
    card_number = 0
    for result in results:
        pid = result["paper_id"]
        document = by_id.get(pid, {"paper_id": pid, "chunks": []})
        heading = _h(document.get("title") or pid)
        url = _safe_url(document.get("url") or document.get("source_url"))
        if url:
            heading = '<a href="' + _h(url) + '" rel="noreferrer">' + heading + "</a>"
        sections.append('<section class="paper"><h1>' + heading + '</h1><p class="paper-id">' + _h(pid) + "</p>")
        for card in result.get("cards", []):
            card_number += 1
            sections.append(_card_html(card, document, card_number))
        if not result.get("cards"):
            sections.append("<p>No polymer cards were retained for this paper.</p>")
        audit = {key: result.get(key, []) for key in
                 ("discarded_entities", "review_queue", "validation_issues", "attribution_warnings")}
        sections.append('<details class="paper-audit"><summary>Paper audit: nonpolymer entities and records needing review</summary>'
                        + '<p>These records are preserved for inspection; an unresolved record is not a demonstrated nonpolymer.</p><pre>'
                        + _h(json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False)) + "</pre></details></section>")
    run_label = run_metadata.get("run_kind") or run_metadata.get("mode") or "Polymer-card run"
    partial_banner = (('<aside class="partial-run" role="status"><strong>Partial run</strong><p>'
                       + _h(_partial_run_message(run_metadata, len(results))) + '</p></aside>')
                      if run_metadata.get("run_complete") is False else "")
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Polymer cards and original evidence</title><style>
:root{color-scheme:light}body{font:17px/1.55 system-ui,Arial,sans-serif;margin:0;background:#f6f7f5;color:#183238}
main{max-width:1040px;margin:auto;padding:32px 24px 64px}h1{font-size:1.7rem;line-height:1.25}h2{font-size:1.45rem;margin:0 0 8px}
h3{font-size:1.1rem;margin:24px 0 5px}a{color:#006b68}p{margin:6px 0 12px}.intro{margin-bottom:32px}.paper{margin-top:40px}
.polymer-card{background:white;border:1px solid #d7dfda;padding:26px 30px;margin:22px 0 32px;overflow-wrap:anywhere}
.attribution-warning{background:#fff7e8;border-left:4px solid #b76a21;padding:12px 18px;margin:16px 0}
.partial-run{background:#fff1d8;border:2px solid #b76a21;padding:16px 20px;margin:22px 0;font-size:1.05rem}
.identity,.paper-id,.group-status,.fact-detail,.location,.source-id,.missing{color:#52686c}.identity,.source-id{font-size:.85rem}
.group-status{font-size:.9rem}.card-group{border-top:1px solid #e1e7e3;margin-top:22px}.facts{padding-left:22px}.fact{margin:14px 0}
.fact-detail{font-size:.92rem}.condition-heading{font-weight:600}details{margin:10px 0}summary{cursor:pointer;color:#006b68}
.evidence{font-size:.9rem}.evidence ol{padding-left:24px}.quote{white-space:normal;border-left:3px solid #a3c4b9;margin:8px 0;padding:6px 14px;background:#f5f8f5}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;padding:18px;border:1px solid #d7dfda}.paper-audit{margin-bottom:35px}
@media print{body{background:white}main{padding:0}.polymer-card{break-inside:avoid}details{display:block}details>*{display:block!important}}
</style></head><body><main><header class="intro"><h1>Polymer cards and original evidence</h1>
<p>Polymers are retained because they are identified as polymers. Performance, purchase status and missing card fields do not decide retention.</p>
<p>Open each “Original evidence” section to see the source text and location. A matched quotation does not by itself verify the scientific interpretation.</p>
<p>Run: """ + _h(run_label) + "</p>" + partial_banner + "</header>" + "\n".join(sections) + "</main></body></html>\n"


def _md(value: Any) -> str:
    escaped = html.escape(_display(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escaped)


def _fence(value: Any) -> str:
    value = _display(value)
    width = max([len(m.group(0)) for m in re.finditer(r"`+", value)] + [2]) + 1
    marker = "`" * width
    return marker + "text\n" + value + "\n" + marker


def _evidence_md(evidence: Any, document: Dict, label: str = "Original evidence") -> str:
    refs = _resolve_evidence(evidence, document)
    if not refs:
        return "\n" + label + ": not attached; needs review.\n"
    lines = []
    for ref in refs:
        lines.extend(["\n" + label + " — " + _md(_location(ref)), "", _fence(ref.get("quote", "")), "",
                      _md(_evidence_status(ref))])
        conversion = _transformation_note(ref)
        if conversion:
            lines.append(_md(conversion))
        if ref.get("document_sha256"):
            lines.append("Source SHA-256: " + _md(ref["document_sha256"]))
    return "\n".join(lines) + "\n"


def _fact_md(fact: Dict, document: Dict, card: Dict, group: str = "") -> str:
    value = fact.get("value")
    if group == "source_tag" and isinstance(value, str):
        value = SOURCE_TAG_LABELS.get(value, value)
    prefix = _md(fact.get("property")) + ": " if group == "properties" else ""
    line = prefix + _md(value)
    if group == "properties" and fact.get("unit") and str(fact["unit"]) not in _display(value):
        line += " " + _md(fact["unit"])
    lines = [line, ""]
    if fact.get("specimen_id"):
        lines.append("Specimen: " + _md(_specimen_label(card, fact["specimen_id"])))
    for key, label in (("basis", "Basis"), ("claim_type", "Application statement"), ("role", "Ingredient role")):
        if fact.get(key):
            lines.append(label + ": " + _md(fact[key]))
    lines.append(_evidence_md(fact.get("evidence"), document))
    if "specimen_evidence" in fact:
        lines.append(_evidence_md(fact["specimen_evidence"], document, "Sample-link evidence"))
    for condition in fact.get("conditions", []):
        lines.append("Condition — " + _md(condition.get("name")) + ": " + _md(condition.get("value")))
        lines.append(_evidence_md(condition.get("evidence"), document))
    return "\n".join(lines)


def render_markdown(results: List[Dict], documents: List[Dict], run_metadata: Dict) -> str:
    by_id = _documents_by_id(documents)
    lines = ["# Polymer cards and original evidence", "",
             "Run: " + _md(run_metadata.get("run_kind") or run_metadata.get("mode") or "Polymer-card run"), "",
             "Quotations and source locations support inspection; they do not certify scientific interpretation.", ""]
    if run_metadata.get("run_complete") is False:
        lines.extend(["**Partial run**", "", _md(_partial_run_message(run_metadata, len(results))), ""])
    for result in results:
        pid = result["paper_id"]
        document = by_id.get(pid, {"paper_id": pid, "chunks": []})
        lines.extend(["## " + _md(document.get("title") or pid), "", "Paper: " + _md(pid), ""])
        for card in result.get("cards", []):
            lines.extend(["### " + _md(card.get("name", "Unnamed polymer")), "", _evidence_md(card.get("identity_evidence"), document)])
            if _record_type(card):
                lines.extend([_md(_record_type(card)), ""])
            warnings = card.get("attribution_warnings", [])
            if warnings:
                lines.extend(["**Sample/material link needs review**", ""])
                lines.extend("- " + _md(_attribution_warning_text(warning))
                             for warning in warnings if isinstance(warning, dict))
                lines.append("")
            classification = card.get("classification", {})
            if classification:
                lines.extend(["Polymer identification: " + _md(classification.get("reason", "No reason supplied")),
                              _evidence_md(classification.get("evidence"), document)])
            for key, label in (("description", "Description"), ("role", "Role in this paper")):
                if isinstance(card.get(key), dict):
                    lines.extend(["#### " + label, "", _fact_md(card[key], document, card)])
            if card.get("aliases"):
                lines.extend(["#### Aliases", ""])
                lines.extend(_fact_md(f, document, card) for f in card["aliases"])
            for key, label in FIELD_LABELS.items():
                group = card.get(key, {})
                status = group.get("status", "not_found_in_provided_text")
                lines.extend(["#### " + label, "", STATUS_LABELS.get(status, _md(status)), ""])
                lines.extend(_fact_md(fact, document, card, key) for fact in group.get("items", []))
                if group.get("invalid_items_count"):
                    lines.append("Additional extracted facts need review; see the audit.")
            if card.get("specimens"):
                lines.extend(["#### Linked formulations and specimens", ""])
                for specimen in card["specimens"]:
                    lines.extend([_md(specimen.get("label", specimen.get("specimen_id"))),
                                  _evidence_md(specimen.get("evidence"), document)])
        audit = {key: result.get(key, []) for key in
                 ("discarded_entities", "review_queue", "validation_issues", "attribution_warnings")}
        lines.extend(["### Paper audit", "", _fence(json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False)), ""])
    return "\n".join(lines).rstrip() + "\n"


def _regular_target_or_missing(target: Path):
    try:
        metadata = target.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("Output target must be a regular file, not a directory or symlink: " + str(target))
    return metadata


def _ignore_disappeared_staging_entry(_function, _path, exception_info) -> None:
    """Allow cleanup races, including automatically removed AppleDouble files."""
    error = exception_info[1]
    if not isinstance(error, FileNotFoundError):
        raise error.with_traceback(exception_info[2])


def _write_output_set(destination: Path, outputs: Dict[str, str]) -> None:
    """Stage a complete run and roll back replacements on ordinary I/O failure.

    Individual filesystem replacements are atomic; the set is not a crash-safe
    database transaction. If restoration itself fails, retain private backups
    and report their location instead of deleting the recovery material.
    """
    try:
        destination_metadata = destination.lstat()
    except FileNotFoundError:
        destination_metadata = None
    if destination_metadata is not None and not stat.S_ISDIR(destination_metadata.st_mode):
        raise ValueError("Output directory must be a directory, not a file or symlink: " + str(destination))
    previous = {}
    # Inspect every target before creating a staging directory or touching an
    # existing result. This catches directories, symlinks and special files.
    for name in outputs:
        metadata = _regular_target_or_missing(destination / name)
        previous[name] = (None if metadata is None else
                          ((destination / name).read_bytes(), stat.S_IMODE(metadata.st_mode)))
    destination.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".polymer-cards-", dir=destination))
    replaced = []
    preserve_backups = False
    try:
        (staging / "new").mkdir()
        (staging / "previous").mkdir()
        for name, content in outputs.items():
            staged_file = staging / "new" / name
            staged_file.write_text(content, encoding="utf-8")
            if previous[name] is not None:
                content_before, mode_before = previous[name]
                backup = staging / "previous" / name
                backup.write_bytes(content_before)
                os.chmod(backup, mode_before)
                os.chmod(staged_file, mode_before)
        # Check again after staging, before beginning any replacement.
        for name in outputs:
            _regular_target_or_missing(destination / name)
        try:
            for name in outputs:
                os.replace(staging / "new" / name, destination / name)
                replaced.append(name)
        except OSError as error:
            restore_errors = []
            for name in reversed(replaced):
                try:
                    if previous[name] is None:
                        (destination / name).unlink()
                    else:
                        os.replace(staging / "previous" / name, destination / name)
                except OSError:
                    restore_errors.append(name)
            if restore_errors:
                preserve_backups = True
                raise OSError("Output commit and restoration failed for " + ", ".join(restore_errors)
                              + "; recovery files retained at " + str(staging)) from error
            raise
    finally:
        if not preserve_backups:
            shutil.rmtree(staging, onerror=_ignore_disappeared_staging_entry)


def write_outputs(results: List[Dict], documents: List[Dict], out_dir: Path | str,
                  run_metadata: Dict, additional_outputs: Dict[str, Any] | None = None) -> Dict[str, str]:
    """Write the same linked records to machine-readable and human-readable files.

    Serialize, preflight and stage the complete output set before replacing any
    previous run. Additional JSON outputs share the same rollback boundary.
    Source text belongs in the chosen run directory, not a public code artifact
    by default.
    """
    def encode(value):
        return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"

    cards = [{**card, "paper_id": result["paper_id"]} for result in results for card in result.get("cards", [])]
    audit = {
        "contract_version": "polymer-cards-v1", "run_metadata": run_metadata,
        "counts": {
            "papers": len(results), "retained_cards": len(cards),
            "discarded_entities": sum(len(r.get("discarded_entities", [])) for r in results),
            "review_records": sum(len(r.get("review_queue", [])) for r in results),
            "validation_issues": sum(len(r.get("validation_issues", [])) for r in results),
            "attribution_warnings": sum(len(r.get("attribution_warnings", [])) for r in results),
        },
        "papers": [{key: r.get(key, [] if key != "statistics" else {}) for key in
                    ("paper_id", "discarded_entities", "review_queue", "validation_issues",
                     "attribution_warnings", "statistics")} for r in results],
        "verification_limit": "Original evidence linkage and mechanical checks do not certify polymer classification or scientific attribution.",
    }
    outputs = {
        "cards.json": encode({"contract_version": "polymer-cards-v1", "run_metadata": run_metadata, "results": results}),
        "cards.jsonl": "".join(json.dumps(card, ensure_ascii=False, allow_nan=False) + "\n" for card in cards),
        "cards.html": render_html(results, documents, run_metadata),
        "cards.md": render_markdown(results, documents, run_metadata),
        "audit.json": encode(audit),
        "sources.json": encode({"documents": documents}),
    }
    if additional_outputs is not None:
        if not isinstance(additional_outputs, dict):
            raise ValueError("Additional outputs must be a filename-to-JSON mapping.")
        for filename, value in additional_outputs.items():
            if (not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", filename)
                    or filename in outputs):
                raise ValueError("Additional output names must be distinct plain filenames.")
            outputs[filename] = encode(value)
    destination = Path(out_dir)
    _write_output_set(destination, outputs)
    return {filename: str(destination / filename) for filename in outputs}
