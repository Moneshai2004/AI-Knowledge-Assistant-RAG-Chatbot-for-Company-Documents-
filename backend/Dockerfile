FROM python:3.10-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for FAISS, PyMuPDF, Peft
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app
COPY . /app/

# Create data dirs in container
RUN mkdir -p /app/data/faiss && mkdir -p /app/data/uploads

# Startup script
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]

