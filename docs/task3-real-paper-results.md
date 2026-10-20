# Task 3: four real polymer papers

Run date: **20 October 2026**. Fork: `nniiovoo/AutoSchema`, branch `task3-selection`.

**Result: all four candidates need more evidence for the shared use.** Cornellà's 50%DA network meets the relative-strength requirement, but its absolute healed strength has not been extracted. The other papers provide useful evidence for different metrics or processes. None supplies both required measurements in this reviewed evidence pack.

This is an executed replay of **assistant-curated, source-linked observations**, using the public Task 3 selector. It is not a fresh AutoSchema model extraction, schema-induction experiment, human-annotated benchmark, material ranking or independent experimental validation. The papers were chosen to illustrate distinct evidence problems. Requirements and expectations were recorded before this suite's execution, with prior knowledge of the papers; this was not blinded validation.

## 1. Fix the use and requirements

The exploratory use is research follow-up for a removable, heat-repairable, low-stress laboratory component. This screen checks two material-coupon prerequisites:

| Mandatory requirement | Acceptance rule |
| --- | --- |
| Relative strength | Ultimate tensile strength (UTS) recovery ≥90%, compared with the original same formulation |
| Absolute healed strength | Healed UTS ≥0.3 MPa; pristine strength cannot fill this field |
| Conditions for both | Partial cut, surfaces recontacted, active heating ≤90°C for ≤60 min, mechanical measurement at reported room temperature |

These are analyst-selected teaching requirements, not industry standards. The 60 min cap covers active heating only. Total handling, cooling and aging time remains unassessed. Numerical room temperature is not invented where the paper gives only an ambient label.

Complete-cut repair, a device demonstration and powder remolding remain distinct experiments. A protocol mismatch leaves an evidence gap for this strict profile. It does not demonstrate failure under an untested protocol.

See the frozen [profile](../examples/task3/real_papers/profile.json) and [pre-execution expectations](../examples/task3/real_papers/expected.json).

## 2. Read the source before assigning the metric

Each record retains the paper, exact formulation, current-work role, metric, baseline, raw value, unit, conditions, claim category, source locator and short excerpt. The [input bundle](../examples/task3/real_papers/input.json) includes twelve short source fragments and ten observations. Context outside each fragment is summarized separately as an assistant source-reading judgment.

| Paper and formulation | Evidence retained | Where checked | What it establishes |
| --- | --- | --- | --- |
| [Cornellà et al., 2024](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adma.202407663), 50%DA dual dynamic network | Modulus recovery 100%; elongation recovery 89%; UTS recovery 98% | Publisher HTML §1.3, Fig. 3C–E; Experimental healing and tensile methods | Three different relative properties after partial-cut repair, 90°C, 1 h; mechanical tests at room temperature |
| [Li et al., 2016](https://www.nature.com/articles/nchem.2492), Fe-Hpdca-PDMS, Fe:ligand 1:2 | Fracture-strain recovery 90 ± 3% after ambient repair for 48 h; 68 ± 2% after −20°C repair for 72 h | Main pp. 621–622, Fig. 3c–d; [SI](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnchem.2492/MediaObjects/41557_2016_BFnchem2492_MOESM156_ESM.pdf) §2.5 p. 10, visually checked | SI defines healing efficiency using fracture strain. Complete cut/recontact; tensile measurement at 25°C. These percentages are not UTS recovery |
| [Terryn et al., 2017](https://researchportal.vub.be/en/publications/self-healing-soft-pneumatic-robots/), DPBM-FGE-J4000 | Young's modulus 5.0 MPa; muscle response after three damage/repair cycles; projected storage-modulus recovery range 98–99% | [Authors' submitted manuscript and SI](https://scispace.com/pdf/self-healing-soft-pneumatic-robots-jaj6eu0n3b.pdf), PDF pp. 10–13, 18, 20, 29 | Modulus, a tested pneumatic device and an author projection remain separate. Neither a range midpoint nor a numeric device-recovery percentage is invented |
| [Montarnal et al., 2011](https://lab.semi.ac.cn/download/0.23601801031433223.pdf), hard DGEBA/glutaric-anhydride network, 10 mol% Zn(acac)₂ | Approximate pristine stress at break 55 MPa; qualitative property retention after powder remolding at 240°C for 3 min | Journal pp. 966–967; Fig. 3 visually checked | Pristine strength and high-temperature reprocessing; neither establishes healed UTS after partial-cut repair |

Terryn's detailed procedure includes about 5 min heating, 35 min at 80°C, 28 min cooling and 24 h at 25°C. Their sum is approximately **25.1 h**, calculated from stated approximate stages, not a measured return-to-service time. The abbreviated 40 min heating description must not become 40 min total downtime. The submitted manuscript was accessible through a mirror; publisher and institutional PDF access failed.

For Montarnal, the source PDF contains neighboring articles. Only the target article's title through references/DOI was considered. The hard network is distinct from the paper's fatty-acid/5 mol% zinc-acetate elastomer. Cornellà's 70%DA printing result is likewise not transferred to 50%DA.

## 3. Check evidence separately from usefulness

The selector checked literal quote occurrence in supplied excerpts, paper/sample IDs, raw numeric text and unchanged units, plus separate review receipts bound to the observation and cited source content by digest. **All ten supplied observation records were accepted by those checks.** Qualitative records have null numeric values; their acceptance does not create a quantitative property.

The [review receipts](../examples/task3/real_papers/reviews.json) are explicitly assistant source-reading judgments. They are not authenticated human signatures or evidence of scientific correctness. Sample–metric–protocol interpretation still depends on the source review; a matching number alone cannot establish that relation. This run does not measure extraction precision or recall.

The real Li text exposed a bounded parser limitation. Task 3 now preserves decimal mean ± deviation text, including `90 ± 3%`, and requires the supplied finite uncertainty bounds to match the raw mean and deviation exactly with the same unit. Missing or inconsistent uncertainty goes to review. The parser does not remove the deviation, infer its statistical meaning, convert units or normalize table-header units.

## 4. Run the shared screen

| Candidate | UTS recovery ≥90% | Healed UTS ≥0.3 MPa | Candidate decision | Decisive missing evidence |
| --- | --- | --- | --- | --- |
| Cornellà 50%DA | `keep_for_followup`: reported 98%, matching partial-cut heating conditions | `retrieve_more` | **`retrieve_more`** | Absolute healed strength not extracted from Fig. 3C/data |
| Li 1:2 | `retrieve_more`: fracture-strain recovery and different repair protocol | `retrieve_more` | **`retrieve_more`** | Matched UTS recovery and absolute healed UTS |
| Terryn J4000 | `retrieve_more`: device response/projected modulus do not fill UTS recovery | `retrieve_more` | **`retrieve_more`** | Direct healed/pristine tensile measurements under matching conditions |
| Montarnal hard network | `retrieve_more`: powder remolding does not fill partial-cut repair | `retrieve_more` | **`retrieve_more`** | Direct low-temperature cut-repair strength measurements |

One of eight mandatory criterion checks passes the stated point-estimate bound; seven require further evidence. There are seven automatically queued criterion follow-ups. There is **no combined material score**. Cornellà's unverified uncertainty and geometry remain additional checks even though its reported relative point estimate passes this narrow criterion.

All four practical application assessments remain **undetermined**. A missing result is not a zero, a failed experiment or proof that the material cannot work.

## 5. Use separate diagnostics to test uncertainty and failure

Two predeclared diagnostics reuse Li's actual fracture-strain metric and matching complete-cut protocols. They are not extra papers or results under the shared UTS profile.

| Diagnostic requirement | Reported evidence | Executed decision |
| --- | --- | --- |
| ≥90% fracture-strain recovery, ambient repair 48 h, measurement 25°C | 90 ± 3%; supplied SD bounds 87–93% | **`manual_review`**, `uncertainty_crosses_requirement` |
| ≥90% fracture-strain recovery, −20°C repair 72 h, measurement 25°C | 68 ± 2%; supplied SD bounds 66–70% | **`exclude_for_use`**, for this protocol and illustrative requirement |

The ambient mean meets the inclusive cutoff. Sending an SD interval that spans the cutoff to review is a declared conservative policy, not a confidence test or a statement that the mean failed. The cold result does not reject the polymer for all uses. Li also contains a later 90 ± 2% description; that discrepancy remains unresolved in the evidence context.

## 6. Resolve gaps with a concrete next action

| Candidate | Next source work | What remains beyond this replay |
| --- | --- | --- |
| Cornellà | Obtain SI §S5; inspect/digitize Fig. 3C or obtain original data; resolve healing specimen geometry and replicates | Absolute healed strength, uncertainty, repeated repair and total downtime. SI access failed 19 October and was not retried on the run date |
| Li | Retrieve matched strength tests; inspect healed curves; clarify the alternate uncertainty and replicate descriptions | SI Table 2's 0.23 ± 0.05 MPa is pristine strength, with units in the table header. Do not multiply it by fracture-strain recovery to fabricate healed UTS |
| Terryn | Inspect Table 1/Fig. S6 for tensile values and repaired state; quantify Fig. 8 device retention with variability | Curve digitization, raw data and movies unchecked; two/three repair cycles do not establish operating fatigue lifetime |
| Montarnal | Obtain SI and matched cut-repair studies; check specimen, rate, pressure and quantitative retention for any separately chosen remolding use | No extracted recovery percentage; repeated processing and uncertainty unresolved; SI unavailable in this source review |

The application owner must separately define required force, geometry, allowable extension, service conditions, downtime, creep/fatigue and repair lifetime. Further literature cannot choose these acceptance requirements. The selector queues source work; it does not execute retrieval. Additional paper-specific checks are retained in the input's `additional_checks_not_run_by_selector` and the profile's unassessed requirements, beyond the seven criterion actions.

## Reproduce and interpret performance

From the repository root:

```sh
python -m unittest -q test_task3_selection test_task3_real_papers
python run_task3_real_papers.py
```

No models, credentials, paid calls or network access are needed to replay the reviewed records. The runner calls the public selection CLI for the shared profile and both diagnostics. It writes `selection.json`, `selection.csv` and `followups.json` per profile, and a `manifest.json` containing input/implementation hashes, Git HEAD, observed counts and expectation mismatches under `outputs/task3_real_papers/`. Hashes identify the actual working files even if Git HEAD predates uncommitted edits. Generated outputs and downloaded papers are not committed.

Observed validation: **34 tests passed** (31 selector/CLI tests plus three replay and output-protection tests); all four shared candidate/criterion expectations and both separately declared diagnostic expectations matched. These are policy replay and regression results, with separate denominators. Four purposively selected papers and supplied assistant reviews cannot establish general screening accuracy, extraction accuracy, recall, time saved or experimental reproducibility.

Phase I schema induction and Phase II extraction are unchanged. An end-to-end evaluation still needs genuine extracted atomic observations, independently adjudicated paper/sample/property/condition relations, and a larger stated-use test set with failures and missing evidence.
