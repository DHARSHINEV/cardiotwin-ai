"""
Core configuration settings for CardioTwin AI.
"""
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "CardioTwin AI"
    VERSION: str = "1.0.0"
    TAGLINE: str = "A living digital representation of the patient for earlier, personalized cardiovascular risk awareness."
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/cardiotwin.db"
    
    # Paths
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    DOCS_DIR: Path = BASE_DIR / "docs"
    
    # Clinical Safety & Demo Defaults
    DEMO_PATIENT_ID: str = "PAT-A-1042"
    DRIFT_WATCH_THRESHOLD: float = 25.0
    DRIFT_ELEVATED_THRESHOLD: float = 50.0
    DRIFT_HIGH_THRESHOLD: float = 75.0
    
    class Config:
        case_sensitive = True

settings = Settings()
