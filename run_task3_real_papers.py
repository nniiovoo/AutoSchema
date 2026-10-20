"""Reproduce the curated four-paper Task 3 replay; no models or network calls."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from select_candidates import _read, main as selection_main


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "examples/task3/real_papers"


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs/task3_real_papers")
    args = parser.parse_args(argv)
    out = args.out_dir.resolve()
    # Generated diagnostic inputs must never replace the reviewed fixtures.
    if out == FIXTURES or FIXTURES in out.parents or out in FIXTURES.parents:
        parser.error("Choose an output directory separate from the reviewed fixtures.")
    bundle = _read(FIXTURES / "input.json")
    expected = _read(FIXTURES / "expected.json")
    diagnostics = _read(FIXTURES / "diagnostic_profiles.json")
    result_names = ("selection.json", "selection.csv", "followups.json")
    destinations = [out / "manifest.json"] + [out / "shared" / name for name in result_names]
    destinations += [out / d["profile"]["profile_id"] / name for d in diagnostics
                     for name in ("input.json", *result_names)]
    for path in destinations:
        if (out not in path.resolve().parents
                or any(p.is_symlink() for p in (path, *path.parents) if out in p.parents)):
            parser.error("Output files must stay within the output directory without symlink redirection.")
    if bundle["profile"] != _read(FIXTURES / "profile.json"):
        raise ValueError("The frozen profile and input profile differ.")
    status = selection_main(["--input", str(FIXTURES / "input.json"), "--reviews", str(FIXTURES / "reviews.json"),
                             "--out-dir", str(out / "shared")])
    if status:
        return status
    records = _read(out / "shared/selection.json")
    actual = {r["candidate_id"]: {"decision": r["decision"],
              "criteria": {c["criterion_id"]: c["decision"] for c in r["criteria"]}} for r in records}
    wanted = {key: {k: value[k] for k in ("decision", "criteria")} for key, value in expected["shared"].items()}
    mismatches = [] if actual == wanted else ["shared candidate/criterion decisions differ from declared expectations"]
    diagnostic_results = {}
    for diagnostic in diagnostics:
        profile = diagnostic["profile"]
        folder = out / profile["profile_id"]
        folder.mkdir(parents=True, exist_ok=True)
        diagnostic_bundle = {"profile": profile, "sources": bundle["sources"], "candidates": [
            next(c for c in bundle["candidates"] if c["candidate_id"] == diagnostic["candidate_id"])]}
        _write(folder / "input.json", diagnostic_bundle)
        status = selection_main(["--input", str(folder / "input.json"), "--reviews", str(FIXTURES / "reviews.json"),
                                 "--out-dir", str(folder)])
        if status:
            return status
        record = _read(folder / "selection.json")[0]
        result = {"decision": record["decision"], "criterion_reason": record["criteria"][0]["reason"]}
        diagnostic_results[profile["profile_id"]] = result
        wanted_diagnostic = {key: expected["diagnostics"][profile["profile_id"]][key] for key in result}
        if result != wanted_diagnostic:
            mismatches.append(profile["profile_id"] + " differs from declared expectation")
    evidence_counts = Counter(e["status"] for r in records for e in r["evidence"]["observations"])
    if len(records) != 4 or evidence_counts != {"supported_as_reported": 10}:
        mismatches.append("Expected four reviewed candidates and ten mechanically accepted supplied review records")
    files = [FIXTURES / name for name in (
        "input.json", "reviews.json", "profile.json", "expected.json", "diagnostic_profiles.json")]
    files += [ROOT / p for p in (
        "run_task3_real_papers.py", "select_candidates.py", "selection_lib/screening.py")]
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    manifest = {
        "run_kind": "assistant_curated_replay_not_extraction_accuracy_or_experimental_validation",
        "git_head": revision.stdout.strip() if revision.returncode == 0 else None,
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "shared_candidates": len(records), "shared_decisions": dict(Counter(r["decision"] for r in records)),
        "supplied_evidence_check_statuses": dict(evidence_counts),
        "shared_required_criterion_decisions": dict(Counter(c["decision"] for r in records for c in r["criteria"])),
        "shared_pending_criterion_actions": sum(len(r["followups"]) for r in records),
        "separate_diagnostics": diagnostic_results, "expectation_mismatches": mismatches,
        "limitations": "Purposive papers; analyst requirements; supplied assistant semantic reviews. Ten accepted records are not ten independently verified scientific claims or extraction accuracy trials.",
    }
    _write(out / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
