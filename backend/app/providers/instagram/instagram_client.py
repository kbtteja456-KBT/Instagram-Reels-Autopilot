"""Official Meta Graph API client for Instagram Reels Content Publishing."""

import asyncio
import os
from typing import Dict, Any, Optional
import httpx

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import InstagramPublishingError


class InstagramClient:
    """Interacts with the official Meta Graph API (v19.0+) for Instagram Reels."""

    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.api_version = settings.instagram_api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def create_reel_container(
        self,
        video_filename: str,
        caption: str,
        cover_image_url: Optional[str] = None,
        share_to_feed: bool = True
    ) -> str:
        """Step 1: Create an asynchronous video upload container with Meta."""
        # Handle mock/sandbox runs
        if self.access_token.startswith("mock_"):
            logger.info("[MetaClient:Mock] Simulating container creation...")
            return "mock_creation_id_178499281729102"

        video_url = f"{settings.public_media_base_url.rstrip('/')}/api/media/download/{video_filename}"
        url = f"{self.base_url}/{self.ig_user_id}/media"
        
        payload: Dict[str, Any] = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true" if share_to_feed else "false",
            "access_token": self.access_token
        }
        if cover_image_url:
            payload["cover_url"] = cover_image_url

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, data=payload)
            data = resp.json()
            if "error" in data:
                err = data["error"]
                raise InstagramPublishingError(
                    message=f"Meta container creation failed: {err.get('message')}",
                    meta_code=err.get("code"),
                    meta_subcode=err.get("error_subcode"),
                    details=err
                )
            creation_id = data.get("id")
            if not creation_id:
                raise InstagramPublishingError("No creation_id returned from Meta Graph API.")
            logger.info(f"[MetaClient] Reel container created successfully: {creation_id}")
            return str(creation_id)

    async def poll_container_status(self, creation_id: str, max_wait_seconds: int = 180, poll_interval: int = 5) -> bool:
        """Step 2: Poll container status until FINISHED, ERROR, or timeout."""
        if self.access_token.startswith("mock_") or creation_id.startswith("mock_"):
            logger.info("[MetaClient:Mock] Container status: FINISHED.")
            return True

        url = f"{self.base_url}/{creation_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token
        }

        start_time = asyncio.get_event_loop().time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                resp = await client.get(url, params=params)
                data = resp.json()
                
                if "error" in data:
                    err = data["error"]
                    raise InstagramPublishingError(
                        message=f"Meta container poll error: {err.get('message')}",
                        meta_code=err.get("code"),
                        details=err
                    )

                status_code = data.get("status_code", "").upper()
                logger.info(f"[MetaClient] Polling container {creation_id} status: {status_code}")

                if status_code == "FINISHED":
                    return True
                elif status_code in ["ERROR", "EXPIRED"]:
                    raise InstagramPublishingError(
                        f"Meta video processing failed with status '{status_code}'.",
                        details=data
                    )

                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= max_wait_seconds:
                    raise InstagramPublishingError(
                        f"Timed out after {max_wait_seconds}s waiting for Meta video container {creation_id}."
                    )

                await asyncio.sleep(poll_interval)

    async def create_reel_container_resumable(
        self,
        video_filepath: str,
        caption: str,
        share_to_feed: bool = True
    ) -> str:
        """Upload Reel using Meta's official direct resumable upload protocol to rupload.facebook.com.
        Zero dependency on public tunnels (ngrok) or static domains.
        """
        if self.access_token.startswith("mock_"):
            logger.info("[MetaClient:Mock] Simulating resumable upload...")
            return "mock_creation_id_178499281729102"

        if not os.path.exists(video_filepath):
            raise InstagramPublishingError(f"Video file not found at: {video_filepath}")

        file_size = os.path.getsize(video_filepath)
        url = f"{self.base_url}/{self.ig_user_id}/media"

        init_payload = {
            "upload_type": "resumable",
            "media_type": "REELS",
            "caption": caption,
            "share_to_feed": "true" if share_to_feed else "false",
            "access_token": self.access_token
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, data=init_payload)
            data = resp.json()
            if "error" in data:
                err = data["error"]
                raise InstagramPublishingError(
                    message=f"Meta resumable container init failed: {err.get('message')}",
                    meta_code=err.get("code"),
                    details=err
                )
            creation_id = data.get("id")
            rupload_uri = data.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{self.api_version}/{creation_id}"

            logger.info(f"[MetaClient] Initialized resumable container {creation_id}. Uploading {file_size} bytes to rupload.facebook.com...")

            headers = {
                "Authorization": f"OAuth {self.access_token}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream"
            }
            with open(video_filepath, "rb") as f:
                content = f.read()

            upload_resp = await client.post(rupload_uri, headers=headers, content=content, timeout=180.0)
            if upload_resp.status_code != 200:
                raise InstagramPublishingError(
                    f"Meta rupload failed with status {upload_resp.status_code}: {upload_resp.text}"
                )
            logger.info(f"[MetaClient] Video binary uploaded successfully to container: {creation_id}")
            return str(creation_id)

    async def publish_container(self, creation_id: str) -> str:
        """Step 3: Publish the ready container to the Instagram profile."""
        if self.access_token.startswith("mock_") or creation_id.startswith("mock_"):
            logger.info("[MetaClient:Mock] Container published successfully.")
            return "mock_media_id_180293847561829"

        url = f"{self.base_url}/{self.ig_user_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, data=payload)
            data = resp.json()
            if "error" in data:
                err = data["error"]
                raise InstagramPublishingError(
                    message=f"Meta media_publish failed: {err.get('message')}",
                    meta_code=err.get("code"),
                    details=err
                )
            media_id = data.get("id")
            if not media_id:
                raise InstagramPublishingError("No media_id returned from media_publish.")
            logger.info(f"[MetaClient] Reel published successfully with media_id: {media_id}")
            return str(media_id)

    async def get_reel_permalink(self, media_id: str) -> Dict[str, Any]:
        """Step 4: Fetch permanent Instagram URL and published timestamp."""
        if self.access_token.startswith("mock_") or media_id.startswith("mock_"):
            return {
                "id": media_id,
                "permalink": "https://www.instagram.com/reel/C_MockReel123/",
                "timestamp": "2026-09-11T18:00:00+0000"
            }

        url = f"{self.base_url}/{media_id}"
        params = {
            "fields": "id,permalink,timestamp",
            "access_token": self.access_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if "error" in data:
                logger.warning(f"[MetaClient] Failed to query permalink: {data['error']}")
                return {"id": media_id, "permalink": f"https://www.instagram.com/p/{media_id}/"}
            return data

    async def get_account_insights(self) -> Dict[str, Any]:
        """Fetch profile followers, media count, and aggregate video views/plays."""
        if self.access_token.startswith("mock_"):
            return {
                "followers_count": 12480,
                "follows_count": 142,
                "media_count": 86,
                "total_plays": 542900,
                "reach": 234100
            }

        url = f"{self.base_url}/{self.ig_user_id}"
        params = {
            "fields": "id,username,name,profile_picture_url,followers_count,follows_count,media_count",
            "access_token": self.access_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if "error" in data:
                raise InstagramPublishingError(f"Account query error: {data['error'].get('message')}")
            return data
