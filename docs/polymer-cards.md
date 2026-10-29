# Polymer cards: revised Task 3 implementation

This workflow implements the revised request: identify polymers in papers from Nina's two domains and make six-group cards with original evidence. Polymer identity determines retention. It does not use conductivity thresholds or application suitability to remove a polymer.

## What was added

- `extract_polymer_cards.py`: a separate public entry point for live extraction and explicit record replay.
- `polymer_cards_lib/sources.py`: PDF page/text-block, JATS section/paragraph and UTF-8 text source preparation; portable JSON excerpt snapshots for reproducible examples. File hashes and stable chunk IDs preserve the source revision.
- `polymer_cards_lib/prompt.py` and `llm.py`: dedicated entity/card extraction instructions and bounded calls through the existing local OpenAI/Azure configuration. Paper text is source data, not instructions.
- `polymer_cards_lib/validation.py`: polymer/nonpolymer/unresolved output routing, six information groups, atomic fact/evidence records, parent/specimen links, original value/unit/condition support and explicit review records.
- `polymer_cards_lib/render.py`: self-contained HTML, Markdown, nested JSON/JSONL, source records and a separate audit. All HTML content is escaped; no network or script is needed to read a card.

The former field-induction, flat extraction and application-screening paths remain unchanged. A schema field such as conductivity is not a polymer entity. The new result mode therefore bypasses the former flat value normalizer and paper-wide CSV writer. [Vocabulary](../CONTEXT.md), [full contract](polymer-card-contract.md), [requirements/code review](polymer-card-reassessment-2026-10-28.md).

## Card structure

Each polymer has paper/entity identity, supported aliases/description, source role, linked specimens, and these six groups:

1. Monomers and reactive building blocks.
2. Composition and explicitly labeled ratio/concentration bases.
3. Synthesis text, distinct from later casting or salt addition.
4. Properties with original value/unit, linked specimen, conditions and evidence.
5. Applications, marked demonstrated/proposed/unspecified.
6. Source tag for the polymer: author-synthesized or commercially purchased when established.

Unfound information remains `not_found_in_provided_text`. Missing fields do not remove a polymer. A salt or solvent can remain an ingredient but is omitted as a standalone polymer card. A reactive precursor can itself be polymeric. Unsupported classification goes to review, rather than silently becoming a nonpolymer decision.

Facts are not independently deduplicated from their evidence. Chemical slashes, ratios, original scientific notation, repeated values at different temperatures, and separate neat/salted/wet specimens remain distinct. Every quote is checked against the cited chunk. Invalid child facts are quarantined for review while their otherwise retained polymer remains visible. The raw response is stored separately.

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

- `cards.html`: readable cards; expand “Original evidence” beneath each identity/fact/condition for the quotation and source location.
- `cards.md`: text version for review or a presentation.
- `cards.json` / `cards.jsonl`: nested machine-readable cards, including all six groups.
- `sources.json`: the actual source chunks and their loaded-file hashes.
- `raw-responses.json`: the supplied or live model response before card validation.
- `audit.json`: standalone omissions, unresolved classifications, invalid facts and run mode.

For excerpt snapshots the file hash verifies the excerpt bytes, while a declared original-document hash is labeled separately. A complete downloaded XML/PDF source is independently hashable when used as the source file. Temporary prompt indices are not substituted for persisted page/section/chunk identity.

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

The live route uses local AutoSchema configuration and accepts both `CHAT_API_KEY` and `OPENAI_API_KEY`. An existing configuration can be selected with `--env-file`; secrets are not included in source prompts, run metadata, responses or logs. Default limits are three papers and 10,000 completion tokens per request, with no hidden model retries. A malformed/truncated response is an error, not a partial completed extraction. Source data are never replaced by a model's invented citation metadata.

**Current run status:** secure local setup was completed and a separate live run made three OpenAI `gpt-5.4` calls on the three original main texts. It produced 18 draft card records, with three identities and 36 facts in the review queue. Source review found both extraction errors and validator/text-preparation limitations. These are not 18 unique, fully correct polymers. Read the [live results and remaining checks](polymer-cards-live-report-2026-10-28.md). The curated replay above remains unchanged and is not a model-accuracy score.

## Validation and practical limits

Focused checks cover retention despite low performance, commercial origin and missing fields; nonpolymer ingredients; malformed identity; cross-paper/parent/specimen mismatches; original value/unit/condition support; scientific notation; repeated measurements; PDF/XML source locations; strict JSON; safe HTML and output preservation. The earlier screening tests remain regression checks.

The complete documented suite passed **79 tests** on 28 October 2026. The three-paper replay was rerun after the numeric-fragment checks and transactional output saving were added. Its selected eight/four retention decisions and zero validation issues were unchanged. [Saved replay evaluation](../examples/polymer_cards/evaluation.json).

```sh
python3 -m unittest -v test_polymer_cards_validation test_polymer_cards_render test_polymer_cards_workflow test_polymer_cards_real_papers test_task3_selection test_task3_dpal_case test_task3_battery_case
```

Evidence is labeled **`quote_matched`**, never scientifically verified. A source span can contain a valid number while a model assigns it to the wrong quantity or specimen. Class membership, polymer origin, metric interpretation and experimental claims still need source review. The example contains selected entities and selected passages; additional polymers found by a full-paper model run are not automatically false positives. Do not infer complete article recall or general extraction accuracy from replaying curated records.

The source reference also protects distinctions that are easy to miss: Guo's 93%±3% is fracture-strain recovery, Chen's precursor/network strengths must not be merged, and Pei's salt-containing conductivity must not become a neat-polymer property. Those semantic expectations are checked separately from quote containment.
