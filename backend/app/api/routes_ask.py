import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.rag_engine import hybrid_search_db, build_context
from app.core.llm import generate_answer
from app.db.session import async_session
from sqlmodel import select
from app.models.models import Document

router = APIRouter(prefix="", tags=["Ask"])


class Query(BaseModel):
    question: str


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
        answer = await generate_answer(query.question, context)

        return {
            "question": query.question,
            "answer": answer,
            "sources": enriched,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
