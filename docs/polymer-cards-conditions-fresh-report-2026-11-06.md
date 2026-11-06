# Fresh polymer extraction: conditions, units and source discrepancies

The requested code changes and a fresh extraction of all three papers are complete. The result is mixed: selected Pei test context, separate percentage units and Chen’s explicit thickness conflict improved, while sample-link and quotation failures remain. These cards are drafts, not a checked database.

[Readable run summary](../examples/polymer_cards/fresh_run_2026-11-06/summary.html) · [Cards and original evidence](../examples/polymer_cards/fresh_run_2026-11-06/cards.html) · [Selected comparison](../examples/polymer_cards/fresh_run_2026-11-06/evaluation/comparison.json) · [Source-checked Pei example](../examples/polymer_cards/checked_pei_2026-10-30/checked-card.html)

## What changed

- Strict live schema `polymer_cards_strict_v3` adds source-linked `properties.conflicts`. The validator preserves both source-qualified observations, requires known specimen links, and keeps the discrepancy unresolved. It never selects or averages thicknesses.
- A source-only Methods index helps the model find protocols in the original text. Instructions require per-observation conditions, preserve uncertainties and separate reaction monitoring from measurement conditions.
- Explicit percentage values must also have a separate source-supported unit field. A missing `%` field is held; the program never fills it automatically. Dimensionless quantities may still have `unit:null`.
- Numerical properties display whether conditions were captured; populated conditions are not certified complete. Conflict notes and both original passages are visible on the cards.
- Evaluation checks separate units and selected Methods context, plus both thickness observations and their unresolved note. Checked answers remain evaluation inputs only.
- The default completion limit remains 24,000 tokens. An explicit limit up to 48,000 is now allowed for longer evidence-rich responses; there are no automatic retries and truncated paper responses are rejected.

See the [contract](polymer-card-contract.md) and [usage guide](polymer-cards.md).

## What actually ran

Three completed OpenAI `gpt-5.4` source-only extraction requests were made: one for each original main-text paper. They received primary text plus lexical source-navigation cues, with **no prior extraction proposals or checked answers**. This differs from the 30 October run, which revised saved proposals.

The first attempt was rejected with HTTP 401 and completed no paper. After secure credential replacement, Pei completed at a 24,000-token cap. Chen’s next response hit that cap and was rejected without accepting partial paper records. An explicitly initiated fresh request for Chen and the first Guo request then completed with 48,000-token caps and 900-second limits. Guo’s completed response used 26,442 completion tokens. The earlier Pei limit was 600 seconds.

The final view combines the three completed fresh responses from two preserved capture batches. No value, quote, identity, condition or sample link was manually rewritten. Between batches, only the CLI’s permitted token-budget bound changed; the schema, system prompt, source snapshots, scientific validation code and checked reference were unchanged. Each recorded user prompt reconstructs from its source document, and parsed provider output equals the saved response.

There were **three successful requests, one truncated request and one separate authentication failure**. Returned usage for the three successful requests was **118,408 tokens** (57,498 input and 60,910 completion). Failed Chen usage was not persisted by the earlier error path and is excluded; this is not a total billed-usage claim. No credentials are in the published artifacts.

## Draft output

| Paper | Raw entity records | Draft cards | Identity review records | Other field/fact review records |
| --- | ---: | ---: | ---: | ---: |
| Pei | 7 | 7 | 0 | 8 |
| Chen | 5 | 5 | 0 | 4 |
| Guo | 12 | 9 | 3 | 26 |
| Total | 24 | 21 | 3 | 38 |

The 21 cards contain 18 declared specific-polymer records and three families. They are not 21 unique verified experimental materials. Forty-one review records include held identities, properties, specimens and other fields; they are not 41 established scientific errors. No standalone nonpolymer root was proposed in this live run, so it does not measure nonpolymer rejection performance.

## Comparison against unchanged checked evidence

| Selected check | Previous saved revision | Fresh extraction |
| --- | ---: | ---: |
| Six Pei BHDS complete-context cases | 0 / 6 | 6 / 6 |
| New, stricter 17 measurement cases | 3 / 17 | 8 / 17 |
| Six selected Guo identity cases | 6 / 6 | 5 / 6 |
| Explicit Chen 12 μm / about 15 μm unresolved conflict | Absent | Both reports and note retained |
| Original nine measurement cases | 6 / 9 | 3 / 9 |

These checks show **mixed progress**, not an overall accuracy improvement. The original nine-case results regressed, and the stronger Methods checks should not hide that. Record granularity and run mode differ; the pilot is not a controlled paired accuracy study.

For separate percentage-unit capture, 19 of 20 percent-containing raw property records in the earlier response had null unit fields. The fresh response has zero null unit fields among 24 such records. This measures field presence on differing record sets; it does not certify every unit, sample or fact scientifically correct. P4’s ratio-style phrase is a separate representation issue, not proof a percent unit was dropped.

| Selected measurement | Fresh automated result | Source-review interpretation |
| --- | --- | --- |
| guo-p3-gpc-pdi | Needs review | Held: the model rewrote the original subscript notation in its quotation. |
| guo-p3-healing-ambient | Needs review | Percent unit, healing duration/environment and metric definition captured; subsequent tensile protocol missing. |
| guo-p3-healing-water | Needs review | Percent unit and underwater healing context captured; subsequent tensile protocol missing. |
| guo-p4-stretch | Needs review | Source-supported “nearly 140 times” wording differs from the frozen percentage representation; no forced conversion. |
| pei-peo-voltage | Needs review | LSV conditions captured, but the model left the measurement specimen link null; held. |
| pei-hdi-voltage | Needs review | LSV conditions captured, but the model left the measurement specimen link null; held. |
| chen-precursor-strength | Needs review | Correct precursor ownership on source review; strict matcher does not accept plural “precursors” for singular reference term. |
| chen-crosslinked-strength | Meets selected checks | Selected value, unit and cross-linked specimen checks match. |
| chen-wet-room-temperature-conductivity | Needs review | Wet 10 μL specimen, temperature and some EIS conditions captured; approximation qualifier, explicit volume condition and blocking-cell condition incomplete. |
| pei-bhds-strength | Meets selected checks | Matrix film, value/unit and mechanical loading condition captured. |
| pei-bhds-elongation | Meets selected checks | Matrix film, separate percent unit and mechanical loading condition captured. |
| pei-bhds-mn-monitoring | Meets selected checks | Reaction-monitoring time/temperature and GPC solvent captured; do not interpret reaction temperature as GPC instrument temperature. |
| pei-bhds-conductivity | Meets selected checks | LiFSI electrolyte, temperature and EIS frequency range captured. |
| pei-bhds-lsv-limit | Meets selected checks | LiFSI electrolyte, “beyond” qualifier, scan rate, voltage range and temperature captured. |
| pei-bhds-transference | Meets selected checks | Dimensionless value, Li symmetric cell and polarization voltage captured. A further section-wide temperature detail remains missing outside this frozen case. |
| guo-p3-recovered-strain-ambient | Needs review | Percent unit and healing context captured; subsequent tensile protocol missing. |
| guo-p5-strain-break | Meets selected checks | Original approximation, percent unit and selected tensile protocol captured. |

## What the source review found

**Pei:** all six selected BHDS observations now retain their required Methods context and correct film/electrolyte forms. However, the model left specimen IDs null for the 3.8 V PEO and 4.1 V PTMG-HDI comparator observations; the validator correctly holds them despite captured LSV conditions. PVDF is still omitted. A further electrical-section default temperature is missing from the transference record outside the frozen six-case criteria. [Pei source review](polymer-card-pei-fresh-source-review-2026-11-06.md).

**Chen:** Methods assigns SHP 12 μm and the PE comparator 15 μm; Results assigns electrochemical SHP membranes about 15 μm. The new card preserves the two SHP statements and an unresolved note with both passages. It neither chooses a thickness nor invents swelling or another explanation. Other prepared, optical and healing specimen thicknesses still need clearer separation. The 5 MPa precursor check is a plural-wording limitation of the matcher, while the conductivity qualification/context gaps are real output omissions. Some held cell-configuration links are conservative-checker limitations. [Chen source review](polymer-card-chen-fresh-source-review-2026-11-06.md).

**Guo:** percent units are captured separately, but several healing measurements still lack the subsequent tensile loading condition. GPC and other facts are held because the model rewrote the source’s subscript/chemical notation inside claimed verbatim quotations. P7 has a named passage in the paper, but its identity evidence uses a range-only passage, so its card remains held. Do not interpret this as P7 being absent from the paper. [Guo source review](polymer-card-guo-fresh-source-review-2026-11-06.md).

## Validation and limits

**176 software tests passed** at the final code freeze, including regressions for lost conflicts, missing percentage units, safe rendering, conflict evaluation and explicit response-budget bounds. All **413 retained evidence-reference occurrences** match supplied source chunks after declared source conversion/whitespace handling; repeated references count again. Neither figure is scientific accuracy.

The evaluation reference was frozen before the successful extraction calls. Three original XML hashes, 19 selected excerpt chunks and 30 explicit source spans were checked. The earlier reference files and published 30 October run remain intact. Reproduction helpers verify original input/request hashes and combine completed requests without editing their records; they make no model calls. [Reference and commands](../examples/polymer_cards/condition_reference_2026-11-06/README.md).

This remains a small assistant source-checked pilot using main texts. It does not include supplements, OCR, graph extraction, exhaustive human annotation or experimental reproduction. A valid unresolved conflict note is a record of uncertainty, not a resolution of the source discrepancy.

The requested implementation and fresh comparison are complete. The next work is quotation fidelity and exact identity/sample links, followed by fuller section-wide protocol coverage and omission review before releasing checked data.
