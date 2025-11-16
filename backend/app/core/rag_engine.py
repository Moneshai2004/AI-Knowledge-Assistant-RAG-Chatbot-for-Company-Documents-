"""
rag_engine.py
Robust, low-RAM Hybrid RAG engine (FAISS + BM25) with metadata & provenance.

Usage:
- build_index_from_pdf(pdf_path, doc_id)   # builds index and saves files in DATA_DIR
- load_index_files()                       # loads FAISS + metadata + BM25 into memory
- hybrid_search(query, top_k=5, alpha=0.6) # returns top chunks with provenance
- build_context(chunks, limit=1500)        # returns context string suitable for prompt

Files produced/loaded:
- data/faiss.index
- data/chunk_metadata.json
- data/bm25_corpus.json
"""

import os
import json
import re
from typing import List, Dict, Tuple, Optional

import numpy as np
import faiss

# try fast PDF lib first
try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except Exception:
    _HAS_FITZ = False
    from PyPDF2 import PdfReader

from rank_bm25 import BM25Okapi

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-base-en")

# Data files
DATA_DIR = os.getenv("RAG_DATA_DIR", "data")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
METADATA_PATH = os.path.join(DATA_DIR, "chunk_metadata.json")
BM25_CORPUS_PATH = os.path.join(DATA_DIR, "bm25_corpus.json")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))  # default for these MiniLM models

os.makedirs(DATA_DIR, exist_ok=True)

import re

_token_cleanup_re = re.compile(r"\s+")
_word_re = re.compile(r"[a-zA-Z0-9\-]+")

def clean_and_tokenize(text: str) -> List[str]:
    """
    Clean noisy HR PDF text and return high-quality tokens for BM25.
    """
    text = text.lower()

    # Fix broken words (remove weird spaces)
    text = text.replace("comp ensation", "compensation")
    text = text.replace("d ecisions", "decisions")
    text = text.replace("abo ut", "about")
    text = text.replace("forme rly", "formerly")
    text = text.replace("inter nal", "internal")
    text = text.replace("exter nal", "external")

    # Remove extra whitespace
    text = _token_cleanup_re.sub(" ", text)

    # Extract clean tokens
    tokens = _word_re.findall(text)

    # Filter out meaningless tokens
    tokens = [
        t for t in tokens
        if len(t) > 2 or t.isdigit()  # keep digits (CIN/address) but remove tiny garbage
    ]

    return tokens

_embed_model = None
def get_model(device: Optional[str] = None):
    """
    Lazy load the SentenceTransformer model. Optionally pass device='cuda' or 'cpu'.
    Example: get_model('cuda')
    """
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        if device:
            _embed_model = SentenceTransformer(EMBED_MODEL_NAME, device=device)
        else:
            _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model

# ------------------------
# PDF loading utilities
# ------------------------
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
        reader = PdfReader(pdf_path)
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        return pages

# ------------------------
# Safe chunker (per page)
# ------------------------
# sensible defaults (tweakable)
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
MAX_PAGE_CHARS = int(os.getenv("RAG_MAX_PAGE_CHARS", "15000"))  # cap to avoid pathological pages

def chunk_page_safe(doc_id: str, page_no: int, text: str,
                    chunk_size: int = CHUNK_SIZE,
                    chunk_overlap: int = CHUNK_OVERLAP,
                    max_page_chars: int = MAX_PAGE_CHARS) -> List[Dict]:
    """
    Chunk a single page into metadata dicts.
    Ensures no infinite loops and truncates extremely large pages.
    """
    if not text:
        return []
    if len(text) > max_page_chars:
        text = text[:max_page_chars]

    chunks = []
    L = len(text)
    i = 0
    while i < L:
        start = i
        end = min(i + chunk_size, L)
        chunk_text = text[start:end]

        chunks.append({
            "doc_id": doc_id,
            "page": page_no,
            "start_char": start,
            "end_char": end,
            "text": chunk_text
        })

        # compute next index and prevent infinite loop
        next_i = end - chunk_overlap
        if next_i <= start:
            # page too short or overlap too large -> stop to avoid loop
            break
        i = next_i
    return chunks

# ------------------------
# Persistence utilities
# ------------------------
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

def save_faiss_index(index: faiss.Index):
    faiss.write_index(index, FAISS_INDEX_PATH)

def load_faiss_index() -> faiss.Index:
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    # create new index (IP with normalized embeddings acts like cosine)
    return faiss.IndexFlatIP(EMBED_DIM)

# ------------------------
# Build index (streaming, low-RAM)
# ------------------------
def build_index_from_pdf(pdf_path: str, doc_id: str, model_device: Optional[str] = None) -> Dict:
    """
    Build or append to FAISS + BM25 from a PDF.
      - pdf_path: path to PDF
      - doc_id: arbitrary identifier for the document
      - model_device: optional 'cuda' or 'cpu' override for get_model()
    Returns summary dict.
    """
    print(">>> build_index_from_pdf:", pdf_path, "doc_id:", doc_id)
    pages = load_pdf_pages(pdf_path)
    print(f">>> PDF pages: {len(pages)}")

    metadata = load_metadata()
    bm25_token_lists = load_bm25_corpus()
    index = load_faiss_index()
    model = get_model(device=model_device) if model_device is not None else get_model()

    new_chunks = 0
    for page_no, page_text in enumerate(pages):
        page_chunks = chunk_page_safe(doc_id, page_no, page_text)
        print(f"  - page {page_no} -> {len(page_chunks)} chunks")
        for meta in page_chunks:
            chunk_text = meta["text"]
            # token for BM25
            bm25_token_lists.append(clean_and_tokenize(chunk_text)
)
            # embed one chunk at a time to avoid memory spikes
            emb = model.encode([chunk_text], normalize_embeddings=True, convert_to_numpy=True)
            emb = emb.astype("float32")
            index.add(emb)  # add to faiss
            metadata.append(meta)
            new_chunks += 1

    # rebuild BM25 object and persist everything
    bm25 = BM25Okapi(bm25_token_lists)
    save_metadata(metadata)
    save_bm25_corpus(bm25_token_lists)
    save_faiss_index(index)

    print(f">>> Indexing done. added_chunks={new_chunks} total_chunks={len(metadata)}")
    return {"added_chunks": new_chunks, "total_chunks": len(metadata)}

# ------------------------
# Load prebuilt files (convenience)
# ------------------------
def load_index_files():
    """
    Ensure FAISS + metadata + BM25 are loadable.
    Returns tuple (index, metadata_list, bm25_object)
    """
    metadata = load_metadata()
    token_lists = load_bm25_corpus()
    index = load_faiss_index()
    bm25 = BM25Okapi(token_lists) if token_lists else None
    return index, metadata, bm25

# ------------------------
# Hybrid retrieval
# ------------------------
def hybrid_search(query: str, top_k: int = 5, alpha: float = 0.6,
                  model_device: Optional[str] = None) -> List[Dict]:
    """
    Hybrid retrieval:
      - semantic via FAISS (inner product on normalized embeddings)
      - lexical via BM25
      - final_score = alpha * sem_norm + (1-alpha) * bm_norm
    Returns list of metadata dicts augmented with fields: score, sem_score, bm_score
    """
    metadata = load_metadata()
    token_lists = load_bm25_corpus()
    index = load_faiss_index()

    # BM25 instance
    bm25 = BM25Okapi(token_lists) if token_lists else None

    # semantic
    model = get_model(device=model_device) if model_device is not None else get_model()
    q_emb = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    if index.ntotal == 0:
        sem_idxs = []
        sem_scores_map = {}
    else:
        D, I = index.search(q_emb, top_k)
        sem_idxs = [int(i) for i in I[0] if i >= 0]
        sem_scores_raw = [float(s) for s in D[0] if s is not None]
        # normalize sem scores to 0..1
        if sem_scores_raw:
            smin, smax = min(sem_scores_raw), max(sem_scores_raw)
            denom = (smax - smin) if smax != smin else 1.0
            sem_scores_map = {idx: (score - smin) / denom for idx, score in zip(sem_idxs, sem_scores_raw)}
        else:
            sem_scores_map = {}

    # lexical (BM25)
    lex_scores_map = {}
    if bm25 is not None:
        qtok = clean_and_tokenize(query)
        bm_scores = bm25.get_scores(qtok)  # vector of scores
        # pick top_k lex candidates
        top_bm_idx = np.argsort(bm_scores)[::-1][:top_k]
        if len(top_bm_idx) > 0:
            bm_vals = [float(bm_scores[i]) for i in top_bm_idx]
            bmin, bmax = min(bm_vals), max(bm_vals)
            denom = (bmax - bmin) if bmax != bmin else 1.0
            for i in top_bm_idx:
                lex_scores_map[int(i)] = (float(bm_scores[i]) - bmin) / denom

    # combine candidates
    candidate_idxs = set(list(sem_scores_map.keys()) + list(lex_scores_map.keys()))
    results = []
    for idx in candidate_idxs:
        s = sem_scores_map.get(idx, 0.0)
        b = lex_scores_map.get(idx, 0.0)
        final = float(alpha * s + (1.0 - alpha) * b)
        meta = metadata[idx] if idx < len(metadata) else {"doc_id": "unknown", "page": -1, "text": ""}
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

# ------------------------
# Context builder for prompt
# ------------------------
def build_context(chunks: List[Dict], max_chars: int = 1500) -> str:
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

# ------------------------
# Convenience main for manual testing
# ------------------------
if __name__ == "__main__":
    # quick local test driver (no heavy defaults executed on import)
    print("RAG engine module. Use build_index_from_pdf(...) or hybrid_search(...).")
    # Example (commented): uncomment to run manually:
    # build_index_from_pdf("data/mydoc.pdf", doc_id="mydoc", model_device="cuda")
    # print(hybrid_search("what is the leave policy?", top_k=3))
