# backend/app/utils/faiss_store.py
import faiss
import os
import threading
import os

_LOCK = threading.Lock()

def save_faiss_index(index: faiss.Index, path: str):
    """Thread-safe save to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _LOCK:
        faiss.write_index(index, path)


def load_faiss_index(path: str, embed_dim: int = None):
    """
    Load a FAISS index safely.

    IMPORTANT:
    - embed_dim is OPTIONAL.
    - If the index file does not exist, return an empty IndexFlatIP(embed_dim).
    - If embed_dim is not provided, default to env EMBED_DIM or 768.
    """
    if os.path.exists(path):
        with _LOCK:
            return faiss.read_index(path)

    # If file does NOT exist → return empty FAISS index
    if embed_dim is None:
        embed_dim = int(os.getenv("EMBED_DIM", "768"))

    return faiss.IndexFlatIP(embed_dim)
