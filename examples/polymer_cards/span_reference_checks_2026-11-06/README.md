# Saved source-span checks

`verify_span_run.py` reads saved scientific-paper records. It never loads local model credentials or makes API calls. It verifies raw-provider JSON, actual request hashes, source snapshots, source-span IDs/offsets, capture-file hashes and rebuilt card validation, then compares the unchanged 17-case, original nine-case and six-Pei reference sets.

The baseline is the preserved **previous fresh run**, `examples/polymer_cards/fresh_run_2026-11-06`, rather than the earlier proposal-conditioned revision. `baseline-reference-freeze.json` preserves the pre-change baseline/reference hashes. No reference case or threshold is changed by this helper.

## Fresh extraction

Use a new evaluation directory:

```sh
python3 examples/polymer_cards/span_reference_checks_2026-11-06/verify_span_run.py \
  --run-dir outputs/polymer_cards_spans_2026-11-06_capture \
  --capture-dirs outputs/polymer_cards_spans_2026-11-06_pei \
                 outputs/polymer_cards_spans_2026-11-06_chen \
                 outputs/polymer_cards_spans_2026-11-06_guo \
  --out-dir /tmp/polymer-span-fresh-check-new
```

If subsequent validation or revision-instruction code changed, add `--historical-code-dir PATH_TO_FROZEN_CAPTURE_CODE`. The directory must contain the original files under their repository-relative paths. Only verified historical `polymer_cards_lib/validation.py` and `polymer_cards_lib/repair.py` are accepted as fallbacks. The helper rebuilds the fresh result with its frozen validation policy and confirms the evaluation's literal/text semantics are unchanged. It does not silently revalidate historical cards under a later policy. The original fresh request does not use the revision instructions.

## Explicit source-grounded revision

Revision receives prior fresh model proposals and must remain labeled separately from independent fresh extraction:

```sh
python3 examples/polymer_cards/span_reference_checks_2026-11-06/verify_span_run.py \
  --mode revision \
  --run-dir outputs/polymer_cards_spans_review_2026-11-06_complete \
  --prior-run-dir outputs/polymer_cards_spans_2026-11-06_capture \
  --capture-dirs outputs/polymer_cards_spans_review_2026-11-06_pei \
                 outputs/polymer_cards_spans_review_2026-11-06_chen \
                 outputs/polymer_cards_spans_review_2026-11-06_guo \
  --out-dir /tmp/polymer-span-revision-check-new
```

To combine completed per-paper revisions first, replace `--run-dir TARGET` with `--assemble-to TARGET`, where the target does not exist. Assembly preserves every response, trace and validated result, checks the prior-input hashes, and makes no model calls. It never overwrites an earlier capture. Original revision inputs remain `prior-records.json` and `prior-sources.json` in the capture directories.

The revision check reconstructs its actual request from primary sources and the separately saved prior fresh response; the canonical previous-response hash and CLI input-file hashes must match. Where a revision freeze omits a separate catalog digest, the verifier explicitly uses the unchanged prior-fresh catalog digest plus the actual reconstructed revision-request hash. It does not invent pre-request metadata.

An optional `--include-baseline-revalidation` adds a separate zero-call check of unchanged legacy raw responses under current validation. It is distinct from both the saved baseline and new model output; historical model quotations are not repaired or rewritten.

## Interpretation

- A valid span ID retrieves exact original source characters. This is **retrieval integrity**, not perfect model-authored quotation fidelity. That authorship metric is inapplicable when the model selects IDs instead of writing quotations.
- Invalid IDs and malformed references are counted and remain visible; a legitimate held model proposal does not block the whole comparison. Every retained reference must resolve with correct offsets and provenance.
- A valid citation can still support the wrong sample or omit relevant conditions. Source-span integrity does not certify scientific attribution.
- Repeated references are counted as occurrences, not independent scientific facts. Record sets and card granularity can differ between runs.
- Selected matches are not overall accuracy or complete coverage. P4's ratio-style wording and Chen's singular/plural specimen wording remain interpretation/matcher limitations; references are not weakened to award matches.

All input source text remains attributed to the original [Pei](https://doi.org/10.1038/s41467-023-43467-w), [Chen](https://doi.org/10.3390/polym13234155) and [Guo](https://doi.org/10.1038/s41467-020-15949-8) papers. These checks use supplied main-text derivatives with declared script-preserving conversion; they are not experimental reproduction or exhaustive human annotation.

## Anchored context composition

`verify_context_composition.py` verifies an ordered context-review chain and rebuilds all three papers under the current validation policy. It keeps base provider records, raw context proposals and composed responses distinct. Only `evidence`, `specimen_id`, `specimen_evidence` and `conditions` may change; every number, unit, identity, root, property and record order remains anchored to the base response.

```sh
python3 examples/polymer_cards/span_reference_checks_2026-11-06/verify_context_composition.py \
  --base-run-dir outputs/polymer_cards_spans_review_2026-11-06_complete \
  --context-dirs outputs/polymer_cards_context_2026-11-06_guo \
                 outputs/polymer_cards_context_focused_2026-11-06_guo \
                 outputs/polymer_cards_context_scoped_2026-11-06_guo \
  --historical-code-dirs PATH_TO_FIRST_CONTEXT_CODE PATH_TO_SECOND_CONTEXT_CODE \
  --fresh-run-dir outputs/polymer_cards_spans_2026-11-06_capture \
  --out-dir /tmp/polymer-context-composition-new
```

The first context request predates the optional focus feature. Its frozen `context_review.py` and `llm.py` source must match the original pre-request hashes; the helper reproduces the old request and confirms old/current pure application produce the same captured result. The focused request uses an explicitly unverified source-audit hypothesis file. Preserve that original `source-audit-focus.json` with the capture so its file hash, canonical trace hash and actual request can be checked. This source-audit-assisted review is not blind independent extraction.

The third request uses frozen `strict_focus:true`: both its request builder and its applicator restrict changes to the declared existing targets. The verifier obtains this flag from the original freeze, checks its trace and passes it to both operations. Earlier false-default requests keep their exact historical behavior. The second capture also needs its verified pre-strict historical code. No numerical expected answer is supplied by this helper, and the checked references are used only after composition for evaluation.

The helper verifies the deterministic application and immutable anchors of every step. An adjacent-source union must use IDs already selected within that same evidence array, retain exact Unicode source offsets and bridge only touching/overlapping ranges or whitespace. It cannot insert unselected words, punctuation, quantities or chemistry. Such unions remain labeled derived support and do not replace original selections.

Context proposals may be held, and valid source references may still describe the wrong experimental context. Report remaining review records and stage regressions; immutable anchors and exact retrieval are not a claim that every context was corrected. The helper itself makes zero model calls.
