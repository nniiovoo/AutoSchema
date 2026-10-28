# Nina's polymer experiment: reading and research notes

Read on **27 October 2026**. This document records learning from Nina's report and the six screenshots supplied by the user. It does not resume candidate screening, choose a battery application, set acceptance thresholds, change code or prompts, execute the report's commands, or edit Nina's Google Doc. Earlier wood-coating work remains historical work; no earlier artifact was deleted or relabelled as battery/disulfide research.

**Plain-English orientation.** Nina is working on the search questions AutoSchema uses to find papers. The report covers two topics and contains eight questions for each. The reported scores rate those questions; they do not yet show which papers were found or which materials should be kept. This reading records that stage and the information needed to understand it. [Nina, P003, P011 and P045–P049](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

## 1. Sources, scope and evidence labels

**Primary report:** [Nina, *Week 10.19–10.23 Experiment Summary*](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit). Native Google Docs content was read on 27 October 2026, from the single tab `t.0`, titled `Tab 1`. The API returned 361 nonempty paragraphs after traversing its body and tables. The document revision read was `AHj4eMTVXDpLujnuFFZbYIWKlSW4_45jxLC1Mm8G6eJeXqtqFp83hPcjNnZ5x4bgnLHY6uqkALUk3GDiIHoN3OAktu9Hok7JiFw1a3JauX0`. P001–P361 below identify the ordered paragraphs of that reading snapshot, not page numbers or native Google Docs anchor IDs. Original API indices are retained in the query inventory. Repeated links point back to the owning report rather than implying that a new independent source verified a claim.

**Evidence labels used in these notes:**

- **Report states:** Nina describes an action or result. The report is the source for that statement, but a narrative or pasted terminal output alone does not independently reproduce the experiment.
- **Directly inspectable in report:** the actual 16 query objects, wording, fields, counts and pasted evaluation summary can be examined.
- **Reading inference:** an interpretation made here from visible material. It is not an experiment Nina reported.
- **Unverified:** the underlying source/artifact was not supplied or was not inspected. Missing access does not prove that an artifact or experiment does not exist.
- **Future team direction:** suggestions quoted or paraphrased from screenshots. They are context for understanding later work, not authorization to execute those steps now.

The report has a seven-part summary, two baseline query-output sections, and a short evaluation transcript. No seed-paper titles, DOIs, embedded images, source hyperlinks, repository URL, per-query judge explanations, or V1 results appear in the native text read here. A separate native-comments read returned zero non-deleted comment threads, with no next page token. [Report, P001–P361](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

## 2. What the six screenshots change

The screenshots are supplied discussion context. Their requests are distinguished from the user's current instruction to **learn and take notes first**.

| Source | What the message communicates | Interpretation for this reading |
| --- | --- | --- |
| S1 | Lisa says the wood-material example can stop at its present state and the group now wants a small test aligned with Nina's two scopes. | The previous wood case is useful historical work, but it is not the current shared research scope. |
| S2 | The two scopes are polymers containing dynamic disulfide bonds, and dynamic polymers used for batteries. | Treat these as two separately named entry scopes. The message does not define their intersection as mandatory. |
| S3 | A later example can use a concrete case from either scope. Lisa suggests two layers: general information checks, and checks depending on a particular material/use. | Record the distinction conceptually. No new rule table or material decision is created in these notes. |
| S4 | A battery sub-use, such as a polymer electrolyte for a particular battery type, is suggested as a possible later example. A configurable rule table could return fits / does not fit / insufficient information, plus reasons. | This is a future design suggestion, not an already selected battery chemistry, numerical threshold, or an executed experiment. |
| S5 | Nina shares this Google Doc and summarizes seed selection, polymer-specific configuration/prompt changes, eight queries per topic, manual evaluation, LLM judging, and planned V0/V1 comparison. | Nina's detailed report is the principal source to inspect. Summary praise or a successful command is not proof of retrieval quality. |
| S6 | The earlier assignment allows a few manually curated materials, distinguishes reliable evidence from suitability, and asks for reasons without ranking unlike conditions. | It explains why the earlier manually curated demonstration was legitimate. It does not override the user's present learning-only instruction. |

Screenshot originals supplied by the user:

- S1: [scope clarification](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-5515602e-c285-4d5f-be1d-76f68c87e2a3.png>).
- S2: [two named scopes](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-11655c31-7184-46a4-9d08-1a6ca1e1ee90.png>).
- S3: [general and specific layers](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-6ea543bf-25c1-4d22-9b19-766a586235c7.png>).
- S4: [possible future battery example](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-0c1c5a42-f408-4ba3-887c-1fa0472c6898.png>).
- S5: [Nina's summary message](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-25464f38-bcdd-47af-a2b7-365fc8282f70.png>).
- S6: [earlier assignment clarification](</var/folders/j5/m0tnvhrx3s9dlcb_h2_5xmhm0000gn/T/codex-clipboard-10350ee0-9cb9-4741-b13d-c1cf0d7dbfd9.png>).

The originals above were copied byte-for-byte to a local source archive outside the Git repository. The document reading snapshot, native revision metadata, all 16 query objects and a SHA256 manifest are archived with them. These are internal reading sources, not public publication links. [Source manifest](</Volumes/Seagate/research /polymer-screening/sources/nina-reading-2026-10-27/source-manifest.json>), [full paragraph-indexed document snapshot](</Volumes/Seagate/research /polymer-screening/sources/nina-reading-2026-10-27/nina-document-reading-snapshot.txt>). Snapshot SHA256: `4ee869baa016296ac6c1b967f5909ac5f2ea80d3c6419c588cdcc8abfde9d926`.

## 3. What Nina reports doing

| Stage | What the report says | Evidence boundary |
| --- | --- | --- |
| Seeds | Three DPAL seed papers per topic. | The six exact paper identities and their source files are absent from the report. [P002–P003](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| Repository setup | A fork and a `task1-queries` branch. | No owning fork URL, commit SHA or diff is supplied. A matching local file elsewhere would not by itself establish Nina's actual revision. [P004–P005](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| Domain configuration | A polymer-specific `DomainSpec`, with `disulfide` and `batteries` subdomains, aliases, research aspects, and a changed seed-extraction prompt. | The actual configuration and prompt diffs are not included. [P006–P007](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| Generation workflow | The existing query-generation workflow was retained; `prompt_pipeline.py` ran with Azure OpenAI, labelled `gpt-5.4`. | This identifies reported software/provider/model labels, not a complete reproducible environment or authenticated API trace. [P008–P012](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| V0 outputs | Eight queries per topic, saved as `queries.json`. | Two complete eight-object query lists are directly visible. This independently confirms the document's object count, not the generation call or retrieval outcome. [P061–P198; P210–P347](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| Manual review | Relevance, coverage, ambiguity, obvious syntax problems, overly specific disulfide terminology, electrolyte emphasis and absent explicit Diels–Alder terms were reviewed. | These are reported observations, not a measured recall estimate. Some string defects are directly visible in the pasted queries. [P013–P018](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| LLM judge | An `evaluate_queries.py` script, Azure `gpt-5.4`, three evaluation criteria, and JSON judge outputs. | Script, full prompt, raw responses, individual scores and explanations are not supplied. Generation and judging share a reported provider/model label; exact deployment independence is not established. [P019–P027](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |
| Planned next work | Prompt refinement, V1 generation using the same seeds and evaluation criteria, then later real retrieval testing. | These are listed as next steps. The document does not show completed V1 or retrieval results. [P046–P049](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) |

### Plain-English explanation of the stage reached

Nina used a few example papers to help the program write search requests for finding more papers. She then inspected those requests and asked an LLM to rate their wording and coverage. The visible work concerns **search-query preparation and evaluation**. It is not yet proof that the requests retrieve the right papers, that material measurements are extracted correctly, or that any material suits a specific battery use. This is a reading inference from the described generation, evaluation and explicitly later retrieval steps. [P008–P012; P020–P027; P045–P049](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

## 4. The two scopes and their relationship

**Topic A** is labelled *Dynamic polymers containing disulfide bonds*. Its queries organize discovery around synthesis, characterization, healing, mechanics, conditions, recycling, adhesives and functional devices. **Topic B** is labelled *Dynamic polymers for battery applications*. Its actual V0 queries mostly concern polymer electrolytes, with terms for preparation, dynamic bonding, mechanics, ion transport, conditions, cells, interfaces and morphology. [A query objects, P063–P196; B query objects, P212–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

A chemistry-based scope and an application-based scope can overlap without being identical. For example, Topic B's characterization query explicitly includes `disulfide`, but also includes `imine`, `boronate`, and `dynamic covalent`. It would therefore be incorrect to silently require every battery paper to concern disulfide chemistry, or to require every disulfide paper to concern batteries. This is a reading inference from the two labels and B2's visible terms, consistent with screenshot S2. [P234–P243](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

The **broad battery title and the narrower electrolyte-heavy outputs differ**. The report itself notes this focus. The eight B queries do not visibly make electrode binders, separators, electrode coatings, and other polymer roles into separately explicit search targets. That absence is an observation about the query text, not a claim that the seed papers or the dynamic-polymer battery literature lack those roles. The desired inclusion boundaries cannot be recovered from this document alone. [P018; P219–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

## 5. Exact reported evaluation results

| Reported item | Topic A: disulfide | Topic B: batteries | What it means |
| --- | --- | --- | --- |
| Query objects | 8 | 8 | Counts in the visible V0 lists. |
| Mean relevance, higher is better | 4.38/5 | 4.38/5 | Single-run subjective judge ratings of topic match. |
| Mean ambiguity risk, lower is better | 2.00/5 | 1.88/5 | Single-run subjective ratings of unclear/misleading wording. |
| Predefined aspect coverage | 7/7 | 7/7 | The judge says all seven of this experiment's predefined aspects are covered. |
| Judge call count in transcript | One call for the eight-query set | One call for the eight-query set | No repeated-judge stability estimate is shown. |

Sources: report summary table [P029–P045](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit) and evaluation transcript [P349–P360](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

Important limits:

1. The report explicitly calls these subjective, single-run LLM ratings and **not retrieval-accuracy measurements**. [P045; P355; P360](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
2. Relevance means query wording matches the topic under the judge's rubric. It is not precision over returned papers. [P023; P045](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
3. Coverage concerns seven predefined aspects. It does not mean seven useful papers, exhaustive scientific coverage, high recall, complete material fields, or a validated application. [P025; P027; P041–P045](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
4. The seven exact aspect labels and their coverage evidence are not included in the supplied report. Eight query themes cannot be silently relabelled as the missing seven-aspect rubric. [P025–P027; P061–P198; P210–P347](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
5. The reported scoring scales and coverage aspects were created for this experiment rather than copied directly from MemoSchema. The report invokes MemoSchema as methodological inspiration, not as the source of these numerical scales. [P020; P027](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
6. Equal rounded relevance means do not prove equal quality or a statistical tie. The per-query scores, repeat runs and uncertainty are not supplied. The small ambiguity-mean difference does not establish that one topic performs better in retrieval. This is a reading inference from the limited aggregate data. [P035–P045; P353–P360](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
7. The generation and judge stages both report Azure `gpt-5.4`. That does not establish independent human adjudication, model-diverse validation, repeatability or calibration. This is a reading inference, not an accusation that the ratings are wrong. [P010; P026; P351–P360](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)

## 6. Inventory of all sixteen V0 queries

All sixteen objects contain the fields `tiers`, `query_bool`, `query_nl`, `synonyms` and `why`. The common hierarchy is `Physical sciences / Chemistry / Materials chemistry / Polymers`, followed by the exact topic label. Field presence and eight objects per topic are directly inspectable. A schema-shaped object being present does not prove semantic adequacy or that its Boolean text executes in a chosen search system. [P063–P196; P212–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

### Topic A: disulfide polymers

| ID | Main purpose and vocabulary | Reading observations | Report locator |
| --- | --- | --- | --- |
| A1 | Synthesis/preparation, poly(thioctic acid), ring-opening/cationic polymerization, initiator. | Explicit seed-like chemistry emphasis; contains the literal joined token `ORabs`. | P070–P077, API 3218–4028 |
| A2 | Structure and bond characterization, NMR, FTIR, Raman, GPC, molecular weight. | Natural-language text contains `Focuson`. These names indicate what a query seeks, not proof that a material's exchange mechanism was measured. | P087–P094, API 4246–5000 |
| A3 | Self-healing, healing time/efficiency, crack closure, bond exchange. | Contains literal `crackrecovery`; visible closure and recovered mechanical performance remain different sought outcomes. | P104–P111, API 5218–5936 |
| A4 | Mechanical/viscoelastic behavior, tensile strength, elongation, toughness, modulus and rheology. | Multiple properties occur in one search theme; they are not interchangeable measurements. | P121–P128, API 6154–6881 |
| A5 | Conditions, temperature, humidity, UV, heat, strain rate. | Broad condition words do not establish that later returned experiments will be comparable. | P138–P145, API 7099–7878 |
| A6 | Recycling, depolymerization, monomer recovery, reprocessing and closed-loop reuse. | Different reuse concepts share one discovery query; the query does not show a completed recycling experiment. | P155–P162, API 8096–8855 |
| A7 | Adhesives/sealants, lap shear, underwater adhesion, interface. | An explicit application theme, distinct from requiring all disulfide polymers to be adhesives. | P172–P179, API 9073–9769 |
| A8 | Functional devices, actuators, liquid-crystal elastomers, electrochemistry/conductivity. | Broad functional catch-all; its phrases are search intent rather than demonstrated device outcomes. | P189–P196, API 9987–10834 |

All A inventory observations cite the [visible Topic A query list](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit). They are reading observations, not a retrieval benchmark.

### Topic B: dynamic polymers for batteries

| ID | Main purpose and vocabulary | Reading observations | Report locator |
| --- | --- | --- | --- |
| B1 | Electrolyte preparation; imine/Schiff-base/vitrimer; casting, curing and hot press. | Its Boolean OR branch can match named mechanisms without requiring the title's polymer-electrolyte phrases. That is visible logical scope, not measured noise. | P219–P226, API 11420–12362 |
| B2 | Structure/dynamic-bond characterization; FTIR, NMR, XPS, Raman, bond exchange; imine, disulfide, boronate. | Natural-language intent permits supramolecular interactions, while Boolean terms emphasize named covalent mechanisms. Neither channel alone proves the intended overall domain coverage. | P236–P243, API 12578–13432 |
| B3 | Mechanics, stretchability, adhesion, remolding and healing; polymer/hydrogel electrolytes. | `"electrolyte"OR` lacks a separating space; literal wildcard syntax appears inside a quoted `"self-heal*"` phrase. Backend behavior must be checked rather than assumed. | P253–P260, API 13648–14463 |
| B4 | Ion transport/electrochemistry; conductivity, EIS, transference number, VTF, stability window. | The terminal battery constraint has an alternative `solid polymer electrolyte` phrase; the exact intended battery-only boundary needs to be understood. | P270–P277, API 14679–15536 |
| B5 | Conditions; temperature, humidity, salt, plasticizer, PEGDME. | Contains `ORabs`. Specific 30/60 °C terms and PEGDME make some seed vocabulary visible; performance has a broad final AND term. | P287–P294, API 15752–16639 |
| B6 | Battery demonstrations; lithium-metal, zinc-ion, solid-state, flexible; symmetric and full cells. | Cell categories and battery systems differ; listing them is not evidence of comparable battery testing or a working full cell. | P304–P311, API 16855–17714 |
| B7 | Interfaces and dendrites; SEI, resistance, plating/stripping, XPS. | Contains `interfaceOR`; the final Boolean gate mentions lithium/anode rather than the explicit battery wildcard used by some other B queries. | P321–P328, API 17930–18786 |
| B8 | Morphology/thermal behavior; free volume, PALS, crystallinity, DSC, TGA, glass transition. | These are characterization/search concepts. The query itself cannot establish a causal structure–performance relation. | P338–P345, API 19002–19828 |

All B inventory observations cite the [visible Topic B query list](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit). They are reading observations, not a retrieval benchmark.

### Shared syntax and channel questions to keep open

- Every Boolean query uses `cat:`, `ti:`, `abs:` and two arXiv category labels, `cond-mat.mtrl-sci` and `physics.chem-ph`. These literals are visible, but the report does not name the search endpoint/parser actually used for retrieval. Its validity and effect must be checked against the owning backend documentation before claiming that a specific string failed or succeeded. [P070–P338](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
- The visible adjacent tokens are A1 `ORabs`, A2 natural-language `Focuson`, A3 `crackrecovery`, B3 `"electrolyte"OR`, B5 `ORabs`, and B7 `interfaceOR`. The document itself flags `ORabs`; the additional locations are directly inspectable here. Whether each affects a real search depends on backend parsing and which query channel is actually executed. [P016; P070; P088; P104; P253; P287; P321](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
- `query_bool`, `query_nl` and `synonyms` are separate fields with partly different vocabulary. Missing a term in one field does not prove it is absent from every channel; conversely a term mentioned only in prose does not prove the execution path sends it to a search backend. [P070–P196; P219–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
- The report notes no explicit Diels–Alder coverage in the battery set. This is directly consistent with the visible B query strings. It remains a coverage question relative to the intended seed/domain scope, not a reason to add chemistry or modify the prompt during this learning-only task. [P018; P219–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)

## 7. What the artifact paths tell us, and what they do not

The report names these paths as outputs or inputs. They are recorded as evidence labels, not commands to execute:

| Reported path / name | Reported role | Source |
| --- | --- | --- |
| `task1-queries` | Nina's branch name | P005 |
| `data/seeds_disulfide` | Topic A seed input directory | P053–P057 |
| `data/seeds_batteries` | Topic B seed input directory | P201–P205 |
| `runs/polymer/disulfide/v0/queries.json` | A V0 query output | P057–P060 |
| `runs/polymer/batteries/v0/queries.json` | B V0 query output | P205–P209 |
| `evaluate_queries.py` | Reported evaluation script | P021; P350 |
| `runs/polymer/evaluation/disulfide_v0.judge.json` | Reported A judge output | P352 |
| `runs/polymer/evaluation/batteries_v0.judge.json` | Reported B judge output | P357 |

Source for this path inventory: [Nina's commands and evaluation transcript](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit), at the locators above. The directory names do not supply file contents, seed identities, a Git commit, an evaluator rubric, or retrieval results.

## 8. Open information gaps

| Missing source / detail | Why it matters to understanding the reported experiment | Current status |
| --- | --- | --- |
| Six seed titles, DOI/DPAL identifiers, files and exact text portions used | Establish what the two topics were actually induced from and whether visible vocabulary reflects those seeds. | Not supplied in the report. |
| Nina's fork URL, exact `task1-queries` commit and base revision | Attribute configuration and prompt behavior to the code that actually ran. | Not supplied in the report. |
| Actual `DomainSpec`, aliases, aspects and seed extraction prompt diff | Check what changed and distinguish domain specification from later query generation. | Reported as changed, underlying diff uninspected. |
| Exact seven-aspect coverage checklist | Interpret the 7/7 number and its agreement with the intended topic scope. | Cardinality is stated, labels are absent. |
| `evaluate_queries.py`, system/user judge prompt, scoring anchors and parsing/error handling | Understand what the judge saw, what its scales mean, and whether a syntactically broken query could still receive a high topic score. | Script is named but not included. |
| Actual judge JSON and raw per-query scores/explanations | Recalculate means and inspect which defects or gaps the judge recognized. | Only aggregates and a summary transcript are visible. |
| Generation and judging configuration, repetitions, seed coverage, deployment identifiers | Assess reproducibility and variability without exposing credentials. | Provider/model label is reported; full run record is absent. |
| Executed retrieval endpoint, query translation, requests, returned papers and deduplication | Establish real behavior of arXiv-like strings and eventual paper precision/coverage. | Retrieval testing is explicitly future work in this document. |
| V1 output and matched V0/V1 comparison | Establish whether a prompt revision improved anything under a fixed comparison. | Planned, no V1 results are included. |
| Original MemoSchema evaluation section and Lisa's 19 October rubric | Separate what Nina borrowed from what she designed locally. | The supplied MemoSchema manuscript was independently read for §10.2 below; Lisa's exact 19 October rubric remains unavailable. Nina's custom scales are not claimed equivalent. |

The absence statements above refer specifically to the [report read on 27 October, P001–P361](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit). They do not assert that Nina lacks these artifacts elsewhere. No API keys, endpoints containing secrets, or private account identifiers are needed to interpret these notes.

## 9. What has been learned before any later Task 3 work

1. The team now wants shared exploration within **Nina's two scopes**, while the wood example remains a completed historical example. Sources: S1–S4 above.
2. Nina's visible deliverable is **V0 search-query generation plus a preliminary manual/LLM query evaluation**. It is not an automatic material-selection result. [P008–P027; P045–P049](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
3. The visible query objects support an exact vocabulary inventory. They do not establish which papers were retrieved or which materials satisfy a later use. [P061–P198; P210–P347; P045](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit)
4. General information checks and material/use-specific checks are conceptually separate in the team discussion. The present note records that idea and does not implement either layer. Sources: S3–S4 above.
5. We should retain unresolved information as unresolved. A named file, positive LLM score or broad topic label cannot fill missing seed identities, test evidence, retrieved-paper results or code provenance. This is the methodological reading inference supported by the source gaps recorded above.

## 10. What the local AutoSchema code and MemoSchema source clarify

### 10.1 Which code was actually inspected

The read-only checkout was on `task3-selection` at commit `0c3699e24e5b1dd74ea409a610cbd3377299267d`. It is our fork's reference code, **not Nina's identified experiment revision**. Its prompt registry and command-line domain choices contain `chem`, `cs` and `ad`, with no `polymer`, `disulfide` or `batteries` entries. Nina reports adding those entries on her own `task1-queries` branch. Therefore the difference is a code-provenance gap, not evidence that her commands failed. [Inspected registry](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_lib/domain.py#L329-L369), [CLI](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_pipeline.py#L173-L186), [Nina P004–P007](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

| Stage in the inspected reference code | What it does | What it does not establish |
| --- | --- | --- |
| Seed preparation | Reads the first five seed PDFs and asks the model for a domain-specific structured snapshot. | That Nina's six particular seed identities, extraction quality, or exact modified prompt have been verified. [Caller](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_pipeline.py#L59-L95) |
| Query input | Concatenates extracted seed snapshots and takes their first 8,000 characters. | That every seed contributes equally. A possible seed/snapshot effect is not a demonstrated cause of Nina's vocabulary emphasis. [Snapshot](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_pipeline.py#L97-L110) |
| Generation and count | The domain prompt requests eight queries. The caller tops up from a general prompt when necessary and caps output at its query budget. | Eight generated objects are an output budget, not an achieved quality score. [Prompt](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_lib/domain.py#L145-L175), [caller](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_pipeline.py#L121-L158) |
| Validation | Checks tier labels, presence of any focus/alias term across Boolean text, natural language or synonyms, and optional block terms. | It is not a complete search-parser check. A valid hierarchy or a topic word in the natural-language channel does not ensure a well-formed, properly scoped Boolean expression. [Validator](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/prompt_lib/validation.py#L14-L44) |
| Source routing | Sends Boolean text to arXiv. For OpenAlex, Nature, CORE and PubMed, it uses natural-language-derived text with the topic prepended. | A defect in `query_bool` does not prove that identical text reached every service. Nina's actual executed requests are absent. [Routing](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/expand_round.py#L70-L84) |
| OpenAlex conversion | Removes Boolean glue, quotes and field-like tokens, deduplicates words, and keeps at most 12 terms and 200 characters; submits this as `search`. | The full displayed query, all its aspect words, or its original Boolean logic are not necessarily preserved. [Cleaner](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/expand_lib/openalex_search_helpers.py#L16-L43), [request construction](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/expand_lib/searches.py#L256-L281) |

This reference-code reading is consistent with AutoSchema's original description of seed-conditioned query generation and source-specific adaptation. It is a stage explanation, not a new execution of Nina's work. The broader paper separately describes schema induction and frozen-schema extraction. Nina's visible query-generation report does not demonstrate completion of those later stages. [AutoSchema, supplied paper, pp. 3–4, §§4.2.1–4.3](</Volumes/Seagate/research /papers/AutoSchema.pdf>).

### 10.2 What Nina borrowed from MemoSchema

The supplied MemoSchema manuscript distinguishes **query quality** from **retrieval quality**. Its evaluation section describes LLM judgments of relevance, novelty, usefulness, specificity, overall quality and drift risk for queries. Retrieval evaluation instead examines paper titles/abstracts for relevance and off-topic behavior. Nina explicitly says that her 1–5 relevance/ambiguity scales and seven coverage aspects were defined for her experiment. Her results should therefore be understood as an adapted query-evaluation exercise, not a numerical reproduction of MemoSchema's published/draft metrics. [MemoSchema, supplied manuscript, p. 5, “Evaluation dimensions”](</Volumes/Seagate/research /papers/MemoSchema.pdf>), [Nina P020–P027](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

A positive LLM rating can be useful preliminary feedback, but it does not substitute for actual returned-paper labels or experimentally supported material data. The primary LLM-judge literature studies judge limitations, including position, verbosity and self-enhancement effects. That general literature does not establish which, if any, affected this particular run; Nina's missing judge artifacts prevent such attribution. [Zheng et al., original paper](https://arxiv.org/abs/2306.05685), [Nina's own evaluation limit, P045 and P355/P360](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

## 11. Primary-documentation audit of the query strings

This is **static reading**, not a search benchmark or a repair of the queries. No original string in Appendix A has been corrected. No query was submitted to a paper database during this audit.

### 11.1 Syntax has to be interpreted for the intended service

Official arXiv documentation defines `ti:`, `abs:`, `cat:`, Boolean operators, parentheses and quoted phrases. All sixteen displayed Boolean strings use that arXiv-style form and restrict to `cond-mat.mtrl-sci` or `physics.chem-ph`. The inspected arXiv adapter does not add its category-free alternative when a query already contains `cat:`. This can constrain discovery to the selected categories if that adapter is used, but no resulting missing-paper count is known. The manual inspected here does not establish the intended wildcard behavior, so `batter*`, `crosslink*`, `remold*` and quoted `self-heal*` cannot be certified or declared universally invalid from this source alone. [arXiv API manual, §5.1](https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction), [reference adapter](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/expand_lib/searches.py#L184-L212), [Nina query lists](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

Current official OpenAlex documentation supports Boolean/phrase search through a different interface and describes wildcards under `search.exact`, with wildcard rejection under default stemmed `search`. The page inspected on 27 October labels its update as **26 October 2026**, after Nina's 19–23 October experiment period. This is current background documentation, not evidence of the behavior of a V0 request made earlier. The local cleaner also strips wildcard punctuation from the natural-language-derived input before its OpenAlex request. It would be wrong to infer an observed OpenAlex wildcard error from these displayed Boolean strings. [OpenAlex searching documentation](https://help.openalex.org/api/searching/), [reference cleaner](https://github.com/nniiovoo/AutoSchema/blob/0c3699e24e5b1dd74ea409a610cbd3377299267d/expand_lib/openalex_search_helpers.py#L16-L43).

### 11.2 Additional static observations

| Query IDs | Observation supported by the literal text | Limit of the conclusion |
| --- | --- | --- |
| A1 and B5 | `ORabs:` fuses an intended operator with a field prefix. | The intended separated `OR` is not written as such. No actual server response is available. |
| B7 | `abs:interfaceOR abs:SEI` similarly fuses text with the operator. | It could alter parsing/meaning; failure or a zero-result search was not demonstrated. |
| A2 and A3 | `Focuson` and `crackrecovery` are joined words. | A3 retains other healing alternatives; this does not show that the whole query retrieves nothing. |
| B3 | A closing quote is adjacent to `OR`; wildcards also occur. | The quote may itself delimit a token. Missing whitespace is a normalization concern, not a proved parser rejection. |
| All A queries | Each allows `ti:"disulfide"` as a topic alternative without an independently mandatory polymer or dynamic-behavior condition. | A logical route for nonpolymeric disulfide papers exists. No false-positive rate was measured. |
| B1 | The first group is electrolyte-title alternatives **OR** generic mechanism alternatives, then preparation and battery/lithium context. | An imine/Schiff-base/vitrimer branch can match without a polymer-electrolyte phrase. This is logical breadth, not measured retrieval noise. |
| B2 | Natural language allows supramolecular interactions, whereas the Boolean mechanism gate names imine, disulfide, boronate or dynamic covalent. | Exclusively noncovalent systems lacking those words could be missed by this channel; retrieval performance remains unknown. |
| B4 | A `Li+` phrase requires correct request encoding. The final group permits “solid polymer electrolyte” instead of a battery word. | The submitted URL and actual transport behavior are unavailable. |
| B5 and B7 | Not every OR branch independently requires an explicit battery term. | Battery relevance cannot be inferred solely from the `tiers` label. These are possible scope risks, not observed off-topic papers. |
| All B queries | Electrolytes dominate the visible targets. Diels–Alder is not named explicitly in either set. | This supports Nina's wording-level observations, not a claim that such chemistry or other battery roles could never match. |

Sources for this table are the exact [A1–A8 and B1–B8 strings in Nina's report](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit), preserved with paragraph and API locators in §6 and Appendix A; interpretation of fields/operators uses the [official arXiv manual](https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction).

The key learning is a distinction between four stages: **the written query, the service-specific query after conversion, the retrieved paper set, and the downstream extracted evidence**. Nina supplies the first and preliminary ratings of it. The later stages cannot be reconstructed from the reported means.

## 12. Polymer background needed to understand the two scopes

These are background learning examples. They are **not identified as Nina's six seeds, not independently verified DPAL memberships, and not a new candidate shortlist**.

### 12.1 Mechanism, role and experiment are separate descriptions

- A **disulfide bond** joins two sulfur atoms, commonly written S–S. In a dynamic system, the relevant question includes what the linkages do under the stated conditions. Establishing S–S composition is distinct from demonstrating exchange or healing. Rekondo's primary work separates a model disulfide-exchange investigation from healing in its elastomer. This does not establish room-temperature healing for every disulfide polymer. [Rekondo et al.](https://doi.org/10.1039/C3MH00061C)
- **Redox reversibility** and **mechanical repair** are different experimental claims. Grocke's disulfide particles use reversible disulfide reduction for charge storage; that result alone does not demonstrate autonomous crack repair. A broad dynamic-polymer definition may include redox-responsive systems, so the distinction concerns demonstrated function rather than declaring them outside the topic. [Grocke et al.](https://doi.org/10.1021/acsmacrolett.1c00682)
- A battery **electrolyte** provides an ion-conducting medium. A **binder** helps hold electrode material together. A **coating** describes a layer placed at a surface, with its actual function needing evidence. An **electrode-active polymer** contributes to charge storage. These roles can overlap and should not be collapsed into a single “battery material” measurement. Wang's paper uses overlapping binder/coating descriptions; Grocke supplies a redox-active example. [Wang author PDF](https://web.stanford.edu/group/cui_group/papers/selfhealing.pdf), [Grocke](https://doi.org/10.1021/acsmacrolett.1c00682)
- A material measurement and a cell demonstration answer different questions. Pei's original article separately treats polymer characterization, ion transport and electrochemical measurements, lithium symmetric cells, and lithium–sulfur cells. A symmetric cell is not automatically the same demonstration as a cell with a sulfur-containing cathode. [Pei full original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10774406/), [original XML accessed](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10774406/fullTextXML)

### 12.2 Small primary-source learning list

| Original paper | What it helps us understand | Access and limitation |
| --- | --- | --- |
| Rekondo et al. (2014), *Catalyst-free room-temperature self-healing elastomers based on aromatic disulfide metathesis*. [DOI](https://doi.org/10.1039/C3MH00061C) | Disulfide chemistry and healing outside a required battery context. | Publisher-indexed abstract/HTML passages inspected; direct full HTML/PDF access returned 403. No full-paper/SI reanalysis. The volume is 2014; first online publication was in September 2013. |
| Wang et al. (2013), *Self-healing chemistry enables the stable operation of silicon microparticle anodes for high-energy lithium-ion batteries*. [DOI](https://doi.org/10.1038/nchem.1802), [author PDF](https://web.stanford.edu/group/cui_group/papers/selfhealing.pdf) | Hydrogen-bond repair in a battery electrode binder/coating, illustrating a battery role beyond disulfide electrolytes. | Author-hosted seven-page PDF read for role and relevant mechanism passages. No full electrochemical or SI reassessment. |
| Pei et al. (2024), *Interfacial self-healing polymer electrolytes for long-cycle solid-state lithium-sulfur batteries*. [DOI](https://doi.org/10.1038/s41467-023-43467-w) | An overlap example involving disulfide/hydrogen-bond chemistry and an electrolyte, with separate material/component/cell experiments. | Original full article and relevant methods accessed through Europe PMC XML. Publication was **8 January 2024**, despite “2023” in its DOI. SI not independently audited. |
| Grocke et al. (2021), *Synthesis and Characterization of Redox-Responsive Disulfide Cross-Linked Polymer Particles for Energy Storage Applications*. [DOI](https://doi.org/10.1021/acsmacrolett.1c00682) | Disulfides as charge-storage sites, so electrochemical reversibility must not silently become a healing claim. | Primary ACS-indexed abstract/introduction inspected; direct PDF access returned 403. No full experimental/SI audit. |

This list teaches the vocabulary and scope distinctions. It supplies no acceptance thresholds, “best material,” screening outcome, or identification of Nina's unspecified seeds.



## Appendix A. Exact V0 query objects as visible in the report

These objects are preserved for source reading and later traceable comparison. Their strings are deliberately not corrected or executed. Each object retains its source's fields and spelling, including visible formatting defects. This appendix is evidence transcription, not a proposed prompt/query revision.


### A1

Source: [Nina, P070–P077](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide bond\" OR abs:\"dynamic disulfide polymer\" OR abs:\"poly(thioctic acid)\") AND (abs:\"ring-opening polymerization\" ORabs:\"cationic polymerization\" OR abs:\"thioctic acid\" OR abs:\"initiator\"))",
  "query_nl": "Find studies on synthesis and preparation of dynamic polymers containing disulfide bonds, especially poly(thioctic acid) made by ring-opening or cationic polymerization. Emphasize monomers, initiators, solvent conditions, and molecular-weight control.",
  "synonyms": [
    "poly(thioctic acid)",
    "dynamic disulfide polymer",
    "disulfide-containing polymer"
  ],
  "why": "Capture synthesis routes and preparation parameters."
}
```


### A2

Source: [Nina, P087–P094](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide bonds\" OR abs:\"disulfide-linked polymer\") AND (abs:\"NMR\" OR abs:\"FTIR\" OR abs:\"Raman\" OR abs:\"GPC\" OR abs:\"molecular weight\" OR abs:\"structure characterization\"))",
  "query_nl": "Retrieve work characterizing chemical structure and dynamic disulfide bonds in polymers. Focuson spectroscopic, chromatographic, and molecular-weight analyses used to verify network formation and exchangeable S-S linkages.",
  "synonyms": [
    "S-S bond exchange",
    "polymer characterization",
    "disulfide-linked polymer"
  ],
  "why": "Identify structure and bond characterization methods."
}
```


### A3

Source: [Nina, P104–P111](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide-containing polymer\" OR abs:\"dynamic disulfide polymer\") AND (abs:\"self-healing\" OR abs:\"healable\" OR abs:\"crackrecovery\" OR abs:\"healing efficiency\" OR abs:\"bond exchange\"))",
  "query_nl": "Search for self-healing behavior in dynamic polymers containing disulfide bonds. Include measurements of healing time, healing efficiency, crack closure, and the role of disulfide exchange in recovery.",
  "synonyms": [
    "healable polymer",
    "self-repairing polymer",
    "disulfide exchange"
  ],
  "why": "Find self-healing performance studies."
}
```


### A4

Source: [Nina, P121–P128](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide bonds\" OR abs:\"disulfide-containing polymer\") AND (abs:\"tensile\" OR abs:\"mechanical properties\" OR abs:\"elongation\" OR abs:\"toughness\" OR abs:\"modulus\" OR abs:\"rheology\"))",
  "query_nl": "Find papers measuring mechanical and viscoelastic properties of dynamic disulfide polymers. Prioritize tensile strength, elongation, toughness, modulus, rheology, and thermomechanical transitions.",
  "synonyms": [
    "viscoelastic polymer",
    "tensile testing",
    "dynamic covalent elastomer"
  ],
  "why": "Collect mechanical and rheological evaluations."
}
```


### A5

Source: [Nina, P138–P145](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"dynamic disulfide polymer\" OR abs:\"disulfide-bonded\") AND (abs:\"temperature\" OR abs:\"humidity\" OR abs:\"UV\" OR abs:\"heat\" OR abs:\"experimental conditions\" OR abs:\"healing temperature\" OR abs:\"strain rate\"))",
  "query_nl": "Retrieve studies on how experimental conditions affect dynamic polymers containing disulfide bonds. Cover temperature, irradiation, strain rate, environment, and other factors influencing bond exchange and performance.",
  "synonyms": [
    "stimuli-responsive polymer",
    "thermal activation",
    "UV-triggered exchange"
  ],
  "why": "Assess condition-dependent performance changes."
}
```


### A6

Source: [Nina, P155–P162](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide-containing polymer\" OR abs:\"poly(thioctic acid)\") AND (abs:\"recyclable\" OR abs:\"depolymerization\" OR abs:\"chemical recycling\" OR abs:\"reprocessing\" OR abs:\"closed-loop\" OR abs:\"monomer recovery\"))",
  "query_nl": "Search for recyclability and reprocessability of dynamic disulfide polymers. Focus on depolymerization, monomer recovery, repolymerization, and closed-loop material reuse enabled by reversible disulfide chemistry.",
  "synonyms": [
    "chemical recycling",
    "depolymerization",
    "reprocessable polymer"
  ],
  "why": "Target recyclability and closed-loop reuse."
}
```


### A7

Source: [Nina, P172–P179](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide-bonded\" OR abs:\"disulfide-linked polymer\") AND (abs:\"adhesive\" OR abs:\"sealant\" OR abs:\"lap shear\" OR abs:\"underwater adhesion\" OR abs:\"interfacial\"))",
  "query_nl": "Find application studies where dynamic polymers containing disulfide bonds are used as adhesives or sealants. Include lap-shear tests, substrate scope, underwater adhesion, and practical bonding performance.",
  "synonyms": [
    "self-healing adhesive",
    "sealant",
    "underwater adhesive"
  ],
  "why": "Capture adhesive and sealant applications."
}
```


### A8

Source: [Nina, P189–P196](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers containing disulfide bonds"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"disulfide\" OR abs:\"disulfide-bonded liquid crystal elastomer\" OR abs:\"dynamic disulfide polymer\") AND (abs:\"actuator\" OR abs:\"liquid crystal elastomer\" OR abs:\"electrochemical\" OR abs:\"ionic conductivity\" OR abs:\"functional application\" OR abs:\"multilayer\"))",
  "query_nl": "Retrieve advanced functional applications of dynamic polymers containing disulfide bonds, including soft actuators, liquid crystal elastomers, and electrochemical or conductive systems. Emphasize how dynamic S-S bonds enable repairable or adaptive device behavior.",
  "synonyms": [
    "disulfide-bonded LCE",
    "soft actuator",
    "functional polymer device"
  ],
  "why": "Broaden to adaptive functional applications."
}
```


### B1

Source: [Nina, P219–P226](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR ti:\"self-healing polymer electrolyte\" OR ti:\"reversible polymer electrolyte\" OR ti:\"dynamic polymer for batteries\") OR (abs:\"Schiff base\" OR abs:imine OR abs:vitrimer)) AND (abs:synthesis OR abs:\"solution casting\" OR abs:\"hot press\" OR abs:crosslink*) AND (abs:batter* OR abs:\"lithium metal\")",
  "query_nl": "Find studies on synthesis and preparation of dynamic polymer electrolytes for batteries, especially imine/Schiff-base or vitrimer networks made by casting, curing, or hot pressing. Emphasize solid polymer electrolyte fabrication routes for lithium batteries.",
  "synonyms": [
    "dynamic polymer electrolyte",
    "vitrimer electrolyte",
    "Schiff-base electrolyte"
  ],
  "why": "Capture preparation strategies for battery-ready dynamic electrolytes"
}
```


### B2

Source: [Nina, P236–P243](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\" OR abs:\"reversible polymer electrolyte\") AND (abs:FTIR OR abs:NMR OR abs:XPS OR abs:raman OR abs:\"bond exchange\") AND (abs:imine OR abs:disulfide OR abs:boronate OR abs:\"dynamic covalent\")) AND abs:batter*",
  "query_nl": "Search for characterization of chemical structure and dynamic bonds in dynamic polymer electrolytes for batteries. Prioritize spectroscopic evidence for reversible covalent or supramolecular interactions and bond-exchange mechanisms.",
  "synonyms": [
    "reversible polymer electrolyte",
    "dynamic covalent electrolyte",
    "self-healing polymer electrolyte"
  ],
  "why": "Identify how dynamic bonding is verified"
}
```


### B3

Source: [Nina, P253–P260](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"self-healing polymer electrolyte\"OR abs:\"dynamic polymer electrolyte\" OR abs:\"self-healing hydrogel electrolyte\") AND (abs:mechanical OR abs:\"stress-strain\" OR abs:stretchability OR abs:adhesion OR abs:remold* OR abs:\"self-heal*\")) AND abs:batter*",
  "query_nl": "Find work measuring mechanical robustness, stretchability, adhesion, remoldability, and self-healing in dynamic polymer electrolytes or self-healing hydrogel electrolytes for batteries. Include flexible and solid-state battery contexts.",
  "synonyms": [
    "self-healing hydrogel electrolyte",
    "dynamic polymer electrolyte",
    "adaptive electrolyte"
  ],
  "why": "Assess mechanics and healing behavior"
}
```


### B4

Source: [Nina, P270–P277](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR abs:\"reversible polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\") AND (abs:\"ionic conductivity\" OR abs:EIS OR abs:\"Li+ transference number\" OR abs:VTF OR abs:\"electrochemical stability window\")) AND (abs:batter* OR abs:\"solid polymer electrolyte\")",
  "query_nl": "Retrieve studies evaluating ion transport and electrochemical properties of dynamic polymer electrolytes for batteries. Focus on conductivity, transference number, activation energy, and oxidative stability measurements.",
  "synonyms": [
    "dynamic polymer electrolyte",
    "reversible polymer electrolyte",
    "solid polymer electrolyte"
  ],
  "why": "Track transport and electrochemical metrics"
}
```


### B5

Source: [Nina, P287–P294](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer for batteries\" ORabs:\"dynamic polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\") AND (abs:temperature OR abs:\"30 °C\" OR abs:\"60 °C\" OR abs:humidity OR abs:\"salt concentration\" OR abs:plasticizer OR abs:PEGDME)) AND abs:performance",
  "query_nl": "Look for studies on how experimental conditions affect dynamic polymer electrolytes for batteries, including temperature, salt content, solvent/plasticizer uptake, and environmental conditions. Emphasize links between conditions and conductivity, healing, or cycling.",
  "synonyms": [
    "dynamic polymer for batteries",
    "plasticized polymer electrolyte",
    "temperature-dependent electrolyte"
  ],
  "why": "Probe condition-performance relationships"
}
```


### B6

Source: [Nina, P304–P311](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR abs:\"reversible polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\") AND (abs:\"lithium metal battery\" OR abs:\"zinc-ion battery\" OR abs:\"solid-state battery\" OR abs:\"flexible battery\") AND (abs:symmetric OR abs:full-cell OR abs:LiFePO4 OR abs:cathode))",
  "query_nl": "Find applications of dynamic polymer electrolytes across battery systems, such as lithium metal, zinc-ion, solid-state, or flexible batteries. Target studies reporting symmetric-cell and full-cell evaluation.",
  "synonyms": [
    "dynamic polymer electrolyte",
    "self-healing hydrogel electrolyte",
    "solid-state battery electrolyte"
  ],
  "why": "Map application-specific battery demonstrations"
}
```


### B7

Source: [Nina, P321–P328](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\" OR abs:\"dynamic polymer for batteries\") AND (abs:dendrite OR abs:interfaceOR abs:SEI OR abs:\"interfacial resistance\" OR abs:\"plating/stripping\" OR abs:XPS)) AND (abs:lithium OR abs:anode)",
  "query_nl": "Search for interfacial phenomena in dynamic polymer electrolytes for batteries, especially dendrite suppression, adaptive contact, SEI chemistry, and plating/stripping stability on metal anodes. Include XPS or impedance-based interface analysis.",
  "synonyms": [
    "dynamic polymer for batteries",
    "anode interface electrolyte",
    "self-healing polymer electrolyte"
  ],
  "why": "Study interface stabilization and dendrite control"
}
```


### B8

Source: [Nina, P338–P345](https://docs.google.com/document/d/1ZI_E0sfhj2QI8wPetKYwLbXkv5HGLw0rwieAUnRCapg/edit).

```json
{
  "tiers": [
    "Physical sciences",
    "Chemistry",
    "Materials chemistry",
    "Polymers",
    "Dynamic polymers for battery applications"
  ],
  "query_bool": "(cat:cond-mat.mtrl-sci OR cat:physics.chem-ph) AND ((ti:\"dynamic polymer electrolyte\" OR abs:\"reversible polymer electrolyte\" OR abs:\"self-healing polymer electrolyte\") AND (abs:\"free volume\" OR abs:PALS OR abs:crystallinity OR abs:DSC OR abs:TGA OR abs:\"glass transition\" OR abs:morphology)) AND abs:batter*",
  "query_nl": "Retrieve studies linking morphology and thermal behavior to performance in dynamic polymer electrolytes for batteries. Focus on free volume, crystallinity, glass transition, thermal stability, and structure-property relationships.",
  "synonyms": [
    "reversible polymer electrolyte",
    "dynamic polymer electrolyte",
    "structure-property electrolyte"
  ],
  "why": "Connect morphology with battery performance"
}
```
