# Polymer-card contract v1

This additive workflow identifies polymer entities and describes them. It does not call the older application selector or use conductivity, commercial origin, source role, or field completeness as retention criteria.

## Input source document

`{paper_id, title, domains, source_files, chunks}`. Each chunk has `chunk_id`, `text`, `source_part`, `locator`, optional `page`, and `document_sha256`. IDs and source locations are supplied by source preparation, never invented by the model. Domains are discovery metadata, not evidence of polymer identity.

JATS-derived text declares `text_transformations:["jats_script_notation_v1"]` in source/chunk metadata and resolved evidence. Numeric superscripts/subscripts retain Unicode position, such as `10⁵`, `cm⁻¹` and `Li₂`; unsupported script characters retain explicit `^{...}` or `_{...}` boundaries. The XML bytes and their SHA256 are unchanged. Quotes match this declared derived text, not the publisher's typeset appearance. Keep earlier run snapshots intact when comparing extraction versions.

## Model response

`{paper_id, entities: [...]}`. New live requests use strict Structured Outputs through `build_response_format()`, schema name `polymer_cards_strict_v1`. All declared keys are required and objects reject extra keys. Nullable fields represent unknown information without inventing it. `extraction_profile()` records the output format, schema name, schema SHA256 and system-prompt SHA256 in live run metadata/traces. A model or Azure deployment without strict JSON-schema support fails explicitly; there is no silent fallback to JSON-only mode. Replay remains compatible with the documented earlier v1 inputs.

The current schema reaches ten levels when expanded objects and arrays are counted. Recheck provider compatibility before adding a deeper nested field.

Each live entity has:

- `entity_id`: unique within the paper; `name`: exact source label, preserving spelling/case rather than an invented expansion; `identity_evidence`: evidence references. Other source-supported names belong in aliases. Generic family descriptions must not duplicate exact member cards or absorb chemically different controls.
- `classification`: `{is_polymer: true|false|null, reason: string, evidence: [...]}`. Null is unresolved classification. True/false without usable original evidence is not a final retention/discard decision.
- `aliases`: a list of facts; `description` and `role`: a fact or null. Role describes the entity's role in this paper.
- `specimens`: a list of `{specimen_id, label, evidence}` linked to this polymer. A salted specimen is not an alias for its matrix.
- Exactly the six information groups `monomers`, `composition`, `synthesis_text`, `properties`, `applications`, `source_tag`. Each is `{status, items}`. Status is `reported`, `not_found_in_provided_text`, `needs_review`, or `conflicting`. Earlier replay inputs may omit optional identity details, specimens or groups; missing groups are filled as not found, without discarding a polymer.

A fact is `{value, evidence, ...}`. Facts in the six groups additionally carry their parent `entity_id`. Value is original source wording or a supported descriptive summary; source text remains in the attached evidence. An evidence reference is `{chunk_id, quote}`. Source metadata is resolved from the document chunk. Do not supply freestanding field-wide values and evidence arrays.

Specialized fact fields:

- Monomers: `role` distinguishes monomer, polymeric reactant, chain extender, etc.; null is allowed in live output, and earlier replay may omit it.
- Composition: required live `basis` describes molar feed, mass ratio, concentration, or another reported basis. Unknown basis is null and the fact goes to review; do not guess it. Required live `specimen_id` may be null when no specimen-specific scope is established. Null optional scope is treated as absent in the accepted fact. Keep amounts/ratios and ingredient names together in `value`; a feed molar ratio and a later polymer:salt mass ratio are separate facts.
- Synthesis text: meaningful source-grounded process text is allowed. Required live `specimen_id` may be null, as above; an established specimen link distinguishes polymer synthesis from later film preparation.
- Properties: `property`, original `value`, original `unit` (or null when absent/inapplicable), `specimen_id`, `specimen_evidence` and `conditions` as a list of `{name, value, evidence}`. The live schema permits a null specimen ID or empty specimen evidence to express uncertainty, but these facts are quarantined rather than accepted. Accepted new properties require a linked specimen and nonempty original `specimen_evidence`, including preparation/testing context connecting the result to its exact form. Earlier replay properties may omit the new evidence field. Preserve original numeric notation; no automatic conversion is promised. Property values, units and conditions must match supporting quotes; numeric fragment checks reject partial ranges, ratios and exponents while allowing sentence punctuation.
- Applications: `claim_type` is `demonstrated`, `proposed`, or `unspecified`; it is descriptive, not a suitability gate. Demonstrated claims should cite actual current-paper experiments, not only introductory proposals. Reported component uses, such as cathode binder, also belong here.
- Source tag: `value` is `author_synthesized` or `commercially_purchased`. If not established for that polymer, leave the group empty. Evidence must be reviewed to distinguish purchased precursors from the final product.

## Validation and output

`build_cards(document, response)` returns `{paper_id, cards, discarded_entities, review_queue, validation_issues, attribution_warnings, statistics}`. Invalid field facts go to review and do not remove an otherwise retained polymer. Preserve the raw response separately. Identity or classification with invalid/absent evidence goes to the classification review queue. A confirmed nonpolymer is omitted as a standalone card but may remain as an ingredient.

`attribution_warnings` are separate advisory records for shared sample labels across polymer cards or ambiguous neat/additive-containing forms. They appear on readable cards and in nested card/result JSON. They do not add quarantined facts, establish chemical equivalence, merge records or automatically reassign measurements. Counts of warnings and review records therefore describe different checks. The rules are deliberately limited; absence of a warning does not certify sample attribution.

Only source identity, type/shape, parent/specimen links and verbatim quote containment are mechanically checked. Use the status `quote_matched`, not scientifically verified. Classification and semantic attribution remain model/reviewer judgments; evaluated examples must report their review provenance. Unknown or contradictory values remain visible.

Paper-scoped IDs prevent cross-paper or cross-sample merging. A scalar value repeated at different temperatures must remain separate observations. Names containing `/`, ratios and units are never split by a generic normalizer. Any statement of experimental reproducibility, extraction accuracy or complete material coverage needs a separate evaluation.

Live runs checkpoint each successfully extracted and validated paper. `run_complete` remains false until all requested papers finish; metadata includes `papers_requested`, `papers_completed`, `model_calls_attempted` and completed `model_calls`. If a later handled request/validation failure occurs, completed papers remain available with `run_complete:false` and `failed_paper_id`; readable output explicitly identifies the partial run. A malformed/truncated response never contributes partial paper records. If the first paper fails there is no new completed-paper checkpoint. Use a fresh output directory for each comparison run. Timeouts and connection failures have safe diagnostic labels without raw provider error text; there are no automatic retries.

The revised workflow is covered by 108 software tests as of 30 October 2026; passing those checks does not establish scientific accuracy. See the [fixes and rerun report](polymer-cards-fixes-2026-10-30.md) for the separately preserved live results and unresolved issues.

## Module interfaces

- `polymer_cards_lib.sources.load_documents(manifest_path)` returns a list of source documents. The manifest is `{papers:[{paper_id,title,domains,sources:[{path,format,source_part,expected_sha256?}]}]}`; paths resolve relative to the manifest. PDF, JATS XML and UTF-8 text retain meaningful location/chunk metadata. JSON source snapshots with `chunks` preserve manually selected original excerpts and their source locators; their coverage is explicitly selected excerpts, not a full-paper search. The loaded file's actual SHA256 is distinct from any declared original-document hash. Supplements belong to the same paper.
- `polymer_cards_lib.validation.build_cards(document, response)` implements the validation/output contract above.
- `polymer_cards_lib.prompt.build_system_prompt()` and `build_user_prompt(document)` provide the dedicated extraction instructions, including a clearly synthetic complete format example. `build_response_format()` supplies the strict live schema; `extraction_profile()` supplies its provenance.
- `polymer_cards_lib.render.write_outputs(results, documents, out_dir, run_metadata)` writes `cards.json`, `cards.jsonl`, `cards.html`, `cards.md`, `audit.json` and `sources.json` without network requests. Every card fact's evidence is expandable/readable; HTML is escaped.
- Root CLI `extract_polymer_cards.py --papers MANIFEST --out-dir OUTPUT` uses the configured model. Default bounds are three papers and 24,000 completion tokens per request; 24,000 is also the current maximum. `--request-timeout` defaults to 300 seconds per live request and accepts at most 900; SDK retries remain zero. `--records FILE` replays explicitly supplied `{responses:[...]}` through the same source preparation, validator and writer without model calls. Replay must not be described as live model extraction.
