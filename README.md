AI HR Policy Assistant

Hybrid RAG System with FAISS + BM25 + LoRA

An internal AI assistant that answers company HR and policy questions with citations, built using a production-grade Retrieval-Augmented Generation (RAG) architecture.

This system prioritizes correctness, transparency, and controllability over raw model intelligence.

Key Capabilities

📄 PDF ingestion & semantic chunking

🔍 Hybrid retrieval

FAISS (semantic similarity, cosine search)

BM25 (lexical keyword matching)

⚖️ Score fusion: final = α·semantic + (1−α)·lexical

📎 Citation-based answers with page navigation

🧠 LoRA fine-tuned generation (style & tone only — not facts)

📊 Admin dashboard (stats, logs, index management)

🧪 Evaluation pipeline (precision, recall, MRR)

🔐 JWT-protected admin APIs

⚙️ Async background indexing

🏗️ System Architecture (High Level)
User Question
     ↓
Hybrid Retrieval
  ├─ FAISS (semantic vectors)
  └─ BM25 (lexical tokens)
     ↓
Score Fusion (α = 0.1)
     ↓
Top-K Chunks
     ↓
Context Builder
     ↓
LLM + LoRA (style only)
     ↓
Answer + Citations

🧠 Why Hybrid Retrieval?

HR and policy documents are lexical by nature — exact wording matters.

Pure semantic search often retrieves related but incorrect clauses.

This system combines:

Semantic similarity → understands natural language

Lexical precision → respects exact policy language

After evaluation, α = 0.1 delivered the best precision@1 and MRR, confirming that lexical signals should dominate in this domain.

🧩 FAISS Position ↔ Chunk Mapping (Important)

FAISS stores only vectors, not metadata.

To reliably map search results back to documents:

Each FAISS index has a corresponding registry entry

The registry stores an ordered mapping:

faiss_position → chunk_id


This guarantees deterministic retrieval even after:

restarts

index merges

background re-indexing

🧠 LoRA Fine-Tuning Philosophy

LoRA is used only to control response style, not to inject knowledge.

❌ No factual learning

❌ No hallucination tolerance

✅ Professional HR tone

✅ Structured, concise answers

If the LoRA adapter fails to load, the backend fails fast instead of silently degrading.

🗂️ Repository Structure (Simplified)
backend/
 ├── app/
 │   ├── api/              # FastAPI routes
 │   ├── core/             # RAG + retrieval logic
 │   ├── services/         # Indexer, evaluator, LoRA loader
 │   ├── models/           # SQLModel DB schemas
 │   ├── repos/            # DB access layer
 │   └── utils/            # FAISS utilities
 │
 ├── lora_models/          # LoRA adapters
 └── data/                 # PDFs, FAISS indexes, eval sets

frontend/
 ├── app/                  # Next.js pages
 ├── components/           # UI components
 └── lib/                  # API helpers

🧪 Evaluation

The system includes a simple but effective evaluation pipeline:

Upload labeled Q&A datasets (JSON)

Run evaluation asynchronously

Metrics stored in DB:

precision-like overlap scoring

per-question retrieval inspection

overall score & runtime

Evaluation is treated as a first-class citizen, not an afterthought.

🛠️ Tech Stack

Backend

FastAPI

SQLModel + SQLite

FAISS

Sentence Transformers

Transformers + PEFT (LoRA)

PyMuPDF

Frontend

Next.js (App Router)

Tailwind CSS

PDF.js

TypeAnimation

🎯 Design Principles

Retrieval > Generation

Transparency over magic

Evaluation before optimization

Models are unreliable — systems must compensate

Fail fast instead of failing silently

📌 Status

✔️ End-to-end functional

✔️ Retrieval evaluated

✔️ Admin observability implemented

🚫 Deployment details intentionally omitted

📎 Notes

This project was built to understand real-world RAG system design, not to showcase prompt tricks.

If you’re interested in production AI engineering, hybrid retrieval, or safe LLM systems — this codebase is meant to be read, not just run.
