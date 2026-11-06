"""Evaluate saved cards only; this script never makes model requests."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unicodedata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    repository = here.parents[2]
    sys.path.insert(0, str(repository))
    from polymer_cards_lib.evaluation import evaluate_run
    from polymer_cards_lib.prompt import build_user_prompt, extraction_profile

    read = lambda path: json.loads(path.read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    run, baseline = read(args.run_dir / "cards.json"), read(args.baseline_dir / "cards.json")
    sources = read(args.run_dir / "sources.json")["documents"]
    raw = read(args.run_dir / "raw-responses.json")
    freeze = read(args.run_dir / "pre-run-freeze.json")
    assert run["run_metadata"]["mode"] == "live_model_extraction", "Expected fresh extraction, not replay/revision"
    assert run["run_metadata"]["run_complete"] is True, "Cannot report a complete three-paper comparison for a partial run"
    assert freeze["checked_references_supplied_to_model"] is False
    assert freeze["previous_model_responses_supplied"] is False
    assert extraction_profile() == freeze["extraction_profile"], "Prompt/schema changed after the run freeze"
    for filename, expected in freeze["source_files_sha256"].items():
        assert digest(repository / filename) == expected, "Code/reference changed after freeze: " + filename
    trace_by_paper = {trace["paper_id"]: trace for trace in raw["traces"]}
    for document in sources:
        trace = trace_by_paper[document["paper_id"]]
        expected = hashlib.sha256(build_user_prompt(document).encode()).hexdigest()
        assert trace["request_prompt_sha256"] == expected == freeze["expected_user_prompt_sha256"][document["paper_id"]]
        assert trace["extraction_profile"] == freeze["extraction_profile"]
        assert trace["finish_reason"] == "stop"
        assert "previous_response_sha256" not in trace
    assert [json.loads(t["raw_response_text"]) for t in raw["traces"]] == raw["responses"]
    original_sources = read(args.baseline_dir / "sources.json")["documents"]
    assert [(d["paper_id"], d["chunks"]) for d in sources] == [(d["paper_id"], d["chunks"]) for d in original_sources]

    references = {
        "conditions": here / "reference.json",
        "focused": here.parent / "identity_reference_2026-10-30.json",
        "pei": here.parent / "checked_pei_2026-10-30/evaluation-cases.json",
    }
    assert digest(references["conditions"]) == read(here / "source-check.json")["reference_sha256"]
    outputs = {}
    for name, path in references.items():
        reference = read(path)
        outputs[name + "-evaluation.json"] = evaluate_run(run, reference)
        outputs["baseline-" + name + "-evaluation.json"] = evaluate_run(baseline, reference)

    normal = lambda text: " ".join(unicodedata.normalize("NFC", text).split())
    chunks = {(d["paper_id"], c["chunk_id"]): c for d in sources for c in d["chunks"]}
    evidence_occurrences = 0

    def visit(value, paper_id):
        nonlocal evidence_occurrences
        if isinstance(value, dict):
            if "chunk_id" in value and "quote" in value:
                assert value["evidence_status"] == "quote_matched"
                assert normal(value["quote"]) in normal(chunks[paper_id, value["chunk_id"]]["text"])
                evidence_occurrences += 1
            for child in value.values():
                visit(child, paper_id)
        elif isinstance(value, list):
            for child in value:
                visit(child, paper_id)

    for result in run["results"]:
        visit(result["cards"], result["paper_id"])

    def outcomes(evaluation):
        return {section: dict(Counter(case["status"] for case in evaluation[section]))
                for section in ("identities", "measurements", "conflicts")}

    def metrics(saved):
        result = Counter()
        for paper in saved["results"]:
            result["cards"] += len(paper["cards"])
            result["review_queue_records"] += len(paper["review_queue"])
            result["validation_flags"] += len(paper["validation_issues"])
            for card in paper["cards"]:
                result["declared_" + str(card.get("identity_kind"))] += 1
                result["accepted_property_items"] += len(card["properties"]["items"])
                result["accepted_conflict_notes"] += len(card["properties"].get("conflicts", []))
        return dict(result)

    outputs["comparison.json"] = {
        "comparison_kind": "selected_source_reference_comparison",
        "baseline_mode": baseline["run_metadata"]["mode"],
        "fresh_mode": run["run_metadata"]["mode"],
        "baseline_metrics": metrics(baseline), "fresh_metrics": metrics(run),
        "baseline_selected_checks": outcomes(outputs["baseline-conditions-evaluation.json"]),
        "fresh_selected_checks": outcomes(outputs["conditions-evaluation.json"]),
        "frozen_baseline_checks": {name: outcomes(outputs["baseline-" + name + "-evaluation.json"]) for name in ("focused", "pei")},
        "frozen_fresh_checks": {name: outcomes(outputs[name + "-evaluation.json"]) for name in ("focused", "pei")},
        "reference_sha256": {name: digest(path) for name, path in references.items()},
        "successful_model_requests": run["run_metadata"]["model_calls"],
        "returned_token_usage": {key: sum(trace["usage"][key] for trace in raw["traces"])
                                 for key in ("prompt_tokens", "completion_tokens", "total_tokens")},
        "limits": ["These selected-case checks are not overall scientific accuracy or exhaustive recall.",
                   "The baseline was a revision conditioned on saved proposals; this run is fresh source-only extraction.",
                   "A source-linked unresolved conflict is preserved, not scientifically resolved.",
                   "Counts can change with record granularity and extraction variation."]}
    outputs["evidence-check.json"] = {
        "retained_evidence_reference_occurrences_matched": evidence_occurrences,
        "repeated_references_count_again": True,
        "all_recorded_user_request_hashes_reconstructed": True,
        "raw_provider_json_equals_saved_responses": True,
        "original_source_snapshot_unchanged": True,
        "code_and_reference_freeze_hashes_verified": True,
        "checked_answers_or_prior_records_supplied": False,
        "note": "Matching source quotation occurrences are not independently verified scientific claims."}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, value in outputs.items():
        target = args.out_dir / name
        if target.exists():
            raise FileExistsError("Evaluation outputs must not overwrite a previous comparison: " + str(target))
    for name, value in outputs.items():
        (args.out_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(outputs["comparison.json"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
