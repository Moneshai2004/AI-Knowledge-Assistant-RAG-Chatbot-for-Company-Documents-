# backend/app/api/routes_evaluation.py

import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import BackgroundTasks

from app.services.evaluator import run_evaluation_job, load_eval_dataset
from app.db.session import async_session
from app.models.models import Evaluation
from sqlalchemy import select

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

EVAL_DIR = "data/eval"
os.makedirs(EVAL_DIR, exist_ok=True)


# -------------------------
# 1) Upload Evaluation Dataset
# -------------------------
@router.post("/upload")
async def upload_eval_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Upload a JSON file only.")

    dst_path = os.path.join(EVAL_DIR, "dataset.json")
    content = await file.read()

    with open(dst_path, "wb") as f:
        f.write(content)

    # quick validation
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")

    return {"status": "success", "items": len(data)}


# -------------------------
# 2) Run Evaluation
# -------------------------
@router.post("/run")
async def run_evaluation(background_tasks: BackgroundTasks):

    # ensure dataset exists
    ds_path = os.path.join(EVAL_DIR, "dataset.json")
    if not os.path.exists(ds_path):
        raise HTTPException(status_code=404, detail="No evaluation dataset uploaded.")

    # run in background 
    background_tasks.add_task(run_evaluation_job)

    return {"status": "started", "message": "Evaluation is running in background."}


# -------------------------
# 3) List all evaluations
# -------------------------
@router.get("/list")
async def list_evaluations():
    async with async_session() as session:
        res = await session.execute(select(Evaluation).order_by(Evaluation.run_at.desc()))
        rows = res.scalars().all()

    return [
        {
            "id": ev.id,
            "score": ev.results.get("overall_score"),
            "params": ev.params,
            "run_at": ev.run_at,
        }
        for ev in rows
    ]
