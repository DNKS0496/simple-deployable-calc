from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/calculator.db"
    log_level: str = "INFO"
    app_env: str = "local"
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()