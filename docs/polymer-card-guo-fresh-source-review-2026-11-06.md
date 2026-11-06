# Guo fresh extraction: units, identities and source-fidelity review

This bounded assistant review checks the fresh Guo result assembled unchanged in `outputs/polymer_cards_fresh_2026-11-06_complete/`. No raw record, source quotation, reference answer or production code is edited here. This is a small selected source audit, not a chemical-accuracy estimate or a claim of overall improvement over the earlier revision.

Original source: [Guo et al., Universally autonomous self-healing elastomer with high stretchability](https://doi.org/10.1038/s41467-020-15949-8), original XML SHA256 `b6e614f9b777ddcb51109ddfa334540b3cf9a0acd27d62cfa80d29caea3a6bd4`, declared `jats_script_notation_v1` conversion. Main text only; exact member proportions in unavailable Supplementary Table 1 remain unknown.

The raw response proposes 12 entities; nine cards remain and three identity records are held. The paper has 29 review records, including held identities and child fields. That count is not 29 scientifically false numbers.

## Percent fields improve while some test conditions remain missing

The fresh P3 card retains these source-supported observations with separate percent units and correct reported uncertainty:

- **93% ± 3% healing efficiency**, healed film at room temperature for 2 h.
- **1200% ± 50% recovered fracture strain**, the same reported healing conditions.
- **93% ± 2% healing efficiency**, a distinct film healed in water for 24 h.

The efficiency observations also attach the original definition as restored fracture strain relative to original fracture strain (`src-b48dd634cfb0cbadc1e7`). These are not strength-recovery measurements. The underwater result is not silently made an ambient-healing result, and no numerical water-bath temperature is invented.

However, the subsequent tensile-test loading rate **10 mm min⁻¹** and its Methods passage (`src-bf623a19fffc11e5efc2`) are missing from these three observations. The stronger selected cases therefore still require review even though their values, percent units, healing conditions and material forms are represented. Healing time/environment and post-healing tensile loading are different conditions.

P5's **ca. 2,000% strain at break** retains its qualifier and separate `%` field, P5 film specimen, room-temperature (20°C) tensile condition and 10 mm min⁻¹ rate. It meets the stronger selected case. P2's 100% stretchability also has a separate percent unit and the stated tensile conditions.

P4 remains **“nearly 140 times its original length”**, with a P4 film, 10 mm min⁻¹ loading rate and room-temperature condition. This is a source-supported ratio-style phrase. Its mismatch with the frozen 14,000% reference remains a raw-representation review. A null unit on that phrase is not by itself proof the percent unit was lost, and no forced numerical conversion was made to satisfy the reference.

## The sixth selected identity fails attachment, not existence in the paper

P2–P6 meet their selected explicit-label checks. P7 is held because its `identity_evidence` quotes only the **P1–P7 range**. The model's separate classification evidence actually includes an original passage explicitly naming **P3, P4, P6 and P7** in polymer characterization (`src-7fff0ff525a418c27c9f`). The source therefore supports P7's identity, but the required explicit identity evidence is not attached to the identity field in the fresh response. The validator does not automatically expand the range or borrow the other field to repair it.

This is a model evidence-placement/strict-contract issue; do not claim the paper lacks evidence for P7. Its exact formulation ratio remains unknown without the supplementary table.

The broader PDMS–SS–IP–BNB umbrella and HO–PDMS–OH entries are also held because their quoted classification evidence does not match the supplied converted source text. The umbrella is declared a specific polymer in the raw response despite varying-ratio family language; its scope would deserve review even after the quotation problem were corrected. Do not assume P1 or P5 contains every disulfide/BNB unit named by the umbrella.

## Quote rewriting prevents valid-looking GPC facts from passing

The P3 response proposes **63 KDa**, **112 KDa** and dimensionless **1.77**, with THF/GPC context and a purified-sample link. Those scientific quantities appear in original Methods / Polymer synthesis (`src-abdf1ced28f9b1e9fb83`). But the model rewrites evidence notation:

- Source `CH₂Cl₂` becomes `CH2Cl2` in the purported original purification quotation.
- Source `M_{n}`, `M_{w}` and `M_{w}/M_{n}` become `Mn`, `Mw` and `Mw/Mn`.
- Elsewhere, source prime/script notation is simplified inside quotations.

Exact quotation containment after declared NFC/whitespace handling consequently fails. The purified-sample specimen is also held, and related synthesis, composition, monomer and application fields have similar quotation-fidelity problems. These are source-fidelity failures in the model's proposed quotations, not proof the original paper lacks a recipe or its GPC values. The correct response is not to silently rewrite historical model records or weaken the frozen references.

The P3 GPC 1.77 result therefore remains absent from retained facts. A null unit is appropriate for this dimensionless ratio; units are not the reason it is held.

## Other holds and coverage limits

Some proposed bound-valued observations omit qualifiers in their raw values: the underwater **up to 1230% ± 30%** strain and saltwater efficiency that could **reach up to 89% ± 3%** are shortened to unqualified values. Strict validation holds them. The numbers are in the source, but the qualifiers matter.

The notched-film 1300% result also lacks a retained film link after that specimen's quote fails. Background PDMS, polyurethane and saturated styrene-butadiene-styrene values are held without linked specimens. They must not be treated as newly measured results from this experimental series. The polymer-only task still permits background/comparator polymers; it does not turn their literature values into current-paper experiments.

The fresh response does not supply a separate PMMA card even though the source names PMMA as the GPC standard. This is another bounded coverage observation, not an exhaustive missing-polymer inventory.

The source's unusual **92.9% ± 30%** rejoined-film strain is preserved rather than silently corrected. The paper—not the extractor—must remain the authority for the reported number, with source review available for any suspected typographical issue.

The fresh run demonstrates corrected percent fields in several targeted observations, alongside incomplete tensile context, source-quotation rewriting, an identity-evidence attachment failure and missing entities. The result remains draft data and does not justify a blanket claim that all three papers improved.
