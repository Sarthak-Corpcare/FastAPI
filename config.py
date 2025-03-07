from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class  Settings(BaseSettings):
    DATABASE_URL: str
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    session_duration: int = Field(default=86400)
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRY: int = Field(default=30)
    REFRESH_TOKEN_EXPIRY: int = Field(default=60)
Config=Settings()
