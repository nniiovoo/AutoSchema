# Polymer cards: checked example and source-grounded revision

One source-checked Pei card was prepared first. The code then gained stricter sample/family guards and a source-grounded revision route, and made **three new model revision calls** on Pei, Chen and Guo. The selected wrong sample owners and six Guo identities are repaired in the new responses. Complete scientific checking remains open, especially Methods/protocol coverage.

[Revised cards with review notes](../examples/polymer_cards/revision_run_2026-10-30/cards-with-review.html) · [Checked Pei card](../examples/polymer_cards/revision_run_2026-10-30/checked-pei-card.html) · [Focused evaluation](../examples/polymer_cards/revision_run_2026-10-30/focused-evaluation.json) · [Pei reference comparison](../examples/polymer_cards/revision_run_2026-10-30/pei-reference-comparison.json) · [Run comparison](../examples/polymer_cards/revision_run_2026-10-30/comparison.json)

## The checked card comes from source review, not the model

The [portable Pei reference](polymer-card-checked-pei-2026-10-30.md) describes PTMG-HDI-BHDS with all six requested groups: three building blocks, three composition entries, three synthesis entries, six selected properties, two applications and the author-synthesized source tag. Its reaction/GPC subject, matrix film and LiFSI electrolyte are distinguished. Original main-text passages support the feed molar ratio, polymer:salt mass ratio, measurements and relevant Methods conditions. This is a bounded, assistant source-checked example, not authenticated human annotation or a complete extraction of every paper fact.

Reference replay made **zero model calls**, with zero quarantined facts and two conservative neat/additive warnings. Those warnings remain visible. The checked card and focused answer files were used only for evaluation; the revision route accepts primary sources, prior model proposals and validator feedback, not checked reference answers.

## What changed in the code

- Strict live schema **`polymer_cards_strict_v2`** requires explicit exact-polymer/family scope. Numerical member results cannot pass under an explicitly broad family or explicitly unresolved scope.
- Sample-link evidence that names a more specific additive-containing form can quarantine a result attached to its bare matrix. The guard uses separate linking/preparation evidence, not a numerical comparison alone, and does not automatically move a value to a different sample.
- Exact-name/alias lookup retrieves candidate original passages for revision. It does not expand ranges such as P1–P7, classify materials or approve sample links. Original source quotations remain strict.
- A new revision request receives the complete primary text, previous extraction as untrusted proposals, compact validation feedback and candidate source locations. It regenerates a full response, preserving prior raw files and recording input/request hashes.
- Focused evaluation checks identity, value, exact sample, conditions and required evidence separately. Missing protocol metadata or a raw-format difference is reported for review rather than counted as a proven wrong numerical result.

The polymer-only retention rule is unchanged. Commercial polymers, controls, precursors and incomplete records remain eligible; application performance is not a filter.

## What actually ran

The CLI used `--repair-records` and `--repair-sources` against the matching original three-paper source snapshot. This was **`live_model_revision`**, conditioned on the saved previous extraction, not a fresh independent extraction and not a curated replay. Three OpenAI `gpt-5.4` requests completed with `finish_reason:stop`, a 24,000-token completion cap, a 600-second request limit and no automatic retries. Returned token usage for these three successful requests was **173,463**. The CLI default request limit remains 300 seconds.

The provider capture is preserved in `outputs/polymer_cards_revision_2026-10-30/`. A final alternate-form guard was completed while those requests were running, so the unchanged new responses were subsequently revalidated with **zero additional model calls** into `outputs/polymer_cards_revision_2026-10-30_revalidated/`. The final receipt records the validator revision and input hashes; no identity, number, quote or sample link was manually rewritten.

All three recorded request hashes reconstruct using the capture-time source-only feedback policy. With the final guard policy, Chen's feedback/request changes because an additional alternate-form check was added after capture; the saved historical hash is unchanged. The [request-source receipt](../examples/polymer_cards/revision_run_2026-10-30/request-source-check.json) records both checks. The source-only revision helper does not load checked reference files.

| Final validation | Pei | Chen | Guo | Total |
| --- | ---: | ---: | ---: | ---: |
| Raw entity records / retained drafts | 7 / 7 | 6 / 6 | 12 / 12 | 25 / 25 |
| Identity records in review | 0 | 0 | 0 | 0 |
| Fact records in review | 4 | 3 | 10 | 17 |
| Validation flags, including summaries | 5 | 3 | 10 | 18 |
| Separate advisory warnings | 4 | 0 | 0 | 4 |

The 25 drafts contain **20 declared specific polymers and five families**; they are not 25 distinct checked experimental materials. Ten cards have 18 composition entries accepted by structural/source checks. This does not make every recipe complete or scientifically verified.

| Stage | Drafts | Identity reviews | Fact reviews | New model calls |
| --- | ---: | ---: | ---: | ---: |
| Earlier 30 October final output | 19 | 6 | 22 | Earlier run |
| Same saved answers through the new guards | 19 | 6 | 26 | 0 |
| Source-grounded model revision, final validation | 25 | 0 | 17 | 3 |

The guard-only increase correctly holds additional suspect facts rather than silently fixing them; the new model revision then supplies source-grounded changes. Counts and card granularity changed, so this is not a paired accuracy measurement. The live revision still provides no standalone nonpolymer rejection benchmark. [Full stage comparison](../examples/polymer_cards/revision_run_2026-10-30/comparison.json).

## Source checks: what improved and what remains

**[Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w).** PEO's **3.8 V** and PTMG-HDI's **4.1 V** now link to their LiFSI electrolytes. BHDS keeps **beyond 5.0 V**, without dropping the limit qualifier. Its matrix-film strength and electrolyte conductivity remain separate. The earlier wrong links are first rejected by the source-link guard; the new model revision supplies the corrected links. However, the voltage entries still omit room temperature and the testing-Methods passage. PVDF coverage remains incomplete. [Detailed source review](polymer-card-revision-source-review-2026-10-30.md).

**[Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8).** All six previously held labels **P2–P7** now have explicit named source passages, rather than relying on range expansion. P3's **1.77** GPC result belongs to a **purified P3 sample**, with THF/GPC context. Its **93% ± 3% after two hours at room temperature** is separate from **93% ± 2% after 24 hours in water**; both attach the fracture-strain-recovery definition. P4, rather than the family, now owns the stretch result. The model preserves the source phrase **“nearly 140 times its original length”**; the frozen reference uses the source's percentage representation. No numerical conversion was forced to make the test pass. P2/P7 still have some measurements held for missing specimens, several separate unit fields remain null despite `%` in the raw value, and full formulation ratios require unavailable supplementary information. [Identity source evidence](polymer-card-guo-identity-evidence-2026-10-30.md).

**[Chen et al. 2021](https://doi.org/10.3390/polym13234155).** The **5 MPa precursor** and **21 MPa cross-linked network** now have separate tensile specimens. The approximately **2.56 × 10⁻³ S·cm⁻¹** room-temperature observation records **10 μL liquid electrolyte**, separate from the temperature series. The **12 μm Methods versus about 15 μm Results** membrane discrepancy is still not an explicit SHP conflict record, and wet-state coverage for the temperature series remains incomplete. External repair before cell assembly must remain distinct from autonomous healing inside an operating battery.

## Focused evaluation is not overall accuracy

All **six selected Guo identity expectations** match. Of **nine selected measurement expectations**, six meet the full selected criteria and three remain for source review: the source-supported P4 phrase differs from the frozen raw percentage representation, while the two Pei comparator voltages have correct owners but incomplete conditions/Methods evidence. Those three statuses are not three established wrong measurements.

The stronger six-property checked-Pei comparison is stricter: **all six model values and sample owners match, but all six complete reference cases still need review** because instrument/test conditions or their Methods citations are missing. These include strength/elongation loading rate, GPC solvent, EIS frequency range, LSV protocol and transference-cell details. The reference was not weakened after seeing the model output. [Full Pei case comparison](../examples/polymer_cards/revision_run_2026-10-30/pei-reference-comparison.json).

At the production freeze, **148 software tests passed**. All **414 retained evidence-reference occurrences** match supplied source chunks after declared conversion/whitespace handling; repeated references count again. Neither number is a scientific-accuracy score. This was one source-grounded revision of a small three-paper pilot, using main texts without supplements, OCR, graph extraction or exhaustive human annotation. The raw and earlier runs remain intact.

The requested checked example, source-link/identity changes and three-paper revision are complete. The next scientific work is fuller Methods coverage, unresolved conflict/state handling and omission checks before treating the resulting cards as checked data.
