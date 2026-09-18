"""Public media download endpoint enabling Meta Graph API to fetch rendered Reels."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.core.logging import logger

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/download/{filename}")
async def download_rendered_reel(filename: str, request: Request):
    """Serve rendered MP4 files for Meta Graph API container ingestion.
    Meta's servers require a publicly accessible URL with byte-range and video/mp4 content type.
    """
    # Prevent path traversal attacks
    clean_filename = os.path.basename(filename)
    reels_path = settings.reels_output_path / clean_filename
    temp_path = settings.temp_path / clean_filename

    target_file: Path
    if reels_path.exists():
        target_file = reels_path
    elif temp_path.exists():
        target_file = temp_path
    else:
        logger.warning(f"[MediaServer] File not found requested by Meta/Client: {clean_filename}")
        raise HTTPException(status_code=404, detail="Requested media file not found.")

    logger.info(f"[MediaServer] Serving media file '{clean_filename}' ({target_file.stat().st_size} bytes)")
    
    return FileResponse(
        path=str(target_file),
        media_type="video/mp4",
        filename=clean_filename,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{clean_filename}"'
        }
    )
