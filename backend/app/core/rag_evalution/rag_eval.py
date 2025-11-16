# rag_eval.py -- Part 1 (core metrics + runner)
import rag_engine
import json
import argparse
from typing import List, Callable, Dict, Any, Tuple
import math
import os
from rag_engine import load_metadata, load_bm25_corpus, load_faiss_index

print("metadata len =", len(load_metadata()))
print("bm25 len =", len(load_bm25_corpus()))
index = load_faiss_index()
print("faiss vectors =", index.ntotal)


# ----------------------------
# Metrics implementations
# ----------------------------
def precision_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    if k <= 0:
        return 0.0
    topk = retrieved[:k]
    if not topk:
        return 0.0
    num_rel = sum(1 for r in topk if r in relevant)
    return num_rel / float(len(topk))

def recall_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    if not relevant:
        return 0.0
    topk = set(retrieved[:k])
    found = sum(1 for r in relevant if r in topk)
    return found / float(len(relevant))

def mrr_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    topk = retrieved[:k]
    for rank, docid in enumerate(topk, start=1):
        if docid in relevant:
            return 1.0 / rank
    return 0.0

def r_precision(retrieved: List[int], relevant: List[int]) -> float:
    # R-Precision: precision at R where R = number of relevant docs
    R = len(relevant)
    if R == 0:
        return 0.0
    return precision_at_k(retrieved, relevant, R)

# ----------------------------
# Evaluate a single query
# ----------------------------
def evaluate_query(query_entry: Dict[str, Any],
                   retriever: Callable[[str, int, float], List[Dict[str, Any]]],
                   top_k: int = 10,
                   alpha: float = 0.6) -> Dict[str, float]:
    """
    query_entry example:
      {
        "query": "...",
        "answer": "...",
        "expected_chunk_ids": [12, 15]
      }
    retriever(query, top_k=..., alpha=...) -> list of result dicts with field 'idx' (the chunk index)
    """
    q = query_entry["query"]
    expected = query_entry.get("expected_chunk_ids", [])
    # call retriever (semantic/hybrid) - retriever must return list of dicts with 'idx'
    results = retriever(q, top_k=top_k, alpha=alpha)
    retrieved_ids = [r["idx"] for r in results]

    # compute metrics
    metrics = {
        "precision@1": precision_at_k(retrieved_ids, expected, 1),
        "precision@5": precision_at_k(retrieved_ids, expected, 5),
        "precision@10": precision_at_k(retrieved_ids, expected, 10),
        "recall@1": recall_at_k(retrieved_ids, expected, 1),
        "recall@5": recall_at_k(retrieved_ids, expected, 5),
        "recall@10": recall_at_k(retrieved_ids, expected, 10),
        "mrr@10": mrr_at_k(retrieved_ids, expected, 10),
        "r_precision": r_precision(retrieved_ids, expected)
    }
    return metrics

# ----------------------------
# Evaluate entire dataset
# ----------------------------
def evaluate_dataset(dataset: List[Dict[str, Any]],
                     retriever: Callable[[str, int, float], List[Dict[str, Any]]],
                     top_k: int = 10,
                     alpha: float = 0.6) -> Dict[str, float]:
    """
    Returns aggregated (mean) metrics across dataset.
    """
    agg = {k: 0.0 for k in ["precision@1","precision@5","precision@10",
                            "recall@1","recall@5","recall@10","mrr@10","r_precision"]}
    n = len(dataset)
    if n == 0:
        return {k: 0.0 for k in agg}
    for entry in dataset:
        m = evaluate_query(entry, retriever, top_k=top_k, alpha=alpha)
        for k, v in m.items():
            agg[k] += v
    # mean
    for k in agg:
        agg[k] /= float(n)
    return agg

# ----------------------------
# Small helper: load eval dataset (json)
# ----------------------------
def load_eval_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# ----------------------------
# CLI: run evaluation
# ----------------------------
def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-file", type=str, default="eval_dataset.json",
                        help="Path to evaluation JSON file (list of query objects).")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--alpha", type=float, default=0.6, help="Alpha for hybrid retriever when used.")
    parser.add_argument("--run-eval", action="store_true", help="Execute evaluation using retrievers from rag_engine.")
    parser.add_argument("--mode", choices=["semantic","hybrid"], default="hybrid",
                        help="Which retriever to evaluate: semantic only or hybrid.")
    args = parser.parse_args()

    if not args.run_eval:
        print("No action. Use --run-eval to execute evaluation.")
        return

    # lazy import of your rag engine to avoid heavy imports when module is loaded
    try:
        import rag_engine
    except Exception as e:
        print("Failed to import rag_engine.py from the current directory:", e)
        return

    data = load_eval_file(args.eval_file)
    # choose retriever wrapper
    if args.mode == "hybrid":
        retriever = lambda q, top_k, alpha: rag_engine.hybrid_search(q, top_k=top_k, alpha=alpha)
    else:
        # semantic-only wrapper: call hybrid_search with alpha=1.0 (pure semantic) OR directly use faiss search if you have one.
        retriever = lambda q, top_k, alpha: rag_engine.hybrid_search(q, top_k=top_k, alpha=1.0)

    agg = evaluate_dataset(data, retriever, top_k=args.top_k, alpha=args.alpha)
    print("=== Evaluation summary ===")
    for k, v in agg.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    cli_main()
