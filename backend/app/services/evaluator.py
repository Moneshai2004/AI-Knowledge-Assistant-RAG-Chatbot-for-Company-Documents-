# backend/app/services/evaluator.py

import os
import json
import time
from datetime import datetime

from app.db.session import async_session
from app.models.models import Evaluation
from app.core.rag_engine import hybrid_search_db, build_context
from app.core.llm import generate_answer

EVAL_DIR = "data/eval"
DATASET_PATH = os.path.join(EVAL_DIR, "dataset.json")


# ----------------------------------------
# Load evaluation dataset
# ----------------------------------------
def load_eval_dataset():
    if not os.path.exists(DATASET_PATH):
        return []

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # expected format:
    # [
    #   {"question": "...", "expected": "..."},
    #   ...
    # ]
    return data


# ----------------------------------------
# VERY SIMPLE scoring
# ----------------------------------------
def score_answer(pred: str, expected: str) -> float:
    if not pred or not expected:
        return 0.0

    pred_low = pred.lower()
    exp_low = expected.lower()

    # 1) exact match bonus
    if pred_low.strip() == exp_low.strip():
        return 1.0

    # 2) partial match (word overlap)
    pred_words = set(pred_low.split())
    exp_words = set(exp_low.split())

    overlap = len(pred_words & exp_words)
    total = len(exp_words)

    if total == 0:
        return 0.0

    return overlap / total


# ----------------------------------------
# RUN FULL EVALUATION JOB
# ----------------------------------------
async def run_evaluation_job():
    dataset = load_eval_dataset()
    if not dataset:
        print("[EVAL] No evaluation dataset found.")
        return

    print(f"[EVAL] Running evaluation for {len(dataset)} questions…")

    results = []
    total_score = 0
    start_time = time.time()

    # ------------------------------------------------------
    # Loop through dataset
    # ------------------------------------------------------
    for item in dataset:
        question = item["question"]
        expected = item.get("expected", "")

        # 1) retrieve RAG chunks
        hits = await hybrid_search_db(question, top_k=5)
        context = build_context(hits, max_chars=1500)

        # 2) generate answer
        answer = await generate_answer(question, context)

        # 3) score answer
        s = score_answer(answer, expected)
        total_score += s

        results.append({
            "question": question,
            "expected": expected,
            "answer": answer,
            "score": s,
            "retrieved_chunks": hits,
        })

    avg_score = total_score / len(dataset)
    took = time.time() - start_time

    print(f"[EVAL] DONE — Avg Score={avg_score:.3f}  Time={took:.1f}s")

    # ------------------------------------------------------
    # Save to DB
    # ------------------------------------------------------
    ev = Evaluation(
        name=f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        params={"dataset_size": len(dataset)},
        results={
            "overall_score": avg_score,
            "details": results,
            "time_sec": took,
        }
    )

    async with async_session() as session:
        session.add(ev)
        await session.commit()
        await session.refresh(ev)

    print(f"[EVAL] Saved evaluation id={ev.id}")

    return ev
