# Day 3 addition: /analyze endpoint for rule-based checks
from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.tools import analyze_billing_text

analyze_router = APIRouter()

@analyze_router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        result = analyze_billing_text(req.text, req.context or "")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"analyze failed: {type(e).__name__}: {e}")
