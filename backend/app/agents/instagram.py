"""InstagramAgent: Coordinates official 2-step Reels upload, polling, publication, and permalink verification."""

import os
from typing import Dict, Any, Optional, List
from backend.app.agents.base import BaseAgent
from backend.app.core.errors import DuplicateUploadPreventedError, InstagramPublishingError
from backend.app.core.security import compute_file_hash
from backend.app.providers.instagram.instagram_client import InstagramClient


class InstagramAgent(BaseAgent):
    """Executes the asynchronous containerized publishing flow for Instagram Reels."""

    def __init__(self, client: Optional[InstagramClient] = None):
        super().__init__("InstagramAgent")
        self.client = client

    def set_client(self, client: InstagramClient) -> None:
        self.client = client

    async def publish_reel(
        self,
        video_filepath: str,
        caption: str,
        existing_hashes: Optional[List[str]] = None,
        cover_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        self.log(f"Initiating Instagram Reel publishing for: {video_filepath}")

        # 1. Duplicate check via SHA-256
        file_hash = compute_file_hash(video_filepath)
        if existing_hashes and file_hash in existing_hashes:
            raise DuplicateUploadPreventedError(file_hash)

        if not self.client:
            raise InstagramPublishingError("Instagram client is not configured or authenticated.")

        filename = os.path.basename(video_filepath)

        # 2. Container Creation (Resumable Direct Binary Upload first)
        creation_id = None
        try:
            self.log("[Stage 1/4] Uploading video binary directly to Meta via Resumable Upload (No tunnel needed)...")
            creation_id = await self.client.create_reel_container_resumable(
                video_filepath=video_filepath,
                caption=caption
            )
        except Exception as resumable_err:
            self.log(f"Direct resumable upload notice: {resumable_err}. Falling back to hosted URL container...", level="WARNING")
            creation_id = await self.client.create_reel_container(
                video_filename=filename,
                caption=caption,
                cover_image_url=cover_image_url
            )

        # 3. Status Polling
        self.log(f"[Stage 2/4] Polling container {creation_id} for transcoding completion...")
        await self.client.poll_container_status(creation_id=creation_id)

        # 4. Publication
        self.log(f"[Stage 3/4] Publishing container {creation_id} to Instagram feed...")
        media_id = await self.client.publish_container(creation_id=creation_id)

        # 5. Permalink Verification
        self.log(f"[Stage 4/4] Verifying permalink for media {media_id}...")
        meta_info = await self.client.get_reel_permalink(media_id=media_id)

        permalink = meta_info.get("permalink", f"https://www.instagram.com/reel/{media_id}/")
        self.log(f"Reel successfully live at: {permalink}")

        return {
            "instagram_media_id": media_id,
            "instagram_url": permalink,
            "file_hash": file_hash,
            "creation_id": creation_id,
            "timestamp": meta_info.get("timestamp")
        }
