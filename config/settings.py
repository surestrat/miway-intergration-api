import os
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Appwrite Settings (Required)
    APPWRITE_ENDPOINT: str = os.getenv('APPWRITE_ENDPOINT', "")
    APPWRITE_PROJECT_ID: str = os.getenv('APPWRITE_PROJECT_ID', "")
    APPWRITE_API_KEY: str = os.getenv('APPWRITE_API_KEY', "")
    
    # Appwrite Database Settings (Required)
    APPWRITE_DATABASE_ID: str = os.getenv('APPWRITE_DATABASE_ID', "")
    APPWRITE_SALES_COLLECTION_ID: str = os.getenv('APPWRITE_SALES_COLLECTION_ID', "")
    APPWRITE_RECORDINGS_COLLECTION_ID: str = os.getenv('APPWRITE_RECORDINGS_COLLECTION_ID', "")
    
    # DTech API Settings
    DIFFERENT_API_TEST: str = os.getenv('DIFFERENT_API_TEST', "https://test-dsp.integrations.different.co.za")
    DIFFERENT_API_PROD: str = os.getenv('DIFFERENT_API_PROD', "https://dsp.integrations.different.co.za")
    DIFFERENT_ACCOUNT_ID: str = os.getenv('DIFFERENT_ACCOUNT_ID', "")
    # AWS Credentials (Required)
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID', "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY', "")
    AWS_REGION: str = os.getenv('AWS_REGION', "eu-west-1")
    AWS_SERVICE: str = os.getenv('AWS_SERVICE', "execute-api")
    # Redis Settings (Optional with defaults)
    REDIS_HOST: str = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))

    # Security Settings (Optional with defaults)
    SECRET_KEY: str = os.getenv('SECRET_KEY', "dev-secret-key-123456789")
    SESSION_COOKIE_NAME: str = os.getenv('SESSION_COOKIE_NAME', "session_id")
    SESSION_EXPIRE_MINUTES: int = int(os.getenv('SESSION_EXPIRE_MINUTES', 1440))

    # Test User Configuration (Optional with defaults)
    TEST_USER_EXTERNAL_ID: Optional[str] = os.getenv('TEST_USER_EXTERNAL_ID', None)
    TEST_USER_FIRST_NAME: Optional[str] = os.getenv('TEST_USER_FIRST_NAME', None)
    TEST_USER_LAST_NAME: Optional[str] = os.getenv('TEST_USER_LAST_NAME', None)
    TEST_USER_PROVIDER_ID: Optional[str] = os.getenv('TEST_USER_PROVIDER_ID', None)
    ROOT_DIR = Path(__file__).parent.parent

    class Config:
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive = True
        extra = "ignore"




# Get the project root directory

settings = Settings()
