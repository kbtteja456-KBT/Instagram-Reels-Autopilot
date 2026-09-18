"""Unit tests for Meta Graph API OAuth 2.0 flow and signed state tokens."""

import asyncio
from backend.app.core.security import generate_oauth_state, verify_oauth_state
from backend.app.core.oauth import MetaOAuthManager


def test_oauth_state_signing_and_verification():
    """Verify HMAC-SHA256 state token generation and tamper verification."""
    workspace_id = "ws_test_123"
    user_id = "usr_test_456"

    state = generate_oauth_state(workspace_id, user_id)
    assert state is not None
    assert len(state.split(":")) == 4

    verified = verify_oauth_state(state)
    assert verified is not None
    v_ws, v_usr = verified
    assert v_ws == workspace_id
    assert v_usr == user_id


def test_tampered_oauth_state_rejected():
    """Verify that modified state tokens are strictly rejected."""
    state = generate_oauth_state("ws_1", "usr_1")
    tampered_state = state.replace("ws_1", "ws_hacked")
    
    verified = verify_oauth_state(tampered_state)
    assert verified is None


def test_meta_authorization_url_generation():
    """Verify official Meta OAuth dialog URL formatting and required scopes."""
    url = MetaOAuthManager.get_authorization_url("ws_prod", "usr_owner")
    assert "https://www.facebook.com" in url
    assert "dialog/oauth" in url
    assert "client_id=" in url
    assert "instagram_content_publish" in url
    assert "instagram_basic" in url
    assert "pages_show_list" in url
    assert "state=" in url


def test_mock_token_exchange():
    """Verify token exchange in mock/test sandbox."""
    async def _run():
        tokens = await MetaOAuthManager.exchange_code_for_tokens("mock_auth_code_999")
        assert "access_token" in tokens
        assert tokens["expires_in"] > 0

        profile = await MetaOAuthManager.resolve_instagram_account(tokens["access_token"])
        assert "instagram_user_id" in profile
        assert profile["username"] == "autopilot_reels"
        assert profile["followers_count"] > 0

    asyncio.run(_run())
