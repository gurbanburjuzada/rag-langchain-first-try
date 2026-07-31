import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# This file's location: .../Project01/src/config.py
# .parent -> src/, .parent.parent -> Project01/ (project root)
project_root = Path(__file__).parent.parent
path_to_data = project_root / "data"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
API_KEY: str | None = os.getenv("API_KEY")
GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 75
RETRIEVAL_K = 5
