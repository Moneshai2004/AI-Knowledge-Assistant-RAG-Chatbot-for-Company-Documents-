# ===========================
# 1) Base image
# ===========================
FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ===========================
# 2) Install Python deps first
# ===========================
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ===========================
# 3) Copy ONLY backend code
# ===========================
COPY app /app/app
COPY start.sh /app/start.sh
COPY railway.toml /app/railway.toml
COPY prod_start.md /app/prod_start.md

# Copy LoRA models ONLY
COPY lora_models /app/lora_models

# Create data dirs
RUN mkdir -p /app/data/faiss && mkdir -p /app/data/uploads

# Startup script
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["./start.sh"]
