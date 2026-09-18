"""AES-256 Fernet encryption, password hashing, HMAC signing, and SHA-256 file hashing."""

import hashlib
import hmac
import os
import time
from typing import Optional, Tuple
from cryptography.fernet import Fernet
import bcrypt

from backend.app.config import settings
from backend.app.core.logging import logger

_fernet_instance: Optional[Fernet] = None


def get_encryption_key() -> str:
    """Retrieve or validate the Fernet encryption key from settings."""
    key = settings.encryption_key
    if not key or len(key) < 32:
        raise ValueError("ENCRYPTION_KEY must be a valid 32-byte url-safe base64 string.")
    return key


def get_fernet() -> Fernet:
    """Lazy singleton for Fernet cipher."""
    global _fernet_instance
    if _fernet_instance is None:
        key = get_encryption_key()
        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet_instance


def encrypt_token(plain_token: str) -> str:
    """Encrypt plain string token to AES-256 ciphertext."""
    if not plain_token:
        return ""
    f = get_fernet()
    return f.encrypt(plain_token.encode("utf-8")).decode("utf-8")


def decrypt_token(cipher_token: str) -> str:
    """Decrypt AES-256 ciphertext back to plain string token."""
    if not cipher_token:
        return ""
    f = get_fernet()
    return f.decrypt(cipher_token.encode("utf-8")).decode("utf-8")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def compute_file_hash(filepath: str) -> str:
    """Calculate the SHA-256 checksum of a file to prevent duplicate uploads."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_oauth_state(workspace_id: str, user_id: str) -> str:
    """Generate an HMAC-SHA256 signed state string {workspace_id}:{user_id}:{timestamp}:{signature}."""
    timestamp = str(int(time.time()))
    payload = f"{workspace_id}:{user_id}:{timestamp}"
    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_oauth_state(state_str: str, max_age_seconds: int = 1800) -> Optional[Tuple[str, str]]:
    """Verify HMAC signature and timestamp expiry (default 30 min window). Returns (workspace_id, user_id) or None."""
    try:
        parts = state_str.split(":")
        if len(parts) != 4:
            return None
        workspace_id, user_id, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        
        # Check expiration
        now = int(time.time())
        if abs(now - timestamp) > max_age_seconds:
            logger.warning(f"[OAuth] State expired: timestamp {timestamp} vs now {now}")
            return None
            
        payload = f"{workspace_id}:{user_id}:{timestamp_str}"
        expected_sig = hmac.new(
            settings.jwt_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(expected_sig, signature):
            return workspace_id, user_id
        return None
    except Exception as e:
        logger.error(f"[OAuth] State verification failed: {e}")
        return None
