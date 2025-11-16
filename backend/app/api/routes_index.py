# backend/app/api/routes_index.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.services.indexer import index_pdf_background
import os
import uuid

router = APIRouter(prefix="/index", tags=["index"])

@router.post("/upload_and_index")
async def upload_and_index(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Save upload
    os.makedirs("data/uploads", exist_ok=True)
    token = uuid.uuid4().hex
    dest = f"data/uploads/{token}_{file.filename}"
    with open(dest, "wb") as f:
        f.write(await file.read())

    doc_id = f"{token}_{file.filename}"
    # Launch background indexing
    background_tasks.add_task(index_pdf_background, dest, doc_id)
    return {"status": "indexing_started", "doc_id": doc_id}
