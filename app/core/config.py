import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "P8 Autonomous Agentic Black-Box Testing Framework"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Base directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ARTIFACTS_DIR: str = os.path.join(BASE_DIR, "artifacts")
    MODELS_DIR: str = os.path.join(BASE_DIR, "weights")
    MOCK_APPS_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "mock_apps")
    
    # Model Thresholds & Config
    MODEL1_CONF_THRESHOLD: float = 0.25
    TIE_BREAK_THRESHOLD: float = 0.05
    FAISS_INDEX_DIM: int = 128
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
