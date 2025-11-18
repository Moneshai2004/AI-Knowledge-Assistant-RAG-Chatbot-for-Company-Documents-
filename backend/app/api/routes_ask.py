# backend/app/api/routes_ask.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.rag_engine import hybrid_search_db, build_context
from app.core.llm import generate_answer

router = APIRouter(prefix="", tags=["Ask"])

class Query(BaseModel):
    question: str

@router.post("/ask")
async def ask(query: Query):
    try:
        hits = await hybrid_search_db(query.question, top_k=5, alpha=0.1)
        context = build_context(hits, max_chars=1500)
        answer = await generate_answer(query.question, context)
        return {"question": query.question, "answer": answer, "sources": hits}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
