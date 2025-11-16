# backend/app/db/session.py

import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# FORCE the correct DB path
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

# Sync engine for creating tables
sync_engine = create_engine(
    SYNC_DB_PATH,
    echo=False,
    future=True
)

async def init_db():
    # nothing here; table creation handled separately
    pass
