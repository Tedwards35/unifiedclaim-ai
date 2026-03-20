import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.rag import rebuild_index
from app.services.source_meta import SourceMeta

if __name__ == "__main__":
    # Example: seed metadata for your initial docs directory batch
    default_meta = SourceMeta(
        source_name="DBHDD",              # or "CDC" or "CMS/NCHS"
        jurisdiction="GA",                # "US" for CDC/ICD-10-CM
        policy_domain="behavioral_health/ops",
        effective_date="",                # fill when known
        link="https://dbhdd.georgia.gov/organization/be-informed/policies"
    ).as_dict()

    # Rebuild index with metadata propagation
    idx = rebuild_index()
    print("Index built and persisted.")