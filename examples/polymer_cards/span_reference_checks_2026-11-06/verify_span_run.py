"""Verify saved source-span extraction and compare unchanged selected references.

No credentials are read and no model requests are made. Span selection checks
verify retrieval integrity, not whether the selected text supports a claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import re
import sys
import unicodedata


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_refs(value, path=""):
    if isinstance(value, dict):
        if "chunk_id" in value and ("span_id" in value or "quote" in value):
            yield path, value
        for key, child in value.items():
            yield from evidence_refs(child, path + "." + key if path else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from evidence_refs(child, f"{path}[{index}]")


def metrics(run):
    counts = Counter()
    per_paper = []
    for result in run["results"]:
        identities = sum(bool(re.match(
            r"^entities\[\d+\](?:$|\.(?:classification|identity_evidence|name|entity_id|identity_kind)(?:$|[.\[]))",
            entry.get("path", ""))) for entry in result["review_queue"])
        row = {"paper_id": result["paper_id"], "cards": len(result["cards"]),
               "review_records": len(result["review_queue"]), "identity_review_records": identities,
               "other_field_review_records": len(result["review_queue"]) - identities,
               "validation_flags": len(result["validation_issues"])}
        for key, value in row.items():
            if key != "paper_id":
                counts[key] += value
        for card in result["cards"]:
            counts["declared_" + str(card.get("identity_kind"))] += 1
            counts["retained_property_items"] += len(card["properties"]["items"])
            counts["retained_conflict_notes"] += len(card["properties"].get("conflicts", []))
        per_paper.append(row)
    return {"totals": dict(counts), "papers": per_paper}


def outcomes(evaluation):
    return {section: dict(Counter(case["status"] for case in evaluation[section]))
            for section in ("identities", "measurements", "conflicts")}


def assemble_revision_captures(directories, prior_directory, output_directory):
    """Combine completed revisions, never editing a response or making a call."""
    from polymer_cards_lib.io import read_json, parse_json
    from polymer_cards_lib.prompt import extraction_profile
    from polymer_cards_lib.render import write_outputs
    from polymer_cards_lib.validation import build_cards

    if output_directory.exists():
        raise FileExistsError("Never overwrite an earlier revision capture")
    prior_raw = read_json(prior_directory / "raw-responses.json")
    documents = read_json(prior_directory / "sources.json")["documents"]
    prior = {r["paper_id"]: r for r in prior_raw["responses"]}
    docs = {d["paper_id"]: d for d in documents}
    if prior_raw["mode"] != "live_model_extraction" or set(prior) != set(docs):
        raise ValueError("Revision assembly requires complete separately saved fresh proposals")
    found, receipts, freezes, model_set = {}, [], [], set()
    for directory in directories:
        saved = read_json(directory / "cards.json")
        raw = read_json(directory / "raw-responses.json")
        source = read_json(directory / "sources.json")["documents"]
        meta = saved["run_metadata"]
        if (meta["mode"] != "live_model_revision" or raw["mode"] != "live_model_revision"
                or meta["run_complete"] is not True or any(len(v) != 1 for v in
                    (saved["results"], raw["responses"], raw["traces"], source))):
            raise ValueError("Each revision capture must contain one completed paper")
        response, trace, result = raw["responses"][0], raw["traces"][0], saved["results"][0]
        paper = response["paper_id"]
        if (paper in found or paper not in docs or trace["paper_id"] != paper
                or result["paper_id"] != paper or source[0]["paper_id"] != paper
                or source[0]["chunks"] != docs[paper]["chunks"]):
            raise ValueError("Revision identity/source mismatch or duplicated paper")
        if (trace["finish_reason"] != "stop" or trace["extraction_profile"] != extraction_profile()
                or trace.get("request_mode") != "source_grounded_model_revision"
                or trace.get("previous_response_sha256") != canonical_hash(prior[paper])
                or parse_json(trace["raw_response_text"]) != response
                or build_cards(docs[paper], response) != result):
            raise ValueError("Completed revision response/trace/validation differs")
        for kind in ("records", "sources"):
            if file_hash(directory / ("prior-" + kind + ".json")) != meta["repair_input_" + kind + "_sha256"]:
                raise ValueError("Original revision CLI input changed")
        freezes.append(read_json(directory / "pre-run-freeze.json"))
        receipts.append({"capture_directory": directory.name,
            "raw_responses_sha256": file_hash(directory / "raw-responses.json"),
            "cards_sha256": file_hash(directory / "cards.json"),
            "sources_sha256": file_hash(directory / "sources.json"),
            "freeze_sha256": file_hash(directory / "pre-run-freeze.json"),
            "attempted_calls": meta["model_calls_attempted"], "completed_calls": meta["model_calls"],
            "provider": meta["provider"], "model": meta["model"],
            "repair_input_records_sha256": meta["repair_input_records_sha256"],
            "repair_input_sources_sha256": meta["repair_input_sources_sha256"]})
        model_set.add((meta["provider"], meta["model"]))
        found[paper] = (response, trace, result, meta)
    if set(found) != set(docs) or len(model_set) != 1:
        raise ValueError("Completed revision captures do not cover the prior fresh papers with one model")
    ordered = [found[d["paper_id"]] for d in documents]
    provider, model = next(iter(model_set))
    metadata = {"contract_version": "polymer-cards-v1", "mode": "live_model_revision",
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "run_kind": "assembled_source_grounded_revision_requests",
        "assembly_note": "Completed new revisions combined without editing model records. Prior fresh proposals were supplied, never checked reference answers.",
        "provider": provider, "model": model, "run_complete": True,
        "papers_requested": len(ordered), "papers_completed": len(ordered),
        "model_calls": sum(r[3]["model_calls"] for r in ordered),
        "model_calls_attempted": sum(r[3]["model_calls_attempted"] for r in ordered),
        "automatic_retries": 0, "extraction_profile": extraction_profile(),
        "max_output_tokens_per_live_request": max(r[3]["max_output_tokens_per_live_request"] for r in ordered),
        "request_caps_by_paper": {d["paper_id"]: r[3]["max_output_tokens_per_live_request"] for d, r in zip(documents, ordered)},
        "repair_input_hashes_by_paper": {d["paper_id"]: {key: r[3][key] for key in
            ("repair_input_records_sha256", "repair_input_sources_sha256")} for d, r in zip(documents, ordered)},
        "prior_fresh_raw_responses_sha256": file_hash(prior_directory / "raw-responses.json"),
        "checked_answers_supplied": False, "prior_fresh_proposals_supplied": True,
        "retention_rule": "polymer identity only; no application or completeness threshold"}
    combined_raw = {"mode": "live_model_revision", "responses": [r[0] for r in ordered], "traces": [r[1] for r in ordered]}
    combined_freeze = {**freezes[-1], "freeze_kind": "verified_revision_capture_freeze_aggregation",
        "note": "Individual pre-request freezes are preserved. This combined receipt was assembled after the calls.",
        "source_capture_freezes": freezes,
        "expected_user_prompt_sha256": {d["paper_id"]: r[1]["request_prompt_sha256"] for d, r in zip(documents, ordered)}}
    write_outputs([r[2] for r in ordered], documents, output_directory, metadata, additional_outputs={
        "raw-responses.json": combined_raw, "pre-run-freeze.json": combined_freeze,
        "capture-receipts.json": {"captures": receipts, "completed_results_preserved_exactly": True,
                                  "assembly_model_calls": 0, "mode": "live_model_revision"}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    run_mode = parser.add_mutually_exclusive_group(required=True)
    run_mode.add_argument("--run-dir", type=Path)
    run_mode.add_argument("--assemble-to", type=Path,
                          help="Combine completed revision captures into a new directory before verification; no model calls.")
    parser.add_argument("--baseline-dir", type=Path,
                        help="Previous fresh extraction; defaults to the preserved published 6 November run.")
    parser.add_argument("--capture-dirs", nargs="+", type=Path,
                        help="Original completed per-paper capture directories for independent hash checks.")
    parser.add_argument("--mode", choices=("fresh", "revision"), default="fresh",
                        help="Fresh source-only extraction, or explicitly labeled revision of new proposals.")
    parser.add_argument("--prior-run-dir", type=Path,
                        help="Required for revision: saved fresh proposals used by the model, never checked answers.")
    parser.add_argument("--historical-code-dir", type=Path,
                        help="Optional frozen validation/repair source files under repository-relative paths for historical fresh capture checks.")
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="A new directory; existing results are never overwritten.")
    parser.add_argument("--include-baseline-revalidation", action="store_true",
                        help="Also check unchanged old raw responses with current validation, making zero model calls.")
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repository))
    from polymer_cards_lib.evaluation import evaluate_run
    from polymer_cards_lib.evidence_spans import CATALOG_VERSION, build_span_catalog, resolve_span
    from polymer_cards_lib.io import read_json, parse_json
    from polymer_cards_lib.prompt import build_user_prompt, extraction_profile
    from polymer_cards_lib.validation import build_cards
    from polymer_cards_lib import validation as current_validation

    if args.out_dir.exists():
        raise FileExistsError("Choose a new output directory; no previous evaluation will be overwritten")
    baseline_dir = args.baseline_dir or repository / "examples/polymer_cards/fresh_run_2026-11-06"
    revision = args.mode == "revision"
    if revision != bool(args.prior_run_dir):
        raise ValueError("Revision requires --prior-run-dir; fresh mode must not receive prior proposals")
    if args.assemble_to:
        if not revision or not args.capture_dirs:
            raise ValueError("Assembly requires explicit revision mode, prior fresh run and per-paper capture directories")
        assemble_revision_captures(args.capture_dirs, args.prior_run_dir, args.assemble_to)
        args.run_dir = args.assemble_to
    baseline_receipt = read_json(Path(__file__).with_name("baseline-reference-freeze.json"))
    for filename, expected in baseline_receipt["reference_files"].items():
        if file_hash(repository / filename) != expected:
            raise ValueError("Frozen reference changed: " + filename)
    for filename, expected in baseline_receipt["baseline_files"].items():
        if file_hash(baseline_dir / filename) != expected:
            raise ValueError("Previous fresh baseline changed: " + filename)

    run = read_json(args.run_dir / "cards.json")
    raw = read_json(args.run_dir / "raw-responses.json")
    sources = read_json(args.run_dir / "sources.json")["documents"]
    freeze = read_json(args.run_dir / "pre-run-freeze.json")
    metadata = run["run_metadata"]
    expected_mode = "live_model_revision" if revision else "live_model_extraction"
    if (metadata["mode"] != expected_mode or raw["mode"] != expected_mode
            or metadata["run_complete"] is not True):
        raise ValueError("Expected the explicitly selected completed extraction/revision mode, not a partial capture")
    profile = extraction_profile()
    if metadata["extraction_profile"] != profile or freeze["extraction_profile"] != profile:
        raise ValueError("The current extraction profile does not match the saved capture")
    by_paper = {document["paper_id"]: document for document in sources}
    results = {result["paper_id"]: result for result in run["results"]}
    responses = {response["paper_id"]: response for response in raw["responses"]}
    traces = {trace["paper_id"]: trace for trace in raw["traces"]}
    if (len(by_paper) != len(sources) or len(results) != len(run["results"])
            or len(responses) != len(raw["responses"]) or len(traces) != len(raw["traces"])
            or not (set(by_paper) == set(results) == set(responses) == set(traces))):
        raise ValueError("Documents, responses, traces and validated results must have unique matching paper IDs")
    baseline = read_json(baseline_dir / "cards.json")
    baseline_sources = read_json(baseline_dir / "sources.json")["documents"]
    if ({d["paper_id"]: d["chunks"] for d in baseline_sources}
            != {d["paper_id"]: d["chunks"] for d in sources}):
        raise ValueError("The original source snapshot differs from the previous fresh run")
    prior_responses, prior_catalogs = {}, {}
    if revision:
        prior_raw = read_json(args.prior_run_dir / "raw-responses.json")
        if prior_raw["mode"] != "live_model_extraction":
            raise ValueError("Revision proposals must come from the separately saved fresh stage")
        prior_responses = {response["paper_id"]: response for response in prior_raw["responses"]}
        prior_sources = read_json(args.prior_run_dir / "sources.json")["documents"]
        if (len(prior_responses) != len(prior_raw["responses"]) or set(prior_responses) != set(by_paper)
                or {d["paper_id"]: d["chunks"] for d in prior_sources}
                != {d["paper_id"]: d["chunks"] for d in sources}):
            raise ValueError("Revision prior papers or original sources differ")
        prior_freeze = read_json(args.prior_run_dir / "pre-run-freeze.json")
        for item in prior_freeze.get("source_capture_freezes", [prior_freeze]):
            keys = list(item["expected_user_prompt_sha256"])
            if len(keys) != 1 or keys[0] in prior_catalogs:
                raise ValueError("Prior fresh catalog freeze is missing or ambiguous")
            prior_catalogs[keys[0]] = item["source_span_catalog"]

    catalogs = {paper: build_span_catalog(document) for paper, document in by_paper.items()}
    globally_known_ids = {span["span_id"]: (paper, span["chunk_id"])
                          for paper, entries in catalogs.items() for span in entries}
    frozen_papers = set()
    request_checks = []
    historical_files = {}
    historical_validation = None
    source_freezes = freeze.get("source_capture_freezes", [freeze])
    for record in source_freezes:
        if (record["checked_references_supplied_to_model"] is not False
                or record["previous_model_responses_supplied"] is not revision):
            raise ValueError("Checked-answer or previous-proposal declaration does not match the selected mode")
        for filename, expected in record["source_files_sha256"].items():
            if file_hash(repository / filename) != expected:
                allowed = {"polymer_cards_lib/validation.py", "polymer_cards_lib/repair.py"}
                historic = args.historical_code_dir / filename if args.historical_code_dir else None
                if (revision or filename not in allowed or historic is None
                        or not historic.is_file() or file_hash(historic) != expected):
                    raise ValueError("Code or reference changed after request freeze: " + filename)
                historical_files[filename] = {"sha256": expected, "purpose": "historical_capture_policy"}
                if filename == "polymer_cards_lib/validation.py" and historical_validation is None:
                    spec = importlib.util.spec_from_file_location("polymer_cards_historical_validation", historic)
                    historical_validation = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(historical_validation)
                    for name in ("_literal", "_text"):
                        if inspect.getsource(getattr(historical_validation, name)) != inspect.getsource(getattr(current_validation, name)):
                            raise ValueError("Frozen evaluation literal/text semantics differ from current code")
        if record["extraction_profile"] != profile:
            raise ValueError("Per-capture extraction profile differs")
        expected_requests = record["expected_user_prompt_sha256"]
        if len(expected_requests) != 1:
            raise ValueError("Each source-span request freeze must identify its one paper")
        paper, expected_request = next(iter(expected_requests.items()))
        if paper in frozen_papers or paper not in by_paper:
            raise ValueError("Missing or repeated source-span request freeze")
        frozen_papers.add(paper)
        catalog_origin = "this_request_prefreeze"
        catalog_record = record.get("source_span_catalog")
        if catalog_record is None and revision:
            # Revision freezes bind the actual request hash and original
            # sources, but do not all repeat a separate catalog digest. Verify
            # its unchanged fresh-stage digest rather than inventing one.
            catalog_record = prior_catalogs.get(paper)
            catalog_origin = "prior_fresh_prefreeze_and_actual_revision_request_reconstruction"
        if catalog_record != {"version": CATALOG_VERSION, "count": len(catalogs[paper]),
                              "sha256": canonical_hash(catalogs[paper])}:
            raise ValueError("Source span catalog differs from pre-request freeze: " + paper)
        trace = traces[paper]
        if revision:
            from polymer_cards_lib.repair import build_revision_user_prompt
            prompt = build_revision_user_prompt(by_paper[paper], prior_responses[paper])
            if (trace.get("request_mode") != "source_grounded_model_revision"
                    or trace.get("previous_response_sha256") != canonical_hash(prior_responses[paper])):
                raise ValueError("Revision trace does not bind the separately saved prior fresh proposal")
        else:
            prompt = build_user_prompt(by_paper[paper])
            if "previous_response_sha256" in trace:
                raise ValueError("Fresh capture must not be conditioned on previous model proposals")
        actual_request = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if (trace["request_prompt_sha256"] != expected_request or actual_request != expected_request
                or trace["extraction_profile"] != profile or trace["finish_reason"] != "stop"):
            raise ValueError("Saved request does not reconstruct in the declared source-grounded mode: " + paper)
        if parse_json(trace["raw_response_text"]) != responses[paper]:
            raise ValueError("Provider raw JSON differs from the saved response: " + paper)
        rebuild = historical_validation.build_cards if historical_validation is not None else build_cards
        if rebuild(by_paper[paper], responses[paper]) != results[paper]:
            raise ValueError("Rebuilt validation differs; any post-run revalidation must be disclosed separately")
        request_checks.append({"paper_id": paper, "user_prompt_sha256": actual_request,
                               "source_span_catalog_count": len(catalogs[paper]),
                               "source_span_catalog_sha256": canonical_hash(catalogs[paper]),
                               "catalog_digest_origin": catalog_origin,
                               "raw_json_and_validation_rebuild_match": True})
    if frozen_papers != set(by_paper):
        raise ValueError("Not every paper has a verified source-only request freeze")

    capture_checks = []
    if args.capture_dirs:
        receipts = read_json(args.run_dir / "capture-receipts.json")["captures"]
        receipt_by_name = {record["capture_directory"]: record for record in receipts}
        if len(receipt_by_name) != len(receipts) or set(receipt_by_name) != {d.name for d in args.capture_dirs}:
            raise ValueError("Capture directories must exactly match the assembly receipt")
        observed = set()
        for directory in args.capture_dirs:
            record = receipt_by_name[directory.name]
            for filename, key in (("cards.json", "cards_sha256"), ("sources.json", "sources_sha256"),
                                  ("raw-responses.json", "raw_responses_sha256"),
                                  ("pre-run-freeze.json", "freeze_sha256")):
                if file_hash(directory / filename) != record[key]:
                    raise ValueError("Original capture hash mismatch: " + str(directory / filename))
            capture_raw = read_json(directory / "raw-responses.json")
            capture_cards = read_json(directory / "cards.json")
            capture_results = capture_cards["results"]
            if revision:
                capture_metadata = capture_cards["run_metadata"]
                capture_freeze = read_json(directory / "pre-run-freeze.json")
                verified_inputs = {}
                for kind in ("records", "sources"):
                    key = "repair_input_" + kind + "_sha256"
                    expected = capture_metadata[key]
                    if capture_freeze["prior_" + kind + "_sha256"] != expected:
                        raise ValueError("CLI prior input differs from pre-request revision freeze")
                    candidates = [path for path in directory.rglob("*.json")
                                  if path.is_file() and not path.name.startswith("._")
                                  and file_hash(path) == expected]
                    if not candidates:
                        raise ValueError("Original revision input is unavailable or changed: " + kind)
                    verified_inputs[kind] = read_json(candidates[0])
                inputs = verified_inputs["records"].get("responses", [])
                if not inputs or any(item != prior_responses.get(item.get("paper_id")) for item in inputs):
                    raise ValueError("CLI revision record input differs from the separately saved fresh proposals")
                input_sources = verified_inputs["sources"].get("documents", [])
                if not input_sources or any(item["chunks"] != by_paper[item["paper_id"]]["chunks"] for item in input_sources):
                    raise ValueError("CLI revision source input differs from the original paper snapshot")
            for response in capture_raw["responses"]:
                paper = response["paper_id"]
                if paper in observed or response != responses[paper]:
                    raise ValueError("A response was repeated or changed during assembly")
                observed.add(paper)
            for trace in capture_raw["traces"]:
                if trace != traces[trace["paper_id"]]:
                    raise ValueError("A trace changed during assembly")
            for result in capture_results:
                if result != results[result["paper_id"]]:
                    raise ValueError("A validated result changed during assembly")
            capture_checks.append({"capture_directory": directory.name, "hashes_verified": True})
        if observed != set(by_paper):
            raise ValueError("Original captures do not cover every assembled paper")

    reference_paths = {
        "conditions": repository / "examples/polymer_cards/condition_reference_2026-11-06/reference.json",
        "focused": repository / "examples/polymer_cards/identity_reference_2026-10-30.json",
        "pei": repository / "examples/polymer_cards/checked_pei_2026-10-30/evaluation-cases.json",
    }
    outputs = {}
    for name, path in reference_paths.items():
        reference = read_json(path)
        outputs[name + "-evaluation.json"] = evaluate_run(run, reference)
        outputs["baseline-" + name + "-evaluation.json"] = evaluate_run(baseline, reference)

    raw_counts, raw_per_paper, invalid_selections = Counter(), [], []
    for paper, response in responses.items():
        counts, unique = Counter(), set()
        for path, ref in evidence_refs(response):
            counts["evidence_reference_occurrences"] += 1
            unique.add(canonical_hash(ref))
            reason = None
            if set(ref) == {"chunk_id", "span_id"}:
                counts["span_selection_occurrences"] += 1
                try:
                    resolve_span(by_paper[paper], ref["chunk_id"], ref["span_id"], catalog=catalogs[paper])
                except ValueError:
                    chunk_ids = {chunk["chunk_id"] for chunk in by_paper[paper]["chunks"]}
                    span_id, chunk_id = ref["span_id"], ref["chunk_id"]
                    if not isinstance(span_id, str) or not isinstance(chunk_id, str):
                        reason = "invalid_reference_id_type"
                    elif chunk_id not in chunk_ids:
                        reason = "unknown_source_chunk"
                    elif span_id in globally_known_ids:
                        bound_paper, bound_chunk = globally_known_ids[span_id]
                        reason = "cross_paper_selection" if bound_paper != paper else "cross_chunk_selection"
                    else:
                        reason = "unknown_or_stale_span_id"
                else:
                    counts["valid_span_selection_occurrences"] += 1
            elif "quote" in ref and "span_id" not in ref:
                counts["legacy_quote_reference_occurrences"] += 1
                reason = "legacy_quote_reference_in_v4_response"
            else:
                counts["malformed_or_spoofed_reference_occurrences"] += 1
                reason = "invalid_v4_reference_shape"
            if reason:
                counts["invalid_or_non_v4_reference_occurrences"] += 1
                invalid_selections.append({"paper_id": paper, "path": path, "reason": reason,
                                           "reference": ref})
        counts["unique_reference_proposals"] = len(unique)
        raw_counts.update(counts)
        raw_per_paper.append({"paper_id": paper, **dict(counts)})

    retained_counts = Counter()
    for paper, result in results.items():
        chunks = {chunk["chunk_id"]: chunk for chunk in by_paper[paper]["chunks"]}
        for _, ref in evidence_refs(result["cards"]):
            retained_counts["evidence_reference_occurrences"] += 1
            if ref.get("evidence_status") != "quote_matched" or ref.get("paper_id") != paper:
                raise ValueError("Retained evidence lacks matched original source identity")
            if ref.get("evidence_origin") != "source_span_selection":
                raise ValueError("Retained V4 evidence is not declared source-span selection")
            selected = resolve_span(by_paper[paper], ref["chunk_id"], ref["span_id"], catalog=catalogs[paper])
            for key in ("quote", "source_start", "source_end", "evidence_origin", "catalog_version"):
                if ref.get(key) != selected[key]:
                    raise ValueError("Retained span provenance differs from the source: " + key)
            start, end = ref["source_start"], ref["source_end"]
            if (not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int)
                    or isinstance(end, bool) or ref["quote"] != chunks[ref["chunk_id"]]["text"][start:end]):
                raise ValueError("Retained original source slice/offset mismatch")
            retained_counts["source_exact_span_occurrences"] += 1

    normal = lambda text: " ".join(unicodedata.normalize("NFC", text).split())
    baseline_raw = read_json(baseline_dir / "raw-responses.json")
    baseline_quote_counts = Counter()
    for response in baseline_raw["responses"]:
        paper = response["paper_id"]
        chunk_text = {chunk["chunk_id"]: chunk["text"] for chunk in by_paper[paper]["chunks"]}
        for _, ref in evidence_refs(response):
            if "quote" in ref and "span_id" not in ref:
                baseline_quote_counts["legacy_quote_reference_occurrences"] += 1
                if ref["chunk_id"] in chunk_text and normal(ref["quote"]) in normal(chunk_text[ref["chunk_id"]]):
                    baseline_quote_counts["model_authored_quote_occurrences_matching_source"] += 1

    outputs["evidence-check.json"] = {
        "catalog_version": CATALOG_VERSION, "raw_reference_counts": dict(raw_counts),
        "raw_reference_counts_by_paper": raw_per_paper,
        "invalid_or_non_v4_raw_selections": invalid_selections,
        "retained_reference_counts": dict(retained_counts),
        "all_retained_provenance_offsets_and_slices_verified": True,
        "v4_raw_references_all_closed_span_selections": raw_counts["span_selection_occurrences"] == raw_counts["evidence_reference_occurrences"],
        "legacy_model_quote_authorship_metric": "not_applicable_to_source_span_selection",
        "baseline_model_authored_quote_counts": dict(baseline_quote_counts),
        "limits": ["Server retrieval of exact source text is not evidence that the model copied a quotation verbatim.",
                   "Valid IDs and exact source slices do not prove scientific attribution or completeness.",
                   "Reference occurrences count repetitions; they are not independent scientific facts."]}
    outputs["verification.json"] = {
        "verification_kind": "saved_source_span_run_and_unchanged_reference_verification",
        "baseline_fresh_run_hashes_verified": True, "all_three_reference_hashes_unchanged": True,
        "all_original_source_chunks_equal_previous_fresh_snapshot": True,
        "all_actual_user_requests_reconstructed": True, "all_raw_provider_json_unchanged": True,
        "all_validated_results_rebuilt_exactly": True, "source_only_request_freezes": request_checks,
        "original_capture_hash_checks": capture_checks,
        "capture_files_independently_available_and_verified": bool(args.capture_dirs),
        "verified_mode": expected_mode, "historical_code_files_used": historical_files,
        "extraction_profile": profile, "model_calls_made_by_verifier": 0,
        "checked_answers_supplied_to_extraction": False,
        "prior_proposals_supplied_to_extraction": revision,
        "revision_prior_fresh_raw_sha256": file_hash(args.prior_run_dir / "raw-responses.json") if revision else None}
    usage = {key: sum(trace["usage"][key] for trace in raw["traces"])
             for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
    outputs["comparison.json"] = {
        "comparison_kind": "previous_fresh_vs_source_grounded_revision" if revision else "previous_fresh_vs_fresh_source_span_extraction",
        "baseline_mode": baseline["run_metadata"]["mode"], "new_run_mode": metadata["mode"],
        "baseline_metrics": metrics(baseline), "new_run_metrics": metrics(run),
        "baseline_selected_checks": outcomes(outputs["baseline-conditions-evaluation.json"]),
        "new_run_selected_checks": outcomes(outputs["conditions-evaluation.json"]),
        "other_frozen_baseline_checks": {name: outcomes(outputs["baseline-" + name + "-evaluation.json"])
                                          for name in ("focused", "pei")},
        "other_frozen_new_run_checks": {name: outcomes(outputs[name + "-evaluation.json"])
                                       for name in ("focused", "pei")},
        "reference_sha256": {name: file_hash(path) for name, path in reference_paths.items()},
        "completed_model_calls_in_capture": metadata["model_calls"],
        "model_calls_attempted_in_capture": metadata["model_calls_attempted"],
        "successful_call_returned_usage": usage,
        "model_calls_made_by_comparison": 0,
        "limits": ["Selected-case matches are not overall scientific accuracy or exhaustive coverage.",
                   "A source-grounded revision uses prior fresh proposals and must not be reported as independent fresh extraction." if revision
                   else "The previous fresh run and this source-span run have different extraction mechanisms.",
                   "Source-span retrieval integrity must not be reported as perfect model quotation fidelity.",
                   "Card and review counts can change with record granularity and validation behavior."]}
    if args.include_baseline_revalidation:
        old_responses = {response["paper_id"]: response for response in baseline_raw["responses"]}
        replay = {"results": [build_cards(document, old_responses[document["paper_id"]]) for document in sources]}
        outputs["baseline-raw-revalidation.json"] = {
            "mode": "automatic_revalidation_of_unchanged_legacy_raw_responses", "additional_model_calls": 0,
            "raw_responses_sha256": file_hash(baseline_dir / "raw-responses.json"),
            "metrics": metrics(replay),
            "selected_evaluation": evaluate_run(replay, read_json(reference_paths["conditions"])),
            "note": "Separate code-only check; old quoted references remain strict and are not repaired into source-span selections."}
    serialized = {filename: json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
                  for filename, value in outputs.items()}
    args.out_dir.mkdir(parents=True, exist_ok=False)
    for filename, content in serialized.items():
        (args.out_dir / filename).write_text(content)
    print(json.dumps(outputs["comparison.json"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
