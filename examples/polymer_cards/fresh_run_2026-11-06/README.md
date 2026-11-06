# Fresh polymer-card extraction, 6 November 2026

Open `summary.html` locally for the comparison and `cards.html` for all draft cards with original evidence. GitHub’s file page may show HTML source; download/open locally for the rendered view. The separately source-checked Pei example is `checked-pei-card.html`, not model output.

## Result and limits

Three completed fresh, source-only OpenAI `gpt-5.4` requests produced 24 raw records and 21 draft cards: 18 specific-polymer records and three families. There are three held identity records and 38 other field/fact review records. These are not 21 unique scientifically checked materials or 41 established errors.

All six selected Pei BHDS full-context cases now meet their frozen criteria. The stricter 17-case set changes from three complete matches to eight, while the original nine-case set regresses from six to three and selected Guo identities from six to five. Chen’s 12 μm / about 15 μm conflict is explicitly retained. This is mixed progress, not overall accuracy improvement.

Zero of 24 percent-containing raw property entries now have a null separate unit field, compared with 19 of 20 in the earlier response. These are differing extracted record sets and field-presence checks, not an accuracy score. P4’s ratio-style wording is a separate frozen-reference representation issue.

No checked reference or old extraction proposals were sent to the model. Both source-only request batches and failed attempts are preserved locally. The final files combine completed responses without editing values, quotations or sample links. `capture-receipts.json` and the original pre-request freezes nested in `pre-run-freeze.json` record the assembly. Only the CLI token-budget bound changed between successful batches; extraction instructions and scientific processing remained unchanged.

## Actual requests

- One authentication failure before any paper completed.
- Pei completed with a 24,000-token cap and 600-second limit.
- The next Chen response reached the 24,000-token limit and was rejected; no partial Chen records were accepted.
- An explicitly initiated remaining-paper batch completed Chen and Guo with 48,000-token caps and 900-second limits.
- Three successful calls returned 118,408 total tokens. Failed truncated-call usage was not persisted and is excluded. This is not total billed usage. No automatic retries.

The combined raw responses remain fresh extractions. Assembly makes zero model calls; it is not a reference-populated replay or revision using prior-run answers.

## Reproduce the saved comparison without API calls

From the repository root:

```sh
python3 examples/polymer_cards/condition_reference_2026-11-06/compare_run.py \
  --run-dir examples/polymer_cards/fresh_run_2026-11-06 \
  --baseline-dir examples/polymer_cards/fresh_run_2026-11-06/baseline \
  --out-dir /tmp/polymer-fresh-comparison-new
```

Choose a new output directory; the helper refuses to overwrite an earlier comparison. It verifies source/request hashes, the prompt/schema and code/reference freeze, raw JSON preservation, and unchanged source snapshots. It then evaluates the three frozen reference sets. The `baseline/` copies are unchanged from the earlier saved revision; their original hashes are in `baseline/provenance.json`.

Rechecking the original XML hashes needs the local original-paper manifest, as described in [the evaluation reference](../condition_reference_2026-11-06/README.md). No key is needed for saved-data comparison. A new live extraction is separate and uses the existing ignored local configuration; do not add credentials to this directory.

## Provenance and source licenses

Sources are original main texts of [Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w), [Chen et al. 2021](https://doi.org/10.3390/polym13234155), and [Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8). These articles are CC BY 4.0; source excerpts and derivative text retain original attribution, DOI/paper IDs, XML hashes and locators. `sources.json` and `baseline/sources.json` contain original-text derivatives under those source licenses, with declared `jats_script_notation_v1` superscript/subscript conversion. Code and assistant-created records do not supersede the article licenses.

Main texts only; no supplements, OCR or graph-only extraction. References are selected assistant source-reviewed material, not authenticated human annotation, complete recall or experimental reproduction. 176 software tests and 413 retained quote-reference occurrences are implementation/source-containment checks, not scientific accuracy.

See the [full report](../../../docs/polymer-cards-conditions-fresh-report-2026-11-06.md), [Pei review](../../../docs/polymer-card-pei-fresh-source-review-2026-11-06.md), [Chen review](../../../docs/polymer-card-chen-fresh-source-review-2026-11-06.md), and [Guo review](../../../docs/polymer-card-guo-fresh-source-review-2026-11-06.md).
