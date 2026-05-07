import os
from pathlib import Path


class Config:
    """Simple configuration management."""
    
    # Ollama
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data/new"
    PROCESSED_DIR = BASE_DIR / "data/processed"
    CHATS_DIR = BASE_DIR / "chats"
    CHROMA_DIR = BASE_DIR / "chroma_db"
    TEMP_DIR = BASE_DIR / "temp"

    # Whisper
    WHISPER_SIZE = os.getenv("WHISPER_SIZE", "base")
    
    # RAG
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5
    
    # Retry
    MAX_RETRIES = 3
    THRESHOLD = 3.0
