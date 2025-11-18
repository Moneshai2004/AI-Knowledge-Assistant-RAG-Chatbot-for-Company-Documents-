# backend/app/db/session.py

import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DB_PATH = "sqlite+aiosqlite:///./data/rag.db"
SYNC_DB_PATH = "sqlite:///./data/rag.db"

engine = create_async_engine(
    DB_PATH,
    echo=False,
    future=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine for table creation
sync_engine = create_engine(
    SYNC_DB_PATH,
    echo=False,
    future=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(sync_engine)
