# backend/app/services/indexer.py

import os
from typing import List
from datetime import datetime
import numpy as np
import faiss

from sqlmodel import select
from sqlalchemy import select as sa_select
from app.utils.faiss_merge import merge_faiss_indexes
from app.repos.repo_rag import get_all_faiss_registries


from app.models.models import Document, Chunk, FaissIndexRegistry
from app.db.session import async_session
from app.core.rag_engine import load_pdf_pages, chunk_page_semantic, get_model
from app.utils.faiss_store import save_faiss_index

DATA_DIR = "data"
FAISS_DIR = os.path.join(DATA_DIR, "faiss")
os.makedirs(FAISS_DIR, exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)
async def merge_all_indexes():
    """Manually merge ALL FAISS indexes into one global index and register it in DB."""
    from app.repos.repo_rag import get_all_faiss_registries, create_faiss_registry

    registries = await get_all_faiss_registries()
    if not registries:
        print("[MERGE] No registries found.")
        return None

    # collect paths and chunk id maps
    faiss_paths = []
    merged_chunk_ids = []
    for r in registries:
        if getattr(r, "faiss_path", None):
            faiss_paths.append(r.faiss_path)
        # ensure we extend in index order
        cids = getattr(r, "faiss_to_chunk_ids", None) or []
        merged_chunk_ids.extend(cids)

    if not faiss_paths:
        print("[MERGE] No FAISS files to merge.")
        return None

    merged_index = merge_faiss_indexes(faiss_paths)
    if merged_index is None:
        print("[MERGE] Failed to merge indexes.")
        return None

    # save merged index to a stable path (overwrite if exists)
    merged_path = os.path.join(FAISS_DIR, "global.index")
    save_faiss_index(merged_index, merged_path)
    print("[MERGE] Saved global merged index:", merged_path)

    # create a DB registry row for global index
    global_registry = FaissIndexRegistry(
        faiss_path=merged_path,
        embed_dim=merged_index.d if hasattr(merged_index, "d") else EMBED_DIM,
        total_chunks=len(merged_chunk_ids),
        faiss_to_chunk_ids=merged_chunk_ids
    )

    async with async_session() as session:
        session.add(global_registry)
        await session.commit()
        await session.refresh(global_registry)

    print("[MERGE] Global registry saved ID=", global_registry.id)
    print(f"[MERGE] Total chunks in global index: {global_registry.total_chunks}")

    return global_registry

async def index_pdf_background(pdf_path: str, doc_id: str, model_device: str = None):
    print(f"[Indexer] Checking document: {doc_id}")

    # ---------------------------------------------------------
    # 0) DUPLICATE CHECK (SQLAlchemy AsyncSession syntax)
    # ---------------------------------------------------------
    async with async_session() as session:
        result = await session.execute(
            sa_select(Document).where(Document.doc_id == doc_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"[Indexer] SKIPPED: '{doc_id}' already indexed (id={existing.id}).")
            return {"status": "exists", "doc_id": doc_id}

    # ---------------------------------------------------------
    # 1) CREATE NEW DOCUMENT ENTRY
    # ---------------------------------------------------------
    async with async_session() as session:
        document = Document(doc_id=doc_id, file_path=pdf_path)
        session.add(document)
        await session.commit()
        await session.refresh(document)

    print(f"[Indexer] Document created: {document.id}")

    # ---------------------------------------------------------
    # 2) LOAD PDF + GENERATE CHUNKS
    # ---------------------------------------------------------
    pages = load_pdf_pages(pdf_path)
    chunk_rows: List[Chunk] = []

    for page_no, text in enumerate(pages):
        chunks = chunk_page_semantic(doc_id, page_no, text)
        for c in chunks:
            chunk_rows.append(
                Chunk(
                    doc_id=doc_id,
                    text=c["text"],
                    page=page_no,
                    start_char=c["start_char"],
                    end_char=c["end_char"],
                )
            )

    # BULK INSERT CHUNKS
    async with async_session() as session:
        session.add_all(chunk_rows)
        await session.commit()
        for ch in chunk_rows:
            await session.refresh(ch)

    # ASSIGN chunk_id = actual DB primary key
    for ch in chunk_rows:
        ch.chunk_id = ch.id

    async with async_session() as session:
        session.add_all(chunk_rows)
        await session.commit()

    print(f"[Indexer] Total chunks prepared: {len(chunk_rows)}")
    if not chunk_rows:
        print("[Indexer] WARNING: No chunks found. Aborting.")
        return

    # ---------------------------------------------------------
    # 3) EMBEDDING + FAISS INDEX
    # ---------------------------------------------------------
    model = get_model(device=model_device)
    embed_dim = model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatIP(embed_dim)

    batch_size = 32
    for i in range(0, len(chunk_rows), batch_size):
        texts = [c.text for c in chunk_rows[i:i+batch_size]]
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")
        index.add(embeddings)

    print(f"[Indexer] Embeddings added: vectors={index.ntotal}")

    # ---------------------------------------------------------
    # 4) SAVE FAISS INDEX FILE
    # ---------------------------------------------------------
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    faiss_filename = f"{doc_id}_{ts}.index"
    faiss_path = os.path.join(FAISS_DIR, faiss_filename)

    save_faiss_index(index, faiss_path)
    print(f"[Indexer] FAISS saved: {faiss_path}")

    ordered_ids = [c.chunk_id for c in chunk_rows]

    # ---------------------------------------------------------
    # 5) SAVE FAISS REGISTRY ENTRY
    # ---------------------------------------------------------
    registry = FaissIndexRegistry(
        faiss_path=faiss_path,
        embed_dim=embed_dim,
        total_chunks=len(ordered_ids),
        faiss_to_chunk_ids=ordered_ids,
    )

    async with async_session() as session:
        session.add(registry)
        await session.commit()
        await session.refresh(registry)

    print(f"[Indexer] Registry saved ID={registry.id}")
    print(f"[Indexer] Completed indexing for {doc_id}")

    return {
        "status": "indexed",
        "doc_id": doc_id,
        "registry_id": registry.id,
        "faiss_path": faiss_path,
        "chunks_indexed": len(chunk_rows),
    }
