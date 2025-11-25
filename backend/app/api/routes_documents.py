# backend/app/api/routes_documents.py
import os
from fastapi import APIRouter
from sqlalchemy import select
from app.db.session import async_session
from app.models.models import Document

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/list")
async def list_documents():
    async with async_session() as session:
        result = await session.execute(select(Document))
        docs = result.scalars().all()

    return [
        {
            "id": d.doc_id,
            "file_name": os.path.basename(d.file_path)
        }
        for d in docs
    ]
