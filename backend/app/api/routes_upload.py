# backend/app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import shutil
from app.services.indexer import index_pdf_background

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data/uploads"
FRONTEND_POLICIES_DIR = "/home/moni/Desktop/ai-knowledge-assistant/policy-frontend/public/policies"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRONTEND_POLICIES_DIR, exist_ok=True)

@router.post("/")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_id = file.filename.split(".")[0]
        file_path = f"{UPLOAD_DIR}/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # ABSOLUTE COPY
        shutil.copy(file_path, os.path.join(FRONTEND_POLICIES_DIR, file.filename))

        background_tasks.add_task(index_pdf_background, file_path, file_id)

        return {
            "status": "success",
            "message": "File uploaded and copied to frontend. Indexing started.",
            "doc_id": file_id,
            "file_name": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
