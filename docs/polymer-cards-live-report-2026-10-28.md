# Task 3: first live polymer-card test

The real extraction completed on 28 October 2026. AutoSchema made **three OpenAI model calls** on three original main texts and produced **18 draft polymer-card records**. This is a live run, separate from the earlier manually prepared replay.

**The cards are useful drafts, not a finished polymer database.** Some records overlap, some facts have wrong specimen links, and some supported information was withheld. Eighteen cards does not mean eighteen distinct, fully correct polymers.

[Read the cards and review notes](../examples/polymer_cards/live_run_2026-10-28/cards-with-review.md) · [HTML with original evidence](../examples/polymer_cards/live_run_2026-10-28/cards-with-review.html) · [Saved evaluation](../examples/polymer_cards/live_run_2026-10-28/evaluation.json)

## What ran

- Model: OpenAI `gpt-5.4`; three calls, all completed normally. Recorded total usage: 79,930 tokens.
- Input: original main-text XML for Pei, Chen and Guo, covering Nina's disulfide and dynamic-battery-polymer domains. These are domain-aligned papers, not claimed to be her exact seeds.
- Retention: polymer identity only. Low performance, commercial origin and incomplete fields do not remove a polymer.
- Output: name, identity evidence, roles, linked specimens and six groups: monomers, composition, synthesis, properties, applications and source tag.
- The original model responses and validated output were preserved unchanged. Review notes were added separately. No second model run or silent repair was used to improve these results.

## Results by paper

| Original experimental paper | Raw entity records | Draft cards retained | Identity records awaiting evidence review | Fact records in review |
| --- | ---: | ---: | ---: | ---: |
| [Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w) | 8 | 6 | 2 | 7 |
| [Chen et al. 2021](https://doi.org/10.3390/polym13234155) | 5 | 4 | 1 | 4 |
| [Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8) | 8 | 8 | 0 | 25 |
| **Total** | **21** | **18** | **3** | **36** |

The **39 review records** contain three identity records and 36 fact records. The separate 58 validation flags also include group-status and empty-group summaries; they are not 58 independent scientific mistakes. One number was wrongly withheld by a validator punctuation rule.

The model returned no standalone nonpolymer candidates. Salts and monomers occur inside polymer cards, but **zero discarded records is not a negative-classification score**. The earlier replay's four nonpolymer cases remain a separate software check.

## Three examples in simple English

**Pei: PTMG-HDI-BHDS.** The card correctly keeps the synthesized polymer. Its neat-film strength of 88.3 MPa is separate from conductivity of the salt-containing electrolyte, 2.4 × 10⁻⁴ S/cm at 30°C. The feed and polymer:salt ratios are present in the paper, but the model omitted the required ratio-basis labels. Those composition items therefore remain in review. [Pei review](../examples/polymer_cards/live_run_2026-10-28/pei-review.md).

| Six fields | What this live example shows |
| --- | --- |
| Monomers/building blocks | PTMG polymeric reactant, HDI and BHDS chain extender, with source evidence. |
| Composition | Needs review. The source distinguishes feed molar ratio 1:2.4:1 from polymer:LiFSI mass ratio 2:1; the required structured basis is missing. |
| Synthesis | Polymer preparation and later salt-containing film preparation are described separately. |
| Properties | Neat-film mechanical strength and salted-electrolyte conductivity have separate specimen links. Other observations still need method/notation review. |
| Applications | Battery use is reported, but the attached “demonstrated” evidence points to introductory wording. Link the actual experiments. |
| Source tag | Correctly marked synthesized by the authors. |

**Chen: precursor versus network.** The live cards correctly keep the 5 MPa precursor result separate from the 21 MPa cross-linked network result. The separate electrolyte-membrane record is held for identity-evidence review; that does not mean it is a nonpolymer. Its raw wet-state and temperature-series observations need clearer specimen boundaries, and the paper's 12 μm versus approximately 15 μm thickness statements need an explicit conflict record. [Chen review](../examples/polymer_cards/live_run_2026-10-28/chen-review.md).

**Guo: P3 healing.** The live family card preserves 93% ± 3% healing efficiency after two hours at room temperature, linked to P3. The metric means recovery of fracture strain, not strength recovery. However, the broad family card also contains chemically different controls as specimens and duplicates their separate cards. Exact polymer/formulation boundaries must be resolved before counting distinct materials. [Guo review](../examples/polymer_cards/live_run_2026-10-28/guo-review.md).

## What still needs checking

1. **Identity evidence:** PTMG-HDI, PTMG and SHPEM were found in raw output but held for quote/name mismatch. Case, plural wording and unsupported quotation changes need separate treatment. Repairing an identity alone must not automatically approve all its facts.
2. **Wrong sample links:** a retained PEO 3.8 V result was attached to neat PEO instead of its LiFSI electrolyte. Raw PTMG-HDI also copied a molecular weight belonging to BHDS; that record was withheld upstream. Literal quote matching cannot catch every wrong-subject assignment.
3. **Missing structured labels:** 17 composition items lack `basis`; 13 Guo property items lack valid specimen links; three Chen groups use origin values as invalid status labels. Much of this information exists in the paper. It is not missing source data.
4. **Validator and text preparation:** Guo's source-supported `1.77` was withheld because the number ends a sentence. JATS superscripts were flattened, for example an exponent can appear as `105` rather than `10⁵`. Inspect the original HTML/PDF before interpreting such numbers.
5. **Experimental context and coverage:** link demonstrated uses to experiments, preserve distinct healing/wetting protocols, and check missing conditions. Supplements and graph-only data were not included. Some background polymers were omitted; the selected reference is not an exhaustive inventory.

## What AutoSchema should improve next

Require a complete output schema with worked examples for composition basis, valid group status and specimen references. Keep an exact source name separate from a canonical name. Represent family/member relationships explicitly. Preserve XML superscripts/subscripts with declared text transformations. Test sentence-final numbers, and add source-based checks for comparator values, neat versus salted materials, protocol differences and demonstrated applications.

These changes should improve extraction and validation; they should not weaken the polymer-only retention rule or invent missing evidence. The existing implementation's 79 software tests passed before this pilot. This live run exposed additional cases those tests did not cover.

No overall scientific accuracy, precision or recall is claimed. The review is an assistant's focused primary-source review, not an authenticated human benchmark. Source receipts, original-artifact hashes and the unchanged model outputs are saved with the [run artifacts](../examples/polymer_cards/live_run_2026-10-28/README.md).
