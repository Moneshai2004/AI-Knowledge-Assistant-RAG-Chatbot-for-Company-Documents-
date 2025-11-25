from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_upload, routes_ask
from app.db.session import create_db_and_tables
from dotenv import load_dotenv
import os
from app.api import routes_upload, routes_ask, routes_admin
from app.api.routes_documents import router as documents_router



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
def on_startup():
    print("### Creating DB Tables...")
    create_db_and_tables()
    print("### Tables created successfully.")

app.include_router(routes_upload.router)
app.include_router(routes_ask.router)
app.include_router(routes_admin.router)
app.include_router(documents_router)

@app.get("/")
def root():
    return {"status": "ok"}
