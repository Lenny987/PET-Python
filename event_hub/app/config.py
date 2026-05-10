from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    heartbeat_interval: int = 30
    max_history_length: int = 50
    redis_retry_max: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf=8", extra="ignore")

settings = Settings()