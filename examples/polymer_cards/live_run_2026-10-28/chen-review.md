# Independent Chen 2021 polymer-card review

Prepared28October2026. Primary-source review before inspecting live-model output. This review does not call a model/API, edit production code or modify frozen references.

Source: Chen et al., *Self-Healing of a Covalently Cross-Linked Polymer Electrolyte Membrane by Diels-Alder Cycloaddition and Electrolyte Embedding for Lithium Ion Batteries*, [DOI10.3390/polym13234155](https://doi.org/10.3390/polym13234155). Original XML: `/Volumes/Seagate/research /polymer-screening/sources/polymer-cards-2026-10-28/chen-original.xml`.

Frozen selected reference: `/Volumes/Seagate/research /AutoSchema/examples/polymer_cards/reference.json`.

## What the selected reference covers

The selected Chen entities are the author-synthesized uncrosslinked copolymer precursor and its BMI-crosslinked polymer network. The reference expects precursor tensile strength5MPa and crosslinked-network tensile strength21MPa, attached to distinct specimens. It identifies LiBOB as a nonpolymer standalone entity. This is a selected reference, not an exhaustive inventory of every polymer named in the full paper.

Model-generated entity IDs may differ from the manually assigned reference IDs. Semantic identity and source attribution should be compared; literal ID mismatch alone is not evidence that a polymer was omitted.

## Primary facts and attribution checks

| Subject | Source-supported fact | Source locator / important boundary |
| --- | --- | --- |
| Precursor identity | Source labels the copolymerP(MMA-BA-(F-MA)); precursor is produced by emulsion polymerization. | Methods2.3, XML`sec2dot3-polymers-13-04155`, paragraph1. It is a polymer, not a small-molecule precursor. |
| Precursor building blocks | MMA, butyl methacrylate(BMA), F-MA; feed molar ratio1:2:1. | Methods2.3 andResults3.1p1. Preserve the monomer-feed basis; do not call this the final polymer/salt ratio. |
| Chemical naming inconsistency | Intro mentions PMMA/PBA, while Methods defines BMA/butyl methacrylate and retains BA in the copolymer label. | Intro final paragraph; Methods2.1/2.3. Do not silently correct BA toBMA or infer butyl acrylate as a source-established monomer. Preserve or flag ambiguity. |
| Precursor synthesis | Emulsifier2.5wt%SDS underN2 at60°C; emulsify1h; ammonium-persulfate initiation and6h continued stirring; precipitation in3wt%Al2(SO4)3; hot-water washing55°C; vacuum drying60°C12h. | Methods2.3. Emulsifier, initiator and precipitant are not all monomers. |
| F-MA synthesis | Made from methacryloyl chloride and furfuryl alcohol, triethylamine, THF;0°C addition thenroom-temperature3h;81%yield. | Methods2.2. These are precursors for the F-MA monomer, not automatically copolymer monomers. |
| Precursor source tag | Author synthesized. | Methods2.3 explicitly prepares the copolymer. Purchased small-molecule inputs in2.1 do not make the polymer commercially purchased. |
| Precursor molecular weight | Number-average molecular weight644,000, GPC. | Results3.1p2/Fig2a. The running text does not print a unit; do not addg/mol without supporting supplied evidence. |
| Precursor tensile strength |5MPa. | Results3.1p2/Fig2b. Not the network's21MPa. |
| Network identity | Precursor crosslinked with BMI through reversible furan/maleimide Diels–Alder chemistry. | Results3.1p1 andMethods2.4. Matrix identity and LiBOB-containing or wetted specimens should remain distinguishable. |
| Network/membrane formulation | Reported copolymer:BMI molar ratio2:1.1; LiBOB added. | Methods2.4. This ratio is not polymer:LiBOB orsalt-to-polymer mass ratio. |
| Network/membrane preparation | Copolymer and salt mixed50°C1h, crosslinker added, doctor-blade cast on glass, vacuum90°C24h. | Methods2.4; Results3.1p1 identifiesNMP. Distinguish crosslinking/membrane preparation from initial precursor polymerization. |
| Network source tag | Author synthesized. | Methods2.4 andResults3.1p1. CommercialBMI/LiBOB inputs do not imply purchased final network. |
| Network tensile strength |21MPa after suitableBMI addition. | Results3.1p2/Fig2b. Do not transfer it to precursor or automatically to every salted/wetted conductivity membrane. |
| LiBOB loading |10wt%LiBOB is described with a prepared approximately20µm morphology film. | Results3.1p3/Fig3b. Do not silently apply this loading to all conductivity or healing samples. |
| Thermal stability |280°C, nitrogen atmosphere. | Results3.1p3/TGA SI FigS1 andabstract. It is a thermal-stability statement, not synthesis or healing temperature. |
| Healing |80°C underN2 forabout2h; cut pieces matched/clamped; around65%originalbreaking-strength recovery. | Results3.2/Fig4. Recovery is breaking strength, not conductivity or capacity recovery. |
| Conductivity series |25,35,45,55,65,70,85,90°C map respectively to1.69e-4,2.69e-4,4.17e-4,6.61e-4,9.33e-4,1.32e-3,1.86e-3,2.34e-3S·cm−1. | Results3.3p2/Fig6a/SI FigS2. Values and ordered temperatures must remain paired. There is no explicit30°C entry. |
| Separate wetted conductivity |2.56e-3S·cm−1 at unspecifiedroomtemperature for membrane with10µLliquid electrolyte. | Results3.3p2. Do not call it dry polymer or assign exact25/30°C. |
| EIS |SS/SHPEM/SS,10−1–10^5Hz,10mV; Methods explicitly sayswithliquidelectrolyte. | Methods2.6; Results3.3p2 usesbulkresistanceσ=l/(RA). Temperature-series liquid state remains ambiguous. |
| Thickness conflict |Methods assignsSHP12µm andPE15µm; Results saysall electrochemicalSHPmembranesabout15µm. | Methods2.6 vsResults3.3p1. Preserve both source statements; a quote match alone does not resolve the discrepancy. |
| Demonstrated application |Li/SHPEM/LiCoO2coin cells; SHPEM as functional separator;Li-metal negative electrode. | Methods2.5 andResults3.3p3–4. Title's lithium-ion wording does not negate the described Li-metal cell. |
| Cathode mixture |LCO:acetyleneblack:PVDF8:1:1 byweight. | Methods2.5. This belongs to the cathode composition, not the SHPEM polymer recipe. PVDF is a distinct polymer component. |
| Cell plasticizer |EC:DMC1:1v/v,10µL added toSHPEM cells. | Methods2.5. Do not attach this amount to initial monomer feed or assume every mechanical film has it. |
| Cycling endpoints |Originalcell96.1%, healedSHPEM95.9%, PEcomparative96.9% after100cycles;140mA/g(1C),3.0–4.3V. | Results3.3p4. These are cell-capacity retention values, not polymerstrength recovery. |
| Healing/application claim |Healed membrane was thermally repaired before assembling into a cell. | Results3.3p4. Autonomous repair inside a sealed operating battery is proposed inResults3.1, not the demonstrated protocol. |

## Additional polymer mentions in full main text

Prompt instructions include purchased polymers, polymeric reactants, controls and background polymers, with roles retained. The full Chen text additionally namesPVDF(cathode binder),PE(commercial separator comparator),PMMA/PBA(background component rationale),PEG/PU in cited priorSHSPEwork,SIPE-5 in cited priorwork, and genericSHSPE/SIPEfamilies. Missing those entities may reveal incomplete full-text inventory, but the two-entity selected reference cannot quantify exhaustive recall or treat an extra valid polymer card as false positive.

Each additional card requires its own evidence. For instance, the main text does not explicitly state a vendor/purchase forPVDF;2.1's materials list does not includePVDF. Do not inherit the nearby statement that other reagents were purchased fromAladdin. PE is explicitly described as commercial in the main article, but its exact chemical-name expansion and supplier must not be invented from an abbreviation alone under the prompt's source-only policy.

## Live run status

At initial source review, `outputs/polymer_cards_live_2026-10-28/` was absent. The facts above are independently prepared expectations. Live-output comparison will be appended when available; no model-performance claim can yet be made.

## Actual live-output review

The live files subsequently became available under `/Volumes/Seagate/research /AutoSchema/outputs/polymer_cards_live_2026-10-28/`. This section independently compares`raw-responses.json`, `cards.json` and`audit.json` with the full original Chen article. Original output files were not changed.

### Inventory and selected-reference checks

Chen's raw response contains5entities: p1copolymer precursor, p2SHPnetwork, p3SHPEM, p4PVDF andp5commercialPEfilm. Validation retains4cards(p1,p2,p4,p5) and sendsp3to classification review. The paper audit reports5review-queue items and11validation issues. No standalone nonpolymer entity is emitted; that fact by itself does not establish success or failure of the discard gate.

Both selected-reference current-work polymer concepts are recovered: the precursor(p1) and BMI-crosslinked network(p2). The retained properties correctly keep precursor5MPa and network21MPa separate. The precursor's molecular-weight value644,000 is preserved with`unit:null`, correctly avoiding an inventedg/mol unit from running text. P1monomers correctly identifyMMA/BMA/F-MA, andp2distinguishes a polymeric precursor reactant fromBMIcrosslinker. This is positive evidence for those selected facts, not exhaustive entity or field accuracy.

### Concrete contract / evidence failures

1. **The key precursor ratio is extracted but unavailable as a validated composition fact.** Rawp1 hasMMA:BMA:F-MA1:2:1 and a correct source quotation, but omits the required`basis`. Its composition group becomes`needs_review` with no usable items. P4's cathode composition andp5's electrolyte composition likewise lack`basis`. P3's raw composition facts also omit`basis`, but its earlier classification failure prevents those fact checks from being reached. These are schema-conformance failures, not proof that the numerical ratios are scientifically wrong.
2. **Source-tag values and statuses are confused.** Rawp1/p2/p3 use`source_tag.status:"author_synthesized"`; p5uses`status:"commercially_purchased"`. Those values belong in the fact item, whereas group status must be`reported`, `not_found_in_provided_text`, `needs_review` or`conflicting`. Valid retainedp1/p2/p5fact items carry chemically plausible source tags, but their groups are correctly flagged`needs_review`. P4does not invent a commercial source forPVDF, which is appropriate.
3. **SHPEM remains a review record rather than a published card.** P3's name is`self-healing polymer electrolyte membrane (SHPEM)` while its quoted original expansion is plural`membranes (SHPEM)`, and another quotation places`(SHP)` elsewhere. The validator reports`entity_name_not_in_original_evidence`. Source text does support SHPEM as a polymer-containing membrane; the review flag is an exact-name/evidence-link issue, not evidence that SHPEM is nonpolymeric. Do not silently reclassify it as a failed or discarded material.
4. **P1's description includes a heading not present in the cited body chunk.** Its first supporting quotation is the section title2.3, attached to the paragraph chunk. A second quotation correctly describes synthesis, but the heading reference fails containment, so the description is nulled. The first quotation exists in the document structure, just not the provided text of that chunk. This is a source-location/link failure rather than an invented scientific concept.

### Scientific / identity concerns not resolved by quote matching

**SHP versus SHPEM linkage is incomplete.** P2represents the crosslinked polymer matrix; p3represents the electrolyte membrane containing it. The model separates them into paper-level entities, rather than expressing p3as a linked salted/wetted specimen of the matrix or explicitly linking their polymer identity. This needs identity review before counting independent polymers or merging facts. It is not safe to label either card a false positive solely from the selected two-entity reference.

**P3captures conductivity values well, but specimen state remains ambiguous.** The raw response preserves all eight ordered conductivity/temperature pairs from25–90°C and does not invent30°C. It separately records the10µL-wetted room-temperature2.56e-3S·cm−1 result with a liquid-amount condition. However, it assigns both the series and the separate wet result to`p3-shpem-15um-electrochem`, and attaches the cell'sEC:DMCplasticizer recipe to that same specimen without resolving which measurements share that state. This carries a real specimen conflation risk even though individual quoted sentences are genuine.

**The real thickness conflict is not surfaced as conflicting structured facts.** P3includes the Methods12µm/PE15µm sentence in identity evidence, but its structured properties only take the Resultsabout15µm value. Its specimen label also fixesabout15µm. It therefore fails to present the12-versus15µm conflict explicitly. This is particularly revealing because the model did quote the12µmstatement somewhere; source availability alone did not preserve the conflict.

**Some proposed property-to-specimen assignments are stronger than the source establishes.** P3attaches average pore diameter1.0µm to its`optimal`formulation, and healed strength recovery to a named membrane specimen, though the source does not independently specify that those demonstrations share every optimal salt/crosslinker/film parameter. It does keep the20µm/10%-loading morphology specimen separate, a useful partial safeguard. Review linkage rather than treating the presence of an ID as proof of an exact tested recipe.

**Unit and condition extraction is incomplete.** Rawp3uses`unit:null` for`about2h` and`about65%`, even though time and percentage units are present in those values. P2's280°Cthermal-stability fact omits the nitrogen atmosphere supplied by the abstract. Conductivity entries mostly include temperature but do not attach the EIS method/frequency/electrode facts. No unsupported30°Cnumber was created, but the six-field cards are not complete test records.

**Device result coverage is limited.** Rawp3distinguishes proposed separator application from demonstrated LCO-based-cell use, which is correct. It does not extract the explicit149/158mAh/g capacity results,0.1C/1C-rate performance, or96.1%/95.9%/96.9%100-cycle retention values. These omissions do not invalidate polymer retention; they limit claimed property/application coverage. The retainedp2matrix has no application items even though the rawp3membrane holds demonstrated device context.

**Background entity coverage is incomplete under the prompt's broad instruction.** Rawp4/p5correctly includePVDFandPE as additional polymers. ExplicitPMMA/PBA,PEG/PU andSIPE-5mentions from the introduction are absent. The model'sPVDFclassification reason also acknowledges reliance on conventional acronym knowledge; the article's cathode-composition quote alone does not mechanically prove its polymer chemistry. These are examples for manual review and future recall annotation, not a numerical all-entity recall estimate from the selected reference.

### Safe report wording

“In the Chen paper, the live model recovered the selected precursor and crosslinked-network identities and correctly separated their5MPa and21MPastrength results. It also foundPVDFandPEcomparison/components. Several ratio and origin fields required review because the output did not follow the card contract. TheSHPEMrecord remained under exact-name evidence review, and its raw specimen state and thickness conflict need scientific checking. The present quote checks do not establish complete or scientifically verified cards.”

No source values, original live outputs, production code or frozen reference labels were modified by this independent review.
