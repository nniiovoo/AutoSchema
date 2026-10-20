# Task 3: evidence-based polymer screening

Completed research pack: **20 October 2026**. Scope: the DPAL article and its supplemental PDF only. This pack contains screening criteria, a checked DPAL example, decisions and an evidence-gap ledger. It does not report a material-performance benchmark or live extraction results.

**Research question:** How should AutoSchema separate reliable source information from material suitability for a particular application?

## 1. What one screening record must contain

The required unit is:

**Exact formulation and specimen state → property and value → unit and baseline → test conditions → source evidence → application requirement.**

A polymer backbone is the main chain; a dynamic-bond category describes a reversible interaction or exchange chemistry. Neither alone uniquely identifies a formulation. A property is a measured response. An application is a function the material is intended to perform. A proposed use and a demonstrated device experiment are different claims.

DPAL supplies literature-level associations. Its tagging, case studies and limitations explain why those associations cannot directly become sample-level acceptance evidence. [DPAL, main pp. 3, 6–8; supplemental methods pp. 10–11](https://doi.org/10.1016/j.matt.2025.102624).

## 2. Separate evidence support from application fit

Keep these columns independent; do not average them into a score.

| Review field | What to check | Allowed conclusion |
| --- | --- | --- |
| Source support | Original passage, table or figure supports this exact claim | Supported, contradicted, ambiguous or unavailable |
| Identity | Property, state and experiment concern the same current-work formulation | Linked, unresolved or different sample |
| Measurement | Metric definition, raw value, unit, baseline and uncertainty are preserved | Interpretable or needs review |
| Experiment category | Library association, specimen measurement, device test, simulation/projection or proposed use | Preserve the actual category |
| Comparability | Processing, measurement and service conditions answer the declared criterion | Comparable, incompatible or incomplete |
| Application fit | Supported comparable evidence meets each mandatory requirement | Pass, fail or undetermined |

An accurate quotation can still be assigned to the wrong sample or metric. A well-supported result can show poor performance. Conversely, a promising statement without methods is insufficient evidence. Replicates, controls, uncertainty and repeated testing inform experimental adequacy; a quote match does not establish reproducibility.

## 3. Concrete application and required evidence

Our **analyst-proposed example** is a laboratory soft robotic gripper that picks up and releases cell-loaded hydrogel specimens in aqueous medium at a nominal **37°C**. The function and temperature are explicit teaching assumptions, not conditions reported for the DPAL leads. The example is motivated by DPAL's biocompatible-soft-robotics case.

The owner must still set specimen dimensions, payload, allowed deformation, actuation mode, contact duration, biological endpoint and cycle life. Do not invent universal acceptance thresholds. The following are our proposed screening criteria, not numerical limits established by DPAL.

| Requirement | Metric or evidence needed | Conditions needed before comparison |
| --- | --- | --- |
| Relevant biological response | Chosen endpoint relative to a matched control, with its definition, uncertainty and replicates | Full formulation; biological model; contact/extract exposure; dose, medium, temperature, duration and controls |
| Successful gripping | Pick-and-release success, supported payload and specimen deformation | Same device/formulation; object geometry; actuation input; aqueous state; temperature; repetitions |
| Adequate compliance and strength | Appropriate modulus, strain at failure and deformation response | Geometry, hydration, conditioning, loading direction/rate and specimen state; a larger value is not universally better |
| Stable repeated operation | Functional retention, fatigue, creep or dimensional drift appropriate to the mechanism | Load/input amplitude, frequency, dwell, environment, duration and cycle count |
| Feasible fabrication and actuation | Demonstrated process and operating window | Temperature, pressure/voltage/other stimulus, solvents or residual components, and resulting device function |
| Repair, **only if required** | A named recovery metric and restored device function | Damage severity, contact, repair conditions, cooling/aging, original same-formulation baseline and repeated repair |

A dynamic bond does not by itself establish self-repair. A coupon modulus cannot substitute for gripping success. Biological evidence on one ingredient cannot be transferred to a different complete formulation.

## 4. Operational screening rules

Apply the rules in order, retaining a reason and owner for each unresolved item.

| Rule | Action |
| --- | --- |
| R1: identify the source and sample | Preserve paper/locator, exact formulation, current-work role and state. Unresolved identity goes to review. |
| R2: verify the observation | Check the metric–value–unit–baseline relation against its original context. Reject an unsupported claim or correct/review it; this does not prove the material failed. |
| R3: establish the experiment category | A device criterion requires an actual experiment on the identified material and relevant function. A tag, proposal or simulation cannot silently fill it. |
| R4: establish the requirement | Undefined acceptance bounds or service conditions go to the application owner. More literature cannot choose the owner's specification. |
| R5: compare compatible evidence | Keep different protocols separate. Unit conversion requires a recorded, reviewed transformation. Different conditions alone do not demonstrate failure at the requested condition. |
| R6: handle uncertainty and conflict | Preserve the reported uncertainty kind. A threshold-straddling interval or conflicting comparable results requires review under the current conservative policy; SD is not a confidence interval. |
| R7: decide fit | After the preceding reviews, adequate comparable passing evidence supports `keep_for_followup`; a supported mandatory failure supports `exclude_for_use`. Missing decisive evidence requires `retrieve_more`. |
| R8: retain the decision boundary | State which use and protocol the decision concerns. Keep means advance research, not complete device qualification. Do not rank incomparable or incomplete records. |

A separately declared hard process limit can reject a **demonstrated processing route**. It does not prove that the polymer could never work through another route. The existing numeric selector treats condition mismatches as evidence gaps; this report does not claim that a separate process-feasibility veto has been implemented.

## 5. Worked DPAL example: five checked reading leads

DPAL Case study 3 reports an intersection of **22 paper records** and lists the following backbone–bond associations with citation totals. These are literature groups and a historical bibliographic snapshot, not five tested formulations or current citation queries. [DPAL, Case study 3, p. 6; related Fig. 4C, p. 8](https://doi.org/10.1016/j.matt.2025.102624).

| Lead | Reported backbone–bond association | Reported citations, metadata only | Evidence judgment | Reading decision | Material-fit decision |
| --- | --- | ---: | --- | --- | --- |
| L01 | Poly(saccharide) / catechol | 713 | Association supported as reported | Keep for targeted reading | Retrieve primary evidence; fit undetermined |
| L02 | Poly(acrylic acid) / catechol | 661 | Association supported as reported | Keep for targeted reading | Retrieve primary evidence; fit undetermined |
| L03 | Poly(vinyl alcohol) / borate ester | 472 | Association supported as reported | Keep for targeted reading | Retrieve primary evidence; fit undetermined |
| L04 | Poly(vinyl alcohol) / catechol | 249 | Association supported as reported | Keep for targeted reading | Retrieve primary evidence; fit undetermined |
| L05 | Poly(vinyl alcohol) / cyclodextrin | 151 | Association supported as reported | Keep for targeted reading | Retrieve primary evidence; fit undetermined |

For every row, the exact formulation, matched biological/device measurements and acceptance limits are unresolved in this source-bounded case. This does not mean the underlying papers lack experiments. No row receives a fabricated sample ID or numerical material observation. Citation ordering is reproduced as source metadata, not our performance ranking. Paper groups may overlap; their counts cannot be treated as independent experimental samples.

The checked output is **five relevant reading leads, zero formulation-level approvals, and zero performance-based material exclusions**. All five material-fit decisions remain undetermined. This is a result of the evidence scope, not a negative experiment on any family.

Machine-readable evidence: [dpal_evidence.json](../examples/task3/dpal_evidence.json). Editable worksheet: [dpal_screening.csv](../examples/task3/dpal_screening.csv). These are literature-triage records, **not** inputs to the numeric material selector.

## 6. What is excluded, and why

The following are **constructed audit examples**, not statements attributed to DPAL or observed AutoSchema mistakes:

| Inference to check | Decision |
| --- | --- |
| Highest citation total means best gripping performance | Reject the claim: citations are not a functional measurement. |
| Co-occurring tags establish this formulation passed the proposed 37°C gripper test | Reject the claim: formulation, protocol and result are missing. |
| A family-level association establishes biological compatibility for every formulation | Reject the transfer: identity and exposure are unspecified. |
| An absent numerical result means the material failed | Reject the inference: missing evidence is not a measured failure. |
| An absent tag proves a property was never studied | Reject the inference: metadata-only discovery can omit full-text information. |

This shows claim-level exclusion without pretending to have measured material-level failures. Demonstrating actual material retention and exclusion requires applicable experimental evidence, which this single library article does not provide for these rows.

## 7. Missing evidence and when to retrieve more

The [evidence register](../examples/task3/dpal_evidence.json) assigns six gap IDs to every lead:

| Gap | Next action | Owner |
| --- | --- | --- |
| G01: exact formulation and state | Identify the underlying record, sample labels, composition and processing | Source reviewer |
| G02: application requirements | Define load, geometry, actuation, exposure and acceptance bounds | Application owner |
| G03: quantitative measurements | Inspect same-sample figures, tables, methods, baseline and uncertainty | Source reviewer |
| G04: actual device experiment | Separate tested function from coupon results, simulation and proposed use | Source reviewer |
| G05: relevant biological evidence | Match the full formulation and exposure to the chosen endpoint and controls | Owner, then source reviewer |
| G06: comparability and repeatability | Check conditioning, replicates, cycles, creep and conflicts | Source reviewer |

Retrieve only to answer a named question that could change a criterion. Stop the numerical comparison while requirements are undefined. If a valid mandatory failure already settles the stated use, do not search selectively for a more favorable number. For inaccessible or unlocated evidence, record coverage and the unresolved decision; do not write “not reported” without an adequate source check.

These follow-ups are **queued, not executed**: the user-selected scope remains DPAL and its supplemental PDF. No additional materials paper was introduced.

## 8. AutoSchema integration and validation boundary

The existing Task 3 selector can compare reviewed atomic material observations against declared numeric criteria. Its evidence receipts are supplied judgments, not authenticated human reviews or scientific proof. Paper-level DPAL leads must first acquire genuine formulation/property/condition relations; bibliographic counts must never be passed as measurements.

This pack completes the DPAL-only research deliverable: criteria, one concrete application example, five checked lead decisions, rejected inference examples and actionable gaps. It does not claim extraction accuracy, validated material-selection performance or an autonomous literature search.

For a later authorized material evaluation, assess source/sample alignment, comparable criterion outcomes, unsafe retentions, incorrect exclusions and decision reasons separately. Returning “need more evidence” everywhere is not proof that the selector recovered useful evidence. No unified score or universal material ranking is needed.

The [practical AutoSchema preparation plan](task3-autoschema-plan.md) separates completed work from the remaining application requirements, source evidence, schema/alignment prerequisites and evaluation steps. It includes the verified synthetic software checks and makes no claim that automatic extraction-to-screening integration is complete.
