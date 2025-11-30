from fastapi import APIRouter, Depends, Query
from sqlmodel import select, func
from app.db.session import async_session
from app.models.models import QueryLog, Chunk, Document, FaissIndexRegistry
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin/stats", tags=["Admin Stats"])

# ----------------------------------------------------
# SUMMARY STATS
# ----------------------------------------------------
@router.get("/summary")
async def get_summary():
    async with async_session() as session:

        # total documents
        docs_q = select(func.count()).select_from(Document)
        docs = (await session.execute(docs_q)).scalar()

        # total chunks
        chunks_q = select(func.count()).select_from(Chunk)
        chunks = (await session.execute(chunks_q)).scalar()

        # total queries ever
        q_total = select(func.count()).select_from(QueryLog)
        total_queries = (await session.execute(q_total)).scalar()

        # queries today
        today = datetime.utcnow().date()
        q_today = select(func.count()).select_from(QueryLog)\
            .where(func.date(QueryLog.timestamp) == today)
        today_queries = (await session.execute(q_today)).scalar()

        # faiss index count
        faiss_q = select(func.count()).select_from(FaissIndexRegistry)
        faiss_count = (await session.execute(faiss_q)).scalar()

        # latest index date
        latest_index = await session.execute(
            select(FaissIndexRegistry)
            .order_by(FaissIndexRegistry.created_at.desc())
            .limit(1)
        )
        latest = latest_index.scalar()

        return {
            "total_documents": docs,
            "total_chunks": chunks,
            "total_queries": total_queries,
            "queries_today": today_queries,
            "faiss_index_count": faiss_count,
            "latest_index_date": latest.created_at if latest else None,
        }

# ----------------------------------------------------
# QUERIES PER DAY (last 14 days)
# ----------------------------------------------------
@router.get("/queries-per-day")
async def queries_per_day(days: int = 14):
    async with async_session() as session:

        cutoff = datetime.utcnow() - timedelta(days=days)

        q = await session.execute(
            select(
                func.date(QueryLog.timestamp).label("day"),
                func.count().label("count")
            )
            .where(QueryLog.timestamp >= cutoff)
            .group_by(func.date(QueryLog.timestamp))
            .order_by(func.date(QueryLog.timestamp))
        )

        items = [
            {"day": str(row.day), "count": row.count}
            for row in q.all()
        ]

        return items

# ----------------------------------------------------
# TOP DOCUMENTS used in answers
# ----------------------------------------------------
@router.get("/top-documents")
async def top_documents(limit: int = 5):
    async with async_session() as session:

        # join QueryLog → Chunk → Document
        q = await session.execute(
            select(
                Document.doc_id,
                Document.file_path,
                func.count().label("hits")
            )
            .join(Chunk, Chunk.id.in_(QueryLog.returned_chunk_ids), isouter=True)
            .join(Document, Document.doc_id == Chunk.doc_id, isouter=True)
            .group_by(Document.doc_id, Document.file_path)
            .order_by(func.count().desc())
            .limit(limit)
        )

        result = []
        for row in q.all():
            result.append({
                "doc_id": row.doc_id,
                "file_path": row.file_path,
                "hits": row.hits,
            })

        return result
