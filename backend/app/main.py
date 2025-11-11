from fastapi import FastAPI

app=FastAPI(title= "AI chat Assistant - Backend")
@app.get("/")
async def root():
    return {"message": "Welcome to the AI chat Assistant Backend!"}
