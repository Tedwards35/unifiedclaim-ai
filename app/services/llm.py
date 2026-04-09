from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from app.core.config import settings

def configure_llm():
    """
    Force LlamaIndex to use ONLY the local Ollama model (llama3:8b or as set in .env).
    This prevents fallback to OpenAI or any other remote LLMs.
    """
    Settings.llm = Ollama(
        model=settings.LLM_MODEL,
        request_timeout=settings.REQUEST_TIMEOUT
    )

# Guard: Remove or block any OpenAI or other LLM usage
import sys
def _block_openai(*args, **kwargs):
    raise RuntimeError("OpenAI or other remote LLMs are not allowed. Only Ollama llama3:8b (local) is permitted.")

try:
    import llama_index.llms.openai
    llama_index.llms.openai.OpenAI = _block_openai
except ImportError:
    pass
