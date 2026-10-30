# Chen sample and condition checks

This assistant source check uses the original main-text XML for [Chen et al. (2021)](https://doi.org/10.3390/polym13234155), with original SHA256 `cfd69ea12c067601a053396289614766ecd9d617fe86497483e61c116407fadc` and declared script-preserving conversion. It is a focused evaluation reference, not authenticated human annotation or a scientific-accuracy benchmark. Exact source spans and component-level matching criteria are in [the three-paper reference](../examples/polymer_cards/identity_reference_2026-10-30.json), which must remain outside the model prompt.

## Precursor and cross-linked strength are different subjects

Results §3.1, chunk `src-629027e6d27659cd9af9`, explicitly reports **5 MPa** for the self-healing polymer precursors and **21 MPa** for the cross-linked polymer network after adding BMI. The precursor name is grounded by preparation §2.3, `src-189865c0a792b53247cf`, which identifies the P(MMA-BA-(F-MA)) copolymer. The latter value must not be attached to the uncross-linked precursor. Neither strength statement alone proves the sample was the later liquid-wetted electrolyte membrane. [Original synthesis and characterization](https://doi.org/10.3390/polym13234155).

The reference therefore tests the two strength values separately, including precursor versus network specimen wording. It deliberately does not invent a tensile-test temperature absent from the cited statement.

## Room-temperature wetted conductivity is not the temperature series

Results §3.3, `src-84988e5beedccc653dff`, reports a separate ionic-conductivity observation **approximate to 2.56 × 10⁻³ S·cm⁻¹ at room temperature**, for SHP electrolyte membranes with **10 μL liquid electrolyte**. The same paragraph lists an eight-temperature series from **25 to 90°C**, with different values. Do not replace room temperature with 30°C or merge the wetted observation with that series. Methods §2.6, `src-35900701ee1c30a4aa44`, also describes the EIS cells as using liquid electrolyte. [Original electrochemical tests](https://doi.org/10.3390/polym13234155).

The focused case checks entity, source value/unit, a wet/liquid specimen context, room-temperature wording and 10 μL amount independently. Missing one piece should be reported as partial alignment, not as proof the paper's value is wrong. Preserve the source's approximation qualifier.

## Thickness has an unresolved contextual discrepancy

Methods §2.6, `src-35900701ee1c30a4aa44`, assigns **12 μm** to the SHP electrolyte membranes used in electrochemical tests and **15 μm** to the PE comparator. Results §3.3, `src-51a89a11fdf0a55dd640`, says all SHP membranes used in electrochemical-performance tests have thickness **about 15 μm**. [Original Methods and Results](https://doi.org/10.3390/polym13234155).

Keep both original statements and their source contexts. Do not transfer the Methods PE value to SHP, silently choose one SHP thickness, or claim these are necessarily measurements of one identical physical specimen. The reference records this under `review_expectations` as a potential sample/context conflict, rather than as a single correct scalar value.

## Evaluation limits

The reference now covers three primary papers, nine selected measurements and one contextual-review expectation. These are selected known problems, not a comprehensive entity inventory or a random test set. Source value/unit spelling, material identity, specimen form, conditions and required evidence are separate checks. No overall accuracy, precision or recall follows from these selected cases.
