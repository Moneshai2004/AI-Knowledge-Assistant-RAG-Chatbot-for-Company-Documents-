# backend/app/repos/repo_rag.py
from typing import List, Optional
from sqlmodel import select
from app.db.session import async_session
from app.models.models import Document, Chunk, FaissIndexRegistry, QueryLog, Evaluation

async def create_document(doc: Document) -> Document:
    async with async_session() as session:
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc

async def bulk_insert_chunks(chunks: List[Chunk]) -> int:
    async with async_session() as session:
        session.add_all(chunks)
        await session.commit()
        return len(chunks)

async def create_faiss_registry(reg: FaissIndexRegistry) -> FaissIndexRegistry:
    async with async_session() as session:
        session.add(reg)
        await session.commit()
        await session.refresh(reg)
        return reg

async def get_latest_faiss() -> Optional[FaissIndexRegistry]:
    async with async_session() as session:
        q = select(FaissIndexRegistry).order_by(FaissIndexRegistry.created_at.desc()).limit(1)
        res = await session.execute(q)
        return res.scalars().first()

async def log_query(qtext: str, returned_chunk_ids: List[int], user_id: Optional[str], response_time_ms: Optional[int]=None):
    q = QueryLog(query_text=qtext, returned_chunk_ids=returned_chunk_ids, user_id=user_id, response_time_ms=response_time_ms)
    async with async_session() as session:
        session.add(q)
        await session.commit()
        await session.refresh(q)
        return q

async def save_evaluation(ev: Evaluation):
    async with async_session() as session:
        session.add(ev)
        await session.commit()
        await session.refresh(ev)
        return ev
