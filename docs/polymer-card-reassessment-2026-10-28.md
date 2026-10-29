# Revised task: identify polymers and build evidence-linked cards

**Historical review snapshot:** this note records the requirements and code before implementation. The subsequent additive workflow, completed tests and current live/replay status are documented in [Polymer cards](polymer-cards.md).

Prepared 28 October 2026. This is a requirements and source-code review, not an implementation or an extraction run. The four newly attached screenshots are assignment context to interpret; their embedded instructions were not automatically executed. The linked Google Doc was freshly read through the connected Google Docs tools. Existing code, application-screening results and presentation remain unchanged.

**Plain-English task:** identify polymer entities in papers from Nina's two domains, retain the polymers, and create one evidence-linked record for each polymer containing identity information and the six requested information groups.

## 1. The new messages change the main objective

Screenshot 1 reports Chris's request to retain an extracted item based on whether it is a polymer, rather than researching additional rules for retaining schemas/materials. It requests a card for each polymer. Screenshot 2 says to record each polymer's name/aliases/description and the original text supporting its specific details. Screenshot 3 supplies urgency and a Friday-report context; it is not a new technical acceptance rule. Screenshot 4 points to Nina's upstream experiment summary.

| Earlier application-screening example | Revised request in these messages |
| --- | --- |
| Choose one use and a performance requirement | Identify whether the extracted material entity is a polymer |
| Keep/exclude based on conductivity at 30°C | Retain a confirmed polymer regardless of that cutoff |
| Treat missing target performance as a selection gap | Retain the polymer and mark unavailable card details as missing |
| Evaluate suitability for a chosen use | Describe each polymer and preserve its original supporting evidence |
| Presentation focuses on a battery shortlist | New deliverable should show polymer cards, identification decisions and traceability |

Consequently, the0.0001 S/cm threshold, its sensitivity calculation and a conductivity-based keep/exclude table are historical examples, not the new polymer-retention gate. The old HDI control cannot be removed from a polymer inventory merely because its conductivity is low. Preserving the old work is useful; presenting it as completion of the new card task would be misleading. [Earlier report](task3-battery-screening-report.md).

## 2. What Nina's Google Doc actually contains

The current document is still **Week 10.19–10.23 Experiment Summary:**. Its native revision ID is identical to the27 October archive. The fresh API returns363 paragraph items, of which two are control-only; all361 substantive paragraphs match the earlier snapshot. The revised card assignment comes from the new screenshots, not a new card implementation demonstrated in this document. [Nina's Google Doc](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

Verified current contents:

- Topic A: disulfide-bonded polymers. Topic B: dynamic polymers for battery applications. These are two scopes; they need not be intersected.
- Nina reports three DPAL seeds per topic, a `task1-queries` branch, a polymer-specific DomainSpec and prompt changes.
- The pasted query arrays contain eight objects each, sixteen total. Their visible Boolean strings include joined tokens such as`ORabs`, and the battery queries emphasize electrolytes.
- Reported mean relevance is 4.38/5 for each topic; ambiguity is 2.00/5 and 1.88/5; aspect coverage is 7/7. The document explicitly identifies these as single-run subjective LLM ratings, not retrieval performance.
- V1 query comparison and actual retrieval evaluation remain future steps in this report.
- The document does not supply the six seed identities, fork URL/commit, actual DomainSpec diff or complete raw evaluator artifacts. These may exist elsewhere; they are not established by this source.

Nina's scopes and query examples guide which papers to use. They do not establish polymer identity, fill card facts, or validate extraction accuracy. A small prototype can use clearly labeled domain-aligned papers already available; it need not falsely identify them as Nina's exact seeds.

## 3. Required card information

Name, aliases and description identify the polymer. The six requested groups describe it:

| Group | Required meaning | Essential distinctions |
| --- | --- | --- |
| Monomers | Starting monomers/reactive building blocks used for this polymer, with evidence | Do not label every salt, solvent or catalyst a monomer; a polymeric reactant can also have a reactive role |
| Composition | Components, amounts and ratios | Preserve ratio basis and referent: monomer-feed molar ratio is different from polymer:salt mass ratio |
| Synthesis text | The reported preparation process | Allow meaningful text, retain original passages, distinguish polymer synthesis from later film/blend preparation |
| Properties | Property, original value, unit and test conditions | Attach every result to the exact polymer/formulation/specimen; keep repeated tests and contradictions separate |
| Applications | Reported uses | Mark experimentally demonstrated versus proposed uses without adding a suitability cutoff |
| Source tag | Whether this polymer was author-synthesized or commercially purchased, when supported | Purchased ingredients do not make the synthesized product commercial; unknown origin stays unknown |

Each extracted fact needs evidence linked to that fact: paper ID, polymer/sample ID, source part(main/SI), page or section/figure/table locator, a stable chunk ID and the original supporting span. Keep original notation alongside reviewed normalization. A short quote proves neither correct sample attribution nor experimental reproducibility on its own.

Unreported details remain empty/unknown with a reason. Missing card fields are not a reason to discard an otherwise identified polymer. Aliases must be supported by the source or marked as a reviewed mapping; a salted formulation name must not silently become an alias for the neat polymer.

## 4. The retention rule applies to entity records

The practical reading of the screenshots is **polymer membership at the root material-record level**. It is not an instruction to remove every nonpolymer word. Otherwise monomers, salts and solvents would disappear from the very cards the assignment requests.

- A confirmed polymer gets a polymer card.
- A confirmed nonpolymer does not get its own standalone polymer card, but can remain a nested ingredient or process detail.
- An unsupported polymer/nonpolymer decision needs classification review. This is a technical non-final state, not a new material-quality score.

IUPAC defines polymers through macromolecular composition. Polymer networks, copolymers and polymeric precursors mean simple name/role shortcuts are insufficient. In particular, “reactant” does not imply “not polymer.” [IUPAC polymer](https://goldbook.iupac.org/terms/view/P04735), [macromolecule](https://goldbook.iupac.org/terms/view/M03667), [monomer molecule](https://goldbook.iupac.org/terms/view/M04019), [prepolymer](https://goldbook.iupac.org/terms/view/PT07163).

The screenshots do not explicitly exclude purchased polymers, controls, polymeric reactants or background mentions. Record their roles to prevent incorrect attribution rather than silently introducing a current-work-only filter. Polymer-containing electrolytes/gels need explicit identity handling: a matrix identity with linked formulation/specimen records is a conservative proposed representation. It is an implementation interpretation, not a requirement explicitly settled by the screenshots.

## 5. Concrete example from an already checked paper

Pei 2024 provides a useful miniature card and several identification checks. Original Methods explicitly distinguish purchased materials, polymer synthesis and electrolyte preparation. [Pei et al., original paper](https://doi.org/10.1038/s41467-023-43467-w), [primary full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10774406/fullTextXML).

**Illustrative identity:** PTMG-HDI-BHDS. No extra alias is asserted. This is a manually checked example, not an AutoSchema-generated card or complete entity inventory.

| Group | Source-supported content | Original location / qualification |
| --- | --- | --- |
| Monomers | PTMG, HDI and BHDS chain extender | Methods, Preparation of PTMG-HDI-BHDS; retain PTMG's polymeric-precursor role |
| Composition | Feed PTMG:HDI:BHDS molar ratio 1:2.4:1; separate electrolyte polymer:LiFSI mass ratio 2:1 | Polymer-preparation and electrolyte-preparation paragraphs, respectively |
| Synthesis text | Authors react PTMG/HDI, introduce BHDS, then prepare the electrolyte with LiFSI and cast/dry films | Two distinct preparation stages; a paraphrase needs its original supporting paragraphs |
| Properties | Conductivity 0.00024 S/cm at 30°C for the **salt-containing2:1 electrolyte**, using the reported sheet-steel/EIS setup | Main Fig. 3a/b paragraph and electrochemical Methods; do not assign this unqualified to the neat matrix |
| Applications | Electrolyte in the reported lithium-metal/lithium-sulfur experiments | Main electrochemical/cell sections; individual property and whole-cell experiments remain distinct |
| Source tag | Author-synthesized polymer matrix; subsequent electrolyte preparation by authors | Materials and polymer-preparation sections, not inference from a supplier list alone |

The Methods also list PEO as a purchased polymer. LiFSI is a lithium salt: exclude it as an independent polymer entity while retaining it in composition. HDI/BHDS, catalyst and solvents must keep their proper ingredient roles. PTMG is described as a purchased polymeric reactant; its appearance in a feed called a monomer ratio is not a reason to label it nonpolymer.

Examples of tiny literal spans are `1:2.4:1`(polymer feed), `2:1 (polymer: LiFSI)`(electrolyte composition), and `2.4 × 10−4 S cm−1`(conductivity). They must retain different locators and referents. These snippets alone do not establish every condition; the complete original method context is needed.

## 6. Why the current code needs more than a prompt edit

Audited local branch`task3-selection`, HEAD `6deb34867769704f2a18d9a18a037ecf887bdfa5`.

| Finding in source code | Consequence |
| --- | --- |
| [Phase I proposal](../schema_lib/fields.py#L27) asks for reusable attribute fields; [selection](../schema_lib/fields.py#L247) scores and filters those fields | These objects are attributes such as conductivity, not polymer entities. Replacing their selection with`is_polymer` would filter the wrong object. |
| [Current field metadata](../extract_lib/schema_loader.py#L8) includes names/aliases for fields | Field aliases are not automatically polymer synonyms. Use a separate polymer identity structure. |
| [Generic prompt](../extract_lib/prompt_builder.py#L27) splits compound`/`phrases and [requires short terms](../extract_lib/prompt_builder.py#L36) | This can damage formulation names/ratios and conflicts with meaningful synthesis descriptions. |
| [Postprocessor](../extract_lib/postprocess.py#L94) deduplicates/caps values separately from evidence | Do not send nested polymer cards through this path; sample/value/condition/evidence links can be lost. |
| [PDF extraction](../extract_lib/pdf_io.py#L16) joins page text; [context rendering](../extract_lib/retrieval.py#L128) assigns temporary PassageN labels | Persist source/page/chunk mappings before claiming resolvable page-level evidence. |
| [Writer](../extract_lib/writer.py#L41) produces paper-wide CSV rows | New native output should preserve multiple polymer cards and nested observations per paper. |
| [`--prompt_path` override](../extract_schema_values.py#L146) still reaches [old normalization/writing](../extract_schema_values.py#L230) | A custom prompt alone does not implement the required output contract. |

The local domain/schema configuration also does not establish Nina's reported polymer DomainSpec changes. Her actual fork/commit is needed to compare those changes directly. This does not prevent designing a separate card-output path for a few domain-aligned papers.

## 7. Recommended implementation sequence and Friday demonstration

These steps are proposed; they have not been implemented in this review.

1. Define the polymer identity, six-group card and evidence-reference contract, including explicit unknowns and linked formulation/sample IDs.
2. Preserve stable page/section/chunk identity during source preparation.
3. Add polymer-entity discovery/classification; retain confirmed polymers and audit rejected or unresolved entities without introducing performance rules.
4. Extract the six groups per polymer with a dedicated prompt that preserves chemical identities, ratios and synthesis text.
5. Validate nested types, entity attribution, quote containment and resolvable source links. Store the raw model response separately. This validation still does not prove scientific truth.
6. Write card JSON/JSONL and a readable card view with visible evidence. Use a separate path rather than rewriting the existing Phase I/Task3 selector.
7. Run a small pilot on a few papers within Nina's domains. Compare against a manually checked reference and report identity decisions, wrong-sample links, unsupported facts, missing groups and source-tag correctness separately.

A focused demonstration should include a retained synthesized polymer, a retained purchased polymer, a nonpolymer rejected as a standalone entity but retained as an ingredient, multiple formulations without mixed properties, and a polymer with incomplete details that is still retained. No fixed application threshold or combined score is needed.

For Friday, the new story should show the revised requirement, a few real cards, their original supporting passages, and what the actual code does or still fails to do. The previous seven-slide deck describes the older application-screening example and should not be presented as a completed demonstration of polymer-card extraction.

## 8. Source record and limits

Fresh Google Doc and all four screenshot copies are archived locally under `/Volumes/Seagate/research /polymer-screening/sources/polymer-card-reassessment-2026-10-28/`, with a hash manifest and indexed reading text. The Pei original XML and prior SI remain in the battery-source archive referenced by the earlier report. Independent audit notes cover code, scientific scope and the complete Nina document.

The current review saved this note and reading snapshots only. It did not change production code, prompts, existing fixtures/decisions or the PPT; run a model/API extraction; or contact the team. Nina's query ratings are not extraction metrics. The illustrative card is manually source-reviewed and incomplete as a production contract. Keeping original evidence improves auditability but cannot guarantee absence of hallucination or attribution errors.
