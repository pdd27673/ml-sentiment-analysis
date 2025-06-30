from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "ML Model Service"
    app_version: str = "1.0.0"
    debug: bool = False
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    model_cache_dir: str = "./model_cache"
    max_text_length: int = 1000
    min_text_length: int = 1
    max_request_size: int = 1024 * 1024  # 1MB
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Optional API keys (from environment)
    google_api_key: Optional[str] = None
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )


settings = Settings()