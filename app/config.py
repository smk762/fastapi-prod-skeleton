from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "fastapi-prod-skeleton"
    ENV: str = "dev"
    REQUEST_TIMEOUT_MS: int = 8000

    DATABASE_URL: str = "sqlite:///./dev.db"

    JWT_ISSUER: str = "fastapi-prod-skeleton"
    JWT_AUDIENCE: str = "fastapi-prod-skeleton"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"

settings = Settings()
