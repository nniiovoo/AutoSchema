"""Verify an anchored context-review chain and rebuild a three-paper derived view.

This makes no model calls. Raw base records, raw context proposals and composed
responses remain distinct. Source retrieval is not scientific certification.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from verify_span_run import canonical_hash, evidence_refs, file_hash, metrics, outcomes


CONTEXT_FIELDS = {"specimen_id", "specimen_evidence", "conditions", "evidence"}


def immutable_view(response):
    result = deepcopy(response)
    for entity in result["entities"]:
        for item in entity.get("properties", {}).get("items", []):
            for field in CONTEXT_FIELDS:
                item.pop(field, None)
    return result


def verify_step(directory, document, previous, repository, historical_directories):
    from polymer_cards_lib import context_review as current_policy
    from polymer_cards_lib.io import read_json, parse_json
    from polymer_cards_lib.validation import build_cards

    freeze = read_json(directory / "pre-run-freeze.json")
    historical_files, policy = {}, current_policy
    for filename, expected in freeze["code_and_reference_sha256"].items():
        if file_hash(repository / filename) == expected:
            continue
        candidates = [d / filename for d in historical_directories if (d / filename).is_file()
                      and file_hash(d / filename) == expected]
        if filename not in {"polymer_cards_lib/context_review.py", "polymer_cards_lib/llm.py"} or not candidates:
            raise ValueError("Context code/reference changed without verified historical source: " + filename)
        historical_files[filename] = expected
        if filename.endswith("context_review.py"):
            spec = importlib.util.spec_from_file_location("historical_context_" + expected[:12], candidates[0])
            policy = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy)
    sources = read_json(directory / "sources.json")["documents"]
    base = read_json(directory / "base-responses.json")["responses"]
    saved_composed = read_json(directory / "composed-responses.json")["responses"]
    captured = read_json(directory / "context-proposals.json")
    saved_audit = read_json(directory / "context-application-audit.json")
    run = read_json(directory / "cards.json")
    if (len(sources) != 1 or sources[0]["chunks"] != document["chunks"] or len(base) != 1
            or base[0] != previous or len(saved_composed) != 1):
        raise ValueError("Context chain base/source does not match the preceding stage")
    checked = freeze.get("checked_answers_supplied", freeze.get("checked_reference_answers_supplied"))
    if (checked is not False or freeze["previous_response_supplied"] is not True
            or file_hash(directory / "base-responses.json") != freeze["base_file_sha256"]
            or file_hash(directory / "base-sources.json") != freeze["source_file_sha256"]):
        raise ValueError("Context base/source scope differs from its pre-request freeze")
    focus = None
    if "focus_file_sha256" in freeze:
        if file_hash(directory / "source-audit-focus.json") != freeze["focus_file_sha256"]:
            raise ValueError("Unverified focus hypotheses changed after their request freeze")
        focus = read_json(directory / "source-audit-focus.json")
    strict_focus = freeze.get("strict_focus", False)
    if not isinstance(strict_focus, bool) or strict_focus and focus is None:
        raise ValueError("Strict context scope requires frozen source-audit targets")
    response_format = policy.build_context_response_format()
    system = policy.CONTEXT_REVIEW_SYSTEM_PROMPT
    profile = {"output_format": response_format["type"], "schema_name": response_format["json_schema"]["name"],
               "schema_sha256": canonical_hash(response_format["json_schema"]["schema"]),
               "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest()}
    if strict_focus:
        prompt = policy.build_context_review_prompt(document, previous, review_focus=focus, strict_focus=True)
    else:
        prompt = (policy.build_context_review_prompt(document, previous) if focus is None else
                  policy.build_context_review_prompt(document, previous, review_focus=focus))
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    trace, proposals = captured["trace"], captured["proposals"]
    if (freeze["response_format"] != response_format or freeze["system_prompt_sha256"] != profile["system_prompt_sha256"]
            or run["run_metadata"]["extraction_profile"] != profile or trace["extraction_profile"] != profile
            or trace["request_mode"] != "source_grounded_context_review" or trace["finish_reason"] != "stop"
            or trace["previous_response_sha256"] != canonical_hash(previous)
            or trace["request_prompt_sha256"] != prompt_hash or freeze["request_prompt_sha256"] != prompt_hash
            or parse_json(trace["raw_response_text"]) != proposals
            or (focus is not None and trace.get("source_audit_focus_sha256") != canonical_hash(focus))
            or strict_focus and trace.get("strict_focus") is not True):
        raise ValueError("Custom context request/schema/raw response does not reconstruct")
    context_kwargs = {"review_focus": focus, "strict_focus": True} if strict_focus else {}
    composed, audit = policy.apply_context_proposals(document, previous, proposals, **context_kwargs)
    if (composed != saved_composed[0] or audit != saved_audit
            or immutable_view(composed) != immutable_view(previous)
            or audit["immutable_fields_preserved"] is not True):
        raise ValueError("Context application differs or immutable claims changed")
    # A history-only prompt extension must not silently change composition.
    if current_policy.apply_context_proposals(document, previous, proposals, **context_kwargs) != (composed, audit):
        raise ValueError("Current and frozen pure context applicators differ on the captured proposals")
    entities = {entity["entity_id"]: entity for entity in previous["entities"]}
    for edit in audit["edit_results"]:
        item = entities[edit["entity_id"]]["properties"]["items"][edit["property_index"]]
        if edit["anchor_sha256"] != policy.property_anchor_sha256(edit["entity_id"], edit["property_index"], item):
            raise ValueError("Applied context edit has a stale immutable target anchor")
    if run["results"] != [build_cards(document, composed)]:
        raise ValueError("Context capture validation does not reproduce")
    return {"directory": directory.name, "paper_id": document["paper_id"], "composed": composed,
            "capture": captured, "audit": audit, "freeze": freeze, "metadata": run["run_metadata"],
            "historical_code_files_verified": historical_files,
            "strict_focus": strict_focus,
            "source_audit_hypotheses_supplied": focus is not None,
            "receipts": {name: file_hash(directory / name) for name in
                ("base-responses.json", "base-sources.json", "context-proposals.json", "composed-responses.json",
                 "context-application-audit.json", "pre-run-freeze.json")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-run-dir", type=Path, required=True)
    context = parser.add_mutually_exclusive_group(required=True)
    context.add_argument("--context-dir", type=Path)
    context.add_argument("--context-dirs", type=Path, nargs="+")
    parser.add_argument("--historical-code-dirs", type=Path, nargs="+", default=[])
    parser.add_argument("--fresh-run-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.out_dir.exists():
        raise FileExistsError("Choose a new composition directory; existing results are never overwritten")
    repository = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repository))
    from polymer_cards_lib.context_review import (
        CONTEXT_REVIEW_SYSTEM_PROMPT, apply_context_proposals,
        build_context_response_format, build_context_review_prompt, property_anchor_sha256)
    from polymer_cards_lib.evaluation import evaluate_run
    from polymer_cards_lib.evidence_spans import build_span_catalog, combine_adjacent_spans, resolve_span
    from polymer_cards_lib.io import read_json, parse_json
    from polymer_cards_lib.render import write_outputs
    from polymer_cards_lib.validation import build_cards

    baseline_dir = args.baseline_dir or repository / "examples/polymer_cards/fresh_run_2026-11-06"
    receipt = read_json(Path(__file__).with_name("baseline-reference-freeze.json"))
    for path, expected in receipt["reference_files"].items():
        if file_hash(repository / path) != expected:
            raise ValueError("Frozen checked reference changed: " + path)
    for path, expected in receipt["baseline_files"].items():
        if file_hash(baseline_dir / path) != expected:
            raise ValueError("Previous fresh baseline changed: " + path)
    base_raw = read_json(args.base_run_dir / "raw-responses.json")
    base_run = read_json(args.base_run_dir / "cards.json")
    documents = read_json(args.base_run_dir / "sources.json")["documents"]
    if base_raw["mode"] != "live_model_revision" or base_run["run_metadata"]["mode"] != "live_model_revision":
        raise ValueError("Context composition expects the separately preserved full-paper revision stage")
    bases = {response["paper_id"]: response for response in base_raw["responses"]}
    docs = {document["paper_id"]: document for document in documents}
    if len(bases) != len(base_raw["responses"]) or set(bases) != set(docs) or len(docs) != len(documents):
        raise ValueError("Base records and sources need unique matching papers")
    baseline = read_json(baseline_dir / "cards.json")
    fresh = read_json(args.fresh_run_dir / "cards.json")
    for directory in (baseline_dir, args.fresh_run_dir):
        other = read_json(directory / "sources.json")["documents"]
        if {d["paper_id"]: d["chunks"] for d in other} != {d["paper_id"]: d["chunks"] for d in documents}:
            raise ValueError("A comparison stage changed the original source snapshot")

    context_directories = args.context_dirs or [args.context_dir]
    working, steps = deepcopy(bases), []
    for directory in context_directories:
        source = read_json(directory / "sources.json")["documents"]
        if len(source) != 1 or source[0]["paper_id"] not in docs or source[0]["chunks"] != docs[source[0]["paper_id"]]["chunks"]:
            raise ValueError("Context chain must target one matching original paper per capture")
        paper = source[0]["paper_id"]
        step = verify_step(directory, docs[paper], working[paper], repository, args.historical_code_dirs)
        working[paper] = step["composed"]
        step["combined_responses"] = [deepcopy(working[d["paper_id"]]) for d in documents]
        steps.append(step)
    targeted = {step["paper_id"] for step in steps}
    combined_responses = [working[doc["paper_id"]] for doc in documents]
    for response in combined_responses:
        if immutable_view(response) != immutable_view(bases[response["paper_id"]]):
            raise ValueError("A composed paper changed immutable scientific claims")
        if response["paper_id"] not in targeted and response != bases[response["paper_id"]]:
            raise ValueError("An untargeted paper's raw response changed")
    results = [build_cards(doc, response) for doc, response in zip(documents, combined_responses)]
    catalogues = {doc["paper_id"]: build_span_catalog(doc) for doc in documents}
    support_counts = Counter()

    def verify_reference_list(refs, doc):
        selected = {}
        for ref in refs:
            if ref.get("evidence_status") != "quote_matched" or ref.get("paper_id") != doc["paper_id"]:
                raise ValueError("Retained reference source identity/status differs")
            if ref.get("evidence_origin") == "source_span_selection":
                exact = resolve_span(doc, ref["chunk_id"], ref["span_id"], catalog=catalogues[doc["paper_id"]])
                if any(ref.get(k) != v for k, v in exact.items()):
                    raise ValueError("Retained span does not match its exact catalogued slice")
                selected[(ref["chunk_id"], ref["span_id"])] = ref
                support_counts["direct_selected_reference_occurrences"] += 1
            elif ref.get("evidence_origin") != "source_span_selection_union":
                raise ValueError("Unexpected legacy or unsupported evidence origin in composed V4 cards")
        chunks = {chunk["chunk_id"]: chunk for chunk in doc["chunks"]}
        for ref in refs:
            if ref.get("evidence_origin") != "source_span_selection_union":
                continue
            ids = ref["span_ids"]
            if not isinstance(ids, list) or len(ids) < 2 or len(set(ids)) != len(ids):
                raise ValueError("Union support lacks distinct original selections")
            originals = []
            for identifier in ids:
                key = (ref["chunk_id"], identifier)
                if key not in selected:
                    raise ValueError("A union uses a source span not already selected in the same evidence list")
                originals.append(selected[key])
            expected = combine_adjacent_spans(doc, originals, catalog=catalogues[doc["paper_id"]])
            if ref not in expected:
                raise ValueError("Union support differs from deterministic original-span composition")
            intervals = sorted((r["source_start"], r["source_end"]) for r in originals)
            end = intervals[0][1]
            for start, stop in intervals[1:]:
                if start > end and not chunks[ref["chunk_id"]]["text"][end:start].isspace():
                    raise ValueError("Union support bridges unselected non-whitespace content")
                end = max(end, stop)
            support_counts["derived_adjacent_union_occurrences"] += 1
        for ref in refs:
            start, end = ref["source_start"], ref["source_end"]
            if (not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int)
                    or isinstance(end, bool) or not 0 <= start < end <= len(chunks[ref["chunk_id"]]["text"])
                    or ref["quote"] != chunks[ref["chunk_id"]]["text"][start:end]):
                raise ValueError("Retained support has invalid offsets or nonoriginal source characters")
            support_counts["source_exact_reference_occurrences"] += 1

    def visit(value, doc):
        if isinstance(value, list):
            if value and all(isinstance(item, dict) and "chunk_id" in item and "quote" in item for item in value):
                verify_reference_list(value, doc)
            for child in value:
                visit(child, doc)
        elif isinstance(value, dict):
            for child in value.values():
                visit(child, doc)

    for doc, result in zip(documents, results):
        visit(result["cards"], doc)
    composed_view = {"results": results}
    reference_paths = {
        "conditions": repository / "examples/polymer_cards/condition_reference_2026-11-06/reference.json",
        "focused": repository / "examples/polymer_cards/identity_reference_2026-10-30.json",
        "pei": repository / "examples/polymer_cards/checked_pei_2026-10-30/evaluation-cases.json"}
    comparisons, outputs = {}, {}
    stages = {"baseline": baseline, "fresh_span": fresh, "full_revision": base_run, "context_composed": composed_view}
    for stage, stage_run in stages.items():
        comparisons[stage] = {"metrics": metrics(stage_run), "selected_checks": {}}
        for name, path in reference_paths.items():
            evaluation = evaluate_run(stage_run, read_json(path))
            outputs[stage + "-" + name + "-evaluation.json"] = evaluation
            comparisons[stage]["selected_checks"][name] = outcomes(evaluation)
    for index, step in enumerate(steps[:-1], 1):
        state = {"results": [build_cards(doc, response) for doc, response in zip(documents, step["combined_responses"])]}
        comparisons["context_step_" + str(index)] = {"metrics": metrics(state), "selected_checks": {}}
        for name, path in reference_paths.items():
            evaluation = evaluate_run(state, read_json(path))
            outputs["context-step-" + str(index) + "-" + name + "-evaluation.json"] = evaluation
            comparisons["context_step_" + str(index)]["selected_checks"][name] = outcomes(evaluation)
    call_count = sum(step["metadata"]["model_calls"] for step in steps)
    usage = {key: sum(step["capture"]["trace"]["usage"][key] for step in steps)
             for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
    verification = {
        "verification_kind": "anchored_context_composition_and_exact_source_support",
        "targeted_paper_ids": sorted(targeted), "actual_context_model_calls": call_count,
        "context_chain": [{"capture_directory": step["directory"], "paper_id": step["paper_id"],
            "request_prompt_sha256": step["capture"]["trace"]["request_prompt_sha256"],
            "custom_profile": step["metadata"]["extraction_profile"],
            "historical_code_files_verified": step["historical_code_files_verified"],
            "strict_focus": step["strict_focus"],
            "unverified_source_audit_hypotheses_supplied": step["source_audit_hypotheses_supplied"]}
            for step in steps],
        "context_requests_custom_profiles_and_raw_provider_json_verified": True,
        "deterministic_context_chain_reproduced": True,
        "base_provider_records_preserved": True, "all_immutable_claims_units_identities_and_order_preserved": True,
        "untargeted_raw_responses_unchanged": True,
        "applied_context_edit_occurrences": sum(step["audit"]["applied_edits"] for step in steps),
        "held_context_edit_occurrences": sum(len(step["audit"]["held_edits"]) for step in steps),
        "retained_source_support_counts": dict(support_counts),
        "all_unions_use_already_selected_same_list_spans_with_no_nonwhitespace_gaps": True,
        "code_and_reference_freezes_verified": True, "all_three_reference_hashes_unchanged": True,
        "model_calls_made_by_verifier": 0,
        "limits": ["Exact retrieval and immutable anchors do not verify scientific context interpretation.",
                   "Context review is not fresh extraction and cannot change unsupported numbers or missing entities.",
                   "Applied edit occurrences may revisit the same property in sequential reviews."]}
    outputs["context-verification.json"] = verification
    outputs["stage-comparison.json"] = {"comparison_kind": "saved_fresh_revision_and_context_stages",
        "stages": comparisons, "context_calls_returned_usage": usage,
        "reference_sha256": {name: file_hash(path) for name, path in reference_paths.items()},
        "limits": ["All selected cases remain unchanged; these results are not overall accuracy or exhaustive recall.",
                   "Stages use different procedures and source-context checks; preserve each stage separately.",
                   "A retained derived source union is retrieval support, not a new model-authored quotation."]}
    profile = steps[-1]["metadata"]["extraction_profile"]
    metadata = {"contract_version": "polymer-cards-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "anchored_context_composition", "run_kind": "Guo context review plus all-three-paper revalidation",
        "composition_note": "Targeted context review chain; other paper responses are unchanged. All three are revalidated under current policy.",
        "provider": steps[-1]["metadata"]["provider"], "model": steps[-1]["metadata"]["model"],
        "model_calls": call_count, "model_calls_attempted": sum(step["metadata"]["model_calls_attempted"] for step in steps),
        "model_papers_targeted_this_stage": len(targeted), "papers_revalidated": len(results), "run_complete": True,
        "prior_fresh_model_calls": fresh["run_metadata"]["model_calls"],
        "prior_full_revision_model_calls": base_run["run_metadata"]["model_calls"],
        "extraction_profile": profile, "checked_answers_supplied": False,
        "source_audit_hypotheses_supplied": any(step["source_audit_hypotheses_supplied"] for step in steps),
        "immutable_claims_preserved": True, "automatic_retries": 0,
        "retention_rule": "polymer identity only; no application or completeness threshold"}
    additional = {"base-raw-responses.json": base_raw,
        "context-chain.json": {"mode": "ordered_context_review_captures", "steps": [
            {key: step[key] for key in ("directory", "paper_id", "capture", "audit", "freeze", "historical_code_files_verified", "source_audit_hypotheses_supplied", "strict_focus")}
            for step in steps]},
        "composed-responses.json": {"mode": "anchored_context_composition", "responses": combined_responses},
        "context-verification.json": verification,
        "input-receipts.json": {"base_raw_sha256": file_hash(args.base_run_dir / "raw-responses.json"),
            "context_capture_files": [{"directory": step["directory"], "files": step["receipts"]} for step in steps]}}
    serialized = {name: json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n" for name, value in outputs.items()}
    write_outputs(results, documents, args.out_dir, metadata, additional_outputs=additional)
    evaluation_dir = args.out_dir / "evaluation"
    evaluation_dir.mkdir()
    for name, text in serialized.items():
        (evaluation_dir / name).write_text(text)
    print(json.dumps({"stage_comparison": {stage: data["selected_checks"]["conditions"] for stage, data in comparisons.items()},
                      "context_verification": verification}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
