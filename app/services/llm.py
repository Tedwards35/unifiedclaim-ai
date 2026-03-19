from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from app.core.config import settings

def configure_llm():
    """
    Force LlamaIndex to use the local Ollama model defined in .env.
    This prevents fallback to OpenAI (no API key).
    """
    Settings.llm = Ollama(
        model=settings.LLM_MODEL,
        request_timeout=settings.REQUEST_TIMEOUT
    )
