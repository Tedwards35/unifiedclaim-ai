import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.core.config import settings

# Configure global embedding model once
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_or_create_index():
    persist_dir = settings.PERSIST_DIR
    if os.path.isdir(persist_dir) and any(os.scandir(persist_dir)):
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            return index
        except Exception:
            pass
    return rebuild_index()

def rebuild_index():
    os.makedirs(settings.PERSIST_DIR, exist_ok=True)
    docs = SimpleDirectoryReader(settings.DATA_DIR, recursive=True).load_data()
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=settings.PERSIST_DIR)
    return index