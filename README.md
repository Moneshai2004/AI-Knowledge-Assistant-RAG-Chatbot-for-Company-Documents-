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
                         │     data/bm25/
