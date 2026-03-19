import os
import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse

from llama_index.llms.ollama import Ollama

from app.models.schemas import AskRequest
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


@router.post("/ask")
def ask(req: AskRequest):
    # Ensure LlamaIndex uses local Ollama (prevents OpenAI fallback)
    configure_llm()

    # Load or create the persistent index
    index = get_or_create_index()

    # Bind Ollama explicitly to the query engine
    llm = Ollama(model=settings.LLM_MODEL, request_timeout=settings.REQUEST_TIMEOUT)
    qe = index.as_query_engine(similarity_top_k=settings.SIMILARITY_TOP_K, llm=llm)

    resp = qe.query(req.question)
    logger.info({"event": "ask", "q": req.question, "response_len": len(str(resp))})
    return {"answer": str(resp)}


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
