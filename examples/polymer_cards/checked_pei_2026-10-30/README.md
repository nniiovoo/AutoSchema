# One source-checked Pei polymer card

This is an **assistant source-checked reference**, prepared from Pei’s original main text and independently checked by another assistant. It is not authenticated human annotation, an exhaustive record or a scientific-accuracy score. It was **not supplied to the extraction/repair model**.

- [Read the card](checked-card.html) (open locally or download the HTML).
- [Portable paper/source manifest](papers.json), [selected source passages](source-excerpts.json), [checked input record](checked-records.json), [expected reference/unknowns](reference.json) and [validation receipt](validation.json).
- [Six focused evaluation cases](evaluation-cases.json). Values and units use exact reference notation after Unicode/whitespace handling; this is narrower than scientific equivalence.
- [Detailed source-check notes](../../../docs/polymer-card-checked-pei-2026-10-30.md).

The single card has all six groups populated: three monomer/building-block entries, three composition entries, three synthesis entries, six selected properties, two demonstrated applications and one author-synthesized source tag. Aliases are empty because no additional unambiguous material-specific alias was established.

The response is suitable for zero-call replay using the project CLI:

```sh
python extract_polymer_cards.py --papers examples/polymer_cards/checked_pei_2026-10-30/papers.json --records examples/polymer_cards/checked_pei_2026-10-30/checked-records.json --out-dir outputs/checked_pei_reference_replay
```

This command replays a checked reference. It is not a live model extraction.

## Source and license

Pei et al. (2024), *Interfacial self-healing polymer electrolytes for long-cycle solid-state lithium-sulfur batteries*, [DOI 10.1038/s41467-023-43467-w](https://doi.org/10.1038/s41467-023-43467-w). Original [JATS XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10774406/fullTextXML), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The original XML SHA256 was verified locally: `ffc5376b77b6b81e29c52134d1f96d0185752dd35d35cb48172b661b13c8e1a8`. Selected text preserves scripts using `jats_script_notation_v1`. No figures or supplementary files are redistributed. The selected-excerpt file has a different hash from the full original XML; the loader verifies that excerpt file and retains the original hash as provenance. Current JSON-source loading does not propagate the conversion flag to each resolved reference; the declaration remains in this source bundle and attribution.
