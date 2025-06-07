from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APPWRITE_ENDPOINT: str
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    DIFFERENT_API_TEST: str
    DIFFERENT_ACCOUNT_ID: str

    class Config:
        env_file = ".env"

settings = Settings()
