# Task 3: select polymer candidates for a stated use

Task 3 asks two separate questions: is an extracted observation supported by its original evidence, and is the material worth following up for a particular use? This optional selection stage keeps those questions separate. Existing Phase I schema induction and Phase II extraction are unchanged.

The stage evaluates explicit criteria and records evidence gaps. It does not assign a universal material score, certify a device, or infer a polymer design rule from one paper.

## Run the synthetic example

From the repository root:

```sh
python select_candidates.py --input examples/task3/input.json --reviews examples/task3/reviews.json --out-dir outputs/task3_demo
```

The example contains invented papers, materials and source passages. Its review receipts are stipulated for demonstrating the rules; they are not evidence that anyone reviewed a real paper. The thresholds are illustrative choices, not industry standards.

Expected candidate decisions with the supplied reviews:

| Candidate | Evidence relevant to the example | Decision |
| --- | --- | --- |
| A | 95% strength recovery under the permitted partial-cut repair protocol; absolute strength 0.40 MPa at room temperature | `keep_for_followup` |
| B | Comparable measured strength recovery is 84%, below the required 90% | `exclude_for_use` |
| C | Recovery meets the criterion; required absolute strength is unavailable because supplementary information is unavailable | `retrieve_more` |

Outputs are `selection.json`, `selection.csv`, and `followups.json` in the selected output directory. The follow-up file explains which evidence or requirement needs attention.

The `--reviews` argument is optional. Without matching supported review receipts, observations cannot establish that a criterion passes or fails; affected criteria require `manual_review`.

The optional `--profile path/to/profile.json` overrides the bundle's application profile while preserving its sources, observations and review receipts. It uses the same strict JSON parser, and outputs cannot overwrite the supplied profile. Qualitative domain eligibility still needs separate review; changing numeric requirements does not automatically reclassify materials. See the current [battery case](task3-battery-screening-report.md) and its [editable profile](../examples/task3/battery_electrolytes/profile.json).

## 1. Define the use before selecting materials

An input bundle has a `profile`, `sources`, and `candidates`. The profile names the application and lists criteria. Each criterion declares a property, unit, inclusive numeric bounds, at least one relevant test condition, whether it is mandatory, and the required claim type. Missing protocol requirements go to the application owner. Claim types are `property_test` (default), `tested_device`, or an explicitly permitted `simulation`; simulated evidence remains simulated evidence.

The example requires strength recovery of at least 90% after a partial cut, using a demonstrated repair protocol no hotter than 90 degrees C and no longer than 60 minutes. It separately requires absolute tensile strength of at least 0.3 MPa measured at room temperature. Passing these two criteria is a reason for research follow-up; it leaves device loading, geometry, creep, repair cycles, uncertainty and other application requirements to be defined and checked.

Protocol bounds describe which reported tests count for this profile. A material repaired at 90 degrees C does not thereby demonstrate ambient-temperature healing. Evidence from a partial cut does not establish repair after complete severing. A result outside the requested protocol leaves a gap for this use; it is not automatically a measured material failure under the requested conditions.

## 2. Preserve one complete observation at a time

Each observation identifies its paper, formulation or sample, role in the paper, property, value, original value text, unit, baseline, claim type, conditions and source quotations. Candidate and observation paper/sample identities must agree. Background examples and cited prior work must not become the current candidate's measurements.

The original sources map source IDs to a paper ID, locator and text. Evidence identifies a source ID and an exact quotation. Mechanical checks can establish that a quote occurs in the supplied source and that IDs match. They cannot establish that the quote supports the assigned metric, sample, baseline or conditions.

Current flat Phase II `values` and `evidence` arrays do not provide all these relationships. Do not invent links or assume the first value belongs to the first sample. Prepare reviewed atomic observations before using this stage; leave unresolved records for review. This stage does not repair schema induction or change normalization.

## 3. Review scientific support separately

Review the original text, tables, figures and methods to check the assigned sample, metric, baseline, conditions and claim type. A quotation containing “89%” does not prove that 89% is tensile-strength recovery; it might describe elongation recovery. A proposed application does not establish a tested device.

A review receipt identifies the observation, paper and sample and binds the reviewed record to its supplied evidence with a `record_digest`. The supported status is an external review judgment. An extractor's own `supported` or `verified` label is not a substitute. A changed record or source requires a matching new receipt.

The digest detects changes to the reviewed content. It does not authenticate a reviewer or prove that a review was correct. A real workflow must control who issues receipts and retain the reviewer’s evidence assessment.

After adjudicating an observation, compute its digest using `selection_lib.screening.review_digest(observation, sources)`. A receipt needs the observation's `paper_id`, `sample_id`, `observation_id`, that `record_digest`, a `reviewer`, and `status` (`supported`, `unsupported` or `uncertain`). Never create supported receipts merely because a quote matched. Keep the review file separate from the extractor response.

## 4. Compare only usable observations

The selector checks identity, evidence, review binding, claim type, unit and conditions before comparing numeric bounds. Units must match exactly; this version performs no automatic conversion. A different metric or incompatible protocol cannot substitute for the required measurement.

Raw values must contain a decimal or e-notation number followed by the unchanged unit, for example `95%`, `0.40 MPa`, or `1.34e-5 %/s`, and occur literally in the evidence quote. The numeric value must agree with that raw number. A reported mean ± deviation, such as `90 ± 3%` (also `+/-`), additionally requires finite `uncertainty.lower` and `uncertainty.upper` bounds equal to the raw mean minus/plus the nonnegative deviation, with the same unit. Preserve the reported uncertainty kind; SD is not a confidence interval. Other notation, table-header unit linkage or converted units require a reviewed normalization extension; they are sent to review rather than guessed.

Missing information is distinct from failure. A comparable supported measurement below a minimum or above a maximum can fail a criterion. An inaccessible supplement, absent condition, missing absolute strength or untested application instead needs further evidence. The `missing` entries and `source_coverage` preserve the reason for the gap; “not extracted” must not become “not reported.”

When supported comparable observations disagree about passing a criterion, the decision requires review rather than choosing the most favorable value. When supplied uncertainty crosses a threshold, the decision also requires review. A point estimate without reported uncertainty can satisfy an illustrative numeric bound; that does not establish experimental certainty or reproducibility.

A supported passing observation can satisfy a criterion while another observation still needs more information. Its pending follow-up remains visible. Required repeated-repair coverage must be expressed using cycle conditions or separate criteria; one passing measurement cannot establish unspecified lifetime performance.

## 5. Read the decision and follow-up together

The four decisions are:

- `keep_for_followup`: all mandatory criteria have supported, comparable passing evidence.
- `exclude_for_use`: a mandatory criterion has comparable supported failing evidence.
- `retrieve_more`: a mandatory criterion lacks decisive evidence, with no overriding review issue or established failure.
- `manual_review`: a mandatory criterion has an unresolved evidence, identity, requirement, conflict or uncertainty problem.

Aggregation uses mandatory criteria only, in this order: `manual_review`, then `exclude_for_use`, then `retrieve_more`, then `keep_for_followup`. Optional criteria remain visible but do not decide the candidate result. Keep the criterion-level explanation: an overall review decision can coexist with a known failing result on another criterion.

“Keep” means a research candidate worth investigating for this profile. It does not demonstrate the complete application. After retrieval or review, update the observations and receipts and rerun selection; the stage produces follow-up requests but does not automatically download papers or alter existing extraction outputs.

## Validation boundary

The current [battery case](task3-battery-screening-report.md) aligns with Nina's battery-polymer scope. Four DPAL papers supply five formulations, including one explicit control. Source review gives one keep, one exclusion and three evidence gaps; actual replay gives two manual reviews and three gaps. Original scientific notation is preserved and exceeds the parser's support in the two decisive cases. Three matching labels concern manually curated null target gaps only; they are not an extraction-performance estimate. Run `python3 -m unittest -v test_task3_selection test_task3_dpal_case test_task3_battery_case` for all 41 focused checks. Domain eligibility, source review and target gaps remain supplied research inputs.

The [completed real-paper case study](task3-screening-report.md) uses five formulations from four verified members of the released DPAL library. Its [atomic inputs](../examples/task3/dpal_experiments/input.json) and [separate reviews](../examples/task3/dpal_experiments/reviews.json) are manually curated from original experiments, not Phase II output. Replay them with the existing CLI, then run `python -m unittest -v test_task3_selection test_task3_dpal_case`.

The [independent reference](../examples/task3/dpal_experiments/reference.json) contains one keep, one exclusion and three retrieval decisions. The [actual replay](../examples/task3/dpal_experiments/evaluation.json) contains one keep, two manual reviews and two retrievals: original table-header unit linkage and thousands-comma notation exceed current normalization support. Do not replace the scientific reference with software outputs or silently edit raw source notation. No production parser change is included in this case study.

The earlier [discovery register](../examples/task3/dpal_evidence.json) still describes literature families, not tested formulations, and must not be passed to the numeric selector. DPAL's paper tags guide discovery but cannot establish numerical performance.

The synthetic example verifies intended rule behavior on explicit inputs. It does not measure real-paper extraction accuracy, scientific review quality, general polymer-screening performance or time saved. A real evaluation needs independently annotated paper/sample/property/condition/evidence relationships and stated application criteria, including missing evidence and challenging negative cases.

The Burnworth optical-healing record preserves two intentional null target values alongside source-reviewed protocol facts. It does not assign a family modulus range to an individual sample or turn two exposures into a quoted scalar closure time. Its missing mode/substrate conditions correctly require retrieval.
