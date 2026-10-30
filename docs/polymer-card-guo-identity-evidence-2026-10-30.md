# Guo member identities and sample evidence

This is an assistant's focused primary-source check on 30 October 2026, not authenticated human annotation or an exhaustive accuracy benchmark. It uses the original main-text XML supplied to AutoSchema, converted with `jats_script_notation_v1`. The original Guo XML SHA256 is `b6e614f9b777ddcb51109ddfa334540b3cf9a0acd27d62cfa80d29caea3a6bd4`. [Guo et al., original paper](https://doi.org/10.1038/s41467-020-15949-8).

The machine-readable [focused reference](../examples/polymer_cards/identity_reference_2026-10-30.json) contains exact source spans, chunk identifiers, expected subjects and known limitations. It is an evaluation reference, not model output, and must not be supplied as an answer sheet to a model test described as independent.

## Explicit identities exist in the main text

The source does not require automatic expansion of `P1–P7` to establish these names. Results / Material characterization, paragraph 10, chunk `src-7fff0ff525a418c27c9f`, first reports successful synthesis of the polymers and then explicitly names **P3, P4, P6, P7, P1 and P2** in the characterization comparison. P5 has a separate explicit parent-polymer synthesis statement. [Guo Results](https://doi.org/10.1038/s41467-020-15949-8).

| Member | Direct source to attach | What it establishes |
| --- | --- | --- |
| P2 | `src-f11f8aed81613a0e81fc`, Results / Rheological and mechanical properties, paragraph 12 | The synthesized parent polymers include `P1, P2: PDMS–SS–IP`; the later comparison identifies P2 as lacking BNB. |
| P3 | `src-abdf1ced28f9b1e9fb83`, Methods / Polymer synthesis, paragraph 29 | An explicit polymerization procedure for P3 and the obtained purified P3 elastomer; direct synthesis evidence is available. |
| P4 | `src-7fff0ff525a418c27c9f` plus `src-f11f8aed81613a0e81fc` | Explicit named polymer characterization and an explicitly identified P4 film in mechanical testing. |
| P5 | `src-f11f8aed81613a0e81fc` | Synthesized parent `P5: PDMS–IP–BNB`; the text explicitly says its film lacks SS. |
| P6 | `src-7fff0ff525a418c27c9f` plus `src-35143d7cf8b1af205722` | Explicit named polymer characterization and the P6 film with reduced PDMS content. |
| P7 | `src-7fff0ff525a418c27c9f` | Explicit named polymer characterization; its BNB signals and low glass-transition context are described. |

These are source-backed formulation/member labels. The author uses PDMS–SS–IP–BNB as a series umbrella, but it is not an exact chemical alias for every control: P2 lacks BNB and P5 lacks SS. Do not place all their measurements on one exact-identity card. The exact ratios for most members are delegated to Supplementary Table 1, which was not supplied. Do not copy P3's recipe to the other members. [Guo synthesis and controls](https://doi.org/10.1038/s41467-020-15949-8).

## P3 requires different measurement samples

**GPC:** Methods / Polymer synthesis, chunk `src-abdf1ced28f9b1e9fb83`, first describes obtaining the **purified P3 sample**, then reports GPC using **THF as eluent**, with `M_{w}/M_{n} = 1.77.`. This is a purified-polymer GPC sample, not automatically a cast-film specimen. The current numeric matcher accepts the sentence-final value, but a valid identity plus an explicit GPC specimen and its linking evidence are still needed. [Guo Methods](https://doi.org/10.1038/s41467-020-15949-8).

**Film:** Methods / Film preparation, `src-3c26b5356cd78c6d5409`, describes dissolving P3 in CH₂Cl₂, casting and drying the film, then cutting it for testing. This anchors the mechanical/healing specimen rather than the GPC sample. [Guo film preparation](https://doi.org/10.1038/s41467-020-15949-8).

**Ambient healing:** Results / Universally self-healing capability, `src-848b57bcf6907681b207`, identifies P3 film and reports `93% ± 3%` healing efficiency after **two hours at room temperature**. [Guo ambient healing](https://doi.org/10.1038/s41467-020-15949-8).

**Underwater healing:** `src-350106dc0f244b268362` explicitly reports a severed P3 film healed **in water for 24 hours**, giving `93% ± 2%`. This is a separate observation and must not be merged with the ambient two-hour result. [Guo underwater healing](https://doi.org/10.1038/s41467-020-15949-8).

**Metric definition:** Methods, `src-b48dd634cfb0cbadc1e7`, defines mechanical healing efficiency as restored fracture strain divided by original fracture strain. Attach this passage to the healing records; do not call the percentage strength recovery. [Guo healing method](https://doi.org/10.1038/s41467-020-15949-8).

## P4 owns the 14,000% stretch result

Results / Rheological and mechanical properties, `src-f11f8aed81613a0e81fc`, explicitly describes the **P4 film** stretched nearly 140 times its original length at `10 mm min⁻¹`, and later names **P4 (14,000%)** in the comparison with P5. The Figure 2 caption, `src-ff90c7815b1740c544fe`, also identifies P4 in panels a/b but uses P3 in later tests. The broad family name and a shared figure do not establish that P3 owns the 14,000% value. [Guo mechanical tests](https://doi.org/10.1038/s41467-020-15949-8).

## Pei sample shorthand needs preparation and testing context

The numeric Results passage `src-5d598cf3569a0bb57b72` abbreviates the comparator labels to PEO (3.8 V) and PTMG-HDI (4.1 V). Preparation `src-6524f9582cedc0d6c138` explicitly makes PEO/LiFSI and PTMG-HDI/LiFSI electrolytes, while electrochemical Methods `src-705d4d9258f66326a788` states that the **SPEs** were tested for electrochemical stability at room temperature. These three passages together support electrolyte sample links; a matching bare PEO name in the numeric quote alone does not. [Pei original paper](https://doi.org/10.1038/s41467-023-43467-w).

## Generic implementation implications

1. When identity evidence contains only a member range, retrieve original same-paper passages containing the exact candidate label and its polymer context. Present the unchanged passages to the extraction/repair step. Avoid rewriting quotes, automatically expanding ranges or treating a mention in an unrelated figure as chemical classification proof.
2. Treat a property quote and its sample-attribution evidence as different requirements. If the supplied attribution evidence names a more specific sibling form than the selected bare specimen, hold that link for correction rather than accepting it as scientifically checked.
3. Represent exact series members and measurement samples separately. A purified GPC sample, a cast film and a healed/wetted film can belong to one polymer without being interchangeable measurement subjects.
4. A source-grounded repair must rerun each fact's evidence/unit/condition/sample checks after repairing identity. Correcting P3's name evidence must not automatically approve every previously held fact.
5. Preserve the original responses and report corrected or re-extracted records as a separate run. The focused reference is for testing; its expected values must not be copied into an allegedly independent extraction.
