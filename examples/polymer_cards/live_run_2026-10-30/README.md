# 30 October polymer-card rerun

This is a new live three-paper OpenAI GPT-5.4 extraction, separate from the unchanged 28 October baseline. Three extraction requests completed successfully. A preceding request failed before returning a completion; its provider-side usage is unknown. A separate model-access check succeeded. Automatic request retries were disabled.

The final cards were automatically revalidated from the unchanged new model responses after adding qualifier-preservation and molecular-weight-versus-recipe guards. See `revalidation.json`; this step made zero additional model calls. No model number, quote or specimen link was silently corrected.

Read [cards with source-review notes](cards-with-review.html), [structured cards](cards.json), [review notes](review-notes.json), [audit](audit.json) and [comparison](comparison.json). The HTML is a static file: open its local copy or download it to view the cards; GitHub’s file page displays the HTML source.

The result is **19 retained drafts, six identities and 22 facts in review**, plus nine advisory sample-link warnings. **Eight cards contain 14 composition entries accepted by the program’s structural/evidence checks.** This is not a scientific-accuracy score. Important sample links, family/member identity and coverage remain unresolved.

All 303 retained evidence-reference occurrences match their supplied converted chunks; repeated references count again. This is not 303 independent scientifically verified facts. All 108 software tests passed for the final code. The main texts were supplied; supplements, graph-only data and exhaustive annotation were not.

Full original XML and `sources.json` remain outside Git. `source-receipts.json` records original-file hashes, conversion version and chunk counts. The source representation preserves scripts, e.g. 10⁵ and cm⁻¹; quotes match that declared conversion.

## Source attribution

Underlying main-text excerpts are reused under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Script notation was converted; original XML hashes are preserved. No paper figures are redistributed.

- Pei et al. (2024), *Interfacial self-healing polymer electrolytes for long-cycle solid-state lithium-sulfur batteries*. [Original paper](https://doi.org/10.1038/s41467-023-43467-w), [original JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10774406/fullTextXML).
- Chen et al. (2021), *Self-Healing of a Covalently Cross-Linked Polymer Electrolyte Membrane by Diels-Alder Cycloaddition and Electrolyte Embedding for Lithium Ion Batteries*. [Original paper](https://doi.org/10.3390/polym13234155), [original JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8659245/fullTextXML).
- Guo et al. (2020), *Universally autonomous self-healing elastomer with high stretchability*. [Original paper](https://doi.org/10.1038/s41467-020-15949-8), [original JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7184568/fullTextXML).

These papers align with Nina’s two research domains; they are not claimed to be her exact seed papers. Assistant source-review notes are not authenticated human annotations.
