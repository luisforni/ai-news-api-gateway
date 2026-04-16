from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Database (passed through to db-service)
    database_url: str = "postgresql+asyncpg://ai_news_user:changeme@db:5432/ai_news"

    # Celery
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100


settings = Settings()
