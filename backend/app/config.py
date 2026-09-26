import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # JWT Auth
    SECRET_KEY: str = "production-ready-resumely-jwt-secret-key-92817291827361"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    DATABASE_URL: str = ""
    
    # AI Model Provider
    AI_PROVIDER: str = "heuristic"  # "gemini", "openai", "heuristic"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-1.5-flash"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000,null"
    
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_supabase_configured(self) -> bool:
        return bool(
            self.SUPABASE_URL 
            and self.SUPABASE_KEY 
            and "placeholder" not in self.SUPABASE_URL
            and "your-project" not in self.SUPABASE_URL
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
