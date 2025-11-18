🧩 AI Knowledge Assistant — System Architecture Diagram
                         ┌─────────────────────────────────────────┐
                         │              FRONTEND UI                │
                         │   (Streamlit → Next.js / React)         │
                         │                                         │
                         │  • Chat Interface                       │
                         │  • File Upload (PDF)                    │
                         │  • Source Viewer                        │
                         └─────────────────────────────────────────┘
                                          │   REST API (HTTPS)
                                          ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI BACKEND                             │
│ ─────────────────────────────────────────────────────────────────────────── │
│                                                                              │
│  ROUTES (API Layer)                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ /upload → saves file + triggers background indexing                    │   │
│  │ /ask    → hybrid RAG pipeline → LLM answer                              │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  BACKGROUND INDEXER                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ 1. PDF → Text Extraction (PyMuPDF)                                      │   │
│  │ 2. Semantic Chunking (custom paragraph logic)                           │   │
│  │ 3. Chunk Insertion (SQLModel → SQLite/Postgres)                         │   │
│  │ 4. Embeddings (BGE-base-en)                                             │   │
│  │ 5. FAISS Vector Index creation                                          │   │
│  │ 6. BM25 Corpus build                                                    │   │
│  │ 7. Save registry entry → DB                                             │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  HYBRID RAG ENGINE                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Semantic Search (FAISS)                                                 │   │
│  │ Lexical Search (BM25)                                                   │   │
│  │ Score fusion (α = 0.1 best)                                             │   │
│  │ Chunk retrieval + context builder                                       │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  LLM LAYER (Groq API)                                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ llama-3.3-70b-versatile                                                  │   │
│  │ - Strict RAG-only answering                                              │   │
│  │ - Zero hallucination rules                                               │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │                       DATABASE                         │
              │                (SQLite → PostgreSQL)                   │
              │                                                        │
              │  Tables:                                               │
              │  • documents                                           │
              │  • chunks                                              │
              │  • faiss_index_registry                                │
              │  • query_log                                           │
              │                                                        │
              └────────────────────────────────────────────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────────────┐
                         │             FILE STORAGE                │
                         │     data/uploads/*.pdf                 │
                         │     data/faiss/*.index                 │
                         │     data/bm25/*.json                  │
                         └─────────────────────────────────────────┘

🌟 README.md (Professional, Attractive, Complete)

Copy this entire README and paste into your GitHub repo.

🚀 AI Knowledge Assistant (Production-Grade Hybrid RAG)

A modern, production-ready AI Knowledge Retrieval System built with:

FastAPI backend

Hybrid RAG (FAISS + BM25)

BGE Embeddings

Groq LLMs (llama-3.3-70b-versatile)

Streamlit → Next.js frontend

SQLite → PostgreSQL

Fully async pipeline

Enterprise PDF semantic chunking

This project transforms raw PDFs into a searchable knowledge engine with high-quality answers and source citations.

📘 Table of Contents

Features

Architecture

Tech Stack

Installation

Environment Variables

API Endpoints

RAG Pipeline Details

Future Improvements

Folder Structure

✨ Features
🔍 Hybrid Retrieval

FAISS Semantic Search

BM25 Keyword Search

Fusion scoring (α = 0.1 optimal from evaluation)

📄 Semantic Chunking Engine

Smart chunking by:

Paragraph detection

Line-wrapping correction

Hyphenation fix

Overlapping windowing

Ideal for large HR/Policy PDFs.

📚 Full Database Integration

PDF metadata

Chunks

FAISS registry

Query log

Future-ready for PostgreSQL

🧠 LLM Answer Engine

Groq llama-3.3-70b-versatile

Zero hallucination rules

Mandatory evidence citations

RAG-strict QA system

⚡ FastAPI Backend

Async indexing

Background tasks

Streaming search pipeline

🏗 Architecture

See full ASCII diagram above (already included).

🛠 Tech Stack
Layer	Technology
Backend API	FastAPI
Vector Search	FAISS
Lexical Search	BM25 (Rank-BM25)
Embeddings	BGE-base-en (768 dims)
LLM	Groq – llama-3.3-70b-versatile
Frontend	Streamlit → Next.js
DB	SQLite (dev) → PostgreSQL (prod)
ORM	SQLModel (SQLAlchemy async)
PDF Parsing	PyMuPDF
🔧 Installation
git clone https://github.com/your-repo/ai-knowledge-assistant
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Frontend (soon):

cd frontend
npm install
npm run dev

🔐 Environment Variables

Create .env:

GROQ_API_KEY=your_key_here
EMBED_MODEL_NAME=BAAI/bge-base-en
EMBED_DIM=768
RAG_DATA_DIR=data
DATABASE_URL=sqlite+aiosqlite:///./data/rag.db

🌐 API Endpoints
POST /upload/

Upload a PDF and begin indexing.

curl -X POST -F "file=@your.pdf" http://localhost:8000/upload/

POST /ask/

Ask a question.

curl -X POST http://localhost:8000/ask \
 -H "Content-Type: application/json" \
 -d '{"question":"What is HR policy?"}'

🧬 RAG Pipeline Details
1. Upload → Background Job

Save PDF

Extract pages

Perform semantic chunking

Insert chunks into DB

Encode all chunks using BGE

Build FAISS index

Build BM25 corpus

Save registry

2. Query → Hybrid Search

Embed query

FAISS similarity search

BM25 lexical scoring

Score fusion

Rank chunks

Build context window

Send to Groq LLM

3. LLM Answer Rules

Must use only RAG context

No outside knowledge

No hallucination

Must add citations

📂 Folder Structure
backend/
│── app/
│   ├── api/
│   │   ├── routes_upload.py
│   │   └── routes_ask.py
│   ├── core/
│   │   ├── rag_engine.py
│   │   ├── llm.py
│   │   └── chunker/
│   ├── db/
│   │   ├── session.py
│   │   └── create_tables.py
│   ├── models/
│   ├── repos/
│   ├── services/
│   │   └── indexer.py
│   └── utils/
│── data/
│   ├── uploads/
│   ├── faiss/
│   ├── bm25/
│   └── rag.db
└── requirements.txt

🚧 Future Improvements (Roadmap)
1. PostgreSQL migration

Production-level durability, indexing, performance.

2. Reranker

Add cross-encoder for boosted accuracy.

3. Vector compression

FAISS IVF-PQ for large documents.

4. Multi-document search

Group results in UI.

5. Frontend upgrade

Build a Next.js chat UI with:

Streaming

PDF viewer

Highlight passages

6. Evaluation Suite

MRR

Recall@K

Custom gold dataset
