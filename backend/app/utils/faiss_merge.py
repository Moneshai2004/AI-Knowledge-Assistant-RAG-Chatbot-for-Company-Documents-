# backend/app/utils/faiss_merge.py

import faiss
import numpy as np
from typing import List, Optional
from app.utils.faiss_store import load_faiss_index, save_faiss_index


def merge_faiss_indexes(index_paths: List[str]) -> Optional[faiss.Index]:
    """
    Merge multiple FAISS IndexFlatIP indexes into a single IndexFlatIP.
    Returns the merged index (in memory) or None on failure.
    """
    if not index_paths:
        return None

    # load first index as base
    base = load_faiss_index(index_paths[0])
    if base is None:
        return None

    for p in index_paths[1:]:
        idx = load_faiss_index(p)
        if idx is None:
            print(f"[MERGE] Warning: failed to load {p}, skipping.")
            continue

        # reconstruct all vectors from idx and add to base
        if idx.ntotal == 0:
            continue
        # reconstruct_n might not be implemented on some index types;
        # use a safe loop fallback
        try:
            xb = idx.reconstruct_n(0, idx.ntotal)
        except Exception:
            # fallback: iterate
            xb = np.zeros((idx.ntotal, base.d), dtype="float32")
            for i in range(idx.ntotal):
                xb[i] = idx.reconstruct(i)
        base.add(xb)

    return base
