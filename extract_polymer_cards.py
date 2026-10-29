"""Extract or replay polymer entities into source-linked six-field cards."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from polymer_cards_lib.io import read_json
from polymer_cards_lib.sources import load_documents


OUTPUT_NAMES = ("cards.json", "cards.jsonl", "cards.html", "cards.md", "audit.json", "sources.json", "raw-responses.json")


def _bounded_int(value):
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("Value must be positive")
    return result


def _protect_inputs(args, documents):
    protected = {p.resolve() for p in (args.papers, args.records, args.env_file) if p is not None}
    protected.update(Path(s["path"]).resolve() for doc in documents for s in doc["source_files"])
    for name in OUTPUT_NAMES:
        output = args.out_dir / name
        if output.is_symlink():
            raise ValueError("Output files must not be symbolic links")
        if output.exists() and not output.is_file():
            raise ValueError("Output paths must be regular files, not directories or special files")
        if output.resolve() in protected:
            raise ValueError("Outputs must not overwrite the source manifest, evidence, records or local model configuration")
        if output.exists() and any(p.exists() and output.samefile(p) for p in protected):
            raise ValueError("Output files must not be hard links to source or local configuration files")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Keep polymer entities and build six-field cards with original evidence; no application-performance filtering.")
    parser.add_argument("--papers", type=Path, required=True, help="Paper/source manifest with local PDF, JATS XML, text or JSON source excerpts.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--records", type=Path, help="Replay supplied responses JSON through source validation without model/API calls.")
    parser.add_argument("--env-file", type=Path, help="Existing local model environment configuration; never copied into outputs.")
    parser.add_argument("--max-papers", type=_bounded_int, default=3, help="Maximum papers to process; default3 keeps the pilot bounded.")
    parser.add_argument("--max-output-tokens", type=_bounded_int, default=10000, help="Bound each live response, maximum24000.")
    args = parser.parse_args(argv)
    try:
        if args.max_output_tokens > 24000:
            raise ValueError("Maximum output token limit is24000 per request")
        documents = load_documents(args.papers)
        if len(documents) > args.max_papers:
            raise ValueError("Manifest exceeds --max-papers; choose a smaller manifest or explicitly raise the limit")
        _protect_inputs(args, documents)
        from polymer_cards_lib.validation import build_cards
        from polymer_cards_lib.render import write_outputs
        metadata = {"contract_version": "polymer-cards-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "mode": "curated_record_replay" if args.records else "live_model_extraction",
                    "retention_rule": "polymer identity only; no application or completeness threshold",
                    "semantic_validation": "Original quote containment is mechanically checked; chemical interpretation and attribution still need source review.",
                    "source_manifest_sha256": hashlib.sha256(args.papers.read_bytes()).hexdigest(),
                    "max_output_tokens_per_live_request": args.max_output_tokens}
        if args.records:
            data = read_json(args.records)
            if not isinstance(data, dict) or not isinstance(data.get("responses"), list):
                raise ValueError("Replay file must contain a responses list")
            responses = data["responses"]
            by_paper = {}
            for response in responses:
                if not isinstance(response, dict) or not isinstance(response.get("paper_id"), str) or response["paper_id"] in by_paper:
                    raise ValueError("Replay responses need unique paper IDs")
                by_paper[response["paper_id"]] = response
            if set(by_paper) != {d["paper_id"] for d in documents}:
                raise ValueError("Replay response papers must exactly match the source manifest")
            responses = [by_paper[d["paper_id"]] for d in documents]
            metadata["model_calls"] = 0
            metadata["input_records_sha256"] = hashlib.sha256(args.records.read_bytes()).hexdigest()
            metadata["replay_note"] = "Supplied records are inputs, not newly generated model extraction. See their provenance."
            raw = {"mode": metadata["mode"], "responses": responses}
        else:
            from polymer_cards_lib.llm import create_client, extract_document
            client, model, provider = create_client(args.env_file)
            metadata.update({"provider": provider, "model": model, "model_calls": 0})
            responses, traces = [], []
            # No output artifacts until all papers produce valid records.
            for document in documents:
                response, trace = extract_document(client, model, document, args.max_output_tokens)
                responses.append(response)
                traces.append({"paper_id": document["paper_id"], **trace})
                metadata["model_calls"] += 1
            raw = {"mode": metadata["mode"], "responses": responses, "traces": traces}
        results = [build_cards(document, response) for document, response in zip(documents, responses)]
        write_outputs(results, documents, args.out_dir, metadata,
                      additional_outputs={"raw-responses.json": raw})
        count = sum(len(r["cards"]) for r in results)
        discarded = sum(len(r["discarded_entities"]) for r in results)
        print(f"{metadata['mode']}: {len(results)} papers, {count} polymer cards, {discarded} standalone nonpolymers omitted. Output: {args.out_dir}")
        return 0
    except (OSError, ValueError) as exc:
        print("Polymer-card input/configuration error: " + str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        # Provider exception messages can contain credentials or request content.
        from polymer_cards_lib.llm import ModelRequestError
        if isinstance(exc, ModelRequestError):
            print(str(exc), file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":
    raise SystemExit(main())
