from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./expertflow.db"
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    ai_model: str = ""  # override model, e.g. "anthropic/claude-sonnet-4-20250514"
    whisper_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
