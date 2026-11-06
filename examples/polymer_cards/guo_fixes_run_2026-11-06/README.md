# Guo fixes and three-paper comparison — 6 November 2026

Open `summary.html` locally for a plain-English result, or `cards.html` for the 27 draft cards and original evidence. GitHub may display the HTML source; download/open the file locally for the rendered view.

The targeted Guo GPC, ambient/recovered-strain, underwater and P5 strain contexts meet the frozen source checks. All six selected Guo member identities match. P4's source ratio wording remains a representation review. Across the three papers, 13 of 17 selected measurement cases meet every criterion, versus 8 in the previous saved fresh baseline. Four selected cases and 25 field/fact records still need review; this is not overall accuracy or a clean 27-material database.

## What is preserved

- Final cards are in `cards.*`; `composed-responses.json` is explicitly derived from model context proposals, not another raw provider extraction.
- `base-raw-responses.json` preserves all three whole-record model revisions and their traces.
- `stages/fresh/` and `stages/full_revision/` retain the new fresh and revision stages. Their selected-case counts are 11/17 and 10/17 respectively. The regression remains visible.
- `captures/` retains each of the three Guo context-review inputs, raw proposal/trace, original focus concerns, freeze, application audit and composed output.
- `context-chain.json`, `input-receipts.json` and `context-verification.json` record the deterministic chain. No measured values, units, entity identities or record ordering change in this chain. Measurement specimen links and evidence/conditions are intentionally mutable context.
- `historical-code/` contains exact, hash-verified context-wrapper/source versions needed to reconstruct the first two requests. They are historical verification inputs, not active workflow files.

There were nine successful model requests in this task: three new fresh extractions, three whole-record source-grounded revisions and three Guo context reviews. Returned usage sums to 726,954 tokens. There were no failed requests or automatic retries. Final two context requests included unverified concerns from a primary-source audit; no corrected numerical answers or frozen reference file was supplied. The final result is a source-audit-assisted correction pilot, not a blind held-out benchmark.

## Reproduce the final saved comparison — zero API calls

From the repository root, choose a new output directory:

```sh
python3 examples/polymer_cards/span_reference_checks_2026-11-06/verify_context_composition.py \
  --base-run-dir examples/polymer_cards/guo_fixes_run_2026-11-06/stages/full_revision \
  --fresh-run-dir examples/polymer_cards/guo_fixes_run_2026-11-06/stages/fresh \
  --context-dirs \
    examples/polymer_cards/guo_fixes_run_2026-11-06/captures/polymer_cards_context_2026-11-06_guo \
    examples/polymer_cards/guo_fixes_run_2026-11-06/captures/polymer_cards_context_focused_2026-11-06_guo \
    examples/polymer_cards/guo_fixes_run_2026-11-06/captures/polymer_cards_context_scoped_2026-11-06_guo \
  --historical-code-dirs \
    examples/polymer_cards/guo_fixes_run_2026-11-06/historical-code/first-context-code \
    examples/polymer_cards/guo_fixes_run_2026-11-06/historical-code/second-context-code \
  --baseline-dir examples/polymer_cards/fresh_run_2026-11-06 \
  --out-dir /tmp/autoschema-guo-final-comparison-new
```

This verifies actual request/profile/focus hashes, raw JSON, anchors, deterministic edits, original source slices and adjacent unions, then revalidates all three papers and compares the unchanged three reference sets. It rejects output overwrite. No API key or model call is needed. Derived run timestamps can differ; scientific records and evaluation JSON should reproduce.

The strict final stage must pass `strict_focus=True` to both request construction and proposal application. The frozen stage supplies that flag to the verifier. The optional library stage is documented in [the guide](../../../docs/polymer-cards.md); it is separate from default fresh extraction.

## Source and interpretation limits

All final 694 retained source-reference occurrences are exact (681 direct selections, 13 adjacent unions), with repeated references counted again. These are source-integrity checks, not 694 independent scientific checks or model-authored quotation accuracy. V4 selects source IDs and retrieves original text; it does not ask the model to retype quotations.

Original articles: [Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w), [Chen et al. 2021](https://doi.org/10.3390/polym13234155) and [Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8). Their CC BY 4.0 source licenses apply to original quotations/derivative source text, with DOI/paper IDs, original XML hashes, source locations and declared `jats_script_notation_v1` conversion retained. Those article licenses are not superseded by the code license.

Main texts only; no supplements, OCR, graph extraction, exhaustive human gold data or experimental reproduction. Remaining Chen sample/state/structured-conflict gaps and broader Guo family/specimen issues are listed in [the full report](../../../docs/polymer-cards-guo-fixes-report-2026-11-06.md) and [source audit](../../../docs/polymer-card-guo-span-review-2026-11-06.md). The source-checked references are assistant-reviewed selections, not authenticated human annotation.
