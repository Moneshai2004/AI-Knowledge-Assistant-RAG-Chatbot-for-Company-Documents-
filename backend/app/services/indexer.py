# backend/app/services/indexer.py
import os
from typing import List
from datetime import datetime
import numpy as np
import faiss

from app.models.models import Document, Chunk, FaissIndexRegistry
from app.db.session import async_session
from app.repos.repo_rag import create_document, create_faiss_registry  # optionally used
from app.core.rag_engine import load_pdf_pages, chunk_page_semantic, get_model  # reuse chunker & model
from app.utils.faiss_store import save_faiss_index, load_faiss_index  # optional helper
from sqlmodel import select

DATA_DIR = os.getenv("RAG_DATA_DIR", "data")
FAISS_DIR = os.path.join(DATA_DIR, "faiss")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))

os.makedirs(FAISS_DIR, exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)


async def index_pdf_background(pdf_path: str, doc_id: str, model_device: str = None):
    """
    1) Insert Document row
    2) Create Chunk objects and insert to DB to obtain chunk IDs in exact insertion order
    3) Encode chunks in the same order and add embeddings to FAISS
    4) Save FAISS file and record FaissIndexRegistry with faiss_to_chunk_ids mapping
    """
    # 1) create document record
    doc = Document(doc_id=doc_id, filename=os.path.basename(pdf_path), source_path=pdf_path)
    doc = await create_document(doc)

    # 2) build chunk objects (Python objects)
    pages = load_pdf_pages(pdf_path)
    chunk_objs = []
    for page_no, page_text in enumerate(pages):
        page_chunks = chunk_page_semantic(doc_id, page_no, page_text)
        for c in page_chunks:
            ch = Chunk(
                doc_id=doc_id,
                page=c.get("page"),
                start_char=c.get("start_char"),
                end_char=c.get("end_char"),
                text=c.get("text"),
                token_count=len(c.get("text").split())
            )
            chunk_objs.append(ch)

    # 3) bulk insert chunks to DB to get DB-assigned IDs in the same order
    async with async_session() as session:
        session.add_all(chunk_objs)
        await session.commit()
        # refresh each to get .id
        for ch in chunk_objs:
            await session.refresh(ch)

    ordered_chunk_ids = [c.id for c in chunk_objs]

    # 4) Build FAISS index and add embeddings in *the same exact order*
    # Prepare FAISS index
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    faiss_name = f"{doc_id}_{ts}.index"
    faiss_path = os.path.join(FAISS_DIR, faiss_name)

    model = get_model(device=model_device)
    batch_size = 32
    index = faiss.IndexFlatIP(EMBED_DIM)

    # encode in batches, preserve order of chunk_objs
    for i in range(0, len(chunk_objs), batch_size):
        texts = [c.text for c in chunk_objs[i:i+batch_size]]
        emb = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        emb = emb.astype("float32")
        index.add(emb)

    # 5) save index to disk
    save_faiss_index(index, faiss_path)

    # 6) create registry entry with mapping array
    registry = FaissIndexRegistry(
        name=faiss_name,
        file_path=faiss_path,
        embed_dim=EMBED_DIM,
        index_type="IndexFlatIP",
        doc_ids=[doc_id],
        faiss_to_chunk_ids=ordered_chunk_ids
    )

    # persist registry in DB
    async with async_session() as session:
        session.add(registry)
        await session.commit()
        await session.refresh(registry)

    return {"doc_id": doc_id, "chunks_indexed": len(ordered_chunk_ids), "faiss_path": faiss_path}
