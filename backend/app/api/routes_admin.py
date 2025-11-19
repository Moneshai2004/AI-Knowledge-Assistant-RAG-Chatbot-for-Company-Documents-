# backend/app/api/routes_admin.py
from fastapi import APIRouter, HTTPException
from app.services.indexer import merge_all_indexes

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/merge")
async def merge_indexes():
    reg = await merge_all_indexes()
    if not reg:
        raise HTTPException(status_code=404, detail="No FAISS registries to merge or merge failed.")
    return {
        "status": "success",
        "global_index_path": reg.faiss_path,
        "total_chunks": reg.total_chunks,
        "registry_id": reg.id
    }
