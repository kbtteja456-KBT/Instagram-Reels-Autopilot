"""Unit tests for the official 2-step Instagram Reels containerized upload pipeline."""

import asyncio
from backend.app.providers.instagram.instagram_client import InstagramClient
from backend.app.agents.instagram import InstagramAgent


def test_containerized_publishing_flow():
    """Verify 2-step container upload -> poll -> publish -> permalink flow."""
    async def _run():
        client = InstagramClient(access_token="mock_user_token_123", ig_user_id="17841400000000001")
        agent = InstagramAgent(client)

        # 1. Container Creation
        creation_id = await client.create_reel_container(
            video_filename="test_reel.mp4",
            caption="Testing AI Reel #viral #reels"
        )
        assert creation_id.startswith("mock_creation_id")

        # 2. Polling
        status_ok = await client.poll_container_status(creation_id=creation_id)
        assert status_ok is True

        # 3. Publish
        media_id = await client.publish_container(creation_id=creation_id)
        assert media_id.startswith("mock_media_id")

        # 4. Permalink
        meta_info = await client.get_reel_permalink(media_id=media_id)
        assert "permalink" in meta_info
        assert "instagram.com/reel" in meta_info["permalink"]

    asyncio.run(_run())
