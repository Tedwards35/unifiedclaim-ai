from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AskRequest(BaseModel):
    question: str

class AnalyzeRequest(BaseModel):
    text: str
    context: Optional[str] = None  # optional notes/visit context

class AnalyzeResponse(BaseModel):
    icd10_codes: List[str]
    cpt_codes: List[str]
    modifiers: List[str]
    flags: List[str]
    suggestions: List[str]
    details: Dict[str, Any]