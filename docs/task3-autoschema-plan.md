# Task 3: completion status and AutoSchema handoff

Updated **21 October 2026**. The [completed experimental case study](task3-screening-report.md) supersedes the 20 October DPAL-only preparation plan. The user authorized experimental papers from DPAL, and the chosen application is a research shortlist for stiff UV-repairable coatings on rigid wood.

## Completed for the assignment

- [x] Choose one application and specify executable requirements, with analyst provenance rather than invented standards.
- [x] Verify two experimental papers' exact membership in the released DPAL CSV.
- [x] Check three formulation records against original experiments and available supplements.
- [x] Keep evidence support separate from application fit, and preserve incompatible conditions and missing facts.
- [x] Freeze source-based reference decisions before running the selector: one keep, one exclusion, one evidence gap.
- [x] Run the existing selector on the real curated observations and report its disagreements rather than altering the reference.
- [x] Record reasons, follow-up owners, source coverage and stopping rules, without a unified score.
- [x] Pass 31 existing tests and three real-case checks.

The two retained sources are Balkenende et al. (2016) and Tzoumani et al. (2023), including their supporting information. The presentation contains three formulations, not three papers.

The [reference](../examples/task3/dpal_experiments/reference.json), [actual evaluation](../examples/task3/dpal_experiments/evaluation.json) and [decision worksheet](../examples/task3/dpal_experiments/decisions.csv) distinguish scientific judgments from software outcomes. The selector agrees on two of three material decisions and five of six criteria. One additional manual review exposes the table-header unit limit; it is not automatically resolved by trusted review receipts. This reduced presentation subset does not establish improved performance.

## What must reach AutoSchema before automatic screening

| Boundary | Current evidence / behavior | Required next change |
| --- | --- | --- |
| Phase I schema to Phase II loader | Induction emits examples/evidence examples; loading expects value types and evidence snippets. Missing cardinality defaults to a single string. | Specify key mappings and reviewed cardinality; do not make every field an array by default. |
| Extracted value to its evidence | Postprocessing independently deduplicates values, caps single-valued fields and truncates quotes. The earlier controlled probe retained A with both A/B quotes. | Preserve formulation, metric, value, unit, baseline, conditions and locator together before destructive normalization. |
| Table measurement to unit | The real blend's original numeric cell is separate from its GPa header; current selector requests review. | Add an explicit, reviewed cell/row/column/header relation while retaining original text and source revision. |
| Experimental adequacy to application fit | Source review supports claims but cannot prove repeatability or a complete device application. | Retain independent adequacy/fit judgments and criterion-specific requirements; do not use an extractor's self-verification as proof. |
| Evidence gaps to retrieval | Code queues actions but early gates hide some later gaps; it does not retrieve missing sources. | Carry the source-based gap ledger forward, with owner and source coverage; rerun only after obtaining decisive evidence. |

Primary code: [schema producer](../schema_lib/fields.py), [schema loader](../extract_lib/schema_loader.py), [normalizer](../extract_lib/postprocess.py), [selector](../selection_lib/screening.py). These production paths were not changed for the case study.

## Next engineering iteration and acceptance checks

1. Reconcile schema keys and cardinality; verify multiple formulations and shared values remain correctly linked.
2. Represent reviewed table-header units without fabricating inline quotations. Update the real-case checks only after reviewing the new behavior against the fixed scientific reference.
3. Confirm that the blend can reach its supported stiffness exclusion without borrowing the neat formulation's repair measurement.
4. Keep WPU's water-mediated result separate from the target UV/wood test; data for another formulation at 10 Hz cannot fill its measurement gap.
5. Evaluate live extraction separately, against independently annotated formulation/property/condition/evidence relations. The current curated replay measures neither extraction accuracy nor autonomous scientific review.

The Task 3 research demonstration is complete. Production handoff changes, a live extraction benchmark, new experiments and finished-coating qualification remain separate work. No model credentials or upstream candidate dataset were needed for this completed demonstration.
