# Polymer cards: revised Task 3 implementation

This workflow implements the revised request: identify polymers in papers from Nina's two domains and make six-group cards with original evidence. Polymer identity determines retention. It does not use conductivity thresholds or application suitability to remove a polymer.

## What was added

- `extract_polymer_cards.py`: a separate public entry point for fresh live extraction, explicit record replay and separately labeled source-grounded model revision.
- `polymer_cards_lib/sources.py`: PDF page/text-block, JATS section/paragraph and UTF-8 text source preparation; portable JSON excerpt snapshots for reproducible examples. File hashes and stable chunk IDs preserve the source revision. A declared JATS transformation preserves superscript/subscript boundaries.
- `polymer_cards_lib/prompt.py` and `llm.py`: dedicated instructions, a complete synthetic worked example, strict live output schema and bounded calls through local OpenAI/Azure configuration. Source-only Methods/testing and cross-reference navigation help locate protocols without supplying checked answers. Paper text is source data, not instructions.
- `polymer_cards_lib/evidence_spans.py`: deterministic source text choices bound to paper/chunk/hash/range. New live evidence selects IDs; the program retrieves original text instead of asking the model to retype a quotation.
- `polymer_cards_lib/validation.py`: polymer/nonpolymer/unresolved routing, six information groups, parent/specimen links, original value/unit/condition checks, explicit source-conflict notes, review records and separate advisory warnings for sample/material ambiguity.
- `polymer_cards_lib/repair.py`: source-only revision context from prior untrusted model records, validator feedback and exact-name lookup candidates. It does not read checked reference answers or automatically repair identities/measurements.
- `polymer_cards_lib/context_review.py`: anchored context proposals and pure composition that protect existing names, values and units; optional strict source-audit focus limits eligible targets. The library model-call wrapper is `llm.review_context_document`, distinct from full-record CLI revision.
- `polymer_cards_lib/render.py`: self-contained HTML, Markdown, nested JSON/JSONL, source records and a separate audit. All HTML content is escaped; no network or script is needed to read a card.

The former field-induction, flat extraction and application-screening paths remain unchanged. A schema field such as conductivity is not a polymer entity. The new result mode therefore bypasses the former flat value normalizer and paper-wide CSV writer. [Vocabulary](../CONTEXT.md), [full contract](polymer-card-contract.md), [requirements/code review](polymer-card-reassessment-2026-10-28.md).

## Card structure

Each polymer has paper/entity identity, supported aliases/description, source role, linked specimens, and these six groups. New live records explicitly distinguish `specific_polymer` from `polymer_family`; unresolved scope is null and legacy replay may omit it.

1. Monomers and reactive building blocks.
2. Composition and explicitly labeled ratio/concentration bases.
3. Synthesis text, distinct from later casting or salt addition.
4. Properties with original value/unit, linked specimen, sample-link evidence, conditions, numerical evidence and unresolved source conflicts.
5. Applications, marked demonstrated/proposed/unspecified.
6. Source tag for the polymer: author-synthesized or commercially purchased when established.

Unfound information remains `not_found_in_provided_text`. Missing fields do not remove a polymer. A salt or solvent can remain an ingredient but is omitted as a standalone polymer card. A reactive precursor can itself be polymeric. Unsupported classification goes to review, rather than silently becoming a nonpolymer decision.

Facts are not independently deduplicated from their evidence. Chemical slashes, ratios, original scientific notation, repeated values at different temperatures, and separate neat/salted/wet specimens remain distinct. New live evidence selects a supplied source-span ID, which resolves to exact characters in its cited chunk. Legacy model/curated quotations still undergo the unchanged source-containment check; they are not fuzzily repaired. Invalid child facts are quarantined for review while their otherwise retained polymer remains visible. The raw response is stored separately.

Live composition facts require a `basis` key: for example, a monomer-feed molar ratio is separate from a polymer:salt mass ratio. Unknown basis is explicit null and remains for review. Composition/synthesis may have null optional specimen scope; properties need a concrete specimen link and nonempty `specimen_evidence` to pass. Origin labels such as `author_synthesized` are item values, never group statuses. The prompt also asks for exact source names, distinct family/control identities and experimental evidence for demonstrated uses.

The earlier 6 November implementation introduced explicit `properties.conflicts:[{property,description,specimen_ids,evidence}]` in live v3; the group remains in V4, now with span-ID evidence. A conflict note keeps competing source reports visible with their own sample contexts; it does not choose a winner. For example, Chen's Methods and Results membrane thickness reports should remain separate and their uncertain relationship should be recorded. The separate PE-film thickness must not be used to resolve SHP. The validator checks the note's source quotes and parent-local specimen IDs, preserves accepted observations, and marks valid conflict groups `conflicting`. Malformed notes go to review. Earlier replays without the new field remain supported.

Testing conditions need their own original evidence. Fresh extraction supplies all original chunks, their `source_span_catalog`, a lexical `method_context_index` of chunk IDs/locators/protocol categories, and a `method_cross_reference_index` linking explicit same-procedure/default cues to neighboring chunks in the same Methods section. This is navigation guidance, not a mapping from a method to a result or an exhaustive Methods search. The prompt asks the model to cross-check loading rates, chromatography context, electrochemical settings, healing definitions and related protocols where the paper establishes their applicability; it must not fill gaps from convention. Healing duration/environment and the subsequent mechanical readout are distinct conditions. Same-procedure references and section defaults must be traced with their source scope and exceptions; the code does not automatically attach them to measurements or create sample links. Numeric output facts carry `conditions_review_status:not_captured` for an empty conditions list, otherwise `captured_not_scientifically_verified`. Neither label establishes completeness. Readable cards explicitly show when no conditions were captured.

Percent units remain separate from raw value notation: a value such as `93% ± 3%` needs `unit:"%"`. If a numeric raw value visibly includes `%` while `unit` is null, the validator holds that fact for review without filling the unit automatically. Source-supported dimensionless results may keep null; other omitted units still need extraction/source checks. No numerical conversion or scientific correctness is implied by passing this guard.

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

The frozen [reference](../examples/polymer_cards/reference.json) was written from original sources before replay. Original/excerpt hashes, exact DPAL membership, attribution and selected coverage are in [provenance](../examples/polymer_cards/provenance.json). These papers align with Nina's domains but are not claimed to be her six unidentified seeds. This selected replay redistributes attributed CC BY 4.0 excerpts. Original XML/PDF files remain outside Git; separately published live runs may include attributed converted main-text snapshots under the original article licenses. [Scientific reference notes](polymer-card-real-paper-reference.md).

## Read the outputs

- `cards.html`: readable cards; expand “Original evidence” beneath each identity/fact/condition, or “Sample-link evidence” beneath a property, for the retrieved original text and source location. V4 evidence also shows source-selection origin and character offsets. Advisory sample/material warnings are displayed separately.
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

The live route uses local AutoSchema configuration and accepts both `CHAT_API_KEY` and `OPENAI_API_KEY`. An existing configuration can be selected with `--env-file`; secrets are not included in source prompts, run metadata, responses or logs. Default limits remain three papers and **24,000 completion tokens per request**. An explicit `--max-output-tokens` may request up to **48,000** for a longer complete response; the chosen budget is recorded in run metadata, and a truncated response still contributes no accepted partial paper records. `--request-timeout` defaults to **300 seconds** and accepts at most 900. SDK retries are zero; timeouts and connection failures receive safe diagnostic labels without logging raw provider errors. Source data are never replaced by a model's invented citation metadata.

Each completed paper is validated and saved before the next one starts. Output metadata records requested/completed papers, attempted calls, completed calls and `run_complete`. Until all papers finish, `run_complete:false` and a visible partial-run banner distinguish the saved subset from a complete test. If a later request fails, already completed papers remain available; no facts are accepted from the failed/truncated/refused response. A handled failure records `failed_paper_id`. If the first paper fails, no new completed-paper checkpoint exists. Use a fresh output directory for a separately labeled rerun; this is per-paper checkpointing, not automatic resumption or retry.

Live requests now use strict JSON schema **`polymer_cards_strict_v4`**, with required keys, explicit nullable unknowns, family/member scope, a required properties-conflict list and valid status/claim/origin enums. Every live evidence reference is `{chunk_id,span_id}`; the model must choose supplied IDs instead of writing quotations. Earlier v2/v3 request formats remain in their historical runs, and quote-based replay remains supported. Run metadata and traces record the schema name, schema hash and system-prompt hash. Models and Azure deployments must support strict JSON-schema output; unsupported requests fail without silently reverting to JSON-only mode. This enforces format, not chemical correctness. [Contract details](polymer-card-contract.md).

The catalogue supplies exact contiguous source choices, including complete chunks when sentence boundaries are unhelpful. IDs are tied to the current paper, chunk, source hash and range. Invalid/mixed IDs remain for review; a V4 reference cannot override retrieved source text or provenance. Resolved evidence preserves `evidence_origin:source_span_selection`, `span_id`, `source_start`, `source_end` and `catalog_version`, along with the original source quotation and location. Character offsets use zero-based Unicode codepoints with an exclusive end, not byte or UTF-16 offsets.

Already selected overlapping/adjacent spans within one chunk may also produce exact derived support, labeled `evidence_origin:source_span_selection_union`, with the original `span_ids` and offsets. Only whitespace can be bridged; unselected words, signs and punctuation cannot be skipped. Individual selections remain visible and no new model evidence ID is invented. This is exact source retrieval, not a claim that the associated scientific interpretation is verified; legacy quotation arrays remain unchanged.

There is no fuzzy quotation repair or automatic scientific correction: old `Mn`/`CH2Cl2` quotations that differ from supplied `M_{n}`/`CH₂Cl₂` text still fail legacy containment. The V4 route avoids retyping by selecting original text; it does not prove that a selected passage supports the associated material, property or condition. The raw model response is retained independently.

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

The example uses a 600-second request limit, as the recorded revision did; the CLI default remains 300. Both repair flags are required. The CLI rejects mismatched paper/source snapshots and protects the prior files from overwrite. Each paper receives one new request, with primary text/current span catalogue, previous records as untrusted proposals, compact validation feedback and exact-name source candidates with span IDs. New evidence uses current span IDs even if earlier proposals used quotations. Candidate passages are lookup guidance, not chemical proof. Checked cards and focused evaluation expectations are not supplied to this model route.

This is labeled **`live_model_revision`**, not a fresh independent extraction or zero-call replay. Prior-file and request-prompt hashes are recorded. The model regenerates responses; source checking and any later program revalidation remain separate. A changed validator can change reconstructed feedback/prompt hashes, so historical requests and final validation policy must be disclosed separately.

The [revision report](polymer-cards-revision-report-2026-10-30.md) records the three-paper revision, six recovered Guo member identities, corrected selected sample owners and remaining incomplete Methods metadata. Its 25 cards include broad families as well as exact members; that is not 25 distinct scientifically verified materials.

## Context-only model proposals

For a bounded protocol/sample review, the library offers `llm.review_context_document(...)` and pure `context_review.apply_context_proposals(...)`. This route returns edits to existing property context instead of regenerating whole cards. The existing CLI `--repair-*` route continues to regenerate full records; it is a different mode.

Context proposals are anchored to an existing entity, original property index, label, value and unit. They may change only the specimen link, link evidence, test conditions and measurement evidence. They cannot change values, units, property names, identities, record order or specimen declarations, and cannot add a missing measurement. Unknown targets/IDs, duplicate edits and forbidden fields are held as whole edits. A proposed edit introducing a new target-property validation failure is rejected, preserving the base context; previously held facts can still gain supported context without being presented as fully checked.

A source-audit focus can identify existing records whose context deserves review using only `{entity_id, property_index, reason}`. These reasons remain unverified hypotheses—not expected values or proof a change is needed. The **opt-in `strict_focus=True`** filters the model's target list while preserving original indexes and all source data, and also rejects out-of-scope proposals during composition. Pass the same focus/flag to both functions. Default `strict_focus=False` preserves the previous broad-review/hint behavior. Strict mode asks for literal source-supported condition wording, avoiding unsupported acronym expansion, and removes the nested fresh-extraction instruction from the source section.

```python
from polymer_cards_lib.llm import review_context_document
from polymer_cards_lib.context_review import apply_context_proposals

# client and model use the existing approved local configuration.
proposals, trace = review_context_document(
    client, model, document, base_response,
    review_focus=source_audit_issues, strict_focus=True,
)
composed_response, audit = apply_context_proposals(
    document, base_response, proposals,
    review_focus=source_audit_issues, strict_focus=True,
)
```

Save the base response, raw proposals/trace, composition audit and composed result separately. The audit verifies protected fields and records applied/held edits. `applied_context_source_linked` means mechanical evidence checks passed; condition applicability still requires scientific source review. Source-audit-guided revision is not fresh extraction or a blind test, and its source/feedback/prompt provenance must be disclosed separately. No reference answers, numerical conversions or manually rewritten model facts are needed for this route.

The [Pei/Chen source audit](polymer-card-pei-chen-span-review-2026-11-06.md) illustrates the remaining scope: supported Pei observations coexist with unresolved Chen specimen/context issues, and the thickness note lacks a separate structured 12 μm observation. A context-only pass cannot add that missing measurement or certify every sample state.

## Validation and practical limits

Focused checks cover retention despite low performance, commercial origin and missing fields; nonpolymer ingredients; malformed identity; cross-paper/parent/specimen mismatches; original value/unit/condition support; scientific notation; repeated measurements; PDF/XML source locations; strict JSON; safe HTML and output preservation. The earlier screening tests remain regression checks.

The 30 October revision freeze passed **148 software tests**, including source scripts, numerical boundaries, strict output requirements, source-grounded revision, exact-name lookup, sample-link/family guards, focused evaluation, safe errors and partial-run checkpoints. The **earlier 6 November implementation freeze passed 176 tests**, adding checks for source-qualified conflicts, explicit unit fields, condition visibility, Methods navigation, stricter focused evaluation and explicit output-budget bounds. The **initial 6 November V4 implementation freeze passed 206 tests**, including source-span selection/provenance, strict legacy compatibility, source-only cross-reference navigation and the bounded cell-stack exception. The **final 6 November implementation freeze passed 232 tests**, adding derived adjacent-source support, anchored context proposals, regression rollback and strict target-scope checks. These are dated software-test counts, not paper counts, scientific-accuracy scores or claims that a new live run has finished. Earlier reports' 79- and 108-test counts describe their historical code versions. [Original replay evaluation](../examples/polymer_cards/evaluation.json).

```sh
python3 -m unittest discover -p 'test_*.py'
```

Evidence is labeled **`quote_matched`**, never scientifically verified. A source span can contain a valid number while a model assigns it to the wrong quantity or specimen. Class membership, polymer origin, metric interpretation and experimental claims still need source review. The example contains selected entities and selected passages; additional polymers found by a full-paper model run are not automatically false positives. Do not infer complete article recall or general extraction accuracy from replaying curated records.

Advisory attribution warnings identify shared sample labels across cards or possible neat/additive ambiguity. They do not establish errors, merge polymers or reassign results. They are counted separately from rejected facts, and their absence is not proof of a correct link. The original model run stays intact; compare any revised live run as a separately labeled result.

Separate sample-link evidence that explicitly names an alternate additive form can now quarantine a bare-form property link. This considers preparation/link evidence rather than treating every numerical comparison as a mismatch, and it can flag an alternate form even if the model omitted that sibling specimen. Numerical member measurements under an explicit family, or with explicitly unresolved live scope, also remain for review. The guards retain the polymer card and never choose a replacement sample automatically.

The additive-form guard has a narrow exception for explicitly introduced electrode/membrane/electrode cell stacks with recognized outer electrode labels, such as asymmetric `SS/SHPEM/Li`. The selected membrane must be the bounded central layer. This prevents treating the electrode suffix as a polymer additive in that specific notation; it does not bypass other preparation text in the paragraph, infer every cell structure, assign a missing specimen or certify a measurement.

The source reference also protects distinctions that are easy to miss: Guo's 93%±3% is fracture-strain recovery, Chen's precursor/network strengths must not be merged, and Pei's salt-containing conductivity must not become a neat-polymer property. Those semantic expectations are checked separately from quote containment.

New, additive evaluation references can require a separate unit field with `unit_field_required:true` and can include `conflict_expectations`. A conflict expectation checks both source-qualified observations, the explicit note and the source passages needed to explain its unresolved scope; one thickness value or a generic warning alone cannot pass. The stricter selected references remain outside model inputs, and earlier frozen reference files are preserved. Full conditions and Methods coverage must be checked separately from correct core values. Comparisons with a new fresh extraction must state that earlier source-grounded revisions had prior proposals as context; they are different request modes and are not a paired overall-accuracy measurement.
