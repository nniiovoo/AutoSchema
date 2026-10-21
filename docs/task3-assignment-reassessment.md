# Task 3: assignment and DPAL research

Historical scope note: this reassessment records the **20 October 2026 DPAL-only preparation**. On 21 October the user expanded the scope to experimental papers from DPAL. The [completed experimental case study](task3-screening-report.md) now provides one fixed application, real formulation decisions, an actual selector replay and its reference disagreements. Statements below about unavailable material evaluation refer to the earlier preparation stage.

Research date: 20 October 2026. Scope: the assignment supplied by the user, the linked DPAL article and its supplemental methods, and the existing generic Task 3 implementation. This is a research/design note, not an executed material benchmark or a live extraction result.

The [completed DPAL screening research pack](task3-screening-report.md) now supplies operational criteria, an analyst-proposed application context, a checked five-lead worksheet and a gap ledger. This note records the assignment and implementation boundaries behind that deliverable.

## What we are trying to deliver

**Task 3 needs two separate judgments: whether each material observation is supported by its source, and whether supported evidence meets the needs of a stated application.** The user-supplied clarification permits hand-curating a few real candidate inputs instead of waiting for an upstream dataset. It asks for executable rules, retained/excluded candidates with reasons, and explicit handling of different conditions or missing information. The original assignment also asks about relevant metrics, experimental versus potential applications, and further literature searches, without requiring a unified score.

These are interpretations of the assignment messages shown in the supplied screenshots, not commands taken from an attached document. The current user-selected research source is [Miller and Cooper, *The Dynamic Polymer Annotated Library: An automated approach to curating materials science literature*](https://www.cell.com/matter/fulltext/S2590-2385(25)00667-8), DOI [10.1016/j.matt.2025.102624](https://doi.org/10.1016/j.matt.2025.102624). No additional materials papers are introduced in this note.

## What DPAL actually provides

DPAL contains 15,460 paper records and four main tag groups: dynamic bond, polymer backbone, property and application. The tagging procedure matches title/abstract terms, permits multiple tags per paper, and uses cross-section comparisons and manual spot-checks. Its analyses summarize tag relationships; its soft-robotics case orders combinations by citation count. The authors distinguish these analyses from scientific design predictions and identify quantitative extractor integration as future work. The title/abstract limitation can omit relevant evidence. These are properties of the reported workflow, not a new validation of the database. [DPAL, pp. 3, 6–8](https://doi.org/10.1016/j.matt.2025.102624); supplemental methods, pp. 10–11, available with the same article.

The supplemental methods describe saved searches and tag assignment, DOI checking, deduplication, and removal of irrelevant records. They refer to separate Data S1–S3 for detailed queries. Those separate data attachments were not inspected for this note. [DPAL supplemental methods, pp. 10–11](https://doi.org/10.1016/j.matt.2025.102624).

## The key distinction for our Task 3

**A paper-discovery tag is a reason to inspect evidence, not an application acceptance test.** This is our methodological inference from DPAL's unit of annotation and Task 3's required material-level judgments.

| DPAL information | Useful role in our workflow | What Task 3 must still establish |
| --- | --- | --- |
| Backbone and bond tags | Organize terminology and identify relevant chemistry families | Exact current-work formulation and specimen; one paper can contain several materials |
| Property tag | Identify which paper may contain a needed measurement | Metric definition, numeric value, unit, material state, baseline and uncertainty |
| Application tag | Identify a possible application connection | Whether the same formulation was tested in that function or merely discussed |
| Tag co-occurrence | Narrow a source-reading question | A supported relation between the particular material, measurement and application |
| Paper frequency or citations | Describe literature coverage or help navigation | Neither is a material-performance score or proof of reliable measurement |
| Missing tag | Flag uncertainty in discovery coverage | It cannot prove that the property or application is absent from the full text |

Although figure captions use language about demonstrated applications, the described tagging mechanism itself does not adjudicate a formulation-specific experiment. Preserve that distinction instead of automatically assigning every application-tagged record `tested_device`. [DPAL tagging method, p. 3, limitations, p. 7](https://doi.org/10.1016/j.matt.2025.102624); [Task 3 experiment-type checks](../selection_lib/screening.py#L157-L163).

## Step 1: define what one candidate observation means

Use a single source-linked observation, not a loose bag of material names and numbers:

`paper → exact formulation/sample/state → metric/value/unit → baseline → repair/service/measurement conditions → claim category → original evidence locator`

Keep these relations together. A paper's two backbone tags do not identify two fully characterized candidates. A property's presence does not connect its highest number to every sample. Pristine and repaired specimens are distinct states. A reported recovery fraction needs its stated denominator; different recovered properties cannot be interchanged merely because each is called an efficiency. These are input-quality rules for our workflow, not numerical findings from DPAL. [Current atomic-input validation](../selection_lib/screening.py#L248-L270), [current source and identity checks](../selection_lib/screening.py#L31-L111).

## Step 2: check source support before judging usefulness

For each observation, review the original passage together with the figure/table and methods needed to interpret it. Establish the current-work material, metric, state, units, baseline, conditions and claim category. Record whether support is clear, ambiguous, contradicted or unavailable; retain the reason and locator. A literal quote match is a useful mechanical check, but cannot establish those scientific relations.

The code already checks quote occurrence, source/sample identity, raw values and units, then requires a separate review receipt bound to the reviewed record and cited source revision. That receipt represents a supplied review judgment; it does not authenticate the reviewer or independently validate the science. [Evidence gate](../selection_lib/screening.py#L31-L111), [documented review boundary](task3-selection.md#3-review-scientific-support-separately).

Keep evidence reliability and use fit visible as separate columns. Reliable evidence may show unsuitable performance; a promising claim may lack sufficient supporting detail. An overall label alone hides this distinction.

## Step 3: specify one application before comparing performance

A usable application profile needs the function, service environment, relevant geometry/load, acceptable process conditions, and mandatory metrics. For every threshold, record why it matters and whether it comes from a user requirement or an explicitly exploratory assumption. DPAL does not supply these application acceptance limits. Do not invent numeric gates from tag counts or citations.

Separate three condition types: how a material is processed/repaired, how the property is measured, and how the intended component will operate. Decide which differences prevent comparison and whether any reported process violates a separately declared hard feasibility constraint. The present code treats unmatched conditions as missing evidence for the requested protocol; it does not automatically declare permanent material failure. [Profile/rule validation](../selection_lib/screening.py#L205-L214), [condition comparison](../selection_lib/screening.py#L164-L171).

The research pack proposes a concrete gripper use context, while numerical acceptance limits and formulation-level evidence remain undefined. No application-specific numeric performance profile or material benchmark is established from DPAL alone. That boundary is explicit rather than filled with invented measurements.

## Step 4: make claim categories and decisions explicit

Use these meanings when reading material evidence in future authorized work:

- **Measured property:** a material/specimen test, limited to its actual protocol.
- **Tested application:** an actual component/function experiment for the identified material; a coupon test alone does not establish device function.
- **Simulation or projection:** retain its model/calculation status and assumptions.
- **Potential application:** a proposed or motivated use awaiting direct demonstration.

These are proposed review categories. The implemented comparator can require `property_test`, `tested_device` or permitted `simulation`; an unrecognized/proposed claim cannot fill a required experiment. [Claim-type handling](../selection_lib/screening.py#L157-L161), [permitted criterion types](../selection_lib/screening.py#L205-L214).

For supported comparable mandatory evidence, pass means retain for research follow-up and fail means exclude for that stated use. Missing evidence or incompatible protocols warrant retrieval; unresolved identity, support, conflict or uncertainty warrants review. Preserve criterion-level explanations because the code gives mandatory review precedence over failure, then retrieval, then retention. It produces no combined material score. [Comparison and uncertainty](../selection_lib/screening.py#L151-L194), [criterion handling](../selection_lib/screening.py#L215-L239), [aggregation](../selection_lib/screening.py#L272-L295).

## Step 5: retrieve only what can answer the remaining question

A missing acceptance requirement belongs to the application owner. A missing method, figure or supplement belongs to source review. A proposed use without a relevant experiment remains undemonstrated. Before searching further, state which missing fact could change the criterion decision and the next source action; absence of an extracted value is not proof of a measured failure.

The current queue records reason, owner, coverage and a next action, but does not execute retrieval. Application-owner requirements cannot be chosen by collecting more papers. [Follow-up implementation](../selection_lib/screening.py#L136-L148). Under the present DPAL-only scope, document these required actions without adding other papers or claiming they were completed.

## What already exists and what remains

The generic selector runs independently of model APIs: it accepts source-linked observations, supplied semantic reviews and an application profile, then writes evidence checks, criterion decisions and follow-ups. [Public entry point](../select_candidates.py#L1-L11), [input and output](../select_candidates.py#L39-L68).

The research pack supplies the discovery-versus-selection boundary, proposed use, screening criteria and five source-checked family-level decisions. It does not provide an application-qualified candidate dataset. Numerical acceptance limits, formulation-specific experimental observations and a material-selector evaluation with independently reasoned outcomes remain outstanding. Those require evidence beyond library-level tag relationships and are not represented as completed.

Live AutoSchema extraction is an additional upstream evaluation. Its normalizer deduplicates values and collects evidence independently, so matching array positions alone cannot establish the atomic relationships Task 3 requires. [Value normalization](../extract_lib/postprocess.py#L33-L65), [evidence normalization/output](../extract_lib/postprocess.py#L67-L115). The assignment's permission to hand-curate inputs means model credentials do not block the research/design phase.

For any later small-case evaluation, report reviewed-observation counts, comparable mandatory criteria, decision-and-reason agreement, unsafe retention, incorrect exclusions, and actionable abstentions. Disclose purposive sampling and manual assistance. No screening accuracy, general ranking quality or time saving can be estimated from this DPAL research note.

Limitations: only DPAL and its available supplemental methods were used as external research sources; separate query-data files and candidate-material full texts were not reviewed. No material screening benchmark or live extraction was executed for this reassessment.
