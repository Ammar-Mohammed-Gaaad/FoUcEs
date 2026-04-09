from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./fakarni.db"
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_port: int = 8000
    api_host: str = "0.0.0.0"

    # OAuth Providers
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    facebook_client_id: str = ""
    facebook_client_secret: str = ""
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""

    # Base URL (used for OAuth redirect URIs)
    base_url: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
