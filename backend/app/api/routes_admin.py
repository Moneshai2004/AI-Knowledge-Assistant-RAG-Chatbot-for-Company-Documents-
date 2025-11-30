# backend/app/api/routes_admin.py
from fastapi import APIRouter, HTTPException
from app.services.indexer import merge_all_indexes
from app.repos.repo_rag import (
    count_documents,
    count_chunks,
    count_queries,
    get_query_logs,
    get_latest_registry
)

router = APIRouter(prefix="/admin", tags=["Admin"])

# -----------------------------
# GET /admin/stats
# -----------------------------
@router.get("/stats")
async def get_stats():
    docs = await count_documents()
    chunks = await count_chunks()
    queries = await count_queries()
    latest = await get_latest_registry()

    return {
        "total_documents": docs,
        "total_chunks": chunks,
        "total_queries": queries,
        "latest_index": latest.faiss_path if latest else None,
        "latest_index_date": latest.created_at if latest else None,
        "embed_dim": latest.embed_dim if latest else None
    }

# -----------------------------
# GET /admin/query-logs
# -----------------------------
@router.get("/query-logs")
async def get_logs(limit: int = 50):
    logs = await get_query_logs(limit=limit)
    return logs

# -----------------------------
# POST /admin/merge (existing)
# -----------------------------
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
