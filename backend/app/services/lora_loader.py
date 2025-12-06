import os
from pathlib import Path
from threading import Lock
from typing import Optional, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = os.getenv("LORA_BASE_MODEL", "gpt2")

_model: Optional[torch.nn.Module] = None
_tokenizer: Optional[AutoTokenizer] = None
_active_lora: Optional[str] = None

_lock = Lock()


def load_lora(lora_dir: str) -> bool:
    """
    Load a LoRA adapter + tokenizer from lora_dir.
    """

    global _model, _tokenizer, _active_lora

    lora_path = Path(lora_dir).resolve()

    if not (lora_path / "adapter_config.json").exists():
        print(f"[LORA] ERROR: adapter_config.json not found in {lora_path}")
        return False

    print(f"[LORA] Loading LoRA from: {lora_path}")

    with _lock:
        # Load tokenizer FROM THE LORA FOLDER
        tok = AutoTokenizer.from_pretrained(str(lora_path))
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token

        # Load base model only once
        print(f"[LORA] Loading base model: {BASE_MODEL}")
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
        )

        # Attach LoRA
        model = PeftModel.from_pretrained(
            base,
            str(lora_path),
            torch_dtype=torch.float32
        )
        model.eval()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        _model = model
        _tokenizer = tok
        _active_lora = str(lora_path)

        print("[LORA] LoRA loaded successfully.")
        return True


def unload_lora() -> bool:
    """Return to pure base model."""
    global _model, _tokenizer, _active_lora

    print("[LORA] Unloading LoRA...")

    with _lock:
        # Load base model tokenizer
        tok = AutoTokenizer.from_pretrained(BASE_MODEL)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token

        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
        )
        base.eval()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        base.to(device)

        _model = base
        _tokenizer = tok
        _active_lora = None

    print("[LORA] LoRA removed; base model active.")
    return True


def get_lora_model() -> Tuple[Optional[torch.nn.Module], Optional[AutoTokenizer]]:
    return _model, _tokenizer


def get_lora_status():
    return {
        "base_model": BASE_MODEL,
        "active_lora": _active_lora,
        "is_lora_loaded": _active_lora is not None
    }
