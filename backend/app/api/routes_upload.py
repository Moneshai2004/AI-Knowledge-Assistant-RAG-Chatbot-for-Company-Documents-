import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.core.rag_engine import rag_pipeline

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):

    try:
        os.makedirs("data/uploads", exist_ok=True)
        file_path = f"data/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        create_rag_pipeline(file_path)

        return {"status": "success", "message": f"{file.filename} processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))