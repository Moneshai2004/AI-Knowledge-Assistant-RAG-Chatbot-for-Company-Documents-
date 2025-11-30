from fastapi import APIRouter, Query
from sqlmodel import select, func
from datetime import datetime
from app.db.session import async_session
from app.models.models import QueryLog, Chunk, Document

router = APIRouter(prefix="/admin/query-logs", tags=["Admin Logs"])

@router.get("/")
async def get_query_logs(
    search: str = "",
    doc: str = "",
    from_date: str = "",
    to_date: str = "",
    limit: int = 50,
    offset: int = 0,
):
    async with async_session() as session:

        query = select(QueryLog)

        # ----------------------------------------------------
        # TEXT SEARCH
        # ----------------------------------------------------
        if search:
            query = query.where(QueryLog.query_text.ilike(f"%{search}%"))

        # ----------------------------------------------------
        # FILTER BY DOCUMENT
        # (join returned_chunk_ids → Chunk → Document)
        # ----------------------------------------------------
        if doc:
            query = (
                select(QueryLog)
                .join(Chunk, Chunk.id.in_(QueryLog.returned_chunk_ids), isouter=True)
                .join(Document, Document.doc_id == Chunk.doc_id, isouter=True)
                .where(Document.doc_id == doc)
            )

        # ----------------------------------------------------
        # DATE RANGE
        # ----------------------------------------------------
        if from_date:
            from_dt = datetime.fromisoformat(from_date)
            query = query.where(QueryLog.timestamp >= from_dt)

        if to_date:
            to_dt = datetime.fromisoformat(to_date)
            query = query.where(QueryLog.timestamp <= to_dt)

        # ----------------------------------------------------
        # ORDER + PAGINATION
        # ----------------------------------------------------
        query = query.order_by(QueryLog.timestamp.desc())
        query = query.limit(limit).offset(offset)

        res = await session.execute(query)
        logs = res.scalars().all()

        # ----------------------------------------------------
        # TOTAL COUNT (without pagination)
        # ----------------------------------------------------
        count_q = select(func.count()).select_from(QueryLog)
        total = (await session.execute(count_q)).scalar()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": logs
        }
