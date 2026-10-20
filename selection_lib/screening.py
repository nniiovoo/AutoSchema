from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from decimal import Decimal, DecimalException, Inexact, localcontext
from typing import Any, Dict, List


def _text(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split()) if isinstance(value, str) else ""


def _number(value: Any) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def review_digest(observation: Dict, sources: Dict) -> str:
    """Bind a separate semantic review to the observation and cited source revision."""
    cited = {e["source_id"]: sources.get(e["source_id"]) for e in observation.get("evidence", [])}
    payload = json.dumps({"observation": observation, "sources": cited}, sort_keys=True,
                         ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _check_evidence(observation: Dict, candidate: Dict, sources: Dict, reviews: List[Dict]) -> Dict:
    result = {"observation_id": observation.get("observation_id"), "status": "manual_review"}

    def fail(reason):
        return {**result, "reason": reason}

    if not _text(observation.get("observation_id")) or not _text(observation.get("property")):
        return fail("observation_identity_missing")
    if any(observation.get(key) != candidate[key] for key in ("paper_id", "sample_id")):
        return fail("sample_or_paper_mismatch")
    if observation.get("role") != "current_work":
        return fail("current_work_sample_not_established")
    if not _text(observation.get("baseline")):
        return fail("baseline_missing")
    evidence = observation.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return fail("source_evidence_missing")
    for item in evidence:
        if not isinstance(item, dict):
            return fail("invalid_evidence_reference")
        if not _text(item.get("source_id")):
            return fail("invalid_evidence_reference")
        source = sources.get(item["source_id"])
        if not isinstance(source, dict):
            return fail("unknown_source")
        if source.get("paper_id") != candidate["paper_id"]:
            return fail("source_paper_mismatch")
        if not _text(source.get("locator")) or not _text(source.get("text")):
            return fail("source_context_or_locator_missing")
        if not _text(item.get("quote")) or _text(item["quote"]) not in _text(source["text"]):
            return fail("quote_not_in_source")
    if observation.get("value") is not None:
        if not _number(observation["value"]):
            return fail("invalid_numeric_value")
        raw = _text(observation.get("value_raw"))
        if not raw:
            return fail("raw_value_missing")
        pattern = r"(?<![\w.+−-])" + re.escape(raw) + r"(?![\w.])"
        if not any(re.search(pattern, _text(e["quote"])) for e in evidence):
            return fail("raw_value_not_in_quote")
        # shortcut: decimal/e mean and optional deviation with unchanged units; review other notation.
        number = r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
        numeric = re.fullmatch(r"([+-]?" + number + r")\s*(?:(?:±|\+/-)\s*(" + number
                               + r"))?\s*((?!.*(?:±|\+/-)).*)", raw)
        if not numeric:
            return fail("raw_value_format_requires_reviewed_normalization")
        try:
            mean = Decimal(numeric[1])
            if mean != Decimal(str(observation["value"])):
                return fail("numeric_and_raw_value_mismatch")
            if numeric[3] != observation.get("unit"):
                return fail("raw_unit_mismatch")
            if numeric[2] is not None:
                interval = observation.get("uncertainty")
                if (not isinstance(interval, dict)
                        or not _number(interval.get("lower")) or not _number(interval.get("upper"))
                        or interval.get("unit") != observation.get("unit")):
                    return fail("raw_deviation_requires_matching_uncertainty")
                with localcontext() as context:
                    context.traps[Inexact] = True
                    deviation = Decimal(numeric[2])
                    if (Decimal(str(interval["lower"])) != mean - deviation
                            or Decimal(str(interval["upper"])) != mean + deviation):
                        return fail("raw_deviation_requires_matching_uncertainty")
        except DecimalException:
            return fail("raw_value_format_requires_reviewed_normalization")
    matches = [r for r in reviews if all(r.get(key) == observation.get(key)
               for key in ("paper_id", "sample_id", "observation_id"))]
    if len(matches) != 1:
        return fail("separate_semantic_review_required")
    review = matches[0]
    if review.get("status") != "supported" or not _text(review.get("reviewer")):
        return fail("semantic_support_not_established")
    try:
        expected = review_digest(observation, sources)
    except (ValueError, TypeError, KeyError):
        return fail("invalid_observation_data")
    if review.get("record_digest") != expected:
        return fail("review_revision_mismatch")
    return {**result, "status": "supported_as_reported", "reason": "quote_present_and_separate_review_supplied",
            "reviewer": review["reviewer"], "record_digest": expected}


def _valid_rule(rule: Any) -> bool:
    if not isinstance(rule, dict) or not rule:
        return False
    if set(rule) == {"equals"}:
        return bool(_text(rule["equals"])) or isinstance(rule["equals"], bool) or _number(rule["equals"])
    if set(rule) - {"minimum", "maximum"} or not all(_number(v) for v in rule.values()):
        return False
    return rule.get("minimum", -math.inf) <= rule.get("maximum", math.inf)


def _matches(value: Any, rule: Dict) -> bool:
    if "equals" in rule:
        expected = rule["equals"]
        if isinstance(expected, bool):
            return isinstance(value, bool) and value == expected
        if _number(expected):
            return _number(value) and value == expected
        return isinstance(value, str) and value == expected
    return (_number(value) and rule.get("minimum", -math.inf) <= value
            <= rule.get("maximum", math.inf))


def _gap(criterion: Dict, reason: str, owner: str = "source_review", candidate: Dict = None) -> Dict:
    if owner == "application_owner":
        action = "Define this use's acceptance requirement and required test conditions. Literature cannot choose the requirement."
    elif owner == "evidence_reviewer":
        action = "Resolve source, sample, metric, unit or review conflicts; preserve the original records and re-review the corrected revision."
    else:
        action = "Check the same sample's original methods, figures and available supplement, then targeted same-formulation primary studies."
        if "inaccess" in reason.lower() or "unavailable" in reason.lower():
            action = "Obtain the original supplementary/source document; retain its access status if it remains unavailable."
    return {"criterion_id": criterion.get("criterion_id"), "property": criterion.get("property"),
            "reason": reason, "owner": owner, "next_action": action, "status": "pending",
            "source_coverage": (candidate or {}).get("source_coverage", {}),
            "retrieval_executed": False}


def _compare(observation: Dict, criterion: Dict, application: str) -> Dict:
    out = {"observation_id": observation["observation_id"]}

    def decision(state, reason):
        return {**out, "decision": state, "reason": reason}

    claim = criterion.get("required_claim_type", "property_test")
    if observation.get("claim_type") != claim:
        return decision("retrieve_more", "required_experiment_type_missing")
    if claim == "tested_device" and observation.get("tested_application") != application:
        return decision("retrieve_more", "required_device_application_not_tested")
    if "baseline" in criterion and observation.get("baseline") != criterion["baseline"]:
        return decision("retrieve_more", "required_baseline_not_established")
    conditions = observation.get("conditions", {})
    if not isinstance(conditions, dict):
        return decision("manual_review", "invalid_condition_record")
    for name, rule in criterion.get("conditions", {}).items():
        if conditions.get(name) is None:
            return decision("retrieve_more", "required_condition_missing:" + name)
        if not _matches(conditions[name], rule):
            return decision("retrieve_more", "required_protocol_not_tested:" + name)
    if observation.get("value") is None:
        return decision("retrieve_more", observation.get("missing_reason", "required_value_not_extracted"))
    if not _number(observation["value"]):
        return decision("manual_review", "invalid_numeric_value")
    if observation.get("unit") != criterion["unit"]:
        return decision("manual_review", "unit_mismatch_requires_reviewed_normalization")
    value = observation["value"]
    lower, upper = criterion.get("minimum", -math.inf), criterion.get("maximum", math.inf)
    interval = observation.get("uncertainty")
    if interval is not None:
        if not isinstance(interval, dict):
            return decision("manual_review", "invalid_uncertainty")
        lo, hi = interval.get("lower"), interval.get("upper")
        if (not _number(lo) or not _number(hi) or not lo <= value <= hi
                or interval.get("unit") != observation["unit"]):
            return decision("manual_review", "invalid_uncertainty")
        if lo < lower <= hi or lo <= upper < hi:
            return decision("manual_review", "uncertainty_crosses_requirement")
    state = "keep_for_followup" if lower <= value <= upper else "exclude_for_use"
    return {**out, "decision": state, "reason": "comparable_reported_point_estimate_compared",
            "comparison": {"value": value, "unit": observation["unit"],
                           "minimum": criterion.get("minimum"), "maximum": criterion.get("maximum")},
            "uncertainty_reported": interval is not None}


def _criterion_result(candidate: Dict, criterion: Dict, profile: Dict, evidence: List[Dict]) -> Dict:
    out = {"criterion_id": criterion.get("criterion_id"), "property": criterion.get("property"),
           "required": criterion.get("required", True), "observations": [], "followups": []}

    def stop(state, reason, owner="source_review"):
        return {**out, "decision": state, "reason": reason,
                "followups": [_gap(criterion, reason, owner, candidate)]}

    bounds = [criterion[k] for k in ("minimum", "maximum") if k in criterion]
    rules = criterion.get("conditions", {})
    if (not _text(criterion.get("criterion_id")) or not _text(criterion.get("property"))
            or not _text(criterion.get("unit")) or not bounds or not all(_number(v) for v in bounds)
            or criterion.get("minimum", -math.inf) > criterion.get("maximum", math.inf)
            or not isinstance(criterion.get("required", True), bool)
            or not isinstance(rules, dict) or not rules or not all(_text(k) and _valid_rule(r) for k, r in rules.items())
            or not _text(criterion.get("required_claim_type", "property_test"))
            or criterion.get("required_claim_type", "property_test") not in {"property_test", "tested_device", "simulation"}):
        return stop("manual_review", "application_requirement_undefined_or_invalid", "application_owner")
    observations = [o for o in candidate["observations"] if o.get("property") == criterion["property"]]
    if not observations:
        reason = next((m.get("reason", "not_extracted") for m in candidate.get("missing", [])
                       if m.get("property") == criterion["property"]), "not_extracted")
        return stop("retrieve_more", reason)
    for observation in observations:
        status = next(e for e in evidence if e["observation_id"] == observation.get("observation_id"))
        if status["status"] != "supported_as_reported":
            out["observations"].append({"observation_id": observation.get("observation_id"),
                                        "decision": "manual_review", "reason": status["reason"]})
        else:
            out["observations"].append(_compare(observation, criterion, profile["application"]))
    states = {o["decision"] for o in out["observations"]}
    if "manual_review" in states:
        return stop("manual_review", next(o["reason"] for o in out["observations"]
                                          if o["decision"] == "manual_review"), "evidence_reviewer")
    comparable = states & {"keep_for_followup", "exclude_for_use"}
    if len(comparable) > 1:
        return stop("manual_review", "conflicting_comparable_results", "evidence_reviewer")
    if comparable:
        gaps = [_gap(criterion, o["reason"], candidate=candidate) for o in out["observations"]
                if o["decision"] == "retrieve_more"]
        return {**out, "decision": comparable.pop(), "reason": "supported_comparable_observations_agree", "followups": gaps}
    reason = out["observations"][0]["reason"]
    return stop("retrieve_more", reason)


def screen_candidate(candidate: Dict, profile: Dict, sources: Dict, reviews: List[Dict]) -> Dict:
    """Screen one sample against all mandatory criteria, without a combined score.

    Separate review receipts are trusted caller inputs, not authenticated human
    signatures. Mechanical checks cannot establish semantic or scientific truth.
    """
    if not isinstance(candidate, dict) or not all(_text(candidate.get(k))
            for k in ("candidate_id", "paper_id", "sample_id")):
        raise ValueError("Each candidate needs candidate_id, paper_id and sample_id.")
    if not isinstance(candidate.get("observations"), list) or not all(
            isinstance(o, dict) for o in candidate["observations"]):
        raise ValueError("Task 3 requires atomic observations; flattened Phase II values cannot establish sample/metric links.")
    ids = [o.get("observation_id") for o in candidate["observations"]]
    if any(not _text(i) for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Observation IDs must be present and unique within a candidate.")
    missing = candidate.get("missing", [])
    if not isinstance(missing, list) or not all(isinstance(m, dict) and _text(m.get("property"))
            and _text(m.get("reason")) for m in missing):
        raise ValueError("Candidate missing information must be a list of property/reason objects.")
    if any("missing_reason" in o and not _text(o["missing_reason"]) for o in candidate["observations"]):
        raise ValueError("Observation missing_reason must be a nonempty string when supplied.")
    if (not isinstance(profile, dict) or not _text(profile.get("profile_id"))
            or not _text(profile.get("application")) or not isinstance(profile.get("criteria"), list)
            or not profile["criteria"] or not all(isinstance(c, dict) for c in profile["criteria"])):
        raise ValueError("An application profile needs profile_id, application and nonempty criteria.")
    criterion_ids = [c.get("criterion_id") for c in profile["criteria"]]
    if any(not _text(i) for i in criterion_ids) or len(criterion_ids) != len(set(criterion_ids)):
        raise ValueError("Criterion IDs must be present and unique.")
    if not isinstance(sources, dict) or not isinstance(reviews, list) or not all(isinstance(r, dict) for r in reviews):
        raise ValueError("Sources must be an object and separate reviews a list of receipts.")
    evidence = [_check_evidence(o, candidate, sources, reviews) for o in candidate["observations"]]
    criteria = [_criterion_result(candidate, c, profile, evidence) for c in profile["criteria"]]
    mandatory = [c for c in criteria if c["required"] is not False]
    states = {c["decision"] for c in mandatory}
    if not mandatory or "manual_review" in states:
        decision = "manual_review"
    elif "exclude_for_use" in states:
        decision = "exclude_for_use"
    elif "retrieve_more" in states:
        decision = "retrieve_more"
    else:
        decision = "keep_for_followup"
    followups = [gap for c in criteria for gap in c["followups"]]
    if not mandatory:
        followups.append(_gap({}, "mandatory_requirements_undefined", "application_owner", candidate))
    evidence_status = ("needs_review" if any(e["status"] == "manual_review" for e in evidence)
                       else "supported_as_reported" if evidence else "no_observations")
    return {"contract_version": "task3-v1", "candidate_id": candidate["candidate_id"],
            "paper_id": candidate["paper_id"], "sample_id": candidate["sample_id"],
            "profile_id": profile["profile_id"], "decision": decision,
            "evidence": {"status": evidence_status, "observations": evidence},
            "criteria": criteria, "followups": followups,
            "source_coverage": candidate.get("source_coverage", {}),
            "limitations": "Research selection only. Semantic reviews are supplied inputs; no experiment or device is independently validated."}
