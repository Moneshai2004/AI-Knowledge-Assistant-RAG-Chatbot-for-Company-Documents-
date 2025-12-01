from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from pathlib import Path
import shutil

from app.services import lora_loader

router = APIRouter(prefix="/lora", tags=["LoRA"])

# Root path for all LoRA adapters
# Result: <project-root>/backend/lora_models
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LORA_ROOT = PROJECT_ROOT / "lora_models"
os.makedirs(LORA_ROOT, exist_ok=True)


@router.post("/upload")
async def upload_lora(folder: str, file: UploadFile = File(...)):
    """
    Upload LoRA files into a folder:

    POST /lora/upload?folder=my_lora
    file = adapter_model.safetensors / adapter_config.json ...
    """
    target_dir = LORA_ROOT / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / file.filename

    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "status": "uploaded",
        "folder": folder,
        "file": file.filename,
        "path": str(target_path),
    }


@router.post("/enable")
async def enable_lora(name: str):
    """
    Enable a LoRA adapter folder:

    POST /lora/enable?name=my_lora

    Which maps to: backend/lora_models/my_lora
    """
    adapter_dir = LORA_ROOT / name

    if not adapter_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"LoRA folder not found: {adapter_dir}",
        )

    ok = lora_loader.load_lora(str(adapter_dir))
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Failed to load LoRA adapter. Check files in folder.",
        )

    return {"status": "enabled", "adapter": name, "path": str(adapter_dir)}


@router.post("/disable")
async def disable_lora():
    """
    Disable LoRA and return to pure base GPT-2.
    """
    lora_loader.unload_lora()
    return {"status": "disabled"}


@router.get("/status")
async def status():
    """
    See if LoRA is active.
    """
    return lora_loader.get_lora_status()
