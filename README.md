# AI HR Policy Assistant

A retrieval-augmented question-answering system over HR policy documents. Ask a
question in plain English, get an answer grounded in the actual policy text with
a citation back to the source page.

I built this because I wanted to query my own company's HR policy manual — a
69-page PDF where finding one clause meant scrolling for ten minutes. The
interesting engineering problem turned out not to be the generation step, but
the retrieval step and, more than that, **how to know whether retrieval is any
good.** Most of the work here is about measuring that.

---

## Architecture

```
PDF upload
   ↓
Text extraction (PyMuPDF) → hyphenation repair → NFKC normalisation
   ↓                        → wrapped-line merge → heading detection
Paragraph-aware semantic chunking (doc_id, page, char offsets retained)
   ↓
   ├──→ Dense: BAAI/bge-base-en embeddings → FAISS index
   └──→ Lexical: cleaned tokens → BM25Okapi corpus
   ↓
Query → both retrievers → min-max normalise each → weighted fusion
        final_score = α · semantic + (1 − α) · lexical
   ↓
Top-k chunks → context builder (char-budgeted) → LLM → cited answer
```

**Stack:** FastAPI · Next.js · FAISS · rank_bm25 · SentenceTransformers (BGE) ·
PyMuPDF · PostgreSQL · JWT auth · Docker Compose

**Features:** PDF upload with async background indexing · hybrid retrieval with
a tunable fusion weight · answers cited to document and page · admin dashboard
with query logs and system stats · JWT-protected admin API · a retrieval
evaluation harness (below).

---

## Retrieval evaluation

Answer quality is subjective; retrieval quality is not. If the right chunk never
reaches the context window, no amount of prompt engineering saves the answer —
so this is the part worth measuring.

`eval/eval_dataset.json` is a **hand-labelled query set**: 25 questions written
against the indexed corpus, each mapped to the chunk id(s) that actually contain
the answer. `eval/rag_eval.py` scores the retriever against it using standard IR
metrics — precision@k, recall@k, MRR@10, hit rate@k and R-precision.

```bash
python eval/rag_eval.py --mode bm25         # lexical baseline
python eval/rag_eval.py --mode semantic     # dense only
python eval/rag_eval.py --mode hybrid       # all three, side by side
python eval/rag_eval.py --sweep-alpha       # find the best fusion weight
```

### Results

Corpus: 49 chunks from a 17-page HR policy document. 25 hand-labelled queries.

| Retriever | MRR@10 | Recall@5 | Hit rate@3 | Precision@1 |
|---|---|---|---|---|
| BM25 (lexical only) | 0.843 | 0.860 | **0.880** | **0.800** |
| Dense only (BGE) | 0.818 | **0.980** | 0.840 | 0.720 |
| Hybrid (α = 0.6) | **0.847** | 0.940 | **0.880** | 0.760 |

Sweeping the fusion weight puts the optimum at **α = 0.4** (MRR@10 **0.857**), so
hybrid does beat BM25 alone — but by 0.014 MRR@10 at the best α and 0.004 at the
shipped α = 0.6, a margin worth far less than the +0.080 Recall@5 it also buys,
and one that 25 queries cannot meaningfully separate from noise.

**What the baseline already tells us.** BM25 alone reaches 0.843 MRR@10 on this
corpus. That is high, and it is not an accident: HR policy questions are
keyword-heavy ("maternity leave", "probation period", "bike allowance"), the
vocabulary in the question closely matches the vocabulary in the document, and
the corpus is small. Lexical search is well suited to exactly this shape of
problem.

That reframes the question the hybrid design has to answer. It is not "does
adding dense retrieval help?" but **"does it help enough to justify loading a
440MB encoder and paying embedding latency on every query?"** The α sweep exists
to answer that with numbers rather than assumption. Where dense retrieval should
earn its place is on paraphrased questions that share no vocabulary with the
source text — so the honest next step is to extend the query set with
deliberately paraphrased questions and see whether the gap opens up.

---

## Getting started

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # from backend/

# Frontend
cd policy-frontend && npm install && npm run dev
```

---

## Notes on the generation layer

`services/lora_loader.py` loads a LoRA adapter over a base model via `peft`.
This was **a deliberate learning exercise, not a production choice**: the base
model is GPT-2, and the goal was to understand adapter training hands-on —
rank, target modules, how the adapter merges at inference. A production
deployment of this system would use an instruct-tuned model for generation; the
adapter path is kept because the experiment is part of what the project is for.

## Known limitations

- Fusion normalises each retriever's scores min-max **within the top-k slice**,
  so the top hit always maps to 1.0 and the bottom to 0.0. This distorts the
  weighted sum when one retriever is confident and the other is not; a rank-based
  fusion such as RRF would be more stable.
- The query set is small (25 queries, one document). Numbers are directional.
- No re-ranker. A cross-encoder over the top-20 is the obvious next improvement.
- Evaluation covers retrieval only, not answer faithfulness.
