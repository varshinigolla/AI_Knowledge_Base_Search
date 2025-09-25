import os
from typing import Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Settings:
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # File Upload
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".docx", ".xlsx", ".csv"}
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Model Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.1
    
    # Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.6
    LOW_CONFIDENCE_THRESHOLD: float = 0.4

settings = Settings()
