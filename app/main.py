from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="UnifiedClaim AI – Day 1")

class AskRequest(BaseModel):
    question: str

@app.get("/status")
def status():
    return {"ok": True}

@app.post("/ask")
def ask(request: AskRequest):
    return {
        "received_question": request.question,
        "message": "Ask endpoint is working"
    }