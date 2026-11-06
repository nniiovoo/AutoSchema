"""Combine completed fresh requests without editing their responses or retrying."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, nargs="+", required=True)
    parser.add_argument("--papers", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--auth-failure", type=Path)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repository))
    from polymer_cards_lib.io import parse_json
    from polymer_cards_lib.prompt import build_user_prompt, extraction_profile
    from polymer_cards_lib.render import write_outputs
    from polymer_cards_lib.sources import load_documents
    from polymer_cards_lib.validation import build_cards

    read = lambda path: parse_json(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    documents = load_documents(args.papers)
    by_id = {d["paper_id"]: d for d in documents}
    found, receipts, freezes = {}, [], []
    attempts = 0
    for directory in args.captures:
        raw, cards = read(directory / "raw-responses.json"), read(directory / "cards.json")
        supplied = {d["paper_id"]: d for d in read(directory / "sources.json")["documents"]}
        metadata, freeze = cards["run_metadata"], read(directory / "pre-run-freeze.json")
        assert metadata["mode"] == raw["mode"] == "live_model_extraction"
        assert freeze["extraction_profile"] == extraction_profile()
        assert freeze["checked_references_supplied_to_model"] is False
        assert freeze["previous_model_responses_supplied"] is False
        attempts += metadata["model_calls_attempted"]
        results = {r["paper_id"]: r for r in cards["results"]}
        traces = {t["paper_id"]: t for t in raw["traces"]}
        for response in raw["responses"]:
            key = response["paper_id"]
            assert key in by_id and key not in found, "Missing/duplicated fresh request identity"
            assert supplied[key]["chunks"] == by_id[key]["chunks"], "Source snapshot changed"
            trace = traces[key]
            assert trace["finish_reason"] == "stop"
            assert trace["extraction_profile"] == extraction_profile()
            assert "previous_response_sha256" not in trace
            assert parse_json(trace["raw_response_text"]) == response
            assert hashlib.sha256(build_user_prompt(by_id[key]).encode()).hexdigest() == trace["request_prompt_sha256"]
            checked = build_cards(by_id[key], response)
            assert checked == results[key], "Validation changed after capture; disclose revalidation separately"
            found[key] = (response, trace, checked, metadata["max_output_tokens_per_live_request"])
        receipts.append({"capture_directory": directory.name, "mode": metadata["mode"],
                         "raw_responses_sha256": sha(directory / "raw-responses.json"),
                         "cards_sha256": sha(directory / "cards.json"),
                         "sources_sha256": sha(directory / "sources.json"),
                         "freeze_sha256": sha(directory / "pre-run-freeze.json"),
                         "request_cap": metadata["max_output_tokens_per_live_request"],
                         "attempted_calls": metadata["model_calls_attempted"],
                         "completed_calls": metadata["model_calls"],
                         "failed_paper_id": metadata.get("failed_paper_id"),
                         "model": metadata["model"], "provider": metadata["provider"]})
        freezes.append(freeze)
    assert set(found) == set(by_id), "Not every requested paper has one completed fresh result"
    assert len({(r["provider"], r["model"]) for r in receipts}) == 1
    current = freezes[-1]
    for filename, expected in current["source_files_sha256"].items():
        assert sha(repository / filename) == expected, "Current code/reference differs from final request freeze"
    for earlier in freezes[:-1]:
        changed = [name for name, expected in earlier["source_files_sha256"].items()
                   if current["source_files_sha256"].get(name) != expected]
        assert set(changed) <= {"extract_polymer_cards.py"}, "Scientific processing changed across batches"
    assert not args.out_dir.exists(), "Never replace an earlier capture"
    ordered = [found[d["paper_id"]] for d in documents]
    raw = {"mode": "live_model_extraction", "responses": [r[0] for r in ordered], "traces": [r[1] for r in ordered]}
    metadata = {"contract_version": "polymer-cards-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "mode": "live_model_extraction", "run_kind": "assembled_fresh_source_only_requests",
                "assembly_note": "Completed fresh responses from separate bounded batches; no response, quotation, sample link or value manually edited.",
                "provider": receipts[0]["provider"], "model": receipts[0]["model"],
                "source_manifest_sha256": sha(args.papers), "model_calls": len(ordered),
                "model_calls_attempted": attempts, "run_complete": True, "papers_requested": len(documents),
                "papers_completed": len(ordered), "max_output_tokens_per_live_request": max(r[3] for r in ordered),
                "request_caps_by_paper": {d["paper_id"]: r[3] for d, r in zip(documents, ordered)},
                "automatic_retries": 0, "extraction_profile": extraction_profile(),
                "checked_answers_supplied": False, "previous_responses_supplied": False,
                "retention_rule": "polymer identity only; no application or completeness threshold",
                "semantic_validation": "Quote containment is mechanically checked; semantic attribution remains for review.",
                "failed_request_usage": "Truncated Chen request usage was not persisted and is excluded from successful-call totals."}
    extras = {"raw-responses.json": raw,
              "capture-receipts.json": {"captures": receipts, "completed_results_preserved_exactly": True,
                                        "only_cli_token_budget_bound_changed_between_batches": True},
              "pre-run-freeze.json": {**current, "freeze_kind": "verified_capture_freeze_aggregation",
                  "note": "Individual pre-request freezes are preserved separately. This receipt verifies their combination; it was not created before the first Pei request.",
                  "source_capture_freezes": freezes,
                  "expected_user_prompt_sha256": {d["paper_id"]: r[1]["request_prompt_sha256"] for d, r in zip(documents, ordered)}}}
    if args.auth_failure:
        extras["authentication-failure.json"] = read(args.auth_failure)
        metadata["separate_authentication_requests_failed"] = extras["authentication-failure.json"]["model_requests_attempted"]
    write_outputs([r[2] for r in ordered], documents, args.out_dir, metadata, additional_outputs=extras)
    print("Combined", len(ordered), "completed fresh requests. No new model calls; raw responses unchanged.")


if __name__ == "__main__":
    main()
