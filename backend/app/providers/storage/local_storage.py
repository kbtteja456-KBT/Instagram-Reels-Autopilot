"""Local storage management and public media URL resolution."""

import os
import shutil
from pathlib import Path
from typing import Optional
from backend.app.config import settings
from backend.app.core.logging import logger


class LocalStorageProvider:
    """Manages disk storage for temporary media and output Reels."""

    def __init__(self):
        self.base_dir = settings.storage_path
        self.reels_dir = settings.reels_output_path
        self.temp_dir = settings.temp_path

    def get_public_media_url(self, filename: str) -> str:
        """Construct the publicly accessible URL that Meta's servers will download."""
        base = settings.public_media_base_url.rstrip("/")
        return f"{base}/api/media/download/{filename}"

    def clean_temp_files(self, job_id: str) -> None:
        """Clean up temporary assets for a given job."""
        job_temp = self.temp_dir / job_id
        if job_temp.exists():
            shutil.rmtree(job_temp, ignore_errors=True)
            logger.info(f"[Storage] Cleaned temporary directory for job: {job_id}")


storage_provider = LocalStorageProvider()
