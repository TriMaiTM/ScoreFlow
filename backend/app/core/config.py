from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Football-Data.org API
    FOOTBALL_API_KEY: str
    FOOTBALL_API_BASE_URL: str = "https://api.football-data.org/v4"
    
    # API-Football.com (100 req/day free)
    API_FOOTBALL_KEY: str = ""
    API_FOOTBALL_ENABLED: bool = False
    
    # ML Model
    MODEL_PATH: str = "./models/prediction_model.pkl"
    ENABLE_ML_PREDICTIONS: bool = True
    
    # Background Scheduler
    ENABLE_SCHEDULER: bool = True  # Set to False to disable auto-updates
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8081"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
