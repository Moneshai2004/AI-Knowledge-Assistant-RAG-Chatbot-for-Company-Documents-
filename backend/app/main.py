from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import routes_upload, routes_ask

app = FastAPI(title="AI Knowledge Assistant - Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_upload.router)
app.include_router(routes_ask.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running fine"}
