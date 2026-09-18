"""Application configuration loaded from environment variables using Pydantic Settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Meta / Instagram Graph API
    meta_app_id: str = "mock_meta_app_id"
    meta_app_secret: str = "mock_meta_app_secret"
    instagram_account_id: Optional[str] = None
    instagram_access_token: Optional[str] = None
    instagram_redirect_uri: str = "http://localhost:8000/api/auth/instagram/callback"
    instagram_api_version: str = "v19.0"
    public_media_base_url: str = "http://localhost:8000"

    @property
    def effective_instagram_token(self) -> str:
        """Resolve valid Instagram token from explicit setting or meta_app_secret fallback."""
        if self.instagram_access_token and not self.instagram_access_token.startswith("mock_"):
            return self.instagram_access_token
        if self.meta_app_secret and self.meta_app_secret.startswith("EAA"):
            return self.meta_app_secret
        return self.instagram_access_token or "mock_token_master"

    @property
    def effective_instagram_account_id(self) -> str:
        """Resolve valid Instagram Account ID from explicit setting or meta_app_id fallback."""
        if self.instagram_account_id and not self.instagram_account_id.startswith("mock_"):
            return self.instagram_account_id
        if self.meta_app_id and self.meta_app_id.isdigit() and len(self.meta_app_id) > 12:
            return self.meta_app_id
        return self.instagram_account_id or "17841400000000001"

    # Database & Broker
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "instagram_autopilot"
    redis_url: str = "redis://localhost:6379/0"

    # Security & Encryption
    encryption_key: str = "rRruxvhakdK2Rh_kmP3Uq8OtItwI7kAqcpaggm0Qo2o="
    jwt_secret: str = "super_secret_jwt_hmac_production_key_for_instagram_autopilot_2026"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Free-Tier AI & Stock Providers
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "nvidia/nemotron-3.5-lightning:free"
    pexels_api_key: Optional[str] = None
    pixabay_api_key: Optional[str] = None
    zero_cost_mode: bool = True

    # Operational Schedule
    timezone: str = "Asia/Kolkata"
    slot1_time: str = "07:00"
    slot2_time: str = "18:00"
    daily_reel_limit: int = 2
    media_storage_dir: str = "./media_storage"
    enable_internal_scheduler: bool = True

    @property
    def storage_path(self) -> Path:
        p = Path(self.media_storage_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def temp_path(self) -> Path:
        p = self.storage_path / "temp"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def reels_output_path(self) -> Path:
        p = self.storage_path / "reels"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def audio_output_path(self) -> Path:
        p = self.storage_path / "audio"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
