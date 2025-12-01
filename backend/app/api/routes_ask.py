import os
import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from app.core.rag_engine import hybrid_search_db, build_context
from app.db.session import async_session
from app.models.models import Document
from app.services import lora_loader


# ----------------------------
# FastAPI Router
# ----------------------------
router = APIRouter(prefix="", tags=["Ask"])


class Query(BaseModel):
    question: str


# ----------------------------
# LoRA Inference
# ----------------------------
def generate_with_lora(question: str, context: str) -> str:
    model = lora_loader.model
    tokenizer = lora_loader.tokenizer

    if model is None or tokenizer is None:
        return "ERROR: LoRA not loaded."

    prompt = f"""
### Instruction:
Answer the question using ONLY the provided context.

### Input:
Context:
{context}

Question:
{question}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "### Response:" in result:
        return result.split("### Response:")[-1].strip()

    return result.strip()


# ----------------------------
# Ask API
# ----------------------------
@router.post("/ask/")
async def ask(query: Query):
    try:
        # --- RAG Search ---
        hits = await hybrid_search_db(query.question, top_k=5, alpha=0.1)

        doc_ids = {h.get("doc_id") for h in hits if h.get("doc_id")}
        doc_map = {}

        if doc_ids:
            async with async_session() as session:
                stmt = select(Document).where(Document.doc_id.in_(doc_ids))
                res = await session.execute(stmt)
                docs = res.scalars().all()
            for d in docs:
                doc_map[d.doc_id] = os.path.basename(d.file_path)

        # --- Format sources ---
        enriched = []
        for h in hits:
            snippet = (h.get("text") or "").replace("\n", " ").strip()
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            enriched.append({
                "chunk_id": h.get("chunk_id"),
                "doc_id": h.get("doc_id"),
                "page": h.get("page"),
                "text": snippet,
                "file_name": doc_map.get(h.get("doc_id")),
                "score": h.get("score"),
            })

        # --- Build RAG context ---
        context = build_context(hits, max_chars=1500)

        # --- Generate using LoRA ---
        answer = generate_with_lora(query.question, context)

        return {
            "question": query.question,
            "answer": answer,
            "sources": enriched,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
