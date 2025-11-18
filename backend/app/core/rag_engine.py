# backend/app/core/rag_engine.py
"""
RAG engine helpers.

Provides:
- get_model(device)
- PDF loading: load_pdf_pages(...)
- Semantic-aware chunker: paragraph_split(...) and chunk_page_semantic(...)
- Legacy file-based helpers (load/save FAISS, metadata)
- Async DB-backed hybrid search: hybrid_search_db(...)
- Context builder: build_context(...)
"""

import os
import json
import re
import unicodedata
from typing import List, Dict, Optional
from datetime import datetime

import numpy as np
import faiss

# PDF libs - prefer PyMuPDF (fitz)
try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except Exception:
    _HAS_FITZ = False
    try:
        from PyPDF2 import PdfReader
    except Exception:
        PdfReader = None

from rank_bm25 import BM25Okapi

# -------------------------
# Config / paths
# -------------------------
DATA_DIR = os.getenv("RAG_DATA_DIR", "data")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
METADATA_PATH = os.path.join(DATA_DIR, "chunk_metadata.json")
BM25_CORPUS_PATH = os.path.join(DATA_DIR, "bm25_corpus.json")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))

os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# Embedding model (lazy)
# -------------------------
_embed_model = None
def get_model(device: Optional[str] = None):
    """
    Lazy-load sentence-transformers model (BAAI/bge-base-en by default).
    Pass device='cuda' or 'cpu' if needed.
    """
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-base-en")
        if device:
            _embed_model = SentenceTransformer(EMBED_MODEL_NAME, device=device)
        else:
            _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model

# -------------------------
# Tokenization / cleaning
# -------------------------
_token_cleanup_re = re.compile(r"\s+")
_word_re = re.compile(r"[a-zA-Z0-9\-]+")

def clean_and_tokenize(text: str) -> List[str]:
    """
    Clean text heuristics and produce tokens for BM25.
    """
    if not text:
        return []
    text = text.lower()
    # targeted fixes for broken PDFs
    replacements = {
        "comp ensation": "compensation",
        "d ecisions": "decisions",
        "abo ut": "about",
        "forme rly": "formerly",
        "inter nal": "internal",
        "exter nal": "external",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = _token_cleanup_re.sub(" ", text)
    tokens = _word_re.findall(text)
    # keep tokens with len > 2 or digits
    tokens = [t for t in tokens if len(t) > 2 or t.isdigit()]
    return tokens

# -------------------------
# PDF loading
# -------------------------
def load_pdf_pages(pdf_path: str) -> List[str]:
    """
    Return list of page texts. Uses PyMuPDF if available (faster), otherwise PyPDF2.
    """
    if _HAS_FITZ:
        doc = fitz.open(pdf_path)
        pages = [page.get_text() or "" for page in doc]
        doc.close()
        return pages
    else:
        if PdfReader is None:
            raise RuntimeError("No PDF backend available (install PyMuPDF or PyPDF2).")
        reader = PdfReader(pdf_path)
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        return pages

# -------------------------
# Chunker helpers
# -------------------------
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
MAX_PAGE_CHARS = int(os.getenv("RAG_MAX_PAGE_CHARS", "15000"))

def _fix_hyphenation(text: str) -> str:
    return re.sub(r'(\w)-\n(\w)', r'\1\2', text)

def _normalize_whitespace(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace('\r', '\n')
    text = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f]', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(lines).strip()

def _merge_wrapped_lines(text: str, min_line_len=40) -> str:
    lines = text.splitlines()
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            merged.append('')
            i += 1
            continue
        j = i + 1
        nxt = lines[j].strip() if j < len(lines) else ''
        is_heading = (len(line) < 80 and line.upper() == line and any(c.isalpha() for c in line)) or line.endswith(':')
        if not nxt:
            merged.append(line)
            i += 1
            continue
        if (len(line) < min_line_len and nxt and (nxt[0].islower() or len(nxt) > min_line_len)) and not is_heading:
            merged.append(line + ' ' + nxt)
            i += 2
            continue
        merged.append(line)
        i += 1
    return "\n".join(merged)

def paragraph_split(text: str) -> List[str]:
    """
    Split text into paragraphs, cleaning and merging wrapped lines.
    """
    text = _fix_hyphenation(text)
    text = _normalize_whitespace(text)
    text = _merge_wrapped_lines(text)
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras

def chunk_paragraphs_to_chunks(doc_id: str, page_no: int, paragraphs: List[str],
                               chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Build chunks from paragraph list. Long paragraphs are windowed; short paras combined.
    """
    chunks = []
    current = ""
    cursor = 0
    for para in paragraphs:
        if len(para) >= chunk_size:
            L = len(para)
            i = 0
            while i < L:
                start = i
                end = min(i + chunk_size, L)
                chunk_text = para[start:end]
                chunks.append({
                    "doc_id": doc_id,
                    "page": page_no,
                    "start_char": cursor + start,
                    "end_char": cursor + end,
                    "text": chunk_text
                })
                i = end - chunk_overlap
                if i <= start:
                    break
            cursor += L + 1
            current = ""
        else:
            if len(current) + 1 + len(para) <= chunk_size:
                if current:
                    current += "\n\n" + para
                else:
                    current = para
            else:
                if current:
                    chunks.append({
                        "doc_id": doc_id,
                        "page": page_no,
                        "start_char": cursor - len(current),
                        "end_char": cursor,
                        "text": current
                    })
                current = para
            cursor += len(para) + 1
    if current:
        chunks.append({
            "doc_id": doc_id,
            "page": page_no,
            "start_char": cursor - len(current),
            "end_char": cursor,
            "text": current
        })
    return chunks

def chunk_page_semantic(doc_id: str, page_no: int, text: str,
                        chunk_size: int = CHUNK_SIZE,
                        chunk_overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Chunk a single page using paragraph-aware logic.
    """
    if not text:
        return []
    if len(text) > MAX_PAGE_CHARS:
        text = text[:MAX_PAGE_CHARS]
    paras = paragraph_split(text)
    return chunk_paragraphs_to_chunks(doc_id, page_no, paras, chunk_size, chunk_overlap)

# -------------------------
# Persistence helpers (legacy file-based)
# -------------------------
def save_metadata(metadata: List[Dict]):
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def load_metadata() -> List[Dict]:
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_bm25_corpus(token_lists: List[List[str]]):
    with open(BM25_CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(token_lists, f, ensure_ascii=False, indent=2)

def load_bm25_corpus() -> List[List[str]]:
    if os.path.exists(BM25_CORPUS_PATH):
        with open(BM25_CORPUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_faiss_index(index: faiss.Index, path: str):
    faiss.write_index(index, path)

def load_faiss_index(path: Optional[str] = None) -> faiss.Index:
    p = path or FAISS_INDEX_PATH
    if os.path.exists(p):
        return faiss.read_index(p)
    return faiss.IndexFlatIP(EMBED_DIM)

# -------------------------
# Async DB-backed hybrid search
# -------------------------
async def hybrid_search_db(query: str, top_k: int = 5, alpha: float = 0.6,
                           model_device: Optional[str] = None) -> List[Dict]:
    """
    DB-backed hybrid search:
    - loads latest FaissIndexRegistry (via repo)
    - loads FAISS index file
    - fetches chunks (from chunks table) and builds BM25
    - runs FAISS + BM25 and returns aligned results (uses faiss_to_chunk_ids mapping if present)
    """
    # lazy imports to avoid circular startup issues
    try:
        from app.repos.repo_rag import get_latest_faiss
        from app.db.session import async_session
        from sqlmodel import select
        from app.models.models import Chunk
    except Exception:
        raise RuntimeError("Database layer imports failed. Ensure app.repos.repo_rag and app.db.session exist.")

    # 1) get registry
    registry = await get_latest_faiss()
    if not registry:
        # nothing indexed
        return []

    # registry might use different attribute names depending on your model version
    faiss_path = getattr(registry, "file_path", None) or getattr(registry, "faiss_path", None)
    index = load_faiss_index(faiss_path)

    # mapping: faiss_index_pos -> chunk_id (may be stored under many names)
    mapping = getattr(registry, "faiss_to_chunk_ids", None) \
              or getattr(registry, "faiss_to_chunk_id_map", None) \
              or getattr(registry, "faiss_to_chunk_id", None) \
              or getattr(registry, "chunk_ids", None) \
              or getattr(registry, "faiss_mapping", None) \
              or []

    # If mapping is falsy or empty, fallback to sequential chunk ids from DB
    if not mapping:
        async with async_session() as session:
            q = select(Chunk)
            result = await session.execute(q)
            rows = result.scalars().all()
        mapping = [r.id for r in rows]

    # 2) fetch chunk rows for all IDs in mapping
    async with async_session() as session:
        q = select(Chunk).where(Chunk.id.in_(mapping))
        result = await session.execute(q)
        rows = result.scalars().all()

    # Build id -> row map and ordered_chunks in same order as mapping
    id_to_row = {r.id: r for r in rows}
    ordered_chunks = []
    for cid in mapping:
        r = id_to_row.get(cid)
        if r:
            ordered_chunks.append({
                "id": r.id,
                "doc_id": r.doc_id,
                "page": getattr(r, "page", None),
                "start_char": getattr(r, "start_char", None),
                "end_char": getattr(r, "end_char", None),
                "text": r.text or ""
            })
        else:
            ordered_chunks.append({
                "id": cid,
                "doc_id": "unknown",
                "page": None,
                "start_char": None,
                "end_char": None,
                "text": ""
            })

    # BM25 corpus in the same order as mapping
    token_lists = [clean_and_tokenize(c["text"]) for c in ordered_chunks]
    bm25 = BM25Okapi(token_lists) if token_lists else None

    # semantic search (FAISS)
    model = get_model(device=model_device) if model_device is not None else get_model()
    q_emb = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    if index.ntotal == 0:
        sem_scores_map = {}
    else:
        D, I = index.search(q_emb, top_k)
        sem_idxs = [int(i) for i in I[0] if i >= 0]
        sem_scores_raw = [float(s) for s in D[0] if s is not None]
        sem_scores_map = {}
        if sem_scores_raw:
            smin, smax = min(sem_scores_raw), max(sem_scores_raw)
            denom = (smax - smin) if smax != smin else 1.0
            for idx_pos, raw_score in zip(sem_idxs, sem_scores_raw):
                if idx_pos < len(mapping):
                    chunk_id = mapping[idx_pos]
                    sem_scores_map[chunk_id] = (raw_score - smin) / denom

    # lexical (BM25) -> positions correspond to mapping positions
    lex_scores_map = {}
    if bm25 is not None:
        qtok = clean_and_tokenize(query)
        bm_scores = bm25.get_scores(qtok)
        top_bm_pos = np.argsort(bm_scores)[::-1][:top_k]
        if len(top_bm_pos) > 0:
            bm_vals = [float(bm_scores[i]) for i in top_bm_pos]
            bmin, bmax = min(bm_vals), max(bm_vals)
            denom = (bmax - bmin) if bmax != bmin else 1.0
            for pos in top_bm_pos:
                if pos < len(mapping):
                    chunk_id = mapping[int(pos)]
                    lex_scores_map[chunk_id] = (float(bm_scores[int(pos)]) - bmin) / denom

    # combine candidate chunk_ids
    candidate_chunk_ids = set(list(sem_scores_map.keys()) + list(lex_scores_map.keys()))
    results = []
    for cid in candidate_chunk_ids:
        s = sem_scores_map.get(cid, 0.0)
        b = lex_scores_map.get(cid, 0.0)
        final = float(alpha * s + (1.0 - alpha) * b)
        meta = next((c for c in ordered_chunks if c["id"] == cid), {"doc_id":"unknown","page":-1,"text":""})
        entry = {
            "chunk_id": cid,
            "doc_id": meta.get("doc_id"),
            "page": meta.get("page"),
            "start_char": meta.get("start_char"),
            "end_char": meta.get("end_char"),
            "text": meta.get("text"),
            "sem_score": float(s),
            "bm_score": float(b),
            "score": final
        }
        results.append(entry)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# -------------------------
# Legacy file-based hybrid (sync) - kept for local debugging
# -------------------------
def hybrid_search_legacy(query: str, top_k: int = 5, alpha: float = 0.6,
                         model_device: Optional[str] = None) -> List[Dict]:
    metadata = load_metadata()
    token_lists = load_bm25_corpus()
    index = load_faiss_index()
    bm25 = BM25Okapi(token_lists) if token_lists else None

    model = get_model(device=model_device) if model_device is not None else get_model()
    q_emb = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    if index.ntotal == 0:
        sem_idxs = []
        sem_scores_map = {}
    else:
        D, I = index.search(q_emb, top_k)
        sem_idxs = [int(i) for i in I[0] if i >= 0]
        sem_scores_raw = [float(s) for s in D[0] if s is not None]
        if sem_scores_raw:
            smin, smax = min(sem_scores_raw), max(sem_scores_raw)
            denom = (smax - smin) if smax != smin else 1.0
            sem_scores_map = {idx: (score - smin) / denom for idx, score in zip(sem_idxs, sem_scores_raw)}
        else:
            sem_scores_map = {}

    lex_scores_map = {}
    if bm25 is not None:
        qtok = clean_and_tokenize(query)
        bm_scores = bm25.get_scores(qtok)
        top_bm_idx = np.argsort(bm_scores)[::-1][:top_k]
        if len(top_bm_idx) > 0:
            bm_vals = [float(bm_scores[i]) for i in top_bm_idx]
            bmin, bmax = min(bm_vals), max(bm_vals)
            denom = (bmax - bmin) if bmax != bmin else 1.0
            for i in top_bm_idx:
                lex_scores_map[int(i)] = (float(bm_scores[i]) - bmin) / denom

    candidate_idxs = set(list(sem_scores_map.keys()) + list(lex_scores_map.keys()))
    results = []
    for idx in candidate_idxs:
        s = sem_scores_map.get(idx, 0.0)
        b = lex_scores_map.get(idx, 0.0)
        final = float(alpha * s + (1.0 - alpha) * b)
        meta = metadata[idx] if idx < len(metadata) else {"doc_id":"unknown","page":-1,"text":""}
        entry = {
            "idx": idx,
            "doc_id": meta.get("doc_id"),
            "page": meta.get("page"),
            "start_char": meta.get("start_char"),
            "end_char": meta.get("end_char"),
            "text": meta.get("text"),
            "sem_score": float(s),
            "bm_score": float(b),
            "score": final
        }
        results.append(entry)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# -------------------------
# Context builder
# -------------------------
def build_context(chunks: List[Dict], max_chars: int = 4000) -> str:
    parts = []
    total = 0
    for c in chunks:
        header = f"[DOC: {c.get('doc_id')} | page {c.get('page')} | chars {c.get('start_char')}:{c.get('end_char')} | score {c.get('score',0):.3f}]\n"
        body = c.get("text", "").strip()
        block = header + body + "\n[---end---]\n"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining <= 0:
                break
            parts.append(block[:remaining])
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts)


if __name__ == "__main__":
    print("RAG engine module.")
