"""Official Meta Graph API OAuth 2.0 flow and Instagram Business/Creator resolution."""

import urllib.parse
from typing import Dict, Any, Optional
import httpx

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.security import generate_oauth_state, verify_oauth_state


class MetaOAuthManager:
    """Manages Meta Graph API OAuth 2.0 flow and Instagram account resolution."""

    GRAPH_API_BASE = "https://graph.facebook.com"
    OAUTH_DIALOG_URL = "https://www.facebook.com"

    SCOPES = [
        "instagram_basic",
        "instagram_content_publish",
        "instagram_manage_insights",
        "pages_show_list",
        "pages_read_engagement",
        "business_management"
    ]

    @classmethod
    def get_authorization_url(cls, workspace_id: str, user_id: str) -> str:
        """Generate official Meta OAuth 2.0 authorization dialog URL with HMAC-signed state."""
        state = generate_oauth_state(workspace_id, user_id)
        params = {
            "client_id": settings.meta_app_id,
            "redirect_uri": settings.instagram_redirect_uri,
            "scope": ",".join(cls.SCOPES),
            "response_type": "code",
            "state": state
        }
        query_string = urllib.parse.urlencode(params)
        return f"{cls.OAUTH_DIALOG_URL}/{settings.instagram_api_version}/dialog/oauth?{query_string}"

    @classmethod
    async def exchange_code_for_tokens(cls, code: str) -> Dict[str, Any]:
        """Exchange authorization code for short-lived token, then upgrade to 60-day Long-Lived Token."""
        # Handle development / testing mock code
        if code.startswith("mock_") or settings.meta_app_id == "mock_meta_app_id":
            logger.info("[MetaOAuth] Detected mock environment/code. Returning simulated Meta OAuth response.")
            return {
                "access_token": f"mock_long_lived_token_{code}",
                "token_type": "bearer",
                "expires_in": 5184000  # 60 days in seconds
            }

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Exchange code for short-lived access token
            short_url = f"{cls.GRAPH_API_BASE}/{settings.instagram_api_version}/oauth/access_token"
            short_params = {
                "client_id": settings.meta_app_id,
                "client_secret": settings.meta_app_secret,
                "redirect_uri": settings.instagram_redirect_uri,
                "code": code
            }
            short_resp = await client.get(short_url, params=short_params)
            short_data = short_resp.json()
            if "error" in short_data:
                raise ValueError(f"Meta token exchange error: {short_data['error'].get('message', short_data)}")

            short_token = short_data["access_token"]

            # 2. Upgrade short-lived token to 60-day Long-Lived User Access Token
            long_url = f"{cls.GRAPH_API_BASE}/{settings.instagram_api_version}/oauth/access_token"
            long_params = {
                "grant_type": "fb_exchange_token",
                "client_id": settings.meta_app_id,
                "client_secret": settings.meta_app_secret,
                "fb_exchange_token": short_token
            }
            long_resp = await client.get(long_url, params=long_params)
            long_data = long_resp.json()
            if "error" in long_data:
                raise ValueError(f"Meta long-lived exchange error: {long_data['error'].get('message', long_data)}")

            return long_data

    @classmethod
    async def resolve_instagram_account(cls, long_lived_user_token: str) -> Dict[str, Any]:
        """Discover linked Facebook Page and connected Instagram Business/Creator account."""
        if long_lived_user_token.startswith("mock_"):
            return {
                "page_id": "100998877665544",
                "page_name": "Autopilot Creators",
                "page_access_token": "mock_page_token_999",
                "instagram_user_id": "17841400000000001",
                "username": "autopilot_reels",
                "name": "AI Reels Autopilot",
                "profile_picture_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150",
                "followers_count": 12480,
                "follows_count": 142,
                "media_count": 86
            }

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Fetch user pages
            pages_url = f"{cls.GRAPH_API_BASE}/{settings.instagram_api_version}/me/accounts"
            pages_resp = await client.get(pages_url, params={"access_token": long_lived_user_token})
            pages_data = pages_resp.json()
            if "error" in pages_data:
                raise ValueError(f"Failed to query Facebook pages: {pages_data['error'].get('message')}")

            pages = pages_data.get("data", [])
            if not pages:
                raise ValueError("No Facebook Pages found. An Instagram Business/Creator account must be linked to a Facebook Page.")

            # 2. Iterate pages to find the one linked to an Instagram Business account
            ig_user_id = None
            page_id = None
            page_name = None
            page_token = None

            for page in pages:
                p_id = page["id"]
                p_token = page.get("access_token", long_lived_user_token)
                ig_check_url = f"{cls.GRAPH_API_BASE}/{settings.instagram_api_version}/{p_id}"
                ig_resp = await client.get(
                    ig_check_url,
                    params={"fields": "instagram_business_account,name", "access_token": p_token}
                )
                ig_data = ig_resp.json()
                if "instagram_business_account" in ig_data and ig_data["instagram_business_account"]:
                    ig_user_id = ig_data["instagram_business_account"]["id"]
                    page_id = p_id
                    page_name = ig_data.get("name", page.get("name"))
                    page_token = p_token
                    break

            if not ig_user_id:
                raise ValueError(
                    "No Instagram Business or Creator account found attached to your Facebook Pages. "
                    "Ensure your Instagram account is Professional (Creator or Business) and linked to a Facebook Page."
                )

            # 3. Query Instagram Profile details
            profile_url = f"{cls.GRAPH_API_BASE}/{settings.instagram_api_version}/{ig_user_id}"
            fields = "id,username,name,profile_picture_url,followers_count,follows_count,media_count"
            prof_resp = await client.get(
                profile_url,
                params={"fields": fields, "access_token": page_token or long_lived_user_token}
            )
            prof_data = prof_resp.json()
            if "error" in prof_data:
                raise ValueError(f"Failed to fetch Instagram profile: {prof_data['error'].get('message')}")

            return {
                "page_id": page_id,
                "page_name": page_name,
                "page_access_token": page_token,
                "instagram_user_id": ig_user_id,
                "username": prof_data.get("username", "instagram_creator"),
                "name": prof_data.get("name", "Creator"),
                "profile_picture_url": prof_data.get("profile_picture_url"),
                "followers_count": prof_data.get("followers_count", 0),
                "follows_count": prof_data.get("follows_count", 0),
                "media_count": prof_data.get("media_count", 0)
            }
