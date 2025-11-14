from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.core.rag_engine import ask_question

router = APIRouter(prefix="/ask", tags=["Ask"])

class query(BaseModel):
    question: str   

@router.post("/")
async def ask(query: query):
    try:
        answer = ask_question(query.question)
        return {"question": query.question, "answer": answer}
    except Exception as e:
        import traceback
        print("ERROR in /ask/")
        traceback.print_exc()   # <-- prints FULL traceback
        raise HTTPException(status_code=500, detail=str(e))

    
