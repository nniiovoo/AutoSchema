# Task 3: practical plan and preparation for AutoSchema

Prepared 20 October 2026. Current research scope: the DPAL article and its supplemental PDF. This is an implementation and evaluation plan; proposed steps below are not reported as completed experiments.

**Our task is to verify the evidence behind polymer observations, then screen the supported observations against one defined application, explaining every retention, exclusion and unresolved decision.**

The assignment permits manually prepared test inputs before connecting an extractor. Keep two questions separate: **does the source support this observation?** and **does it meet this use's requirements?** See the [assignment interpretation](task3-assignment-reassessment.md) and [screening criteria](task3-screening-report.md).

## 1. Know what is ready and what is missing

Already prepared:

- A screening report with evidence checks, application criteria, decisions and retrieval stopping rules.
- A [checked evidence register](../examples/task3/dpal_evidence.json) and [editable worksheet](../examples/task3/dpal_screening.csv) covering five DPAL chemistry-family reading leads.
- A [generic screening stage](../selection_lib/screening.py), [command-line entry point](../select_candidates.py), synthetic demonstration and [test suite](../test_task3_selection.py).

DPAL Case study 3 supplies paper-level associations, without the same-formulation measurements needed to approve these leads for our device. Quantitative-extractor integration is future work. [DPAL, Case study 3, p. 6; limitations and outlook, pp. 7–8](https://doi.org/10.1016/j.matt.2025.102624).

**The highest-risk mismatch is treating a paper-level association as a tested material.** Our five leads are retained for reading; none has an admissible atomic material measurement in this case. Genuine performance-based material retention/exclusion remains an evaluation gap.

## 2. Phase A: define one use and its acceptance requirements

The current teaching example is a laboratory gripper handling cell-loaded hydrogel specimens in aqueous medium at nominal 37°C. This is an analyst-proposed scenario, not a DPAL experiment or acceptance standard. The application owner must define:

- Object dimensions, payload, allowed deformation and successful pick-and-release behavior.
- Actuation input, medium, temperature, exposure duration and required operating cycles.
- Biological model, endpoint, contact context, controls and acceptance bounds.
- Mandatory requirements versus desirable features; repair is optional unless explicitly required.

Record each requirement's metric, unit, bound, conditions and rationale. A larger modulus is not automatically better, and ingredient-level biological evidence cannot establish compatibility of a complete formulation. The [report's application table](task3-screening-report.md#3-concrete-application-and-required-evidence) provides the worksheet structure.

**Acceptance:** every mandatory requirement is defined, or visibly assigned to the owner as unresolved. Do not manufacture numerical limits to make the example executable. The existing synthetic repair/strength profile is a separate rules demonstration; its thresholds cannot be reused as gripper requirements.

## 3. Phase B: prepare auditable evidence records

For each genuine material observation, preserve:

`paper + formulation/sample/state + current-work role + metric + raw value/unit + baseline + conditions + claim category + original locator/context`

Review the passage with the necessary table, figure and methods. Check the same current-work sample and metric. Preserve `property_test`, `tested_device` and `simulation`; a proposed use cannot substitute. Record replicates, uncertainty, controls and source coverage; source support alone does not establish reproducibility.

Use separate review receipts after semantic review. The existing digest detects changes to supplied observations and sources; it neither authenticates the reviewer nor proves scientific correctness. [Evidence and review checks](../selection_lib/screening.py#L23-L111).

**Acceptance:** every accepted observation has a traceable locator and reviewed relations. Unknown identity, inaccessible supplements and unextracted information retain their precise reasons. The DPAL leads remain literature-triage records with empty measurements. Further material-paper evidence is outside the current scope and would require an expanded study.

## 4. Phase C: apply executable decisions

Apply the [documented selector contract](task3-selection.md) in this order:

| Check | Decision or action |
| --- | --- |
| Unresolved identity, absent observation baseline, unsupported assignment, stale review or undefined requirement | `manual_review`, with the responsible reviewer or application owner |
| Missing value or required experiment/condition, or a reviewed result using a different required baseline | `retrieve_more`, with a specific question and coverage record |
| Different protocol | Keep separate; do not interpret it as failure under the requested conditions |
| Conflicting comparable outcomes or uncertainty crossing a bound | `manual_review` |
| Supported comparable mandatory failure | `exclude_for_use`, naming the failed requirement |
| All mandatory requirements have supported comparable passes | `keep_for_followup`, limited to this research profile |

Keep criterion-level reasons alongside the overall result. Current aggregation prioritizes review, then exclusion, then retrieval, then retention. A missing result is not a measured failure. A passing result is not complete device qualification. The current selector queues follow-ups but does not retrieve sources. [Comparison and aggregation](../selection_lib/screening.py#L151-L295).

## 5. Phase D: prepare the AutoSchema connection

First reconcile the schema handoff: [induction emits](../schema_lib/fields.py#L283-L293) examples/evidence examples, while [extraction expects](../extract_lib/schema_loader.py#L38-L63) value types and evidence snippets. A controlled synthetic probe loaded the produced shape as `string` with empty evidence snippets; normalizing values A/B kept A while retaining both quotes. This is a contract failure, not a DPAL extraction result. Specify explicit key mappings and reviewed cardinality; do not make every field an array.

Keep discovery leads, atomic observations and application profiles separate. Preserve source relations before normalization; route incomplete records to review.

The [postprocessor](../extract_lib/postprocess.py#L33-L116) separately deduplicates values, caps single-valued fields and truncates quotations. Flat `values`/`evidence` output cannot establish sample–metric–condition links by list position. A future adapter must preserve these relations and context; it is not implemented.

The selector currently supports numeric criterion bounds and simple condition rules, exact units and supplied semantic reviews. It does not perform unit conversion, complex biological/device adjudication or a separate hard process-route veto. Those decisions need reviewed preparation or a deliberately specified extension.

**Acceptance:** family tags, citations and proposed applications cannot enter as numerical material-performance evidence; ambiguous mappings remain unresolved.

## 6. Phase E: evaluate and present honestly

Use the following test families, marking completed runs separately from proposed tests:

- **Rule behavior:** supported pass/fail, missing evidence and undefined requirements.
- **Evidence integrity:** wrong sample/metric, quotation absent, changed record/source and invalid review.
- **Comparability:** units, baseline, protocol, experiment category, conflict and uncertainty.
- **Integration:** multiple formulations, repeated values, shared context, table units and truncated evidence; these adapter tests are planned.
- **Real evidence evaluation:** independently checked material observations, useful retained/excluded cases and retrieval outcomes; unavailable within this DPAL-only case.

Before a later real-material run, freeze the source-reviewed reference decisions and their reasons independently of selector output. Compare evidence support, protocol comparability and application fit separately. Report incorrect retentions, incorrect exclusions, correct and unnecessary abstentions, and reason/owner accuracy as counts with denominators. Returning “need more evidence” for every lead does not demonstrate useful material selection. Do not report extraction accuracy, time saved or general screening performance from synthetic tests.

Verified 20 October 2026: 31 existing tests passed. A fresh synthetic CLI run returned A: `keep_for_followup`, B: `exclude_for_use`, C: `retrieve_more`. These verify controlled software behavior, not real-polymer extraction or screening performance.

Completion checklist, separating preparation from later validation:

- [x] Scope, screening rules, DPAL reading decisions and gaps documented.
- [x] Existing code boundary and required integration contract identified.
- [x] Existing tests and synthetic demonstration rerun.
- [ ] Application owner supplies complete acceptance requirements.
- [ ] If research scope expands: material evidence supports independently reviewed pass/fail cases.
- [ ] A future adapter preserves atomic relations and passes integration tests.
- [ ] Real-case outcomes are compared with the checked reference and reported with limitations.

Present the assignment, two separate judgments, decision flow, DPAL example and remaining work. Label the result **screening preparation and evidence-gap triage**, while reserving material-performance claims for the later evidence evaluation.
