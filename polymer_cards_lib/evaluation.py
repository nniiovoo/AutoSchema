"""Compare a validated run with selected source-checked expectations.

This is an evaluation-only lookup, never a retention rule or a scientific
accuracy score. It does not read a reference while producing model records.
"""
from __future__ import annotations

import math
import re
import unicodedata

from polymer_cards_lib.validation import _literal, _text


def _strings(value, label, *, nonempty=False):
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise ValueError(label + " must be a list of nonempty strings")
    if nonempty and not value:
        raise ValueError(label + " must not be empty")
    return value


def _string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be a nonempty string")
    return value


def _compact(value):
    return "".join(unicodedata.normalize("NFC", str(value)).split())


def _value_and_unit(value, unit):
    if (not isinstance(value, (str, int, float)) or isinstance(value, bool)
            or isinstance(value, float) and not math.isfinite(value)):
        raise ValueError("Measurement value must be finite text or a finite number")
    if unit is not None and (not isinstance(unit, str) or not unit.strip()):
        raise ValueError("Measurement unit must be a nonempty string or null")
    text, suffix = _compact(value), _compact(unit) if unit is not None else ""
    if not text:
        raise ValueError("Measurement value must not be empty")
    return text if not suffix or text.endswith(suffix) else text + suffix


def _list(reference, key):
    value = reference.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, dict) for v in value):
        raise ValueError(key + " must be a list of objects")
    return value


def _reference_cases(reference):
    if not isinstance(reference, dict):
        raise ValueError("Evaluation reference must be an object")
    identities = _list(reference, "identity_expectations") + _list(reference, "guo_identities")
    measurements = _list(reference, "measurement_expectations")
    seen = set()
    for item in identities:
        key = (_string(item.get("paper_id"), "Identity paper_id"), _string(item.get("name"), "Identity name"))
        if key in seen:
            raise ValueError("Identity expectations must be unique within each paper")
        seen.add(key)
    seen = set()
    for item in measurements:
        claim = _string(item.get("claim_id"), "Measurement claim_id")
        _string(item.get("paper_id"), "Measurement paper_id")
        if claim in seen:
            raise ValueError("Measurement claim_ids must be unique")
        seen.add(claim)
        labels = item.get("entity_labels", [item["entity_name"]] if "entity_name" in item else [])
        _strings(labels, "entity_labels", nonempty=True)
        if "value" not in item or "unit" not in item:
            raise ValueError("Measurement expectation requires value and unit")
        _value_and_unit(item["value"], item["unit"])
        for key in ("specimen_require_any", "specimen_forbid", "evidence_chunk_ids_required", "property_terms"):
            _strings(item.get(key, []), key)
        groups = item.get("condition_value_terms", [])
        if not isinstance(groups, list):
            raise ValueError("condition_value_terms must be a list of alternative-term lists")
        for group in groups:
            _strings(group, "condition_value_terms alternatives", nonempty=True)
    if "review_expectations" in reference:
        _list(reference, "review_expectations")
    return identities, measurements


def _results(run):
    results = run.get("results") if isinstance(run, dict) else run
    if not isinstance(results, list):
        raise ValueError("Run must contain a results list")
    by_paper = {}
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            raise ValueError("Each run result must be an object")
        paper_id = _string(result.get("paper_id"), "Result paper_id")
        if paper_id in by_paper:
            raise ValueError("Run result paper_ids must be unique")
        for key in ("cards", "review_queue", "discarded_entities"):
            values = result.get(key, [])
            if not isinstance(values, list) or not all(isinstance(v, dict) for v in values):
                raise ValueError("Result " + key + " must be a list of objects")
        by_paper[paper_id] = (index, result)
    return by_paper


def _labels(card):
    names = [card.get("name", "")]
    aliases = card.get("aliases", [])
    if isinstance(aliases, list):
        names += [a.get("value", "") for a in aliases if isinstance(a, dict)]
    return [n for n in names if isinstance(n, str)]


def _has_label(card, labels):
    return any(_literal(label, name) for label in labels for name in _labels(card))


def _matched_refs(refs):
    return [ref for ref in refs if isinstance(ref, dict) and ref.get("evidence_status") == "quote_matched"
            and _text(ref.get("quote"))] if isinstance(refs, list) else []


def _identity_reasons(card, labels):
    reasons = []
    if card.get("classification", {}).get("is_polymer") is not True:
        reasons.append("polymer_classification_not_retained")
    if "identity_kind" in card and card["identity_kind"] != "specific_polymer":
        reasons.append("specific_polymer_scope_not_established")
    if not _has_label(card, labels):
        reasons.append("parent_identity_does_not_match")
    refs = _matched_refs(card.get("identity_evidence"))
    for alias in card.get("aliases", []):
        if isinstance(alias, dict) and any(_literal(label, str(alias.get("value", ""))) for label in labels):
            refs += _matched_refs(alias.get("evidence"))
    if not any(_literal(label, ref["quote"]) for label in labels for ref in refs):
        reasons.append("explicit_source_label_not_attached")
    return reasons


def _term(term, text, *, positive=False):
    needle, haystack = _compact(term).casefold(), _compact(text).casefold()
    for match in re.finditer(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack):
        if positive:
            before, after = haystack[:match.start()], haystack[match.end():]
            if re.search(r"(?:without(?:any)?|freeof|notcontaining|no)$", before) or re.match(r"[-−–]?free\b", after):
                continue
        return True
    # Removing spaces makes labels such as 'P1 LiFSI electrolyte' one word.
    # Match a non-numeric physical-state term on the unjoined source spelling.
    if not any(c.isdigit() for c in term):
        needle = r"\s*".join(re.escape(p) for p in _text(term).casefold().split())
        for match in re.finditer(r"(?<!\w)" + needle + r"(?!\w)", _text(text).casefold()):
            before, after = _text(text).casefold()[:match.start()], _text(text).casefold()[match.end():]
            if positive and (re.search(r"(?:without\s+(?:any\s+)?|free\s+of\s+|not\s+containing\s+|no\s+)$", before)
                             or re.match(r"[-−– ]?free\b", after)):
                continue
            return True
    return False


def _associated_refs(prop, specimen):
    refs = _matched_refs(prop.get("evidence")) + _matched_refs(prop.get("specimen_evidence"))
    refs += _matched_refs(specimen.get("evidence"))
    for condition in prop.get("conditions", []):
        if isinstance(condition, dict):
            refs += _matched_refs(condition.get("evidence"))
    return refs


def _measurement_reasons(card, prop, case):
    labels = case.get("entity_labels", [case["entity_name"]] if "entity_name" in case else [])
    reasons = _identity_reasons(card, labels)
    if prop.get("entity_id") != card.get("entity_id"):
        reasons.append("property_parent_entity_mismatch")
    specimens = {s.get("specimen_id"): s for s in card.get("specimens", []) if isinstance(s, dict)}
    specimen = specimens.get(prop.get("specimen_id"))
    if specimen is None:
        reasons.append("linked_specimen_missing")
        specimen = {}
    elif "entity_id" in specimen and specimen["entity_id"] != card.get("entity_id"):
        reasons.append("specimen_parent_entity_mismatch")
    label = specimen.get("label", "")
    required = case.get("specimen_require_any", [])
    if required and not any(_term(term, label, positive=True) for term in required):
        reasons.append("specimen_required_term_missing")
    for term in case.get("specimen_forbid", []):
        if _term(term, label):
            reasons.append("specimen_forbidden_term_present:" + term)
    conditions = [str(c.get("value", "")) for c in prop.get("conditions", []) if isinstance(c, dict)]
    for alternatives in case.get("condition_value_terms", []):
        if not any(_term(term, value, positive=True) for term in alternatives for value in conditions):
            reasons.append("required_condition_missing:" + "|".join(alternatives))
    if case.get("property_terms") and not any(_term(term, str(prop.get("property", ""))) for term in case["property_terms"]):
        reasons.append("property_term_not_matched")
    refs = _associated_refs(prop, specimen)
    if not _matched_refs(prop.get("evidence")):
        reasons.append("measurement_evidence_not_source_matched")
    ids = {r.get("chunk_id") for r in refs}
    reasons += ["required_evidence_chunk_missing:" + key for key in case.get("evidence_chunk_ids_required", []) if key not in ids]
    return reasons


def _measurement_candidate(card, prop, case, path, *, exact):
    reasons = _measurement_reasons(card, prop, case)
    notes = []
    if not exact:
        reasons.insert(0, "raw_value_or_unit_not_exact_reference")
    elif (prop.get("unit") is None and case["unit"] is not None
          and _compact(prop["value"]).endswith(_compact(case["unit"]))):
        notes.append("unit_field_missing_but_unit_in_raw_value")
    return {"path": path, "entity_id": card.get("entity_id"), "specimen_id": prop.get("specimen_id"),
            "value": prop.get("value"), "unit": prop.get("unit"), "reasons": reasons, "notes": notes,
            "match_kind": "raw_value_and_unit" if exact else "source_related_value_variant",
            "legacy_scope_undeclared": "identity_kind" not in card}


def _source_related(card, prop, case):
    labels = case.get("entity_labels", [case["entity_name"]] if "entity_name" in case else [])
    if not _has_label(card, labels):
        return False
    required = set(case.get("evidence_chunk_ids_required", []))
    if not required:
        return False
    specimen = next((s for s in card.get("specimens", []) if s.get("specimen_id") == prop.get("specimen_id")), {})
    attached = {e.get("chunk_id") for e in _associated_refs(prop, specimen)}
    return bool(required & attached)


def _held_value(record, expected):
    if isinstance(record, dict):
        if "property" in record and "value" in record and "unit" in record:
            if _value_and_unit(record["value"], record["unit"]) == expected:
                return True
        return any(_held_value(v, expected) for v in record.values())
    return isinstance(record, list) and any(_held_value(v, expected) for v in record)


def _identity_review(record):
    """A held child fact does not hold its already-retained polymer identity."""
    path = record.get("path")
    return isinstance(path, str) and re.match(
        r"^entities\[\d+\](?:$|\.(?:classification|identity_evidence|name|entity_id|identity_kind)(?:$|[.\[]))",
        path,
    ) is not None


def evaluate_run(run, reference):
    """Return selected match/review outcomes, never a universal quality score.

    The input must be a saved validator run. Source quotation containment is
    assumed from that run; this function has no original source text to recheck.
    Legacy undeclared scope is not silently reclassified as family or individual.
    """
    identities, measurements = _reference_cases(reference)
    papers = _results(run)
    identity_results, measurement_results = [], []
    for case in identities:
        entry = {"paper_id": case["paper_id"], "name": case["name"], "candidates": []}
        index, result = papers.get(case["paper_id"], (None, {}))
        for ci, card in enumerate(result.get("cards", [])):
            if _has_label(card, [case["name"]]):
                entry["candidates"].append({"path": f"results[{index}].cards[{ci}]",
                    "reasons": _identity_reasons(card, [case["name"]]), "legacy_scope_undeclared": "identity_kind" not in card})
        held = any(_identity_review(q) and (_has_label(q, [case["name"]])
                   or isinstance(q.get("record"), dict) and _has_label(q["record"], [case["name"]]))
                   for q in result.get("review_queue", []))
        good = any(not c["reasons"] for c in entry["candidates"])
        entry["status"] = "matched_focused_expectation" if good else "needs_source_review" if entry["candidates"] or held else "not_retained"
        entry["identity_held_for_review"] = held
        identity_results.append(entry)
    for case in measurements:
        entry = {"claim_id": case["claim_id"], "paper_id": case["paper_id"], "candidates": []}
        expected = _value_and_unit(case["value"], case["unit"])
        index, result = papers.get(case["paper_id"], (None, {}))
        for ci, card in enumerate(result.get("cards", [])):
            for pi, prop in enumerate(card.get("properties", {}).get("items", [])):
                if _value_and_unit(prop.get("value"), prop.get("unit")) != expected:
                    continue
                entry["candidates"].append(_measurement_candidate(card, prop, case,
                    f"results[{index}].cards[{ci}].properties.items[{pi}]", exact=True))
        if not entry["candidates"]:
            for ci, card in enumerate(result.get("cards", [])):
                for pi, prop in enumerate(card.get("properties", {}).get("items", [])):
                    if _source_related(card, prop, case):
                        entry["candidates"].append(_measurement_candidate(card, prop, case,
                            f"results[{index}].cards[{ci}].properties.items[{pi}]", exact=False))
        labels = case.get("entity_labels", [case["entity_name"]] if "entity_name" in case else [])
        held = any((_has_label(q, labels) or isinstance(q.get("record"), dict) and _has_label(q["record"], labels))
                   and _held_value(q.get("record"), expected) for q in result.get("review_queue", []))
        good = any(not c["reasons"] for c in entry["candidates"])
        entry["status"] = "matched_focused_expectation" if good else "needs_source_review" if entry["candidates"] or held else "not_retained"
        entry["matching_value_held_for_review"] = held
        measurement_results.append(entry)
    return {"evaluation_kind": "focused_source_expectation_check", "reference_version": reference.get("reference_version"),
            "identities": identity_results, "measurements": measurement_results,
            "unevaluated_reference_sections": ["review_expectations"] if reference.get("review_expectations") else [],
            "limits": ["Selected expectation matches are not scientific accuracy, precision, recall, or exhaustive paper coverage.",
                       "Source containment and record structure are assumed from the validator run; scientific interpretation still needs source review.",
                       "Exact raw notation is compared with NFC/whitespace handling and nonduplicated units; equivalent numerical conversions are not inferred.",
                       "Legacy records without identity_kind are reported as undeclared, not assigned a new scope."]}
