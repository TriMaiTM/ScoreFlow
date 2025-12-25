from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    
    DB_POOL_SIZE: int = 5                    # Số connections mở sẵn
    DB_MAX_OVERFLOW: int = 2                # Tối đa thêm 10 connections
    DB_POOL_TIMEOUT: int = 30                # Đợi 30s nếu pool đầy
    DB_POOL_RECYCLE: int = 3600              # Recycle connections sau 1 giờ
    DB_POOL_PRE_PING: bool = True     
    DB_CONNECT_TIMEOUT: int = 120  # 🆕 Tăng lên 120s cho Render cold start
    DB_COMMAND_TIMEOUT: int = 120       # Kiểm tra connection trước khi dùng

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 4320  # 30 days
    
    # Football-Data.org API
    FOOTBALL_API_KEY: str
    FOOTBALL_API_BASE_URL: str = "https://api.football-data.org/v4"
    
    # API-Football.com (100 req/day free)
    API_FOOTBALL_KEY: str = ""
    API_FOOTBALL_ENABLED: bool = False
    
    # ML Model
    MODEL_PATH: str = "./models/prediction_model_v2.pkl"
    ENABLE_ML_PREDICTIONS: bool = True
    
    # Background Scheduler
    ENABLE_SCHEDULER: bool = True  # Set to False to disable auto-updates
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8081",
        "http://localhost:19000",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "*"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("DATABASE_URL_ASYNC")
    @classmethod
    def assemble_async_db_connection(cls, v: str | None) -> str:
        if v:
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
