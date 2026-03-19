import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.rag import rebuild_index

if __name__ == "__main__":
    idx = rebuild_index()
    print("Index built and persisted.")