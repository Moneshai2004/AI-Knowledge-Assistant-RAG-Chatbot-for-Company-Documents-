# backend/app/db/create_tables.py

from sqlmodel import SQLModel
from app.db.session import sync_engine

# IMPORTANT: import models so SQLModel.metadata is populated
from app.models.models import Document, Chunk, FaissIndexRegistry, QueryLog, Evaluation

print("Creating all tables using sync engine...")
SQLModel.metadata.create_all(sync_engine)
print("Done.")
