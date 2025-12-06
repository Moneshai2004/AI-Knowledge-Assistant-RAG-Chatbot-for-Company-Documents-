import os
import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from app.core.rag_engine import hybrid_search_db, build_context
from app.db.session import async_session
from app.models.models import Document
import app.services.lora_loader as lora


router = APIRouter(prefix="", tags=["Ask"])


class Query(BaseModel):
    question: str


def generate_with_lora(question: str, context: str) -> str:
    model, tokenizer = lora.get_lora_model()

    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="LoRA not loaded")

    prompt = (
        "You are an assistant that answers using ONLY the provided context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    device = next(model.parameters()).device

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
        padding=True,
    )

    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)    # FIXED

    output_ids = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.2,
        no_repeat_ngram_size=3,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    )

    # remove prompt
    generated = output_ids[0, input_ids.shape[1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()

    # Clean up GPT-2 repeating "Answer:"
    if text.lower().startswith("answer:"):
        text = text[7:].strip()

    return text


@router.post("/ask/")
async def ask(query: Query):
    try:
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

        context = build_context(hits, max_chars=1500)
        answer = generate_with_lora(query.question, context)

        return {
            "question": query.question,
            "answer": answer,
            "sources": enriched,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
