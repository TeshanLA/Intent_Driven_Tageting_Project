from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Privacy-Preserving Ad Recommendation API"
    app_env: str = "development"
    database_url: str = "sqlite:///./prototype.db"
    frontend_origin: str = "http://localhost:3000"
    session_expiry_minutes: int = 30
    model_dir: str = "../ml/exported_models"
    ads_csv_path: str = "../data/ads_pool.csv"
    articles_json_path: str = "../data/articles.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )

    @property
    def backend_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def resolve_path(self, relative_or_absolute: str) -> Path:
        path = Path(relative_or_absolute)
        return path if path.is_absolute() else (self.backend_dir / path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
