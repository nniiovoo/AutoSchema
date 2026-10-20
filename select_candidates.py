"""Run Task 3 selection on source-linked observations, without model or API calls."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

from selection_lib.screening import screen_candidate


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate JSON key: " + key)
        out[key] = value
    return out


def _invalid_number(value):
    raise ValueError("Invalid JSON number: " + value)


def _finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        _invalid_number(token)
    return value


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=_invalid_number, parse_float=_finite_float)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Task 3: check evidence, screen candidates for a stated use, and queue evidence gaps.")
    parser.add_argument("--input", type=Path, required=True, help="JSON bundle containing profile, sources and atomic candidates.")
    parser.add_argument("--reviews", type=Path, help="Separate source/semantic review receipts. Without these, observations need review.")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = _read(args.input)
        reviews = _read(args.reviews) if args.reviews else []
        if not isinstance(bundle, dict) or not isinstance(bundle.get("candidates"), list) or not bundle["candidates"]:
            raise ValueError("Input must contain a nonempty candidates list, plus profile and sources.")
        ids = [c.get("candidate_id") if isinstance(c, dict) else None for c in bundle["candidates"]]
        if any(not isinstance(i, str) or not i.strip() for i in ids) or len(ids) != len(set(ids)):
            raise ValueError("Candidate IDs must be present and unique.")
        records = [screen_candidate(c, bundle.get("profile"), bundle.get("sources"), reviews)
                   for c in bundle["candidates"]]
        outputs = [args.out_dir / name for name in ("selection.json", "selection.csv", "followups.json")]
        inputs = {p.resolve() for p in (args.input, args.reviews) if p is not None}
        if any(path.resolve() in inputs for path in outputs):
            raise ValueError("Output paths must not overwrite input or review files.")
        args.out_dir.mkdir(parents=True, exist_ok=True)
        outputs[0].write_text(json.dumps(records, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        gaps = [{"candidate_id": r["candidate_id"], "profile_id": r["profile_id"], **g}
                for r in records for g in r["followups"]]
        outputs[2].write_text(json.dumps(gaps, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        with outputs[1].open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["candidate_id", "paper_id", "sample_id", "profile_id", "decision", "evidence_status", "pending_actions"])
            for r in records:
                writer.writerow([r["candidate_id"], r["paper_id"], r["sample_id"], r["profile_id"], r["decision"], r["evidence"]["status"], len(r["followups"])])
        print(f"Screened {len(records)} candidates; {len(gaps)} pending actions. Results: {args.out_dir}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Task 3 input/output error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
