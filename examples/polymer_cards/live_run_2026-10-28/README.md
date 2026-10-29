# First live polymer-card run

Actual OpenAI `gpt-5.4` extraction of three full main texts on 28 October 2026. Three calls returned 21 entity records; validation produced 18 draft card records and held three identities plus 36 facts for review. Some retained records overlap. No scientific accuracy score or complete polymer inventory is claimed.

Start with the [plain-English report](../../../docs/polymer-cards-live-report-2026-10-28.md), [card notes](cards-with-review.md), or [HTML cards with original evidence and warnings](cards-with-review.html). The HTML opens locally in a browser; GitHub may display its source.

## Files

- `cards.json`, `raw-responses.json`, `audit.json`: byte-for-byte copies of the first live run. They contain known unresolved errors and are not corrected ground truth.
- `cards-with-review.html`: the original card view with visible review warnings added. Underlying extracted facts were not changed.
- `cards-with-review.md`, `review-notes.json`: concise per-card findings.
- `evaluation.json`: actual run counts, token usage, limitations and implementation revision.
- `source-receipts.json`: primary URLs, original XML hashes and source-text coverage.
- `artifact-hashes.json`: hashes of original local outputs and published copies.
- `pei-review.md`, `chen-review.md`, `guo-review.md`: independent assistant source-review notes. These are focused checks, not exhaustive human annotations.

## Source attribution and license

Original evidence excerpts in these artifacts derive from the following papers, each published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/):

- Fei Pei et al. (2024), *Interfacial self-healing polymer electrolytes for long-cycle solid-state lithium-sulfur batteries*. [Original paper](https://doi.org/10.1038/s41467-023-43467-w).
- Chen et al. (2021), *Self-Healing of a Covalently Cross-Linked Polymer Electrolyte Membrane by Diels-Alder Cycloaddition and Electrolyte Embedding for Lithium Ion Batteries*. [Original paper](https://doi.org/10.3390/polym13234155).
- Guo et al. (2020), *Universally autonomous self-healing elastomer with high stretchability*. [Original paper](https://doi.org/10.1038/s41467-020-15949-8).

Text was selected, serialized from JATS XML and placed in extraction/review records. XML serialization flattened some superscript/subscript markup; scientific interpretation must be checked against the originals. These source-derived excerpts retain CC BY 4.0 attribution. Complete original XML files and local credentials are not included here.

The papers align with Nina's two domains; they are not claimed to be her unidentified exact seed papers. No supplements, OCR or graph-number extraction were used. The earlier curated replay remains a separate example in the parent directory.
