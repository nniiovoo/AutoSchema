# Task 3: polymer electrolyte screening for AutoSchema

Prepared 27 October 2026 on the fork's `task3-selection` branch.

**Simple explanation:** check that a polymer's reported result belongs to the right material, then decide whether it meets the requirements of one battery use—or needs more evidence.

This is the current small Task 3 demonstration for Nina's **battery-polymer scope**. The earlier wood-coating example remains a historical method exercise. Her other scope is disulfide polymers; a battery example does not have to contain disulfide bonds. Nina's query-generation work supplies the discovery context; this study checks candidate evidence afterward. These four papers are verified DPAL members, but membership in Nina's unidentified seed set is not established. [Nina's summary](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit), [reading notes](nina-polymer-scope-reading-notes-2026-10-27.md), [DPAL release](https://github.com/kmiller621/DPAL/releases/tag/July2025).

The source-reviewed decisions are **one keep, one exclusion and three evidence gaps** across four papers and five formulations, including one performance control. The actual selector produces **two manual reviews and three evidence gaps**. This difference exposes a scientific-notation limitation; it is retained in the results.

## Step 1 — Choose one specific use

We want a first-stage shortlist of **nonaqueous polymer electrolytes for lithium-metal cells operated at 30°C**. An electrolyte lets ions move between electrodes. This example first checks how well it conducts ions; complete battery suitability needs additional evidence.

For this demonstration, require reported **ionic conductivity ≥ 0.0001 S/cm at 30°C**, measured by impedance spectroscopy, EIS, between blocking steel electrodes. The exact salt-containing formulation must be identifiable. This is an analyst-selected research threshold after exploratory reading, not an industry standard or universal definition of a good electrolyte. It was frozen before the separate reference review and software replay.

The [editable rule table](../examples/task3/battery_electrolytes/profile.json) contains the threshold, units, temperature and method. SS retains the source's meaning: Pei explicitly uses sheet steel. Thickness, assembly, resistance definition and electrode details remain in the records. Accepting reported conductivity for this broad entry screen does not establish identical geometry or isolate bulk conductivity across studies. We do not rank the papers.

## Step 2 — Apply two layers of rules

| Layer | What we check | If unresolved |
| --- | --- | --- |
| General evidence checks | Correct paper and exact sample; correct property/value/unit; original source and location; linked formulation/test conditions; measured, simulated or proposed claim | Review the record or request evidence. |
| Rules for this use | Eligible lithium-salt electrolyte; 30°C conductivity from the permitted test; at least 0.0001 S/cm | Exclude only a comparable failing measurement. Otherwise request missing evidence. |

General evidence principles stay the same when the application changes. The use-specific rule table changes. The numeric engine requires explicit bounds and conditions; **qualitative eligibility remains a reviewed input** in [eligibility.json](../examples/task3/battery_electrolytes/eligibility.json), not an automated chemistry classifier. Do not disguise eligibility as an invented numeric performance score.

“Keep” means continue research after this entry check. “Exclude” concerns this shortlist only. “Need more evidence” is neither a pass nor an experimental failure. Software evidence/format problems receive a separate **manual review** status.

## Step 3 — Check four real experimental papers

| Paper and link | Material examined | Original evidence locations |
| --- | --- | --- |
| [Pei et al., 2024: Interfacial self-healing polymer electrolytes](https://doi.org/10.1038/s41467-023-43467-w) | PTMG-HDI-BHDS/LiFSI 2:1 by mass; PTMG-HDI/LiFSI 2:1 control | Main electrochemical-characterization paragraph/Fig.3a/b; electrolyte-preparation and electrochemical Methods; SI Figs.14/16. |
| [Cao et al., 2021: Imine-bond self-healing electrolyte](https://doi.org/10.1039/d0ra10035h) | **ShSPE-3**, LiTFSI, EO/Li molar ratio 16:1 | Main Fig.8; SI recipe, EIS methods and Fig.S3. Distinguish salted ShSPE-3 from unsalted ShSP-3. |
| [Chen et al., 2021: Diels–Alder electrolyte membrane](https://doi.org/10.3390/polym13234155) | SHPEM, source-named P(MMA-BA-(F-MA)):BMI-LiBOB; copolymer:BMI 2:1.1 | Methods §§2.3–2.6; Results §3.3/Fig.6 and SI Fig.S2. Preserve BA/BMA naming and liquid-state ambiguities. |
| [Chen et al., 2023: Zwitterionic ionic-gel electrolyte](https://doi.org/10.3390/batteries9090452) | SHIGE: D-IEM/SBMA polymer with 1 M LiTFSI in EMIM TFSI | Official PDF §§2.4/2.6, p.8/Fig.3. Exact polymer/ionic-liquid proportion remains unspecified in the checked method. |

Original full texts and available SI were read, not just abstracts or DPAL tags. [Provenance](../examples/task3/battery_electrolytes/provenance.json) records exact DPAL DOI matches, original-file hashes and URLs. Downloaded papers stay outside Git. Discovery tags cannot replace original preparation details.

## Step 4 — Make the source-based decisions

| Formulation | Checked conductivity evidence | Decision | Why / next action |
| --- | --- | --- | --- |
| Pei BHDS/LiFSI 2:1 | **0.00024 S/cm at 30°C** | **Keep for follow-up** | Above 0.0001 in the permitted reported test. Continue with salted-material healing and battery checks. |
| Pei HDI/LiFSI 2:1 control | **0.000065 S/cm at 30°C** | **Exclude from this shortlist** | Below the threshold. This is a performance control; dynamic-polymer eligibility is not independently established here. |
| Cao ShSPE-3 | 0.000167 S/cm at **60°C**; **30°C EIS is plotted** | **Need more evidence** | Obtain exact 30°C conductivity/fit and geometry, or declare a digitized estimate with uncertainty. Do not substitute 60°C. |
| Chen 2021 SHPEM | 0.000169 at **25°C**, 0.000269 at **35°C**, S/cm | **Need more evidence** | No exact 30°C numeric entry established. Clarify liquid state/formulation. Do not silently interpolate. |
| Chen 2023 SHIGE | 0.000906 S/cm at **25°C**; **30°C is plotted** | **Need more evidence** | Obtain exact 30°C value and polymer/ionic-liquid ratio. A plotted point does not supply an exact extracted scalar. |

The three unresolved materials are not thereby poor electrolytes. Their reported results remain valid under their established conditions. The [reference](../examples/task3/battery_electrolytes/reference.json) was separately source-reviewed and frozen before replay. It is assistant adjudication, not authenticated human ground truth or a blinded benchmark.

## Step 5 — Ask what a passing result still does not prove

Pei is the worked example. Match the **salted 2:1 BHDS formulation** to its 30°C conductivity, then check SS/electrolyte/SS EIS, total-resistance calculation and the dual-integrated assembly about 200 μm thick. Do not assign identical architecture to the HDI control. This entry result passes, but it does not isolate why the formulations differ. [Pei primary paper](https://doi.org/10.1038/s41467-023-43467-w).

Keep healing and cycling evidence attached to its own sample. Pei's neat-polymer mechanical/scratch results do not automatically describe the LiFSI-containing electrolyte. Main text and SI disagree on symmetric-cell lifetime and two full-cell capacity values; those remain unresolved and are not screening gates. In Chen 2021, Methods gives SHP thickness 12 μm while Results says about 15 μm; the separate 10 μL-wetted result cannot become a dry-matrix measurement. SHIGE has conflicting cycling temperatures and acknowledges possible residual solvent. [Pei SI](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-43467-w/MediaObjects/41467_2023_43467_MOESM1_ESM.pdf), [Chen 2021](https://doi.org/10.3390/polym13234155), [Chen 2023](https://doi.org/10.3390/batteries9090452).

Before full battery selection, define cathode/loading, temperature, current/rate, areal capacity, pressure and electrolyte amount. Then check lithium compatibility, stability, transference, durability and exact-formulation healing. Optical closure, recovered strength and recovered conductivity are different endpoints. Missing facts lead to specific follow-ups, rather than combining the best numbers from different samples.

## Step 6 — Compare with the actual selector

The input is manually curated from primary papers. This run uses AutoSchema's existing Task 3 selector; **it does not run model extraction, schema induction or automatic retrieval**. Known non-target numbers remain in `related_results`. Three target-gap observations deliberately have null values; the software is not credited with discovering those gaps or extracting their numbers.

| Record | Source reference | Actual selector | Explanation |
| --- | --- | --- | --- |
| Pei BHDS | Keep | Manual review | Original multiplication/exponent notation exceeds current parser support. |
| Pei HDI control | Exclude | Manual review | Same notation problem; the scientific exclusion remains in the reference. |
| Cao | Need evidence | Retrieve more | Exact target number remains null; 30°C plotted evidence is preserved. |
| Chen 2021 | Need evidence | Retrieve more | Reviewed non-target protocol is 25°C; no target substitution. |
| SHIGE | Need evidence | Retrieve more | Exact target number remains null; 30°C plotted evidence is preserved. |

The Pei raw values retain original multiplication signs and exponents. The parser reads the coefficient before rejecting the numeric/raw relation and does not consume the supplied normalization explanation. Rewriting original quotations into convenient e-notation would hide this limitation. Three of five broad decisions agree, **all three being evidence gaps**; neither decisive reference case is automatically decided. This is not extraction accuracy, general screening accuracy, improved model performance or measured time saved. The old wood case has a different context/denominator and is not a before/after comparison. [Actual evaluation](../examples/task3/battery_electrolytes/evaluation.json), [worksheet](../examples/task3/battery_electrolytes/decisions.csv).

One small CLI addition, `--profile`, lets a separate rule file override numeric application requirements without editing observations/receipts. The numeric engine, schema induction and extraction code are unchanged. Eligibility still needs review when the application changes.

```sh
python3 select_candidates.py --input examples/task3/battery_electrolytes/input.json --profile examples/task3/battery_electrolytes/profile.json --reviews examples/task3/battery_electrolytes/reviews.json --out-dir outputs/task3_battery
python3 -m unittest -v test_task3_selection test_task3_dpal_case test_task3_battery_case
```

Outputs are selection JSON/CSV plus pending requests. **41 focused tests pass**, including the historical case, current evidence-gap replay and separate-profile safeguards. These tests validate software behavior and recorded artifacts, not experimental reproducibility.

## Step 7 — What AutoSchema needs next

| Improvement | Why needed |
| --- | --- |
| Atomic sample/property/value/unit/condition/evidence links | Salt-free polymer, salted film, wet membrane and integrated cell cannot exchange results merely because names resemble each other. |
| Reviewed scientific-notation and unit normalization, preserving originals | Both decisive Pei cases currently stop at manual review; table-header units need equivalent support. |
| Figure/raw-data provenance and declared approximation | Cao and SHIGE plot 30°C evidence; exact values need extraction or explicit digitization with uncertainty. |
| Formulation/state/protocol fields and conflict handling | Wet state, geometry and cycling temperature change interpretation. Preserve conflicting source statements. |
| Validated categorical eligibility beside editable numeric rules | Electrolyte role/dynamic chemistry remain supplied review; the numeric selector does not establish them. |
| Targeted retrieval, re-review and replay | Start with the same sample's methods/SI/raw data; then seek exact-formulation primary work. Requests are pending, not automatically executed. |

The requested small demonstration is complete: a defined use, two rule layers, real-paper decisions, actual replay and explicit missing evidence. Full electrolyte qualification and end-to-end extraction remain future work. [Inputs](../examples/task3/battery_electrolytes/input.json), [reviews](../examples/task3/battery_electrolytes/reviews.json), [pending actions](../examples/task3/battery_electrolytes/next-actions.json).
