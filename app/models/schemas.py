
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AskRequest(BaseModel):
    """Request model for /ask endpoint."""
    question: str  # The user's question to retrieve policy context for.
    policy_only: bool = False  # If true, restricts to policy domain (behavioral_health/ops).
    sources: Optional[List[str]] = None  # List of source names to filter (e.g., ["DBHDD", "CDC"]).

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