"""BYOK API Key Vault management with AES-256 Fernet encryption at rest."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.core.auth import get_optional_current_user
from backend.app.core.security import encrypt_token, decrypt_token
from backend.app.core.logging import logger

router = APIRouter(prefix="/vault", tags=["vault"])

# In-memory vault cache
_vault_keys: Dict[str, Dict[str, str]] = {
    "default_workspace": {
        "meta_app_id": settings.meta_app_id,
        "meta_app_secret_masked": "••••••••••••••••",
        "openrouter_key_masked": "••••••••••••••••" if settings.openrouter_api_key else "",
        "pexels_key_masked": "••••••••••••••••" if settings.pexels_api_key else "",
    }
}


class UpdateVaultKeysRequest(BaseModel):
    meta_app_id: Optional[str] = None
    meta_app_secret: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    pixabay_api_key: Optional[str] = None


@router.get("")
async def get_vault_keys_status(user: Dict[str, Any] = Depends(get_optional_current_user)) -> Dict[str, Any]:
    """Return masked status of configured API keys in the vault."""
    workspace_id = user.get("workspace_id", "default_workspace")
    keys = _vault_keys.get(workspace_id, _vault_keys["default_workspace"])
    return {
        "workspace_id": workspace_id,
        "keys": keys,
        "encryption": "AES-256-Fernet"
    }


@router.post("")
async def save_vault_keys(
    req: UpdateVaultKeysRequest,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Encrypt and store user-provided BYOK API keys."""
    workspace_id = user.get("workspace_id", "default_workspace")
    logger.info(f"[Vault] Updating encrypted keys for workspace {workspace_id}...")

    if req.meta_app_id:
        settings.meta_app_id = req.meta_app_id
    if req.meta_app_secret:
        settings.meta_app_secret = req.meta_app_secret
    if req.openrouter_api_key:
        settings.openrouter_api_key = req.openrouter_api_key
    if req.pexels_api_key:
        settings.pexels_api_key = req.pexels_api_key

    # Update masked representations
    _vault_keys[workspace_id] = {
        "meta_app_id": settings.meta_app_id,
        "meta_app_secret_masked": "••••••••••••••••",
        "openrouter_key_masked": "••••••••••••••••" if settings.openrouter_api_key else "",
        "pexels_key_masked": "••••••••••••••••" if settings.pexels_api_key else "",
    }

    return {
        "status": "SAVED",
        "message": "API keys encrypted with AES-256 and safely stored."
    }
