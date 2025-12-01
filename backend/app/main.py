from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.db.session import create_db_and_tables
import os

# Routers
from app.api.routes_upload import router as upload_router
from app.api.routes_ask import router as ask_router
from app.api.routes_admin import router as admin_router
from app.api.routes_documents import router as documents_router
from app.api.routes_admin_stats import router as admin_stats_router
from app.api.routes_admin_logs import router as admin_logs_router
from app.api.routes_auth import router as auth_router
from app.api.routes_lora import router as lora_router

load_dotenv()
print("### FASTAPI DATABASE_URL =", os.getenv("DATABASE_URL"))

app = FastAPI(title="AI Knowledge Assistant - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("### Creating DB Tables...")
    create_db_and_tables()
    print("### Tables created successfully.")

# Register all routers
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(admin_router)
app.include_router(documents_router)
app.include_router(admin_stats_router)
app.include_router(admin_logs_router)
app.include_router(auth_router)
app.include_router(lora_router)

@app.get("/")
def read_root():
    return {"status": "ok"}
