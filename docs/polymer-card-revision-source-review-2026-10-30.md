# Focused source review of the live card revision

Reviewed 30 October 2026 using the new capture in `outputs/polymer_cards_revision_2026-10-30/`: `cards.json`, `raw-responses.json` and the exact source snapshot in `sources.json`. Paths below refer to that capture before any separately recorded final revalidation. This is an assistant's focused primary-source check, not authenticated human annotation or a comprehensive benchmark. The evaluation reference was not changed to fit the new output.

## Guo: all six previously held identities now have explicit source labels

The captured Guo result has 12 retained records and no identity records held. The six previously held member labels appear in original same-paper quotations, rather than being obtained by expanding `P1–P7`. Their source contexts support the named polymer members. This does not mean the 12 records represent 12 independently tested, distinct formulations. [Guo original paper](https://doi.org/10.1038/s41467-020-15949-8).

| Member | Captured card path | Attached source basis |
| --- | --- | --- |
| P2 | `results[2].cards[3]` | `src-f11f8aed81613a0e81fc`: explicit P2 mechanical passage plus the synthesized-parent-polymer statement `P1, P2: PDMS–SS–IP`. |
| P3 | `results[2].cards[4]` | `src-abdf1ced28f9b1e9fb83`: explicit P3 polymerization and purified P3 elastomer. |
| P4 | `results[2].cards[5]` | `src-f11f8aed81613a0e81fc`: explicitly identified P4 film and generic different-polymer preparation context. |
| P5 | `results[2].cards[6]` | `src-f11f8aed81613a0e81fc`: explicit P5 film and synthesized parent `P5: PDMS–IP–BNB`. |
| P6 | `results[2].cards[7]` | `src-35143d7cf8b1af205722`: explicit reduced-PDMS P6 film and generic polymer preparation context. |
| P7 | `results[2].cards[8]` | `src-7fff0ff525a418c27c9f`: explicit polymeric-backbone statement naming P3, P4 and P7. |

The control structures remain distinguished: P2 lacks BNB, whereas P5 lacks SS/disulfide. No P3 recipe was copied to these other members. Their exact unit proportions remain unavailable without Supplementary Table 1. [Guo synthesis and control comparison](https://doi.org/10.1038/s41467-020-15949-8).

## Guo: the principal measurement subjects are repaired

**P3 GPC:** `results[2].cards[4].properties.items[2]` now contains `1.77`, linked to `p5-gpc-sample`, labeled **purified P3 sample**. Its sample evidence quotes purification and the ensuing GPC measurement; its condition records GPC using THF as eluent. This supports the intended purified-polymer measurement subject, rather than the previous missing specimen or a cast-film assumption. Source: Methods / Polymer synthesis, `src-abdf1ced28f9b1e9fb83`. [Guo GPC method](https://doi.org/10.1038/s41467-020-15949-8).

**P3 ambient healing:** `results[2].cards[4].properties.items[4]` preserves `93% ± 3%`, linked to `p5-healed-film-rt`, with **two hours** and **room temperature** recorded. Its sample evidence attaches the Methods definition `src-b48dd634cfb0cbadc1e7` as well as the numerical Results passage `src-848b57bcf6907681b207`. The percentage means recovered fracture strain relative to original fracture strain, not tensile-strength recovery. [Guo healing result and method](https://doi.org/10.1038/s41467-020-15949-8).

**P3 underwater healing:** `results[2].cards[4].properties.items[8]` separately preserves `93% ± 2%`, linked to `p5-healed-film-water`, with **water** and **24 hours** recorded. The numerical passage `src-350106dc0f244b268362` and the same metric definition are attached. The ambient two-hour and underwater 24-hour observations have not been merged. [Guo underwater result](https://doi.org/10.1038/s41467-020-15949-8).

**P4 stretchability:** `results[2].cards[5].properties.items[0]` now belongs to `p6-film`, labeled **P4 film**, with the source value **“nearly 140 times its original length”** and `10 mm min⁻¹` loading rate. This repairs the previous family-level ownership error. The model retained a legitimate source phrase rather than the reference's other same-paragraph representation, `14,000%`; that raw-format difference must not be called an incorrect owner or scientifically false value. The source quotation and qualifier should remain unchanged. Source: `src-f11f8aed81613a0e81fc`. [Guo P4 mechanical result](https://doi.org/10.1038/s41467-020-15949-8).

The broad `PDMS–SS–IP–BNB` card no longer carries the member-specific P4 stretchability measurement. It still exists alongside exact member cards, so family/member counting remains an interpretation issue. [Guo series description](https://doi.org/10.1038/s41467-020-15949-8).

## Pei: the selected voltage links are now electrolytes

- `results[0].cards[1].properties.items[1]`: PEO **3.8 V** now points to `p2-peo-lifsi`, labeled PEO/LiFSI.
- `results[0].cards[3].properties.items[2]`: PTMG-HDI **4.1 V** now points to `p4-lifsi-electrolyte`, labeled PTMG-HDI/LiFSI.
- `results[0].cards[4].properties.items[7]`: BHDS retains **beyond 5.0 V**, linked to its LiFSI electrolyte, preserving the source limit qualifier.

The two comparator links agree with the electrolyte preparation `src-6524f9582cedc0d6c138`, the numerical Results `src-5d598cf3569a0bb57b72` and the SPE testing context in Methods `src-705d4d9258f66326a788`. The captured voltage entries attach preparation and Results, but still have empty condition lists and do not attach that testing-Methods passage. Corrected sample ownership therefore does not mean complete protocol metadata. PVDF is still omitted from the captured Pei roots despite its presence in the electrode recipe. [Pei original paper](https://doi.org/10.1038/s41467-023-43467-w).

## Chen: better sample separation, unresolved thickness context

The captured precursor **5 MPa** entry, `results[1].cards[0].properties.items[1]`, uses a precursor tensile specimen. The **21 MPa** entry, `results[1].cards[3].properties.items[0]`, separately uses a cross-linked-network specimen. Source: `src-629027e6d27659cd9af9`. [Chen precursor/network results](https://doi.org/10.3390/polym13234155).

The wetted room-temperature observation, `results[1].cards[3].properties.items[15]`, preserves **approximate to 2.56 × 10⁻³ S·cm⁻¹**, a specimen labeled with **10 μL liquid electrolyte**, and both room temperature and liquid-electrolyte amount as conditions. It is separate from the eight-temperature series. The model also separates the prepared ~20 μm film, ~10 μm transparency film, healing-demo film, electrochemical membrane and wetted membrane states. [Chen electrochemical source](https://doi.org/10.3390/polym13234155).

The **12 μm Methods versus about 15 μm Results** discrepancy for electrochemical SHP membranes remains unresolved: the captured SHP entry records about 15 μm, while the 12 μm statement is only present inside a citation attached to the PE comparator. It is not an explicit SHP conflict/context record. The temperature-series wet/liquid state is also less complete than the separate 10 μL observation. [Chen Methods and Results](https://doi.org/10.3390/polym13234155).

## Remaining limits

- Several Guo percentage values include `%` inside `value` while the separate `unit` is null. The source quantities are readable, but unit metadata is incomplete; distinguish this from a wrong numerical result.
- P2's 100% stretchability and P7's thermal result are still withheld for missing measurement specimens. Resolving identity did not automatically approve those facts.
- P5's qualitative “negligible” healing entry omits the structured exception “except underwater,” although the original quotation and a separate underwater ~60% entry preserve that context. Its conditions still need improvement.
- Full member ratios, supplements and graph-only data were not supplied. No complete scientific-accuracy score follows from these selected cases.
- The focused evaluator must report representation or metadata mismatches separately from proven scientific attribution errors. The frozen reference was not changed after seeing this revision.

No raw model output, source quotation, production code or evaluation expectation was changed during this review. Any final program revalidation must be labeled separately from the provider capture audited here.
