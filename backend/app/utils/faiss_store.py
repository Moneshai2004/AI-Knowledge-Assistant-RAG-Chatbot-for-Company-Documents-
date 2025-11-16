# backend/app/utils/faiss_store.py
import faiss
import os
import threading

_LOCK = threading.Lock()

def save_faiss_index(index: faiss.Index, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _LOCK:
        faiss.write_index(index, path)

def load_faiss_index(path: str, embed_dim: int):
    if not os.path.exists(path):
        # create new
        return faiss.IndexFlatIP(embed_dim)
    with _LOCK:
        return faiss.read_index(path)
