# Selected conditions, units and thickness reference

This is an **evaluation-only**, assistant source-checked reference for the 6 November 2026 fresh extraction. It is not authenticated human annotation, an exhaustive inventory or experimental reproduction. No checked answer or file in this directory is to be included in extraction prompts.

- `reference.json`: six named Guo identity cases, 17 selected measurement cases and one unresolved Chen thickness-context case.
- `source-excerpts.json`: 19 complete selected original main-text chunks, with source identity, location and original XML hashes. These are derivative excerpts from the declared script-preserving conversion.
- `source-check.json`: original file hash checks, older frozen reference hashes and this reference/excerpt hashes. No model calls were used to prepare the reference.

The unchanged older [nine-measurement/identity reference](../identity_reference_2026-10-30.json) and [six-property Pei reference](../checked_pei_2026-10-30/evaluation-cases.json) remain the comparisons with the previous run. This additive reference includes their 15 measurements, adds two explicit percent-valued Guo observations, requires separate unit fields when a source unit is reported, and strengthens selected Methods checks. Report the additive outcomes separately; do not compare its count directly with a weaker earlier case set.

## Conditions and units

Pei's 88.3 MPa matrix-film strength and 2000% elongation require the mechanical-test loading condition. GPC observations require the reported solvent while keeping reaction time/temperature separate from unknown GPC instrument temperature. Electrolyte measurements require the corresponding electrical protocol and actual specimen. The original source calls 5 cm per minute a “strain rate”; no normalized strain-rate conversion is invented.

Guo's healing conditions describe the cut film before subsequent tensile measurement. Healing duration/environment and mechanical loading remain separate. Percent units should populate their own fields, including 93% ± 3%, 93% ± 2%, 1200% ± 50% and ca. 2,000%. A null unit is appropriate for dimensionless Mw/Mn and lithium transference number; those do not become errors merely for lacking a unit.

Chen's room-temperature conductivity with 10 μL liquid electrolyte is separate from the 25–90°C series. The EIS frequency range, amplitude and blocking-electrode cell describe the conductivity protocol; the Li symmetric interface-stability cell is a separate test.

## Chen thickness remains unresolved

Methods assigns SHP membranes 12 μm and the PE comparator 15 μm. Results says all SHP electrochemical-test membranes are about 15 μm. Both SHP observations must remain with original evidence and a visible unresolved context/conflict note. Do not select a preferred thickness or claim the two observations necessarily describe one identical physical specimen. Do not transfer the PE comparator's Methods thickness to SHP.

## Sources and limits

The originals are [Pei et al.](https://doi.org/10.1038/s41467-023-43467-w), [Chen et al.](https://doi.org/10.3390/polym13234155) and [Guo et al.](https://doi.org/10.1038/s41467-020-15949-8). They are open-access articles under CC BY 4.0; original author attribution and source identifiers accompany the excerpts. Source text underwent declared `jats_script_notation_v1` conversion to retain superscripts/subscripts. No supplements, OCR or graph-only values were checked.

Case matching checks selected raw value/unit spellings, source-linked specimens and protocol context. Alternative condition spellings listed in the reference do not make the evaluator a numerical unit-conversion engine. Source quotation matching and a matched case are not an overall scientific-accuracy score.

To recheck the frozen files, original hashes, 19 derivative chunks and 30 explicit quote spans without model calls, run from the repository:

```sh
python3 examples/polymer_cards/condition_reference_2026-11-06/verify_reference.py --paper-manifest '/Volumes/Seagate/research /polymer-screening/sources/polymer-cards-2026-10-28/full-papers.json'
```

`baseline-evaluation.json` applies these new selected checks to the unchanged 30 October revision output: six identity cases match, three of 17 measurement cases meet every selected condition, 14 need source review, and the Chen context conflict is absent. That stricter baseline is separate from the original nine-case/six-Pei results. In particular, P4's supported “nearly 140 times” phrase differs from the frozen percentage representation; a ratio-style phrase is not by itself proof a percent unit was dropped.

## Saved-run comparison helpers

`compare_run.py` evaluates a saved fresh extraction against the unchanged reference sets and checks source/request hashes. `assemble_runs.py` combines only completed fresh responses from matching source-only capture batches; it rejects missing papers, duplicate responses, changed scientific processing or edited raw provider JSON. Neither helper makes model calls. The [published fresh run](../fresh_run_2026-11-06/README.md) provides a self-contained saved-comparison command and discloses the truncated/authentication attempts.
