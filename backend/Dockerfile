# ---- Stage 1: Builder ----
FROM python:3.10-slim AS builder

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install only necessary pip packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.10-slim

WORKDIR /app

# Copy only installed libs (NOT build tools)
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app
COPY app /app/app
COPY start.sh /app/start.sh
COPY railway.toml /app/railway.toml
COPY prod_start.md /app/prod_start.md
COPY lora_models /app/lora_models

RUN mkdir -p /app/data/faiss && mkdir -p /app/data/uploads
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["bash", "/app/start.sh"]
