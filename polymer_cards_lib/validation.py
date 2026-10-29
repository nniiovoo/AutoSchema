"""Validate polymer-card records without applying an application-quality filter.

This module checks source linkage and record structure.  A matched quotation is
not a scientific review of the model's classification or attribution.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import math
import re
import unicodedata
from typing import Any, Dict, List


FIELD_NAMES = (
    "monomers", "composition", "synthesis_text", "properties",
    "applications", "source_tag",
)
GROUP_STATUSES = {"reported", "not_found_in_provided_text", "needs_review", "conflicting"}
SOURCE_TAGS = {"author_synthesized", "commercially_purchased"}
APPLICATION_CLAIMS = {"demonstrated", "proposed", "unspecified"}


def _text(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split()) if isinstance(value, str) else ""


def _scalar(value: Any) -> bool:
    if _text(value):
        return True
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def _literal(value: Any, quote: str) -> bool:
    needle = _text(str(value))
    if not needle:
        return False
    haystack = _text(quote)
    numeric_start = needle[0].isdigit() or needle[0] in "+-−."
    if not numeric_start:
        return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack) is not None

    numeric_end = needle[-1].isdigit()
    superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
    # A complete number may touch its unit.  Numeric continuation must not
    # turn a decimal, thousands group, exponent, fraction or ratio into a new
    # scalar.  Complete raw ranges/uncertainties are still allowed as values.
    suffix = (r"(?![\d." + superscripts + r"]|[eE][+−-]?\d|[:/]\d)"
              if numeric_end else r"(?![\w.])")
    pattern = r"(?<![\w.+−–—⁺⁻-])" + re.escape(needle) + suffix
    operator = r"(?:[-−–—]|±|\+\s*/\s*[-−]|\bto\b|\bthrough\b)"
    # Cover the common '30°C–60°C' form as well as '30–60°C'.  Unit text is
    # contextual only; it is checked separately against the supplied unit.
    unit_text = r"[A-Za-zµμ°%/]+"
    previous_endpoint = re.compile(r"\d(?:\s*" + unit_text + r")?\s*" + operator + r"\s*$")
    next_endpoint = re.compile(r"\s*(?:" + unit_text + r"\s*)?" + operator + r"\s*[+−-]?(?:\d|\.\d)")
    next_scale = re.compile(r"\s*[×xX*·⋅∙]\s*10|\s*\^\s*[+−-]?\d")
    for match in re.finditer(pattern, haystack):
        before, after = haystack[:match.start()], haystack[match.end():]
        if re.search(r"\d,$", before) or (numeric_end and re.match(r",\d", after)):
            continue
        if previous_endpoint.search(before) or next_endpoint.match(after):
            continue
        if numeric_end and (next_scale.match(after) or re.match(r"\(\d+(?:\.\d+)?\)", after)):
            continue
        if re.search(r"\d\($", before):
            continue
        return True
    return False


def _unit_literal(value: str, quote: str) -> bool:
    # Units can immediately follow numbers (95%, 30°C, 12MPa).  Still avoid
    # accepting S/cm as the suffix of mS/cm or m as the prefix of mAh.
    needle = _text(value)
    haystack = _text(quote)
    suffix = r"(?!\w)" if needle[-1].isalnum() else ""
    for match in re.finditer(re.escape(needle) + suffix, haystack):
        previous = haystack[match.start() - 1] if match.start() else ""
        # isalpha distinguishes actual unit prefixes from superscript digits,
        # which Python's broader \w-but-not-\d class also contains.
        if needle[0].isalpha() and (previous.isalpha() or previous == "_"):
            continue
        return True
    return False


class _Invalid(ValueError):
    pass


def _chunks(document: Dict) -> Dict:
    if not isinstance(document, dict) or not _text(document.get("paper_id")):
        raise ValueError("Source document needs a paper_id.")
    entries = document.get("chunks")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Source document needs a nonempty chunks list.")
    out = {}
    for chunk in entries:
        if not isinstance(chunk, dict) or not all(_text(chunk.get(k)) for k in
                ("chunk_id", "text", "source_part", "locator", "document_sha256")):
            raise ValueError("Source chunks require identity, original text and source location.")
        if chunk["chunk_id"] in out:
            raise ValueError("Source chunk IDs must be unique within a paper.")
        if re.fullmatch(r"[a-fA-F0-9]{64}", chunk["document_sha256"]) is None:
            raise ValueError("Source document_sha256 must be a SHA256 hexadecimal digest.")
        if ("paper_id" in chunk and chunk["paper_id"] != document["paper_id"]):
            raise ValueError("Source chunk paper identity does not match its document.")
        if "page" in chunk and (not isinstance(chunk["page"], int) or isinstance(chunk["page"], bool)
                                or chunk["page"] < 1):
            raise ValueError("Source page numbers must be positive integers.")
        out[chunk["chunk_id"]] = chunk
    return out


def build_cards(document: Dict, response: Dict) -> Dict:
    """Build retained cards, discarded entities and an explicit review queue.

    Confirmed polymers are retained even when individual card fields fail
    validation.  Malformed identity/classification is unresolved, not silently
    interpreted as a nonpolymer.  Whole-input identity errors raise ValueError.
    Neither the numeric Task 3 selector nor its suitability thresholds is used.
    """
    chunks = _chunks(document)
    paper_id = document["paper_id"]
    if not isinstance(response, dict) or response.get("paper_id") != paper_id:
        raise ValueError("Response paper_id must match its original source document.")
    entities = response.get("entities")
    if not isinstance(entities, list):
        raise ValueError("Response entities must be a list.")
    try:
        json.dumps(response, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Response must contain finite JSON data only.") from exc

    cards: List[Dict] = []
    discarded: List[Dict] = []
    review_queue: List[Dict] = []
    issues: List[Dict] = []
    classification_reviews = 0
    ids = Counter(e.get("entity_id") for e in entities
                  if isinstance(e, dict) and isinstance(e.get("entity_id"), str))

    def issue(entity, path, reason, record=None, review=True):
        item = {"paper_id": paper_id, "entity_id": entity.get("entity_id") if isinstance(entity, dict) else None,
                "name": entity.get("name") if isinstance(entity, dict) else None,
                "path": path, "reason": reason}
        issues.append(item)
        if review:
            review_queue.append({**item, "record": deepcopy(record)})

    def evidence(refs):
        if not isinstance(refs, list) or not refs:
            raise _Invalid("original_evidence_missing")
        resolved = []
        for ref in refs:
            if not isinstance(ref, dict) or not _text(ref.get("chunk_id")):
                raise _Invalid("invalid_evidence_reference")
            chunk = chunks.get(ref["chunk_id"])
            if chunk is None:
                raise _Invalid("unknown_source_chunk")
            if not _text(ref.get("quote")) or _text(ref["quote"]) not in _text(chunk["text"]):
                raise _Invalid("quote_not_in_original_source")
            if "paper_id" in ref and ref["paper_id"] != paper_id:
                raise _Invalid("evidence_paper_mismatch")
            for key in ("source_part", "locator", "document_sha256", "page"):
                if key in ref and ref[key] != chunk.get(key):
                    raise _Invalid("evidence_source_metadata_mismatch:" + key)
            item = {"chunk_id": ref["chunk_id"], "quote": ref["quote"], "paper_id": paper_id,
                    "source_part": chunk["source_part"], "locator": chunk["locator"],
                    "document_sha256": chunk["document_sha256"], "evidence_status": "quote_matched"}
            if "page" in chunk:
                item["page"] = chunk["page"]
            resolved.append(item)
        return resolved

    def fact(raw, entity, path, field=None, specimen_ids=None):
        if not isinstance(raw, dict) or not _scalar(raw.get("value")):
            raise _Invalid("fact_value_missing_or_invalid")
        if field in FIELD_NAMES and raw.get("entity_id") != entity["entity_id"]:
            raise _Invalid("fact_parent_entity_mismatch")
        if "entity_id" in raw and raw["entity_id"] != entity["entity_id"]:
            raise _Invalid("fact_parent_entity_mismatch")
        if "paper_id" in raw and raw["paper_id"] != paper_id:
            raise _Invalid("fact_paper_mismatch")
        ev = evidence(raw.get("evidence"))
        result = deepcopy(raw)
        result["evidence"] = ev
        result["evidence_status"] = "quote_matched"
        result["semantic_review_status"] = "not_performed_by_validator"
        if "specimen_id" in raw and (not _text(raw["specimen_id"])
                                     or raw["specimen_id"] not in (specimen_ids or set())):
            raise _Invalid("fact_specimen_not_linked_to_polymer")
        if field in {"synthesis_text", "description", "aliases", "role"} and not _text(raw["value"]):
            raise _Invalid("text_fact_requires_text")
        if field == "aliases" and not any(_literal(raw["value"], e["quote"]) for e in ev):
            raise _Invalid("alias_not_in_original_evidence")
        if field == "composition" and not _text(raw.get("basis")):
            raise _Invalid("composition_basis_missing")
        if field == "applications":
            if (not isinstance(raw.get("claim_type", "unspecified"), str)
                    or raw.get("claim_type", "unspecified") not in APPLICATION_CLAIMS):
                raise _Invalid("application_claim_type_invalid")
            result.setdefault("claim_type", "unspecified")
        if field == "source_tag" and raw["value"] not in SOURCE_TAGS:
            raise _Invalid("polymer_source_tag_invalid")
        if field == "properties":
            if not _text(raw.get("property")):
                raise _Invalid("property_name_missing")
            if not _text(raw.get("specimen_id")) or raw["specimen_id"] not in (specimen_ids or set()):
                raise _Invalid("property_specimen_not_linked_to_polymer")
            if "unit" not in raw or (raw["unit"] is not None and not _text(raw["unit"])):
                raise _Invalid("property_unit_missing_or_invalid")
            if not any(_literal(raw["value"], e["quote"]) for e in ev):
                raise _Invalid("property_value_not_in_original_evidence")
            if raw["unit"] is not None and not any(_unit_literal(raw["unit"], e["quote"]) for e in ev):
                raise _Invalid("property_unit_not_in_original_evidence")
            conditions = raw.get("conditions")
            if not isinstance(conditions, list):
                raise _Invalid("property_conditions_must_be_a_list")
            checked_conditions = []
            for condition in conditions:
                if (not isinstance(condition, dict) or not _text(condition.get("name"))
                        or not _scalar(condition.get("value"))):
                    raise _Invalid("property_condition_invalid")
                if "entity_id" in condition and condition["entity_id"] != entity["entity_id"]:
                    raise _Invalid("condition_parent_entity_mismatch")
                if "specimen_id" in condition and condition["specimen_id"] != raw["specimen_id"]:
                    raise _Invalid("condition_specimen_mismatch")
                if "paper_id" in condition and condition["paper_id"] != paper_id:
                    raise _Invalid("condition_paper_mismatch")
                cev = evidence(condition.get("evidence"))
                if not any(_literal(condition["value"], e["quote"]) for e in cev):
                    raise _Invalid("condition_value_not_in_original_evidence")
                checked_conditions.append({**deepcopy(condition), "evidence": cev,
                                           "evidence_status": "quote_matched"})
            result["conditions"] = checked_conditions
        return result

    for index, entity in enumerate(entities):
        path = "entities[" + str(index) + "]"
        if not isinstance(entity, dict):
            issue({}, path, "invalid_entity_record", entity)
            classification_reviews += 1
            continue
        if not _text(entity.get("entity_id")) or not _text(entity.get("name")):
            issue(entity, path, "entity_identity_missing", entity)
            classification_reviews += 1
            continue
        if "paper_id" in entity and entity["paper_id"] != paper_id:
            issue(entity, path, "entity_paper_mismatch", entity)
            classification_reviews += 1
            continue
        if ids[entity["entity_id"]] != 1:
            issue(entity, path, "duplicate_entity_id", entity)
            classification_reviews += 1
            continue
        try:
            ident_ev = evidence(entity.get("identity_evidence"))
            if not any(_literal(entity["name"], e["quote"]) for e in ident_ev):
                raise _Invalid("entity_name_not_in_original_evidence")
            classification = entity.get("classification")
            if not isinstance(classification, dict):
                raise _Invalid("classification_missing")
            member = classification.get("is_polymer")
            if member is not None and not isinstance(member, bool):
                raise _Invalid("classification_must_be_boolean_or_null")
            if member is None:
                raise _Invalid("polymer_classification_unresolved")
            if not _text(classification.get("reason")):
                raise _Invalid("classification_reason_missing")
            class_ev = evidence(classification.get("evidence"))
        except _Invalid as exc:
            issue(entity, path + ".classification", str(exc), entity)
            classification_reviews += 1
            continue

        identity = {"paper_id": paper_id, "entity_id": entity["entity_id"], "name": entity["name"],
                    "identity_evidence": ident_ev,
                    "classification": {**deepcopy(classification), "evidence": class_ev,
                                       "evidence_status": "quote_matched",
                                       "semantic_review_status": "not_performed_by_validator"},
                    "evidence_status": "quote_matched",
                    "semantic_review_status": "not_performed_by_validator"}
        if not member:
            discarded.append({**identity, "decision": "discarded_nonpolymer"})
            continue

        card = {**identity, "decision": "retained_polymer", "aliases": [],
                "description": None, "role": None, "specimens": []}
        raw_specimens = entity.get("specimens", [])
        if not isinstance(raw_specimens, list):
            issue(entity, path + ".specimens", "invalid_specimens_list", raw_specimens)
            raw_specimens = []
        specimen_counts = Counter(s.get("specimen_id") for s in raw_specimens
                                  if isinstance(s, dict) and isinstance(s.get("specimen_id"), str))
        for i, specimen in enumerate(raw_specimens):
            try:
                if not isinstance(specimen, dict) or not all(_text(specimen.get(k)) for k in ("specimen_id", "label")):
                    raise _Invalid("specimen_identity_missing")
                if specimen_counts[specimen["specimen_id"]] != 1:
                    raise _Invalid("duplicate_specimen_id")
                if "entity_id" in specimen and specimen["entity_id"] != entity["entity_id"]:
                    raise _Invalid("specimen_parent_entity_mismatch")
                if "paper_id" in specimen and specimen["paper_id"] != paper_id:
                    raise _Invalid("specimen_paper_mismatch")
                sev = evidence(specimen.get("evidence"))
                card["specimens"].append({**deepcopy(specimen), "entity_id": entity["entity_id"],
                                          "evidence": sev, "evidence_status": "quote_matched"})
            except _Invalid as exc:
                issue(entity, path + ".specimens[" + str(i) + "]", str(exc), specimen)
        specimen_ids = {s["specimen_id"] for s in card["specimens"]}

        aliases = entity.get("aliases", [])
        if not isinstance(aliases, list):
            issue(entity, path + ".aliases", "invalid_aliases_list", aliases)
            aliases = []
        for i, raw in enumerate(aliases):
            try:
                card["aliases"].append(fact(raw, entity, path, "aliases", specimen_ids))
            except _Invalid as exc:
                issue(entity, path + ".aliases[" + str(i) + "]", str(exc), raw)
        for field in ("description", "role"):
            if entity.get(field) is not None:
                try:
                    card[field] = fact(entity[field], entity, path, field, specimen_ids)
                except _Invalid as exc:
                    issue(entity, path + "." + field, str(exc), entity[field])

        for field in FIELD_NAMES:
            raw_group = entity.get(field)
            group_path = path + "." + field
            if raw_group is None:
                card[field] = {"status": "not_found_in_provided_text", "items": []}
                continue
            if not isinstance(raw_group, dict) or not isinstance(raw_group.get("items"), list):
                issue(entity, group_path, "invalid_information_group", raw_group)
                card[field] = {"status": "needs_review", "items": [], "invalid_items_count": 1}
                continue
            status = raw_group.get("status")
            invalid = 0
            if not isinstance(status, str) or status not in GROUP_STATUSES:
                issue(entity, group_path, "invalid_group_status", raw_group, review=False)
                status = "needs_review"
            items = []
            for i, raw in enumerate(raw_group["items"]):
                try:
                    items.append(fact(raw, entity, group_path, field, specimen_ids))
                except _Invalid as exc:
                    issue(entity, group_path + ".items[" + str(i) + "]", str(exc), raw)
                    invalid += 1
            if status == "not_found_in_provided_text" and (items or invalid):
                issue(entity, group_path, "missing_group_contains_items", raw_group, review=False)
                status = "needs_review"
            if status == "reported" and not items:
                issue(entity, group_path, "reported_group_has_no_usable_items", raw_group, review=False)
                status = "needs_review"
            if invalid and status != "conflicting":
                status = "needs_review"
            if field == "source_tag" and len({f["value"] for f in items}) > 1:
                issue(entity, group_path, "conflicting_polymer_source_tags", raw_group, review=False)
                status = "conflicting"
            if field == "properties":
                seen = {}
                for item in items:
                    conditions = tuple(sorted((_text(c["name"]), str(c["value"])) for c in item["conditions"]))
                    key = (_text(item["property"]), item["specimen_id"], item["unit"], conditions)
                    value = str(item["value"])
                    if key in seen and seen[key] != value:
                        issue(entity, group_path, "multiple_property_values_for_same_stated_conditions",
                              raw_group, review=False)
                        status = "conflicting"
                    seen[key] = value
            card[field] = {"status": status, "items": items}
            if invalid:
                card[field]["invalid_items_count"] = invalid
        cards.append(card)

    return {"contract_version": "polymer-cards-v1", "paper_id": paper_id, "cards": cards,
            "discarded_entities": discarded, "review_queue": review_queue, "validation_issues": issues,
            "statistics": {"input_entities": len(entities), "cards": len(cards), "retained_polymers": len(cards),
                           "discarded_entities": len(discarded), "discarded_nonpolymers": len(discarded),
                           "classification_review_entities": classification_reviews,
                           "review_queue": len(review_queue), "validation_issues": len(issues)},
            "validation_scope": "Source quote containment and record links only; polymer classification, "
                                "origin and semantic attribution are model/reviewer judgments, not verified by this validator."}
