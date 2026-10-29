# Independent review of Guo2020 live polymer-card extraction

Primary DOI: https://doi.org/10.1038/s41467-020-15949-8. Original XML: `/Volumes/Seagate/research /polymer-screening/sources/polymer-cards-2026-10-28/guo-original.xml`. Prepared28October2026. Original source and frozen reference read before inspecting any live output. This is an assistant source review, not authenticated human annotation or an exhaustive independent material inventory.

## Checks prepared before outputs existed

- P3 is an author-synthesized PDMS–SS–IP–BNB elastomer; MethodsSec10 is a sample-specific synthesis and recipe. A family name is not permission to transfer a property between all P1–P7 formulations.
- The HO–PDMS–OH reactive precursor is polymeric; being a reactant must not make it a nonpolymer. MainSec9 sends purchased-reagent details to SI, so commercial origin is not established by the checked main text alone.
- IPDI is an isophorone diisocyanate monomer in ResultsSec2. Omit its standalone polymer card while retaining its ingredient role.
- P3's93%±3% self-healing efficiency at room temperature after2h is a **fracture-strain recovery ratio**, confirmed by Sec11/p3. It is not tensile-strength recovery, not the same as recovered fracture strain1200%±50%, and not the10min qualitative demonstration.
- The electrical conductor in Sec6 uses liquid metalEGaIn as conducting wire and P3 as encapsulation/support. Immediate electrical reconnection is not intrinsic electrical conductivity of neatP3.
- Sec10 gives GPC sampleP3 Mn63KDa, Mw112KDa, Mw/Mn1.77, THFeluent. These values must not be assigned to a different formulation or the precursor.
- Names vary in ordering(PDMS–SS–IP–BNB versusPDMS–IP–SS–BNB) inside the source. A scientific source inconsistency or naming variant requires explicit attribution; it is not blanket evidence for sample identity equivalence.
- Additional polymers such asPMMA(GPCstandard), PTFE(mould/dish), PDMS, polyurethane orstyrene-butadiene-styrene may legitimately appear as controls, apparatus materials or cited background. The selected frozen reference is not exhaustive; extra cards are not automatically false positives. Their roles and properties still need correct attribution.

## Live output status

At initial inspection, `outputs/polymer_cards_live_2026-10-28/` did not yet exist. The expectations above were prepared before outputs were read. The completed first live run is reviewed below; no source-reference labels were altered to match the outputs.

## Completed live-source review

Files inspected: `cards.json`, `raw-responses.json`, `audit.json` and `sources.json` under the specified output directory. Guo's result contains8retained card records, no standalone nonpolymer records,25quarantined/review records and33validation issues. These counts describe this model response and validator, not a complete recall/precision benchmark.

### Correctly retained evidence and distinctions

- The main family card`p2` retains reactive PDMS/IPDI/SS/BNB building blocks and meaningful synthesis text. Source origin is author-synthesized, supported by the polymerization and preparation sections.
- P3's93%±3% healing efficiency is retained with specimen`p2-P3-film` and the source condition room temperature for2h. Recovered fracture strain1200%±50% is a separate observation. Neither is mislabeled as strength recovery.
- Demonstrated artificial conductor and proposed e-skin/harsh-environment uses are distinguished. No EGaIn electrical recovery was placed in the neat polymer's property list.
- PDMS's origin is left unreported rather than assuming commercial purchase from the reagent role. PMMA standard, Sylgard184, polyurethane and styrene-butadiene-styrene background cards have visible roles and do not receive the main polymer's measurements.
- Missing property/specimen links and missing composition basis trigger review. The polymer cards remain retained, so incomplete fields do not become a performance-based exclusion.

### Problems and remaining limitations

1. **The main card groups chemically different parent polymers.** `p2`, namedPDMS–SS–IP–BNB, includesP1/P2(noBNB) andP5(noSS) as specimens, while`p3` and`p4` separately describe those parent polymers. This is overbroad grouping and duplicate representation. The specimen IDs preserve some measurement attribution, but8cards cannot be described as8distinct, nonoverlapping polymer identities.
2. **P3 is not a separate exact polymer card.** It is represented as a specimen inside a family card. The frozen reference expects an exactP3 record. This is a granularity/identity mismatch; do not claim an exact reference-entity match from row counts or aliases alone. A published family and a known member should have explicit parent/member relationships or distinct exact records.
3. **Composition information is present in the source but absent from usable card fields.** All the Guo composition items were quarantined because the model omitted the required`basis`field. This includes the P3feed recipe, PDMS/IPDIratio, film solution and tube solution. Label this as model-contract failure, not a statement that the paper lacks composition.
4. **The healing metric remains underspecified in the label.** Its retained property name is generic`healing efficiency (η)`. The source supports it, but an explicit denominator/method note should identify fracture-strain recovery. The card does not include the defining MethodsSec11/p3quotation. That omission is a completeness/interpretation risk, even though no incorrect strength label is present.
5. **Some important method conditions remain only in evidence.** P3Mn/Mw are attached to a film specimen, although their source describes GPC on the purified P3polymer. THFeluent/GPC are visible in the source quote but not structured conditions. A polymer/GPCspecimen would be more precise than a mechanical-testfilm label.
6. **The reactive precursor is represented by a broad PDMS root.** `p1`'s role/evidence preserve the hydroxy-functional reactive precursor, but the rootname is genericPDMS. Its synthesis_text describes use of PDMS to make another polymer rather than synthesis of PDMS itself. Preserve that distinction when comparing to the exactHO–PDMS–OH reference entity or displaying a “synthesis”section.
7. **No live negative classification was exercised.** All8returned entities were called polymers. IPDI is retained as an ingredient, correctly, but was not proposed as a standalone nonpolymer audit record. Thus zero discarded records does not demonstrate negative-classification performance. Curated negative tests, if run separately, must be reported separately.

### Suggested report wording

“The Guo live run produced eight polymer card records and preserved the P3healing observation with its specimen and condition. It also exposed family/member duplication and missing composition-basis fields. Original quotations matched, but exact identity granularity and field semantics still need review. This is a pilot, not an exhaustive or independently human-labeled extraction benchmark.”

No production files, model responses, reference, credentials or output labels were edited by this review.
