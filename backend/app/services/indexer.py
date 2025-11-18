# backend/app/services/indexer.py

import os
from typing import List
from datetime import datetime
import numpy as np
import faiss

from app.models.models import Document, Chunk, FaissIndexRegistry
from app.db.session import async_session
from app.repos.repo_rag import create_document
from app.core.rag_engine import load_pdf_pages, chunk_page_semantic, get_model
from app.utils.faiss_store import save_faiss_index

DATA_DIR = os.getenv("RAG_DATA_DIR", "data")
FAISS_DIR = os.path.join(DATA_DIR, "faiss")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))

os.makedirs(FAISS_DIR, exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)


async def index_pdf_background(pdf_path: str, doc_id: str, model_device: str = None):
    print(f"[Indexer] Starting indexing: {pdf_path}")

    # ---------------------------
    # 1) CREATE DOCUMENT ROW
    # ---------------------------
    document = Document(
        doc_id=doc_id,
        file_path=pdf_path,
        meta_json=None
    )
    document = await create_document(document)
    print(f"[Indexer] Document created: {document.id}")

    # ---------------------------
    # 2) EXTRACT PAGES & CHUNK
    # ---------------------------
    pages = load_pdf_pages(pdf_path)
    chunk_rows: List[Chunk] = []

    for page_no, text in enumerate(pages):
        chunks = chunk_page_semantic(doc_id, page_no, text)

        for idx, c in enumerate(chunks):
            chunk_rows.append(
                Chunk(
                    doc_id=doc_id,
                    chunk_id=idx,                    # FIXED (int only)
                    text=c["text"],
                    page=c["page"],
                    start_char=c["start_char"],
                    end_char=c["end_char"],
                )
            )

    print(f"[Indexer] Total chunks prepared: {len(chunk_rows)}")

    if not chunk_rows:
        print("[Indexer] WARNING: No chunks found. Aborting.")
        return

    # ---------------------------
    # 3) INSERT CHUNKS (BULK)
    # ---------------------------
    async with async_session() as session:
        session.add_all(chunk_rows)
        await session.commit()
        for ch in chunk_rows:
            await session.refresh(ch)

    ordered_chunk_ids = [c.id for c in chunk_rows]
    print(f"[Indexer] Inserted chunks in DB. First={ordered_chunk_ids[0]}, Last={ordered_chunk_ids[-1]}")

    # ---------------------------
    # 4) ENCODE & FAISS
    # ---------------------------
    model = get_model(device=model_device)
    index = faiss.IndexFlatIP(EMBED_DIM)

    batch_size = 32
    for i in range(0, len(chunk_rows), batch_size):
        batch_texts = [c.text for c in chunk_rows[i:i+batch_size]]
        embeddings = model.encode(
            batch_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        index.add(embeddings)

    print(f"[Indexer] Embeddings added: vectors={index.ntotal}")

    # ---------------------------
    # 5) SAVE INDEX
    # ---------------------------
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    faiss_filename = f"{doc_id}_{ts}.index"
    faiss_path = os.path.join(FAISS_DIR, faiss_filename)

    save_faiss_index(index, faiss_path)
    print(f"[Indexer] FAISS saved: {faiss_path}")

    # ---------------------------
    # 6) SAVE REGISTRY (MATCHES MODEL)
    # ---------------------------
    registry = FaissIndexRegistry(
        faiss_path=faiss_path,
        bm25_path="",      # or "none" — anything non-null
        embed_dim=EMBED_DIM,
        total_chunks=len(ordered_chunk_ids)
    )

    async with async_session() as session:
        session.add(registry)
        await session.commit()
        await session.refresh(registry)

    print(f"[Indexer] Registry saved ID={registry.id}")
    print(f"[Indexer] Completed indexing for {doc_id}")

    return {
        "doc_id": doc_id,
        "chunks_indexed": len(chunk_rows),
        "faiss_path": faiss_path,
        "registry_id": registry.id
    }
