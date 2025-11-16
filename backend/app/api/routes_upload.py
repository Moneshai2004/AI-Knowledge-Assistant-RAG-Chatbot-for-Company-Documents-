# backend/app/api/routes_upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import os

from app.services.indexer import index_pdf_background

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        os.makedirs("data/uploads", exist_ok=True)
        file_path = f"data/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Create DB entry for Document
        from app.db.session import async_session
        from app.models.models import Document
        
        async with async_session() as session:
            doc = Document(
                doc_id=file.filename.split(".")[0],
                file_path=file_path,
                meta_json=None
            )
            session.add(doc)
            await session.commit()
            await session.refresh(doc)

        return {"status": "success", "message": "File uploaded and saved."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
