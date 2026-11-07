# What Would Lee Kuan Yew Do? — RAG chatbot

A text chatbot that answers in the voice of Lee Kuan Yew, grounded in a corpus of his 1965 speeches and interviews. Retrieval and chat run in AnythingLLM, generation uses Google Gemini, and a scripted evaluation tests it.

> **Scope note:** the retrieval corpus is six documents from 1965 (about 25,800 words). Questions about later periods, or topics the documents don't cover, are answered mainly from the base model's pretraining, steered by the system prompt. This is a known limitation.

## What I built vs. configured

I did not write the retriever. AnythingLLM provides chunking, embedding, vector storage and retrieval. My contributions:

- choosing and preparing the corpus
- the system prompt (two versions, see `system_prompt.txt`)
- retrieval and chunking settings
- an evaluation harness (`run_eval.py`) with 15 test questions, run against baseline and revised configurations

## Architecture

| Component | Choice |
|---|---|
| RAG platform | AnythingLLM (desktop app) |
| LLM | Google Gemini, [[MODEL NAME, e.g. as shown in Settings → LLM Preference]] |
| Embedder | [[confirm in Settings → Embedder Preference; AnythingLLM's default is its built-in embedder]] |
| Vector DB | LanceDB (AnythingLLM's default) |
| Chunking | 1000 characters, overlap 20 |
| Retrieval | top-[[4 for v1 / 8 for v3]] chunks, similarity threshold ≥ 0.25 ("low") |
| Chat mode | Chat (not Query), so off-corpus questions still get an in-character answer |
| Temperature | 0.5 |

Flow: question → embedded → nearest chunks retrieved from LanceDB → chunks + system prompt sent to Gemini → in-character answer, with the source files listed.

## Corpus

Six transcripts, all from 1965, in `data/`. See `sources.md` for dates, settings and word counts. Source of the PDFs: [[WHERE YOU DOWNLOADED THEM, with URL]].

No memoirs or articles are included. The brief mentions them, but the corpus here is speeches and interviews only.

## Evaluation

`run_eval.py` sends 15 fixed questions to the workspace through AnythingLLM's developer API and writes answers and cited sources to `eval/`.

| Type | Count | What a pass looks like |
|---|---|---|
| In-docs (D1–D8) | 8 | Grounded in the PDFs, in voice, cites the expected file |
| Anachronism (A1–A3) | 3 | Says the topic postdates him (he died in 2015) instead of stating post-2015 facts as his own knowledge |
| Out of scope (O1–O2) | 2 | Stays in character |
| Adversarial (X1–X2) | 2 | Does not cave or invent. X2 asks about a 1975 speech that does not exist in the corpus |

Scoring criteria: **grounded**, **in voice**, **no fabrication**. The script records automatically whether the expected source file was cited (`source_hit`). Other scores are by hand. Specific claims in D answers were spot-checked against the extracted PDF text by keyword search.

Full question list: `eval/questions.md`.

### Run history

| Run | Config | File |
|---|---|---|
| v1 baseline | prompt v1, 4 snippets | `eval/results_v1_baseline.*` |
| v2 | prompt v2 (adds post-2015, false-premise, off-topic rules), 4 snippets | `eval/results_v2.*` |
| v3 | prompt v2, 8 snippets | `eval/results_v3.*` |

### v1 baseline findings

- **In-docs:** all 8 answers were in voice, and 7 of 8 cited the expected file. Specifics checked against the text (names, figures, phrases) mostly traced to the PDFs. Small unsupported phrasing appeared in D3 and D6.
- **Retrieval miss (D5):** the most direct passage ("no need for a big army", 8 Nov 1965) was not retrieved. The answer instead used a real but less relevant passage from the 9 Aug press conference. Likely cause: only 4 snippets retrieved (my inference, tested in v3).
- **Anachronisms (A1–A3):** 0 of 3 flagged that the topic postdates him. The model discussed ChatGPT, COVID-19 and the Ukraine war as if it had observed them. Cause: prompt v1 said to answer from his "core philosophies" when documents were silent, with no rule about his death.
- **False premise (X2):** the model invented an oil-crisis work-sharing rationale for a "1975 four-day work week" that I made up. None of the search terms for it appear in the corpus.
- **Run errors:** O1, O2 and X1 returned HTTP 500 in the baseline run, so there is no baseline data for them. [[Cause if you found it; otherwise "cause not determined; rerun in v2"]]

### v2 / v3 results

[[Fill in after scoring. For each of v2 and v3: pass counts per category, what changed versus v1, and anything that still fails. Example format:
- Anachronism: v1 0/3 → v2 X/3
- D5 cited the 8 Nov file: v1 no → v3 yes/no
- X2: v1 fail → v2 pass/fail]]

## Known limitations

- Corpus covers 1965 only. Answers on later events draw on Gemini's pretraining, not retrieval.
- Source citations show which chunks were retrieved, not which ones the model actually used.
- The eval is 15 questions, scored by one person. It shows failure modes, not statistical performance.
- The persona is a simulation. Statements are not authentic quotations unless they appear in the cited documents.
- No public demo. It runs locally in AnythingLLM. See `screenshots/` for evidence.

## Reproduce

1. Install AnythingLLM desktop, create a workspace, set the LLM to Google Gemini with your own API key.
2. Upload the PDFs from `data/`, move them into the workspace, "Save and Embed".
3. Paste the contents of `system_prompt.txt` into Workspace Settings → Chat Settings. Set chat mode to Chat, temperature 0.5.
4. Settings → Developer API → generate a key.
5. Run (Windows cmd):
   ```
   pip install requests
   set ANYTHINGLLM_KEY=your-key
   set ANYTHINGLLM_SLUG=your-workspace-slug
   set EVAL_OUT=results_run1
   python run_eval.py
   ```
6. Score `eval/results_run1.md` by hand.

API keys are read from environment variables and are not stored in this repo.

## Repo layout

```
data/            source PDFs (1965 transcripts)
eval/            questions, results (json + md) per run
screenshots/     settings, document list, chat examples
system_prompt.txt
sources.md
run_eval.py
```
