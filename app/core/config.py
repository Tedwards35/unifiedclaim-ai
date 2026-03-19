import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3:8b")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data/docs")
    PERSIST_DIR: str = os.getenv("PERSIST_DIR", "./data/chroma_index")
    SIMILARITY_TOP_K: int = int(os.getenv("SIMILARITY_TOP_K", "4"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "120"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")

settings = Settings()