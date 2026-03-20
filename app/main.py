import os
from app.core.config import settings

# Startup validation: require ADMIN_API_KEY in production mode for security
if os.getenv("MODE") == "prod" and not settings.ADMIN_API_KEY:
    raise RuntimeError("ADMIN_API_KEY is required in production mode.")
import logging, os
from fastapi import FastAPI
from app.api.routes import router
from app.api.analyze import analyze_router

# Basic file logging
os.makedirs("./logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("./logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="UnifiedClaim AI – Day 2 (RAG + Upload)")
app.include_router(router)
app.include_router(analyze_router)