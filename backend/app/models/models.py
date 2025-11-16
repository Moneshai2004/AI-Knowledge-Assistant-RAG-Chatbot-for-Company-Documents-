from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, JSON


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_id: str
    file_path: str
    meta_json: Optional[str] = None  # renamed from reserved "metadata"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Chunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_id: str
    chunk_id: int
    text: str
    page: int
    start_char: int
    end_char: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FaissIndexRegistry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faiss_path: str
    bm25_path: str
    embed_dim: int
    total_chunks: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QueryLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_text: str
    user_id: Optional[str] = None
    returned_chunk_ids: List[int] = Field(sa_column=Column(JSON), default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = None


class Evaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    params: dict = Field(sa_column=Column(JSON), default_factory=dict)
    results: dict = Field(sa_column=Column(JSON), default_factory=dict)
    run_at: datetime = Field(default_factory=datetime.utcnow)
