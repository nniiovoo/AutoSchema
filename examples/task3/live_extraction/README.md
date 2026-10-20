# Planned live Phase II / Task 3 comparison

Preparation date: 20 October 2026. Baseline fork commit: `9313675`, branch `task3-selection`.

**Status: the actual entry point was invoked and loaded this schema, but stopped at client initialization because `CHAT_API_KEY` was missing. Zero model requests and zero successful extraction records were generated. No extraction-performance score is claimed here.**

## Fixed extraction condition

Use the existing `extract_schema_values.py` entry point, PDF reader, passage retriever, default system prompt, model client and normalizer unchanged. The supplied `schema.json` defines sixteen analyst-written polymer fields. It contains no reference values, paper-specific formulations or example evidence. This tests Phase II with a manually specified schema; it does not test Phase I polymer schema induction.

The prior checked records in `../real_papers/` remain a frozen, partial reference. They are not supplied to the model. The application profile, thresholds and diagnostic expectations remain unchanged.

| Paper-level packet | Pages | Source coverage |
| --- | --- | --- |
| Cornellà 2024 | 11 | Published main paper, institutional cover pages removed |
| Li 2016 | 42 | Main paper followed by available SI |
| Terryn 2017 | 28 | Author submitted manuscript with SI, institutional cover removed |
| Montarnal 2011 | 4 | Main article plus neighboring-article fragments on first/last pages; source contamination explicitly retained |

Lossless packet preparation preserves each retained page's text, content streams and page boxes. Original-document and packet hashes and page mappings are saved locally. Cornellà/Montarnal SI is not included. Different source coverage must not become a model error by assumption.

## CPU preflight findings

The unchanged passage retriever selected 23 passages for Cornellà, 26 for Li, 41 for Terryn and 13 for Montarnal. A separate assistant audit located all ten selected reference headline facts in those contexts (seven numeric, three qualitative). This is a partial-reference retrieval check, not extraction accuracy or proof that complete sample/property/protocol tuples are present.

Li's SI definition of healing efficiency is present in selected Passage 2. Terryn's detailed practical heating/cooling/ambient-dwell protocol is readable in full text but absent from the selected passages; a different simulated recovery description is present. Montarnal's context includes preceding-article fragments in Passages 6 and 11, and following-article fragments in Passages 12 and 13. These are explicit context-coverage and document-boundary findings for the eventual model evaluation.

Full preflight prompts, passage maps, hashes, source coverage, audit reasoning and the credential-blocked attempt are retained locally under the ignored run directory. No model output exists to adjudicate yet.

## Execute when local credentials are ready

The normal client loader requires `CHAT_API_KEY`, including `LLM_PROVIDER=openai`. Keep secrets in the local ignored `.env` or process environment, never in this example. It uses `CHAT_MODEL` for OpenAI. The normal client path currently does not read `OPENAI_API_KEY` as a fallback. See `prompt_lib/llm_client.py`.

Prepared PDFs, source records and local trace tools are under the ignored directory `outputs/task3_live_extraction_2026-10-20/`. With the required runtime installed, run from the repository root using a fresh output directory:

```sh
python outputs/task3_live_extraction_2026-10-20/trace_extraction.py \
  --repo . \
  --pdf-dir outputs/task3_live_extraction_2026-10-20/inputs \
  --schema examples/task3/live_extraction/schema.json \
  --out-dir outputs/task3_live_extraction_2026-10-20/run_01 \
  --n-papers -1 \
  --max-chars-per-paper 0
```

The local trace wrapper invokes the real entry point and forwards native request parameters unchanged. It retains exact prompts, full raw SDK responses with usage/finish metadata, elapsed time and parsed pre-normalization records; exception bodies are suppressed. It does not supply answers or replace the model. The native code permits three application attempts per paper; SDK retries are additional. Actual provider/model/settings, hashes and runtime versions must accompany any results. A preflight credential check is not a successful model request.

## Compare four distinct stages

1. **Source and retrieval coverage:** determine whether each checked fact is in the supplied PDF text and then in the actual model context. No OCR or figure digitization is performed.
2. **Extraction:** audit raw values and their explicit evidence pairing before normalization. Check the cited passage and quote, exact metric, formulation, material state, baseline, uncertainty, conditions and claim category. Normalization deduplicates values independently from evidence; equal positions after normalization alone do not establish alignment.
3. **Partial-reference coverage:** the checked target set has ten observations: seven numeric and three qualitative. Report recovery of these selected facts, partial matches and missing attributes. This is conditional coverage, not exhaustive paper-wide recall. When a source defines fracture-strain and elongation-at-break recovery equivalently, treat duplicate emissions across those fields as one semantic fact. Audit extra numeric/application claims too. Supported other formulations and background statements can be valid broad extraction, while remaining unusable for the selected current-work candidate.
4. **Task 3 handoff:** pass only genuinely extraction-linked atomic observations with separately audited support. Do not copy omitted relations from the reference into the model record. Unresolved sample/protocol/metric links remain unresolved. Report unassisted handoff separately from extraction with manual enrichment.

All four checked shared candidate labels are `retrieve_more`; an empty handoff would match them too. Therefore final-label agreement alone is not success. Show accepted extraction-derived observations, Cornellà's informative relative-strength criterion, Li's distinct diagnostic reasons, and missing absolute healed strength separately. Preserve any source-supported reference correction as an explicit erratum rather than forcing agreement.

No live results have been generated at preparation time. Full source PDFs, prompt context and generated model outputs remain local and are not committed.
