import os
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# -----------------------------
# Base model config
# -----------------------------
BASE_MODEL = os.getenv("LORA_BASE_MODEL", "gpt2")

# Global state – shared across app
model: Optional[torch.nn.Module] = None
tokenizer: Optional[AutoTokenizer] = None
active_lora_path: Optional[str] = None


def load_base_model():
    """
    Load the base model (GPT-2) without any LoRA.
    Called once, and again when we unload LoRA.
    """
    global model, tokenizer, active_lora_path

    # If we already have base model and no LoRA, reuse it
    if model is not None and active_lora_path is None and tokenizer is not None:
        return model, tokenizer

    print(f"[LORA] Loading base model: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    # GPT-2 has no pad token; use EOS as pad
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,
    )
    model.eval()
    active_lora_path = None

    print("[LORA] Base model loaded.")
    return model, tokenizer


def load_lora(adapter_dir: str) -> bool:
    """
    Attach a LoRA adapter stored in adapter_dir.
    adapter_dir must contain:
      - adapter_config.json
      - adapter_model.safetensors
    """
    global model, tokenizer, active_lora_path
    from pathlib import Path

    adapter_dir = str(Path(adapter_dir))
    cfg_path = Path(adapter_dir) / "adapter_config.json"

    print(f"[LORA] Requested LoRA load from: {adapter_dir}")

    if not cfg_path.exists():
        print(f"[LORA] ERROR: adapter_config.json not found in {adapter_dir}")
        return False

    # Ensure base model exists
    load_base_model()

    try:
        print(f"[LORA] Attaching LoRA adapter from {adapter_dir} ...")
        lora_model = PeftModel.from_pretrained(
            model,
            adapter_dir,
            torch_dtype=torch.float32,
        )
        lora_model.eval()

        model = lora_model
        active_lora_path = adapter_dir

        print("[LORA] LoRA loaded successfully.")
        return True

    except Exception as e:
        print(f"[LORA] ERROR while loading LoRA: {e}")
        active_lora_path = None
        return False


def unload_lora() -> bool:
    """
    Remove LoRA and go back to pure base model.
    """
    global model, tokenizer, active_lora_path
    print("[LORA] Unloading LoRA and reloading base model...")

    model = None
    tokenizer = None
    active_lora_path = None

    load_base_model()
    print("[LORA] LoRA unloaded; base model active.")
    return True


def get_lora_status():
    """
    Small helper for /lora/status endpoint.
    """
    return {
        "base_model": BASE_MODEL,
        "active_lora": active_lora_path,
        "is_lora_loaded": active_lora_path is not None,
    }
