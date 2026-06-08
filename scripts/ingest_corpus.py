import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.ingest import ingest  # noqa: E402

if __name__ == "__main__":
	ingest()
