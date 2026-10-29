# Polymer-card contract v1

This additive workflow identifies polymer entities and describes them. It does not call the older application selector or use conductivity, commercial origin, source role, or field completeness as retention criteria.

## Input source document

`{paper_id, title, domains, source_files, chunks}`. Each chunk has `chunk_id`, `text`, `source_part`, `locator`, optional `page`, and `document_sha256`. IDs and source locations are supplied by source preparation, never invented by the model. Domains are discovery metadata, not evidence of polymer identity.

## Model response

`{paper_id, entities: [...]}`. Each entity has:

- `entity_id`: unique within the paper; `name`: original polymer/material name; `identity_evidence`: evidence references.
- `classification`: `{is_polymer: true|false|null, reason: string, evidence: [...]}`. Null is unresolved classification. True/false without usable original evidence is not a final retention/discard decision.
- `aliases`: optional list of facts; `description`: optional fact; `role`: optional fact, describing the entity's role in this paper.
- `specimens`: optional list of `{specimen_id, label, evidence}` linked to this polymer. A salted specimen is not an alias for its matrix.
- Exactly the six information groups `monomers`, `composition`, `synthesis_text`, `properties`, `applications`, `source_tag`. Each is `{status, items}`. Status is `reported`, `not_found_in_provided_text`, `needs_review`, or `conflicting`. Missing groups are filled as not found, without discarding a polymer.

A fact is `{value, evidence, ...}`. Facts in the six groups additionally carry their parent `entity_id`. Value is original source wording or a supported descriptive summary; source text remains in the attached evidence. An evidence reference is `{chunk_id, quote}`. Source metadata is resolved from the document chunk. Do not supply freestanding field-wide values and evidence arrays.

Specialized fact fields:

- Monomers: optional `role` distinguishing monomer, polymeric reactant, chain extender, etc.
- Composition: `basis` describes molar feed, mass ratio, concentration, or another reported basis; optional `specimen_id` distinguishes matrix from formulation. Keep amount/ratio and ingredient names together in `value` if needed.
- Synthesis text: text is allowed; optional `specimen_id` distinguishes polymer synthesis from later film preparation.
- Properties: `property`, original `value`, original `unit`(or null when absent or inapplicable, including dimensionless/qualitative properties), mandatory `specimen_id`, and `conditions` as a list of `{name, value, evidence}`. Preserve original numeric notation. No automatic conversion is promised. Property values and units must appear in their supporting quotes; summaries that cannot meet this check need review, not a silent rewrite.
- Applications: `claim_type` is `demonstrated`, `proposed`, or `unspecified`; it is descriptive, not a suitability gate.
- Source tag: `value` is `author_synthesized` or `commercially_purchased`. If not established for that polymer, leave the group empty. Evidence must be reviewed to distinguish purchased precursors from the final product.

## Validation and output

`build_cards(document, response)` returns `{paper_id, cards, discarded_entities, review_queue, validation_issues, statistics}`. Invalid field facts go to review and do not remove an otherwise retained polymer. Preserve the raw response separately. Identity or classification with invalid/absent evidence goes to the classification review queue. A confirmed nonpolymer is omitted as a standalone card but may remain as an ingredient.

Only source identity, type/shape, parent/specimen links and verbatim quote containment are mechanically checked. Use the status `quote_matched`, not scientifically verified. Classification and semantic attribution remain model/reviewer judgments; evaluated examples must report their review provenance. Unknown or contradictory values remain visible.

Paper-scoped IDs prevent cross-paper or cross-sample merging. A scalar value repeated at different temperatures must remain separate observations. Names containing `/`, ratios and units are never split by a generic normalizer. Any statement of experimental reproducibility, extraction accuracy or complete material coverage needs a separate evaluation.

## Module interfaces

- `polymer_cards_lib.sources.load_documents(manifest_path)` returns a list of source documents. The manifest is `{papers:[{paper_id,title,domains,sources:[{path,format,source_part,expected_sha256?}]}]}`; paths resolve relative to the manifest. PDF, JATS XML and UTF-8 text retain meaningful location/chunk metadata. JSON source snapshots with `chunks` preserve manually selected original excerpts and their source locators; their coverage is explicitly selected excerpts, not a full-paper search. The loaded file's actual SHA256 is distinct from any declared original-document hash. Supplements belong to the same paper.
- `polymer_cards_lib.validation.build_cards(document, response)` implements the validation/output contract above.
- `polymer_cards_lib.prompt.build_system_prompt()` and `build_user_prompt(document)` provide the dedicated extraction instructions.
- `polymer_cards_lib.render.write_outputs(results, documents, out_dir, run_metadata)` writes `cards.json`, `cards.jsonl`, `cards.html`, `cards.md`, `audit.json` and `sources.json` without network requests. Every card fact's evidence is expandable/readable; HTML is escaped.
- Root CLI `extract_polymer_cards.py --papers MANIFEST --out-dir OUTPUT` uses the configured model. `--records FILE` replays explicitly supplied `{responses:[...]}` through the same source preparation, validator and writer without model calls. Replay must not be described as live model extraction.
