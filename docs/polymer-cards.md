# Polymer cards: revised Task 3 implementation

This workflow implements the revised request: identify polymers in papers from Nina's two domains and make six-group cards with original evidence. Polymer identity determines retention. It does not use conductivity thresholds or application suitability to remove a polymer.

## What was added

- `extract_polymer_cards.py`: a separate public entry point for fresh live extraction, explicit record replay and separately labeled source-grounded model revision.
- `polymer_cards_lib/sources.py`: PDF page/text-block, JATS section/paragraph and UTF-8 text source preparation; portable JSON excerpt snapshots for reproducible examples. File hashes and stable chunk IDs preserve the source revision. A declared JATS transformation preserves superscript/subscript boundaries.
- `polymer_cards_lib/prompt.py` and `llm.py`: dedicated instructions, a complete synthetic worked example, strict live output schema and bounded calls through local OpenAI/Azure configuration. Paper text is source data, not instructions.
- `polymer_cards_lib/validation.py`: polymer/nonpolymer/unresolved routing, six information groups, parent/specimen links, original value/unit/condition checks, explicit review records and separate advisory warnings for sample/material ambiguity.
- `polymer_cards_lib/repair.py`: source-only revision context from prior untrusted model records, validator feedback and exact-name lookup candidates. It does not read checked reference answers or automatically repair identities/measurements.
- `polymer_cards_lib/render.py`: self-contained HTML, Markdown, nested JSON/JSONL, source records and a separate audit. All HTML content is escaped; no network or script is needed to read a card.

The former field-induction, flat extraction and application-screening paths remain unchanged. A schema field such as conductivity is not a polymer entity. The new result mode therefore bypasses the former flat value normalizer and paper-wide CSV writer. [Vocabulary](../CONTEXT.md), [full contract](polymer-card-contract.md), [requirements/code review](polymer-card-reassessment-2026-10-28.md).

## Card structure

Each polymer has paper/entity identity, supported aliases/description, source role, linked specimens, and these six groups. New live records explicitly distinguish `specific_polymer` from `polymer_family`; unresolved scope is null and legacy replay may omit it.

1. Monomers and reactive building blocks.
2. Composition and explicitly labeled ratio/concentration bases.
3. Synthesis text, distinct from later casting or salt addition.
4. Properties with original value/unit, linked specimen, sample-link evidence, conditions and numerical evidence.
5. Applications, marked demonstrated/proposed/unspecified.
6. Source tag for the polymer: author-synthesized or commercially purchased when established.

Unfound information remains `not_found_in_provided_text`. Missing fields do not remove a polymer. A salt or solvent can remain an ingredient but is omitted as a standalone polymer card. A reactive precursor can itself be polymeric. Unsupported classification goes to review, rather than silently becoming a nonpolymer decision.

Facts are not independently deduplicated from their evidence. Chemical slashes, ratios, original scientific notation, repeated values at different temperatures, and separate neat/salted/wet specimens remain distinct. Every quote is checked against the cited chunk. Invalid child facts are quarantined for review while their otherwise retained polymer remains visible. The raw response is stored separately.

Live composition facts require a `basis` key: for example, a monomer-feed molar ratio is separate from a polymer:salt mass ratio. Unknown basis is explicit null and remains for review. Composition/synthesis may have null optional specimen scope; properties need a concrete specimen link and nonempty `specimen_evidence` to pass. Origin labels such as `author_synthesized` are item values, never group statuses. The prompt also asks for exact source names, distinct family/control identities and experimental evidence for demonstrated uses.

## Run the checked real-paper example

```sh
python3 extract_polymer_cards.py --papers examples/polymer_cards/papers.json --records examples/polymer_cards/curated-responses.json --out-dir outputs/polymer_cards_demo
```

This runs source preparation, nested validation, retention/discard routing and rendering. It makes **zero model calls**. The records are explicitly assistant-curated from selected original passages; they are not represented as saved model output.

| Primary paper | Domain coverage | Selected polymer cards retained | Standalone nonpolymers omitted |
| --- | --- | --- | --- |
| [Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w) | Disulfide and batteries | PTMG-HDI-BHDS; PTMG-HDI; purchased PEO; polymeric PTMG reactant | LiFSI; HDI reagent |
| [Chen et al. 2021](https://doi.org/10.3390/polym13234155) | Batteries | Precursor copolymer; cross-linked polymer network | LiBOB salt |
| [Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8) | Disulfide, nonbattery | P3 elastomer; reactive PDMS precursor | IPDI reagent |

The replay produces **eight polymer cards and four standalone nonpolymer discards**, matching the selected source-based retention reference. It preserves the lower-conductivity HDI polymer, purchased PEO and incomplete precursor records. LiFSI remains within the relevant electrolyte composition. This verifies the new retention rule on the supplied records; it does not measure a model's classification accuracy or full-paper recall.

The frozen [reference](../examples/polymer_cards/reference.json) was written from original sources before replay. Original/excerpt hashes, exact DPAL membership, attribution and selected coverage are in [provenance](../examples/polymer_cards/provenance.json). These papers align with Nina's domains but are not claimed to be her six unidentified seeds. Only attributed CC BY 4.0 excerpts are redistributed; complete original papers remain outside Git. [Scientific reference notes](polymer-card-real-paper-reference.md).

## Read the outputs

- `cards.html`: readable cards; expand “Original evidence” beneath each identity/fact/condition, or “Sample-link evidence” beneath a property, for the quotation and source location. Advisory sample/material warnings are displayed separately.
- `cards.md`: text version for review or a presentation.
- `cards.json` / `cards.jsonl`: nested machine-readable cards, including all six groups and any advisory attribution warnings. These warnings are separate from the quarantined fact/identity review queue.
- `sources.json`: the actual source chunks and their loaded-file hashes.
- `raw-responses.json`: the supplied or live model response before card validation.
- `audit.json`: standalone omissions, unresolved classifications, invalid facts and run mode.

For excerpt snapshots the file hash verifies the excerpt bytes, while a declared original-document hash is labeled separately. A complete downloaded XML/PDF source is independently hashable when used as the source file. Temporary prompt indices are not substituted for persisted page/section/chunk identity.

New JATS runs declare `jats_script_notation_v1` in source/evidence metadata. Numeric scripts retain their position (`10⁵`, `cm⁻¹`, `Li₂`); other script content uses explicit `^{...}` or `_{...}` boundaries. Original XML bytes and hashes remain unchanged. Quotes are checked against this derived text, and preserved earlier runs keep their original source snapshots.

## Live model extraction

Use the same CLI without `--records`, with a manifest of local original sources:

```json
{
  "papers": [
    {
      "paper_id": "the DOI or stable paper ID",
      "title": "Article title",
      "domains": ["disulfide"],
      "sources": [
        {"path": "article.xml", "format": "jats", "source_part": "main"},
        {"path": "supplement.pdf", "format": "pdf", "source_part": "supplement"}
      ]
    }
  ]
}
```

Paths resolve relative to the manifest. Expected SHA256 values can be supplied to reject changed source files. Supported source formats are PDF, JATS XML, UTF-8 text and selected-excerpt JSON snapshots. PDF processing extracts text and preserves page numbers; it does not perform OCR or extract numeric graph data.

```sh
python3 extract_polymer_cards.py --papers path/to/full-papers.json --out-dir outputs/polymer_cards_live
```

The live route uses local AutoSchema configuration and accepts both `CHAT_API_KEY` and `OPENAI_API_KEY`. An existing configuration can be selected with `--env-file`; secrets are not included in source prompts, run metadata, responses or logs. Default limits are three papers and **24,000 completion tokens per request**. `--request-timeout` defaults to **300 seconds** and accepts at most 900. SDK retries are zero; timeouts and connection failures receive safe diagnostic labels without logging raw provider errors. Source data are never replaced by a model's invented citation metadata.

Each completed paper is validated and saved before the next one starts. Output metadata records requested/completed papers, attempted calls, completed calls and `run_complete`. Until all papers finish, `run_complete:false` and a visible partial-run banner distinguish the saved subset from a complete test. If a later request fails, already completed papers remain available; no facts are accepted from the failed/truncated/refused response. A handled failure records `failed_paper_id`. If the first paper fails, no new completed-paper checkpoint exists. Use a fresh output directory for a separately labeled rerun; this is per-paper checkpointing, not automatic resumption or retry.

Live requests now use strict JSON schema **`polymer_cards_strict_v2`**, with required keys, explicit nullable unknowns, family/member scope and valid status/claim/origin enums. Run metadata and traces record the schema name, schema hash and system-prompt hash. Models and Azure deployments must support strict JSON-schema output; unsupported requests fail without silently reverting to JSON-only mode. This enforces format, not chemical correctness. [Contract details](polymer-card-contract.md).

**Historical live test, 28 October:** three OpenAI `gpt-5.4` calls on the original main texts produced 18 draft records, with three additional identities and 36 facts in review. Source review found extraction errors and validator/text-preparation limitations. These are not 18 unique, fully correct polymers. The [original live report](polymer-cards-live-report-2026-10-28.md) and saved outputs remain unchanged as the comparison baseline. Those numbers are not results of the revised code. The curated replay above is also separate and is not a model-accuracy score.

Changes and separately labeled rerun outcomes are documented in the [30 October fixes and rerun report](polymer-cards-fixes-2026-10-30.md). Improvements to format and mechanical checks do not establish that all scientific attribution problems are fixed.

## One checked card, then source-grounded revision

The [checked Pei example](polymer-card-checked-pei-2026-10-30.md) is one assistant source-checked PTMG-HDI-BHDS card with information in all six groups, explicit sample forms and original passages. Its [portable records](../examples/polymer_cards/checked_pei_2026-10-30/checked-records.json) are reference material, not model output or an exhaustive inventory. Replaying that example makes zero model calls; its two conservative sample warnings remain visible rather than being removed to make the result look perfect.

To ask the model to revise an existing extraction, provide its original source snapshot as well as its records:

```sh
python3 extract_polymer_cards.py \
  --papers path/to/full-papers.json \
  --repair-records outputs/polymer_cards_fixed_2026-10-30/raw-responses.json \
  --repair-sources outputs/polymer_cards_fixed_2026-10-30/sources.json \
  --out-dir outputs/polymer_cards_revision \
  --request-timeout 600
```

The example uses a 600-second request limit, as the recorded revision did; the CLI default remains 300. Both repair flags are required. The CLI rejects mismatched paper/source snapshots and protects the prior files from overwrite. Each paper receives one new request, with primary text, previous records as untrusted proposals, compact validation feedback and exact-name source candidates. Candidate passages are lookup guidance, not chemical proof. Checked cards and focused evaluation expectations are not supplied to this model route.

This is labeled **`live_model_revision`**, not a fresh independent extraction or zero-call replay. Prior-file and request-prompt hashes are recorded. The model regenerates responses; source checking and any later program revalidation remain separate. A changed validator can change reconstructed feedback/prompt hashes, so historical requests and final validation policy must be disclosed separately.

The [revision report](polymer-cards-revision-report-2026-10-30.md) records the three-paper revision, six recovered Guo member identities, corrected selected sample owners and remaining incomplete Methods metadata. Its 25 cards include broad families as well as exact members; that is not 25 distinct scientifically verified materials.

## Validation and practical limits

Focused checks cover retention despite low performance, commercial origin and missing fields; nonpolymer ingredients; malformed identity; cross-paper/parent/specimen mismatches; original value/unit/condition support; scientific notation; repeated measurements; PDF/XML source locations; strict JSON; safe HTML and output preservation. The earlier screening tests remain regression checks.

The revised suite passes **148 software tests** at the 30 October revision freeze, including source scripts, numerical boundaries, strict output requirements, source-grounded revision, exact-name lookup, sample-link/family guards, focused evaluation, safe errors and partial-run checkpoints. This is a software-test count, not a paper count or accuracy score. Earlier reports' 79- and 108-test counts describe their historical code versions. [Original replay evaluation](../examples/polymer_cards/evaluation.json).

```sh
python3 -m unittest discover -p 'test_*.py'
```

Evidence is labeled **`quote_matched`**, never scientifically verified. A source span can contain a valid number while a model assigns it to the wrong quantity or specimen. Class membership, polymer origin, metric interpretation and experimental claims still need source review. The example contains selected entities and selected passages; additional polymers found by a full-paper model run are not automatically false positives. Do not infer complete article recall or general extraction accuracy from replaying curated records.

Advisory attribution warnings identify shared sample labels across cards or possible neat/additive ambiguity. They do not establish errors, merge polymers or reassign results. They are counted separately from rejected facts, and their absence is not proof of a correct link. The original model run stays intact; compare any revised live run as a separately labeled result.

Separate sample-link evidence that explicitly names an alternate additive form can now quarantine a bare-form property link. This considers preparation/link evidence rather than treating every numerical comparison as a mismatch, and it can flag an alternate form even if the model omitted that sibling specimen. Numerical member measurements under an explicit family, or with explicitly unresolved live scope, also remain for review. The guards retain the polymer card and never choose a replacement sample automatically.

The source reference also protects distinctions that are easy to miss: Guo's 93%±3% is fracture-strain recovery, Chen's precursor/network strengths must not be merged, and Pei's salt-containing conductivity must not become a neat-polymer property. Those semantic expectations are checked separately from quote containment.
