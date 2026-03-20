import os

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.core.config import settings
from app.services.source_meta import SourceMeta

# Configure global embedding model once
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# FOLDER_META: Maps subfolder names to canonical metadata for ingestion
FOLDER_META = {
    "dbhdd": SourceMeta(
        source_name="DBHDD",
        jurisdiction="GA",
        policy_domain="behavioral_health/ops",
        effective_date="",
        link="https://dbhdd.georgia.gov/organization/be-informed/policies",
    ).as_dict(),
    "cdc": SourceMeta(
        source_name="CDC",
        jurisdiction="US",
        policy_domain="ipc",
        effective_date="",
        link="https://www.cdc.gov/infection-control/hcp/core-practices/index.html",
    ).as_dict(),
    "icd10": SourceMeta(
        source_name="CMS/NCHS",
        jurisdiction="US",
        policy_domain="coding_dx",
        effective_date="2025-10-01",
        link="https://www.cms.gov/files/document/fy-2026-icd-10-cm-coding-guidelines.pdf",
    ).as_dict(),
}

def _load_docs_with_meta(base_dir: str):
    """Loads documents from subfolders, applying robust metadata mapping for each source."""
    all_docs = []
    for sub in os.listdir(base_dir):
        sub_path = os.path.join(base_dir, sub)
        if not os.path.isdir(sub_path):
            continue

        # Skip folder if no files inside
        if not any(os.scandir(sub_path)):
            continue

        default_meta = FOLDER_META.get(sub, {})
        try:
            docs = SimpleDirectoryReader(sub_path, recursive=True).load_data()
        except ValueError:
            # Skip if SimpleDirectoryReader still finds no files
            continue

        for i, d in enumerate(docs):
            d.metadata = d.metadata or {}
            file_path = d.metadata.get("file_path", "")

            # Prefer exact folder meta; fallback to file_path contains
            if default_meta:
                d.metadata.update(default_meta)
            elif file_path and "dbhdd" in file_path.lower():
                d.metadata.update(FOLDER_META["dbhdd"])
            # (add additional elifs later for other sources if needed)

            all_docs.append(d)
    return all_docs

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
    docs = _load_docs_with_meta(settings.DATA_DIR)
    print(f"[DEBUG] Loaded {len(docs)} documents with robust metadata.")
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=settings.PERSIST_DIR)
    return index