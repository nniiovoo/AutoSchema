# Task 3: checked polymer screening for one application

Completed case study: **21 October 2026**, on the `task3-selection` fork. We selected one application, checked four formulations from three real experimental papers in DPAL, froze reference decisions independently of selector output, and ran the existing selector. This completes the requested small screening demonstration and documents the software's disagreements. It does not claim that extraction-to-selection automation is complete.

**Task 3 separates two questions: does the original source support the observation, and does comparable evidence meet this application's requirements?** Missing evidence is a distinct outcome, not a failed experiment. No combined material score or ranking is used.

## 1. Real papers with verified DPAL provenance

We downloaded the authors' [July 2025 DPAL release](https://github.com/kmiller621/DPAL/releases/tag/July2025), parsed its 15,460 CSV records, and matched exact titles, DOIs and Zotero keys. The CSV SHA256 is `33d3d63d837e5687ad80001aef1a3103180d011831f925a1a66007fbbcc4fca8`. Ordinals count data records after the header, not physical CSV lines. These papers are verified library members; we do not assert membership in DPAL's biocompatible-soft-robotics intersection.

| Experimental paper | DPAL record / key | Role in this case |
| --- | --- | --- |
| [Balkenende et al. (2016), Optically responsive supramolecular polymer glasses](https://doi.org/10.1038/ncomms10995) | 13072 / YQL784D6 | Same-paper neat/blended formulations with matched stiffness measurements |
| [Wang et al. (2020), Room-temperature autonomous self-healing glassy polymers with hyperbranched structure](https://doi.org/10.1073/pnas.2000001117) | 11970 / YW8WL95T | Reported stiffness with unresolved target measurement protocol |
| [Tzoumani et al. (2023), Room-Temperature Self-Healable Blends of Waterborne Polyurethanes with 2-Hydroxyethyl Methacrylate-Based Polymers](https://doi.org/10.3390/ijms24032575) | 12814 / NIAFVEMT | Scratch-healing result that cannot establish the requested formulation/protocol measurements |

The [provenance manifest](../examples/task3/dpal_experiments/provenance.json) preserves release information, selected records and original-document hashes. Full papers and the CSV are archived outside the repository; only short exact excerpts and paraphrased assessments are committed. The Tzoumani PDF obtained through a mirror has an MD5 checksum matching the original publisher PDF checksum declared in primary EuropePMC XML; its supplement came from EuropePMC's original bundle. Wang's main article was available, but a usable supplement was not obtained. Access failure is not evidence that a measurement was never reported.

## 2. Choose an application before making decisions

The application is a **research shortlist for a stiff, UV-repairable coating on rigid wood**, allowing hot-melt fabrication and local photothermal heating. It is a laboratory entry screen, with separately fabricated film stiffness explicitly permitted as a same-formulation proxy. It is not a qualification of an installed protective coating.

These are **analyst-selected demonstration requirements**, chosen after exploratory reading and fixed before the independent reference and software replay. They are not industrial standards, paper recommendations or a blinded material-discovery benchmark.

| Mandatory criterion | Acceptance requirement | Required evidence |
| --- | --- | --- |
| C1: initial stiffness | Dynamic **flexural storage modulus E' at least 3.0 GPa** | Unhealed material; DMA three-point bending; 25 C; 1 Hz; heating 5 C/min |
| C2: optical repair response | Visible razor-cut closure within **30 s**, allowing a remaining shallow scar | 300 micrometre coating on wood; UV 320-390 nm; 500 mW/cm2; actual timed optical experiment |

C1 asks for stiffness, not tensile strength, static flexural modulus or shear storage modulus. C2 asks for a limited visible response, not complete microscopic restoration, recovered strength or repeated-repair durability. The thresholds make the example executable; their engineering relevance must be revisited for any real product.

Preserve the source's reported plus/minus extent. For this conservative demonstration, a band wholly above or below the bound supports that direction; crossing it requires review. The statistic in the glass paper is not identified, so its band is not relabelled SD or a confidence interval. This is a screening convention, not a statistical significance test.

## 3. Checked evidence and material decisions

Original pages, relevant tables/figures and available methods/supplements were checked. A separate research assistant derived the reference without reading selector output; another independently audited the glass evidence. These are assistant source judgments, not human expert ground truth. The [reference file](../examples/task3/dpal_experiments/reference.json) preserves the frozen decisions and their reasons.

| Exact material | What the original evidence establishes | Scientific screening decision |
| --- | --- | --- |
| Neat amorphous **(UPyU)3TMP** | C1: 3.65 +/- 0.51 GPa; descriptive band 3.14-4.16. C2: first-step visible closure after 12 s under target wood/UV conditions; a shallow scar remains. | **Keep for follow-up:** both narrowly defined criteria pass. |
| **(UPyU)3TMP with 1.5 equivalents UPy-C6-U-EH** | C1: 1.47 +/- 0.29 GPa; band 1.18-1.76 under the same DMA protocol. Target repair was not established for this blend. | **Exclude for this use:** a supported mandatory stiffness failure settles the screen. Missing repair remains a gap, not a second failure. |
| **RHP-1**, MBA/BDA molar feed 1/1.125 | Main article reports 2,721 MPa at 25 C. Required DMA mode, frequency and heating rate remain unverified; target timed UV-on-wood repair is unestablished. | **Need more evidence:** do not convert a lower, unqualified number into a comparable failure. |
| **WPU1/20P(HEMA-co-DMAM80)** | Qualitative water-triggered scratch closure on a free film. Supplementary DMA concerns different formulations at 10 Hz, not this formulation under C1. | **Need more evidence:** neither requested measurement is established; a different repair trigger is not proof of failure. |

Sources and locators: [Balkenende, main pp. 3-6, Table 1, Fig. 6a/b p. 7 and Optical healing methods p. 8](https://doi.org/10.1038/ncomms10995); [Wang, thermomechanical results, Fig. 2C/D and Materials and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC7260978/); [Tzoumani, Fig. 8e/f p. 11, preparation p. 13, repair methods p. 14 and supplemental Fig. S2](https://pmc.ncbi.nlm.nih.gov/articles/PMC9916575/).

### Walk through the neat/blended pair

1. **Identify the formulation.** Keep neat and chain-stopper blend separate. Never transfer the neat coating's repair result to the blend.
2. **Identify the metric and conditions.** Table 1 names storage modulus, assigns its GPa header, and identifies three DMA measurements. Common methods provide the matching protocol. A static flexural modulus elsewhere in the same table is a different quantity.
3. **Check the requirement.** The neat reported band clears C1. The 1.5-equivalent blend's band lies below C1. This same-paper comparison supports a use-specific exclusion without ranking unrelated papers.
4. **Check what repair actually means.** The neat result meets C2's shallow-scar allowance. Methods describe another exposure for scar removal; the first step must not become a claim of complete repair. Local heating reaches 188 C. Hot repair and an ambient pre-repair stiffness test are separate conditions.
5. **Keep the decision boundary.** Retention advances investigation. It does not establish adhesion, abrasion resistance, barrier performance, repeatability or durability. Film DMA was not measured in situ on wood. [Original experiment and methods](https://doi.org/10.1038/ncomms10995).

For the WPU record, “20” means additive mass relative to WPU solids, not 20% of the whole blend; DMAM80 is the nominal feed designation. Its available mechanical studies cannot be borrowed across formulation and frequency. A source label mentioning healing is useful discovery information, but it cannot fill an unmeasured timed UV criterion. [Tzoumani, sections 2.2, 2.4 and 3.3; Fig. 8; supplement](https://doi.org/10.3390/ijms24032575).

## 4. Actual selector replay: show the disagreements

We manually prepared atomic observations with original notation, identities, conditions, locators and separate source-review receipts. The existing selector and Phase I/II code were **not changed**. We did not append table units, remove thousands commas or invent a missing condition to make records pass.

| Candidate | Frozen source-based reference | Actual selector | Explanation |
| --- | --- | --- | --- |
| Neat UPy glass | Keep | Keep | Inline value/unit, matching reviewed conditions and both criteria admitted. |
| 1.5-equivalent blend | Exclude | Manual review | Original table cell has no inline unit; the parser cannot use its separately cited GPa header (`raw_unit_mismatch`). |
| RHP-1 | Need more evidence | Manual review | Thousands-comma notation triggers `numeric_and_raw_value_mismatch` before protocol comparison. Resolving notation would still leave scientific protocol and repair gaps. |
| WPU composite | Need more evidence | Need more evidence | Prepared input explicitly records missing target measurements. This does not demonstrate that an extractor independently found the gaps. |

The replay matches **2 of 4 overall decisions** and **6 of 8 criterion decisions**. It makes no unsupported retention or incorrect exclusion in these four cases, but adds two review decisions. The supported exclusion is missed by automation; the RHP evidence gap is reached only as a source-format review issue. Do not call this general screening accuracy or successful evidence retrieval.

This small purposive case diagnoses two concrete handoff limitations: **table cell-to-header unit relations** and **reviewed normalization of numeric notation**. A supplied semantic review does not override mechanical validation. Future changes must preserve original text and explicit transformations rather than weakening the evidence gate. Upstream flat extraction arrays also still need formulation/metric/condition relations before this stage.

Checked results: [evaluation.json](../examples/task3/dpal_experiments/evaluation.json), [decision worksheet](../examples/task3/dpal_experiments/decisions.csv), [atomic inputs](../examples/task3/dpal_experiments/input.json), [separate reviews](../examples/task3/dpal_experiments/reviews.json). These are real-paper **curated inputs and an actual selector run**, not actual LLM extraction output.

## 5. Follow-up rules and stopping points

| Candidate / gap | Owner and next action | Stopping rule |
| --- | --- | --- |
| Neat: finished-coating performance | Application owner defines adhesion, barrier, abrasion and lifetime needs; source reviewer checks relevant experiments | Do not promote research retention into product readiness. |
| Blend: table unit; unknown repair | Software/evidence reviewer specifies traceable cell/header normalization; retain repair unknown | Established stiffness failure already excludes this profile; more repair searching cannot reverse it. |
| RHP-1: notation and protocol | Evidence/software reviewer handles the comma without changing the raw string; source reviewer obtains usable original SI and verifies DMA | A corrected number alone cannot establish comparability. If access remains blocked, preserve that status. |
| RHP-1: repair | Source reviewer seeks an exact-formulation timed coating/wood UV experiment | Contact healing is not a substitute; if no applicable evidence is found, a new experiment is needed. |
| WPU: stiffness and repair | Source reviewer seeks exact-formulation target DMA and timed wood/UV evidence | Do not transfer other formulations' 10 Hz data or treat untimed water healing as a failed UV test. |

The code emits six pending actions. Its early format gates do not enumerate every later scientific gap; the source-based ledger above remains necessary. Retrieval was performed for this study's original papers and supplements, but queued future actions were not autonomously executed.

## 6. Reproduce and report the completion boundary

From the repository root:

```sh
python select_candidates.py --input examples/task3/dpal_experiments/input.json --reviews examples/task3/dpal_experiments/reviews.json --out-dir outputs/task3_dpal_experiments
python -m unittest -v test_task3_selection test_task3_dpal_case
```

The new checks bind fixture reviews to their cited source revisions, replay actual CLI decisions, retain the two reference disagreements and prevent unsupported numeric formats from silently producing a selection. All **34 tests passed** on 21 October 2026: 31 existing checks and three real-case checks. They do not assert that all source-based decisions are automated correctly. The independent reference was frozen before the replay and was not rewritten to match it.

**Completed:** executable criteria, one application, three DPAL-member experimental papers, four formulation decisions, evidence and condition checks, actual code replay, separately reported reference/software outcomes, and targeted gaps. No unified score is required.

**Outside this completed case study:** live AutoSchema extraction accuracy, autonomous retrieval, production normalization fixes, human expert adjudication, new experiments and full coating qualification. Sources were selected to expose useful decision types; the small dependent sample cannot estimate performance across DPAL.

The earlier [five-lead discovery register](../examples/task3/dpal_evidence.json) and [worksheet](../examples/task3/dpal_screening.csv) remain historical literature-triage artifacts. They are not the experimental input used here.
