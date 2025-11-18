# backend/app/api/routes_upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os

from app.services.indexer import index_pdf_background

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # 1) Save file
        file_id = file.filename.split(".")[0]
        file_path = f"{UPLOAD_DIR}/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 2) Trigger indexing in background
        background_tasks.add_task(index_pdf_background, file_path, file_id)

        return {
            "status": "success",
            "message": "File uploaded. Indexing started.",
            "doc_id": file_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
