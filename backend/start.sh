#!/bin/bash
set -e

# ensure data dirs exist
mkdir -p /app/data/faiss
mkdir -p /app/data/uploads

# run uvicorn with recommended production settings
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2
