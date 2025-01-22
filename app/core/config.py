from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Morfeo API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    WELCOME_MESSAGE: str = "DEVELOPMENT MODE"
    MAILHOG_HOST: str = "localhost"
    MAILHOG_PORT: int = 1025
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    UNSTRUCTURED_API_KEY: Optional[str] = None
    HUGGING_FACE_HUB_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 