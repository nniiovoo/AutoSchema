# Polymer cards: fixes and three-paper rerun

The revised code improves extraction structure and catches additional mistakes. A new live run on the same three original main texts produced **19 draft cards**, and **8 cards contain at least one composition entry accepted by validation**. Scientific attribution problems remain. This is a small pilot, not an accuracy benchmark or a finished polymer database.

[Read the revised cards with source-review notes](../examples/polymer_cards/live_run_2026-10-30/cards-with-review.html) · [Cards in Markdown](../examples/polymer_cards/live_run_2026-10-30/cards.md) · [Source-review notes](../examples/polymer_cards/live_run_2026-10-30/review-notes.json) · [Comparison data](../examples/polymer_cards/live_run_2026-10-30/comparison.json) · [Original 28 October report](polymer-cards-live-report-2026-10-28.md)

## What changed

- **Scientific notation:** JATS preparation now preserves superscript/subscript boundaries, such as `10⁵` rather than `105`, and records its text transformation. Original XML hashes remain unchanged.
- **Numeric checks:** a complete sentence-final value such as `1.77.` is accepted. Partial ratios, fractions, exponents, decimals and values stripped of qualifiers are rejected. For example, `5.0` cannot stand in for `beyond 5.0`.
- **Extraction structure:** strict JSON schema requires all six groups, valid statuses, a composition-basis key and explicit sample-link evidence for properties. Unknowns can be null and remain for review. A complete synthetic example distinguishes a feed molar ratio from a polymer:salt mass ratio. A molecular-weight-only observation is no longer accepted as a recipe.
- **Sample review:** source evidence supporting the sample link is retained separately from the numerical quote. Advisory warnings identify shared sample labels and possible neat/additive confusion. They do not merge materials or automatically move measurements to another sample.
- **Run reliability:** completed papers are checkpointed. Incomplete runs have explicit metadata and a visible banner. Request timeout defaults to 300 seconds, with no automatic retries; failures have safe diagnostics.

Polymer identity remains the only retention criterion. Commercial origin, low performance and incomplete fields do not remove a polymer. The legacy application-screening and default extraction workflows were not replaced.

## What was actually run

Three new OpenAI `gpt-5.4` extraction calls completed on the original Pei, Chen and Guo main-text XML. The manifest and original source revisions match the earlier run. The live request used strict schema `polymer_cards_strict_v1`; schema/prompt fingerprints are saved in run metadata. The completed rerun reports three papers requested, three completed, and `run_complete:true`.

One preceding extraction request failed before returning a response; its cause was not established. A subsequent model-access health check succeeded before the separately recorded three-call rerun. No hidden automatic retries were used. Returned usage for the **three successful requests** was 104,153 tokens; this is not an accounting claim about the failed request.

Two final validator guards—preserving numeric qualifiers and rejecting molecular-weight-only composition—were added after the provider run started. The unchanged new model responses were therefore **revalidated offline with zero additional model calls**. The final output below is that revalidation, not a silently edited model answer. The [revalidation receipt](../examples/polymer_cards/live_run_2026-10-30/revalidation.json) records input hashes and validator revision. The revalidation's raw responses and source snapshot are byte-identical to the new live capture.

The original 28 October output and raw responses were also preserved; their SHA256 values were checked. The final local cards are in `outputs/polymer_cards_fixed_2026-10-30_revalidated/`, separate from both the original run and the new provider capture.

## Before and after

| Measure | 28 October baseline | 30 October rerun, final validation |
| --- | ---: | ---: |
| Raw entity records | 21 | 25 |
| Retained draft cards | 18 | 19 |
| Identities awaiting evidence review | 3 | 6 |
| Fact entries in review | 36 | 22 |
| Cards with accepted composition entries | 0 of 18 | 8 of 19 |
| Accepted composition entries | 0 | 14 |
| Composition entries missing a basis | 17 | 1 |
| Validation flags, including group summaries | 58 | 33 |
| Advisory attribution warnings | Check not implemented | 9 |

Counts come from the [saved comparison](../examples/polymer_cards/live_run_2026-10-30/comparison.json). Card identities and granularity changed between runs, so these are not paired accuracy measurements. Fewer review entries do not prove fewer scientific errors, and six held identities do not mean six confirmed nonpolymers. The nine advisory warnings are separate from quarantined facts and are not nine established mistakes.

## What the paper checks show

**[Pei et al. 2024](https://doi.org/10.1038/s41467-023-43467-w): disulfide polymers and batteries.** Seven cards were retained; four have seven accepted composition entries. The BHDS matrix and its salt-containing electrolyte have separate feed and polymer:salt ratios. Its 88.3 MPa film-strength result remains separate from electrolyte conductivity of `2.4 × 10⁻⁴ S cm⁻¹` at 30°C. The BHDS molecular-weight exponent is preserved, and the earlier wrong transfer of that value to PTMG-HDI was not repeated. However, PEO's 3.8 V and PTMG-HDI's 4.1 V results still point to neat-polymer labels even though testing context indicates their electrolytes. They now receive warnings, not automatic corrections. The BHDS raw `5.0` result from a `beyond 5.0` statement is withheld by the final qualifier guard. A broad family overlaps exact cards, and PVDF was omitted.

**[Chen et al. 2021](https://doi.org/10.3390/polym13234155): battery polymers.** Six cards were retained; three have six accepted composition entries. The 5 MPa precursor and 21 MPa cross-linked result remain separated. PVDF's 8:1:1 cathode recipe and component use are now filled. The wet room-temperature test better records the 10 µL electrolyte context, and nitrogen-atmosphere evidence is attached. The membrane/network scope still needs review, and the source's 12 µm versus approximately 15 µm thickness statements are not yet represented as an explicit conflict. Better-filled fields do not settle those distinctions.

**[Guo et al. 2020](https://doi.org/10.1038/s41467-020-15949-8): disulfide polymers.** Six cards were retained, with six additional identities held for evidence review. A range quote mentioning P1–P7 does not literally establish each individual label, such as P3, under the current name-evidence rule. This is an unresolved evidence representation issue, not proof those materials are nonpolymers. The `1.77` numeric punctuation bug is fixed in software, but its live observation remains held because P3 identity and GPC sample scope are unresolved. P3 healing information is present in raw output but not in an accepted P3 card. The broad family still carries a 14,000% stretch result belonging to P4; exact member attribution remains wrong. Only one card has one accepted composition entry after the molecular-weight-only guard.

## Checks and remaining limits

The full regression suite passed **108 software tests**, including source scripts, sentence punctuation, numeric fragments/qualifiers, composition field boundaries, strict request shape, sample evidence, warnings, safe errors and partial-run saving. This count is not a paper count or a scientific accuracy score.

All **303 retained evidence-reference occurrences** match their supplied source chunks after declared text/whitespace handling, with zero containment failures. Repeated citations count again. This is not 303 independently verified scientific claims. [Evidence check](../examples/polymer_cards/live_run_2026-10-30/evidence-check.json).

Only the original main texts were supplied: no supplement extraction, OCR or graph-data reading. The selected reference is not an exhaustive entity inventory. Neither run returned standalone nonpolymer candidates, so these live results do not measure negative-classification performance. This was one uncontrolled rerun, and the source review was an assistant's focused check rather than authenticated human annotation.

Next work should resolve exact family/member and wet/neat/electrolyte scope, attach explicit evidence for range-defined identities, represent conflicting conditions, and audit omissions. Keep the raw outputs intact and evaluate any further correction as a separately labeled result. **The implementation and rerun are complete; scientific checking and correction remain open.**
