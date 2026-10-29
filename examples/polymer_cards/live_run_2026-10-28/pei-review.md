# Independent source review: Pei2024 polymer cards

Status: source baseline prepared before live output inspection; completed comparison against the first live run on 2026-10-28 (local date).

## Scope and independence

- Paper: Pei et al., *Interfacial self-healing polymer electrolytes for long-cycle solid-state lithium-sulfur batteries*, Nature Communications (2024), DOI [10.1038/s41467-023-43467-w](https://doi.org/10.1038/s41467-023-43467-w).
- Source: complete main-text JATS XML in the external source archive; no supplement in the live input unless later recorded by the run.
- Source SHA256: `ffc5376b77b6b81e29c52134d1f96d0185752dd35d35cb48172b661b13c8e1a8`.
- Frozen selected reference SHA256: `75c137a9aedbb132b62f521c66324fe03b2b9d68799d2c0afe6a82aeeb331a1b`.
- This review is assistant primary-source adjudication, not authenticated human ground truth. No model API was called by this reviewer.
- Frozen reference has four selected positive polymer entities and two selected nonpolymer negative entities for this paper. It is not exhaustive whole-paper entity ground truth.

## Source baseline

| Identity | Source and role | Appropriate origin / retention |
|---|---|---|
| PTMG-HDI-BHDS | Sec3 structural design; Sec13 preparation | Author-synthesized polymer; keep |
| PTMG-HDI | Sec12 preparation | Author-synthesized control polymer; keep |
| PEO | Sec11 Materials; Sec14 electrolyte preparation | Purchased polymer; keep |
| PTMG (polytetrahydrofuran, 2000 g mol−1) | Sec11 Materials; Sec12/13 polymeric reactant | Purchased polymeric reactant; keep despite sparse fields |
| HDI | Sec11 Materials; Sec12/13 reactive small molecule | Omit standalone polymer card; preserve as ingredient |
| LiFSI | Sec11 Materials; Sec14 salt | Omit standalone polymer card; preserve as ingredient |
| PAN | Sec15 SPAN preparation | Legitimate additional polymer in full text; not an error merely because absent from selected reference |
| SPAN | Sec1 and Sec15 sulfurized polyacrylonitrile cathode | Legitimate additional polymer-containing material; retain with correct composition/role if classified as polymer |
| PVDF | Sec17 cathode formulation | Legitimate additional polymer binder; limited origin evidence |
| Teflon/PTFE | Sec14 casting mold | Polymer apparatus mention; role must be preserved rather than misrepresented as studied electrolyte |

The paper also uses the broad family label poly(ether-urethane). Whether this is an independent class card or a description of PTMG-HDI-based matrices should be handled consistently; it must not silently duplicate the same specimen.

## Key attribution checks

1. **Neat versus salted material.** Sec4/Fig2d reports breaking strength 88.3 MPa and ultimate elongation 2000% for PTMG-HDI-BHDS; PEO and PTMG-HDI controls have 17.8 and 31.2 MPa respectively. These are polymer mechanical observations, not automatically measured strengths of the salted LiFSI formulations.
2. **Conductivity.** Sec5/Fig3 gives PTMG-HDI-BHDS/LiFSI = 2.4 × 10−4 S cm−1; PTMG-HDI/LiFSI = 6.5 × 10−5 S cm−1; PEO/LiFSI = 1.2 × 10−5 S cm−1, all at 30 °C. Each value must remain attached to its named electrolyte specimen.
3. **Feed versus formulation.** Sec12 PTMG:HDI molar feed = 1:1.2. Sec13 PTMG:HDI:BHDS molar feed = 1:2.4:1. Sec14 polymer:LiFSI mass ratio = 2:1. These cannot be interchanged or combined into one unqualified composition number.
4. **Synthesis versus origin.** Purchased PEO/PTMG/HDI/BHDS are inputs. Sec12/13 state that the final PTMG-HDI and PTMG-HDI-BHDS polymers were synthesized. A purchased reagent statement does not make the final polymer commercially purchased.
5. **Raw notation.** JATS flattening represents superscripts as adjacent characters (e.g. PEO Mw appears as 6 × 105 g mol−1). A parsed/normalized scientific number may be sensible, but it must not be claimed as an unchanged raw source string.
6. **Battery data.** Capacity in mAh gSPAN−1 and mAh gS−1 belongs to a tested cell/cathode configuration, not an intrinsic matrix-polymer property. The mass denominator and configuration must remain explicit.
7. **Methods conditions.** Default electrochemical tests are 30 °C unless specified. Pouch-cell pressure (~200 kPa) must not be transferred to coin cells. The ~200 μm combined thickness in Sec5 specifically describes the dual-integrated BHDS experiment; do not assume this for every control specimen.
8. **Source-tag restraint.** Sec11 explicitly names supplier for PEO/PTMG and several small molecules. PAN/PVDF are used in later Methods but are not specifically given suppliers there; a supplier claim requires original evidence.

## Limits

Quote containment is not semantic evidence verification. A quote can be literal yet linked to the wrong entity, property, specimen, or condition. Full main-text extraction cannot independently establish absence of contradictory supplemental observations. No conductivity cutoff, application ranking, or field-completeness exclusion belongs in the current polymer-only retention rule.

## Live result comparison

The run metadata says `mode=live_model_extraction`, OpenAI `gpt-5.4`, three model calls for three full-main-text papers. This review covers Pei only. Its raw response has 8 entities; validation produced 6 cards, 2 classification-review entities, 9 review records, 14 validation issues, and 0 standalone nonpolymer discards. All cards carry six group containers, but this does not mean six complete information groups.

### Selected reference coverage

| Frozen source expectation | Raw model entity | Final result | Source interpretation |
|---|---|---|---|
| PTMG-HDI-BHDS | p4 | Retained | Correct polymer retention |
| PTMG-HDI | p3 | Classification review | Correctly recognized in raw; usable main-text source establishes polymer, but supplied evidence includes a nonverbatim figure caption quote |
| PEO | p2 | Retained | Correct purchased polymer retention |
| PTMG | p5 | Classification review | Correctly recognized in raw; source capitalizes Polytetrahydrofuran, while model name starts lowercase; literal entity-name matching withheld it |
| LiFSI negative case | Not enumerated as standalone entity | No discard record | Preserved as ingredient; not a tested negative classification |
| HDI negative case | Not enumerated as standalone entity | No discard record | Preserved as ingredient; not a tested negative classification |

Selected positive discovery was **4/4 in raw output; 2/4 in retained cards**, with the other 2/4 explicitly routed to review rather than labeled nonpolymer. These are descriptive counts on four selected examples, not overall extraction accuracy. No nonpolymer negative-case score can be calculated from this live response because the negatives were not enumerated.

Additional retained PAN (p6), SPAN (p7), and PVDF (p8) are legitimate full-main-text mentions absent from the limited frozen reference. Their extra discovery is not a false positive by that fact alone. The broad p1 poly(ether-urethane)-based SPE card likely describes the same material family as p4 rather than a separate experimental candidate; mark class-versus-specific relation or deduplicate cautiously. The polymer casting equipment PTFE/Teflon was not separately extracted. Without exhaustive entity annotation, this is a visible scope omission rather than a computed whole-paper recall error.

### Source-attribution findings

| Priority / reach | Observation | Source basis and suggested action |
|---|---|---|
| Important; retained p2 property | PEO electrochemical window 3.8 V is assigned to specimen `p2-peo` (neat PEO), not `p2-peo-lifsi` | Sec5/Fig3e and Methods/Sec17 concern SPE electrochemical measurements; electrolyte preparation Sec14 defines PEO/LiFSI. Link this electrochemical observation to salted formulation, preserving context. A literal quote match did not catch this. |
| Important; raw p3 currently withheld | Mn `7.3 × 105 g mol−1` was assigned to PTMG-HDI | Sec4 paragraph1 explicitly states PTMG-HDI-BHDS polymerization was monitored and its Mn/viscosity were significantly higher than PTMG-HDI. This value belongs to BHDS (p4), not comparator p3. Do not restore the full p3 card by fixing only identity evidence; first remove/review this misattributed fact. |
| Important; raw p3 currently withheld | PTMG-HDI electrochemical window4.1V is assigned to `p3-film` rather than `p3-lifsi` | Same salted/neat issue as PEO. The raw conductivity observation itself correctly uses `p3-lifsi`. |
| Provenance; retained p2 application | `claim_type=demonstrated` comparison-electrolyte application cites only the Introduction statement that PEO-based electrolytes are widely studied | This particular quote supplies background, not a current experimental demonstration. Current-work evidence exists in Sec5/7 and should be linked. The statement can be correct while its attached proof is insufficient. |
| Provenance; retained p4 application | `claim_type=demonstrated` integrated SSLMB use cites “Herein, we propose...” in Introduction | Current-work experiments later in Sec6/7 demonstrate the application. Link that evidence rather than relying on proposal wording. High-voltage application is correctly labeled proposed. |
| Data loss / contract adherence | All nine raw Pei composition items lack `basis`; no Pei composition item survives in final cards | Missing basis correctly triggers review instead of guessing. Prompt/model schema should require explicit molar-feed, mass-ratio or mass-fraction basis with specimen link. PEO molecular weight is also misplaced under composition; it belongs in properties with a PEO specimen. |
| Data loss / literal condition format | SPAN initial discharge capacity602mAh gSPAN−1 was sent to review because activation condition combines noncontiguous source text | The model condition `0.05 C between1.0 and3.0V` omits an intervening parenthesis in the literal source, so it fails exact containment. Use separate activation-rate and voltage-range conditions, each with its own original quote. Before retaining, attach the capacity to the full SPAN|PTMG-HDI-BHDS|Li cell rather than only generic `SPAN@SPE`. |
| Computational origin; raw p5 withheld | PTMG repeat-unit LUMO1.35eV and Li+ bindingenergy−0.83eV have null specimen IDs | Fig3d is explicitly calculated, not a direct experimental property measurement. Add a computational/repeat-unit specimen or leave in review; preserve observation type. Current validator has not reached these facts because entity classification was already withheld. |
| Possible duplicate / classification granularity | p1 broad poly(ether-urethane)-based SPE overlaps p4 PTMG-HDI-BHDS | Both are polymer descriptions; absence of a separate synthesis/recipe suggests family description rather than independent candidate. A relation/class label is preferable to counting it as an additional distinct synthesized polymer. |

### What worked

- p4 correctly separates neat-film breaking strength88.3MPa/elongation2000% from salted-film conductivity2.4×10−4S cm−1 at30°C. No automatic transfer of those mechanical measurements to the salted film was found.
- Correct conductivity numeric values and30°C are present for BHDS, PEO, and the raw PTMG-HDI card, with correct electrolyte specimen links.
- p4 preserves the electrochemical qualifier “beyond5.0V” and the dimensionless Li+ transference number0.81; no artificial unit was added.
- PEO is correctly tagged commercially purchased; final PTMG-HDI-BHDS is correctly tagged author-synthesized. Raw PTMG and PTMG-HDI origin tags also match Sec11/Sec12. PAN/PVDF origin is left unknown rather than an invented supplier.
- Incomplete PAN and PVDF cards remain retained. Missing information did not remove known polymers.
- Composition and malformed condition records remain in the audit queue, not silently discarded from raw provenance.

### Completion assessment

The live pipeline runs and produces auditable polymer-only cards, but this Pei run still needs semantic fact review. It should not be described as fully correct extraction, complete polymer coverage, or validated scientific evidence. The first changes to prioritize are (1) mandatory composition basis/specimen fields, (2) entity-name case handling with original wording preserved, (3) comparator/subject attribution, (4) neat-versus-formulated electrochemical specimen alignment, and (5) application claim evidence tied to experiments. Mechanical quote matching remains useful but insufficient for these scientific distinctions.

### Reviewed artifact hashes


- `cards.json`: `5663f0ef8c7ef3423d54f86323bd9c171c6b06642644ef32d1a944012927bfbd`.
- `raw-responses.json`: `9d54235f3d645a1a0c13dcd02454a4c0e1f42753a063f8245c9c0a7bb67c1c82`.
- `audit.json`: `e0063000714848b5ac7a0e5075c9d41f36d724821ada2447a8b0509b002c43d6`.
- `sources.json`: `32e165d5b71b0fb7f89c565b2b691eff81b076cd8b93ccbc72457c0e653ad469`.
