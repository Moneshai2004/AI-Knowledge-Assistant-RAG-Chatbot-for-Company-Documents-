#!/usr/bin/env python3
"""
Retrieval evaluation harness for the AI HR Policy Assistant.

Measures retrieval quality (not answer quality) of the hybrid FAISS + BM25
retriever against a hand-labelled query set, using standard IR metrics.

Usage, from the repository root:

    python eval/rag_eval.py --mode hybrid
    python eval/rag_eval.py --mode semantic
    python eval/rag_eval.py --mode bm25
    python eval/rag_eval.py --sweep-alpha          # find the best fusion weight
    python eval/rag_eval.py --mode hybrid --json results.json

The query set (eval/eval_dataset.json) is hand-labelled: each query names the
chunk id(s) that actually contain the answer. Metrics are averaged over queries.
"""

import argparse
import json
import os
import sys
from typing import Any, Callable, Dict, List

# --- make `app.*` importable regardless of where this is run from -------------
REPO_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
BACKEND = os.path.join(REPO_ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

DEFAULT_DATASET = os.path.join(REPO_ROOT, "eval", "eval_dataset.json")


# --- metrics ------------------------------------------------------------------
def precision_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    topk = retrieved[:k]
    if not topk:
        return 0.0
    return sum(1 for r in topk if r in relevant) / float(len(topk))


def recall_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    if not relevant:
        return 0.0
    topk = set(retrieved[:k])
    return sum(1 for r in relevant if r in topk) / float(len(relevant))


def mrr_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    for rank, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def hit_rate_at_k(retrieved: List[int], relevant: List[int], k: int) -> float:
    return 1.0 if any(r in relevant for r in retrieved[:k]) else 0.0


def r_precision(retrieved: List[int], relevant: List[int]) -> float:
    R = len(relevant)
    return precision_at_k(retrieved, relevant, R) if R else 0.0


METRIC_KEYS = [
    "precision@1", "precision@3", "precision@5",
    "recall@1", "recall@3", "recall@5", "recall@10",
    "mrr@10", "hit_rate@1", "hit_rate@3", "hit_rate@5", "r_precision",
]


def evaluate_query(entry: Dict[str, Any], retriever: Callable, top_k: int) -> Dict[str, float]:
    gold = entry.get("expected_chunk_ids", [])
    retrieved = [r["idx"] for r in retriever(entry["query"], top_k)]
    return {
        "precision@1": precision_at_k(retrieved, gold, 1),
        "precision@3": precision_at_k(retrieved, gold, 3),
        "precision@5": precision_at_k(retrieved, gold, 5),
        "recall@1": recall_at_k(retrieved, gold, 1),
        "recall@3": recall_at_k(retrieved, gold, 3),
        "recall@5": recall_at_k(retrieved, gold, 5),
        "recall@10": recall_at_k(retrieved, gold, 10),
        "mrr@10": mrr_at_k(retrieved, gold, 10),
        "hit_rate@1": hit_rate_at_k(retrieved, gold, 1),
        "hit_rate@3": hit_rate_at_k(retrieved, gold, 3),
        "hit_rate@5": hit_rate_at_k(retrieved, gold, 5),
        "r_precision": r_precision(retrieved, gold),
    }


def evaluate_dataset(dataset: List[Dict[str, Any]], retriever: Callable, top_k: int) -> Dict[str, float]:
    agg = {k: 0.0 for k in METRIC_KEYS}
    if not dataset:
        return agg
    for entry in dataset:
        for k, v in evaluate_query(entry, retriever, top_k).items():
            agg[k] += v
    return {k: v / len(dataset) for k, v in agg.items()}


def make_retriever(mode: str, alpha: float) -> Callable:
    """
    mode 'semantic' -> alpha 1.0 (dense only)
    mode 'bm25'     -> alpha 0.0 (lexical only)
    mode 'hybrid'   -> the given alpha
    """
    from app.core.rag_engine import hybrid_search_legacy

    effective = {"semantic": 1.0, "bm25": 0.0}.get(mode, alpha)
    return lambda q, k: hybrid_search_legacy(q, top_k=k, alpha=effective)


def print_table(rows: List[tuple]) -> None:
    width = max(len(str(r[0])) for r in rows) + 2
    for label, metrics in rows:
        print(f"\n  {str(label):<{width}}")
        for k in METRIC_KEYS:
            print(f"    {k:<14} {metrics[k]:.3f}")


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate retrieval quality.")
    p.add_argument("--dataset", default=DEFAULT_DATASET)
    p.add_argument("--mode", choices=["hybrid", "semantic", "bm25"], default="hybrid")
    p.add_argument("--alpha", type=float, default=0.6,
                   help="Fusion weight: final = alpha*semantic + (1-alpha)*bm25")
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--sweep-alpha", action="store_true",
                   help="Evaluate alpha from 0.0 to 1.0 and report the best by MRR@10")
    p.add_argument("--json", dest="json_out", default=None, help="Write results to this JSON file")
    args = p.parse_args()

    with open(args.dataset, encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Query set: {args.dataset}  ({len(dataset)} hand-labelled queries)")

    results: Dict[str, Dict[str, float]] = {}

    if args.sweep_alpha:
        print(f"Sweeping alpha at top_k={args.top_k}…\n")
        print(f"  {'alpha':>6}  {'MRR@10':>8}  {'Recall@5':>9}  {'HitRate@3':>10}")
        best = (None, -1.0)
        for i in range(11):
            a = i / 10.0
            m = evaluate_dataset(dataset, make_retriever("hybrid", a), args.top_k)
            results[f"alpha={a:.1f}"] = m
            print(f"  {a:>6.1f}  {m['mrr@10']:>8.3f}  {m['recall@5']:>9.3f}  {m['hit_rate@3']:>10.3f}")
            if m["mrr@10"] > best[1]:
                best = (a, m["mrr@10"])
        print(f"\n  Best alpha by MRR@10: {best[0]:.1f}  (MRR@10 = {best[1]:.3f})")
    else:
        rows = []
        for mode in (["semantic", "bm25", "hybrid"] if args.mode == "hybrid" else [args.mode]):
            m = evaluate_dataset(dataset, make_retriever(mode, args.alpha), args.top_k)
            label = f"{mode}" + (f" (alpha={args.alpha})" if mode == "hybrid" else "")
            results[label] = m
            rows.append((label, m))
        print_table(rows)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nWrote {args.json_out}")


if __name__ == "__main__":
    main()
