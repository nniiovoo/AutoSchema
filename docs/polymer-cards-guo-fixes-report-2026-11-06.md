# Guo evidence, context and sample-link fixes

The targeted Guo fixes are implemented and source-reviewed. All three papers were extracted again, then reviewed against the unchanged checked evidence. The final view is **27 draft cards with 25 field/fact review records**. Thirteen of 17 selected measurement cases meet every criterion, compared with eight in the previous saved fresh run; six of six selected Guo identities match. These are selected pilot checks, not overall scientific accuracy.

[Readable summary](../examples/polymer_cards/guo_fixes_run_2026-11-06/summary.html) · [Cards and original evidence](../examples/polymer_cards/guo_fixes_run_2026-11-06/cards.html) · [Stage comparison](../examples/polymer_cards/guo_fixes_run_2026-11-06/evaluation/stage-comparison.json) · [Composition verification](../examples/polymer_cards/guo_fixes_run_2026-11-06/context-verification.json)

## Concrete changes

- **Exact source evidence:** new live schema `polymer_cards_strict_v4` asks for source-span IDs rather than generated quotations. The server retrieves the unchanged original text. IDs bind paper, chunk, source hash, text and Unicode character range. Unknown, stale or mismatched selections are held. Legacy quoted inputs remain strict; there is no fuzzy quotation repair.
- **Adjacent selected evidence:** two already selected source passages can support a qualified value across a boundary such as “ca.” and its number. Only touching/overlapping ranges or whitespace-only gaps in one chunk can be combined. Derived support retains all selected IDs and original offsets; it never bridges unselected words or changes the raw value.
- **Protocol navigation:** source-only Methods cross-references connect healing procedures to subsequent mechanical testing. They are navigation cues, not automatic global condition assignments.
- **Sample-link checking:** an explicitly described electrode/membrane/electrode cell stack is distinguished from adding salt to a polymer. The exception is narrow, checks electrode-token boundaries and leaves genuine additive preparations guarded.
- **Stable context repair:** optional `review_context_document` proposes only specimen links, conditions and evidence for anchored existing measurements. Values, units, names, identities and order are protected. Strict focus exposes only requested original property indexes and rejects edits outside that scope. An edit introducing a new target-property validation failure is held atomically. Raw proposals and composed records are separate.

The polymer-only retention rule and the six information groups are unchanged. No application-performance threshold, quality rank or uniform score was introduced. The original AutoSchema induction workflow remains separate from this additive polymer-card workflow.

## What is fixed in Guo

Original source: [Guo et al., Universally autonomous self-healing elastomer with high stretchability](https://doi.org/10.1038/s41467-020-15949-8).

| Observation | Source-supported final context |
| --- | --- |
| P3 GPC dispersity 1.77, with molecular-weight observations | Purified P3 measurement sample, THF and explicit GPC method; kept separate from film tests |
| P3 93% ± 3% ambient healing and 1200% ± 50% recovered strain | Healing conditions, post-healing tensile conditions and source-defined strain-recovery metric remain separate |
| P3 93% ± 2% after 24 h in water | Unsupported 60 × 20 geometry from another caption panel removed; relevant post-healing Methods and rate attached, without inventing water-bath temperature |
| P5 ca. 2,000% strain at break | Approximation preserved, both adjacent source selections combined transparently, applicable film-test conditions attached |
| Selected member identities P2–P7 | Explicit named source evidence, rather than range expansion |

Five selected Guo measurement cases meet all frozen requirements. P4 retains the valid original “nearly 140 times its original length” wording; the frozen reference uses a percentage representation, so that case remains a representation review. No numerical conversion was forced to award a match.

The final scoped pass applied five context edits after primary-source audit. It did not rewrite their measured values or units. Earlier context stages did change some allowed specimen links, including a Tg link; do not generalize the immutable-entity-ID guarantee to all measurement specimen IDs. [Detailed Guo source audit](polymer-card-guo-span-review-2026-11-06.md).

## Actual testing and model calls

The same original main texts were used for [Pei](https://doi.org/10.1038/s41467-023-43467-w), [Chen](https://doi.org/10.3390/polym13234155) and [Guo](https://doi.org/10.1038/s41467-020-15949-8). The reference answer files were frozen and never passed to a model.

| Stage | Actual model calls | Selected measurement matches | Selected Guo identities |
| --- | ---: | ---: | ---: |
| Previous saved V3 fresh baseline | Previous task | 8 / 17 | 5 / 6 |
| New V4 fresh source-only extraction | 3 | 11 / 17 | 6 / 6 |
| Whole-record source-grounded revision | 3 | 10 / 17 | 6 / 6 |
| First two context reviews | 2 | 10 / 17 | 6 / 6 |
| Strictly scoped, source-audit-assisted context review | 1 | 13 / 17 | 6 / 6 |

The whole-record revision regressed from 11 to 10 selected matches; the first two context passes did not improve that aggregate. Their outputs and rejected proposals are preserved. The final scoped pass repaired only the identified context targets. This history should not be presented as steady improvement from each model pass.

There were **nine successful new OpenAI gpt-5.4 requests**, with **726,954 returned tokens**, no failed requests and no automatic retries in this task. Fresh and whole-record responses were capped at 48,000 completion tokens; context reviews at 16,000, with 900-second limits. Source verification, composition and revalidation made no additional model calls.

The final two context requests included explicit **unverified primary-source audit concerns**, such as a possible caption-panel mismatch and absent method metadata. They did not include corrected numeric answers or the checked-reference file. The result is a source-audit-assisted correction pilot, **not a blind or held-out extraction benchmark**. The final combined view is deterministic composition of preserved model proposals; it is not another fresh provider response.

## Final three-paper output

| Paper | Draft cards | Field/fact review records |
| --- | ---: | ---: |
| Pei | 5 | 9 |
| Chen | 11 | 12 |
| Guo | 11 | 4 |
| Total | 27 | 25 |

There are 24 declared specific-polymer records and three families. These are not 27 unique, fully checked experimental materials. There are zero identity-review records in this final view, but that does not certify every chemical scope or family/member label. Review records include attribution, qualifier and metadata limitations; they are not 25 established wrong scientific facts.

All eight selected Pei cases stay matched. Chen still has important gaps: the 21 MPa record is held for its null specimen link; the wet-conductivity specimen label is too generic; and the conflict note preserves 12 μm Methods and about 15 μm Results but lacks a separate structured 12 μm observation. The full conflict case therefore remains incomplete. [Pei/Chen source audit](polymer-card-pei-chen-span-review-2026-11-06.md).

| Selected measurement | Final automated result | Interpretation |
| --- | --- | --- |
| guo-p3-gpc-pdi | Meets selected checks | Purified P3 sample, THF and explicit GPC method are now linked. |
| guo-p3-healing-ambient | Meets selected checks | Healing time/environment, post-healing tensile protocol and metric definition are separate. |
| guo-p3-healing-water | Meets selected checks | Unsupported panel geometry removed; post-healing Methods linked without inventing bath temperature. |
| guo-p4-stretch | Needs review | The source-supported “nearly 140 times” phrase differs from the frozen percentage representation. |
| pei-peo-voltage | Meets selected checks | LiFSI electrolyte form, original value and LSV protocol retained. |
| pei-hdi-voltage | Meets selected checks | LiFSI electrolyte form, original value and LSV protocol retained. |
| chen-precursor-strength | Needs review | Correct precursor on source review; strict singular/plural label matching still flags it. |
| chen-crosslinked-strength | Needs review | The source-supported value is held because its model record still has a null specimen link. |
| chen-wet-room-temperature-conductivity | Needs review | Qualifier and selected conditions present; specimen label remains too generic for the separate wet-form check. |
| pei-bhds-strength | Meets selected checks | Matrix film and selected mechanical-test conditions retained. |
| pei-bhds-elongation | Meets selected checks | Matrix film, percent unit and selected mechanical-test conditions retained. |
| pei-bhds-mn-monitoring | Meets selected checks | Reaction time/temperature stay distinct from GPC solvent and unknown instrument temperature. |
| pei-bhds-conductivity | Meets selected checks | LiFSI electrolyte and selected EIS conditions retained. |
| pei-bhds-lsv-limit | Meets selected checks | Original “beyond” qualifier and selected LSV protocol retained. |
| pei-bhds-transference | Meets selected checks | Dimensionless value and selected transference-cell conditions retained. |
| guo-p3-recovered-strain-ambient | Meets selected checks | Original recovery quantity and post-healing tensile context retained. |
| guo-p5-strain-break | Meets selected checks | Original ca. qualifier, adjacent source support and attributable film-test conditions retained. |

## Verification and remaining limits

**232 software tests passed** at the final freeze. The final three-paper source check verifies **694 retained evidence-reference occurrences**: 681 direct selections and 13 derived adjacent unions. Repeated references count again. This measures source integrity, not 694 independent scientific verifications or model-authored quotation accuracy. V4 does not ask the model to write quotations.

The verifier reconstructs all context requests, custom response profiles and focus hashes, reproduces anchored composition, checks raw provider JSON, and verifies that numerical claims, units, entity identities and record order remain unchanged. The three reference hashes remain unchanged. All three papers are revalidated under the final policy, while their raw model responses remain intact.

Broader Guo family scope, DSC specimen specificity, other caption-panel assignments and four held Guo fields remain for review. This remains main-text-only work without supplements, OCR, graph extraction, exhaustive human gold annotation or experimental reproduction. Source-exact passages can still be scientifically misattributed; the separate source audit remains necessary.

[Artifacts and reproduction commands](../examples/polymer_cards/guo_fixes_run_2026-11-06/README.md) · [Contract](polymer-card-contract.md) · [Usage guide](polymer-cards.md)
