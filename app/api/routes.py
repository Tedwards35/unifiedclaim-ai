def _policy_check_snippets(index, question: str, max_snippets: int = 3, sources: list[str] | None = None):
    """Returns up to 3 policy-supporting snippets, preferring DBHDD/CDC/CMS if no sources given."""
    wanted_sources = sources or ["DBHDD", "CDC", "CMS/NCHS"]  # Prefer these sources by default
    filter_kwargs = _build_metadata_filters(policy_only=True, sources=wanted_sources)
    qe = index.as_query_engine(similarity_top_k=6, **filter_kwargs)
    resp = qe.query(question)
    items = []
    for n in getattr(resp, "source_nodes", [])[:max_snippets]:
        node = getattr(n, "node", None)
        if not node:
            continue
        meta = getattr(node, "metadata", {}) or {}
        content = node.get_content()[:600] if hasattr(node, "get_content") else ""
        items.append({
            "snippet": content,
            "source": meta.get("source_name", ""),
            "jurisdiction": meta.get("jurisdiction", ""),
            "policy_domain": meta.get("policy_domain", ""),
            "effective_date": meta.get("effective_date", ""),
            "link": meta.get("link", ""),
        })
    return items

def _append_retrieval_log(event: str, payload: dict):
    """Appends a retrieval event to logs/retrieval_log.jsonl for audit/debug."""
    os.makedirs("logs", exist_ok=True)
    rec = {"ts": time.time(), "event": event, **payload}
    with open("logs/retrieval_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
import os
import json
import time
import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse

from llama_index.llms.ollama import Ollama

from app.models.schemas import AskRequest
from fastapi import Body
from typing import Dict, Any, List
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters
from app.services.source_meta import SourceMeta
from app.services.rag import get_or_create_index, rebuild_index
from app.core.config import settings
from app.services.llm import configure_llm

router = APIRouter()
logger = logging.getLogger("app")


def _check_api_key(x_api_key: Optional[str]):
    if settings.ADMIN_API_KEY:
        if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.get("/status")
def status():
    return {"ok": True}


def _build_metadata_filters(policy_only: bool, sources: list[str] | None) -> Dict[str, Any]:
    filters = []
    if policy_only:
        # Filter for policy domain (adjust as needed for your schema)
        filters.append(MetadataFilter(key="policy_domain", value="behavioral_health/ops"))
    if sources:
        for s in sources:
            filters.append(MetadataFilter(key="source_name", value=s))
    if not filters:
        return {}
    return {"filters": MetadataFilters(filters=filters)}

@router.post("/ask")
def ask(req: AskRequest = Body(...)):
    """Handles policy Q&A with optional metadata filters. Body only; returns friendly message if no content."""
    configure_llm()
    index = get_or_create_index()
    filter_kwargs = _build_metadata_filters(policy_only=req.policy_only, sources=req.sources)
    qe = index.as_query_engine(similarity_top_k=4, **filter_kwargs)
    resp = qe.query(req.question)

    # Retrieval logging (audit/debug)
    _append_retrieval_log("ask", {
        "question": req.question,
        "policy_only": req.policy_only,
        "sources": req.sources,
        "response_len": len(str(resp)),
    })

    # Friendly fallback if no content
    if not str(resp).strip():
        return {"answer": "I couldn’t retrieve a specific passage for that policy question with the current sources. Try broadening sources, or reindex with additional policy files."}
    return {"answer": str(resp)}

from app.models.schemas import AnalyzeRequest


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    configure_llm()
    # ...existing analysis logic...
    index = get_or_create_index()
    # After your existing result dict is built:
    policy_query = (
        "DBHDD discharge or transition planning documentation requirements, "
        "including discharge summaries, follow-up plans, aftercare, and required records "
        "when services are terminated or transitioned."
    )

    policy_support = _policy_check_snippets(
        index,
        policy_query,
        sources=["DBHDD"]
    )

    def _summarize_policy_support(policy_support: list[dict]) -> str:
        """
        Create a concise, human-readable summary of policy requirements
        based on retrieved policy support snippets.
        """
        if not policy_support:
            return "No specific policy excerpts were identified for this scenario."

        bullets = []
        for item in policy_support:
            text = item.get("snippet", "").lower()
            if "discharge summary" in text:
                bullets.append("Completion of a discharge summary documenting services provided, outcomes, referrals, and discharge disposition.")
            if "transition" in text or "discharge/transit" in text:
                bullets.append("Documentation of discharge or transition planning, including follow-up and continuity of care.")
            if "progress notes" in text:
                bullets.append("Maintenance of progress notes reflecting services delivered and client participation.")
            if "signature" in text:
                bullets.append("Documentation of client and/or guardian participation and required signatures when applicable.")

        if not bullets:
            return "DBHDD policy requires appropriate documentation at discharge, including summaries and supporting records."

        # Deduplicate while preserving order
        bullets = list(dict.fromkeys(bullets))

        return "DBHDD discharge documentation requirements include: " + " ".join(bullets)

    policy_summary = _summarize_policy_support(policy_support)

    result = {}  # replace with your actual result dict
    result["policy_support"] = policy_support
    result["policy_summary"] = policy_summary
    return result


@router.post("/upload")
def upload(file: UploadFile = File(...), x_api_key: Optional[str] = Header(default=None)):
    _check_api_key(x_api_key)
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    dest_path = os.path.join(settings.DATA_DIR, file.filename)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())
    rebuild_index()
    logger.info({"event": "upload", "filename": file.filename, "docs": settings.DATA_DIR})
    return JSONResponse({"ok": True, "indexed": file.filename})


@router.post("/reindex")
def reindex(x_api_key: Optional[str] = Header(default=None)):
    _check_api_key(x_api_key)
    rebuild_index()
    logger.info({"event": "reindex"})
    return {"ok": True}
