"""User registration, login, and workspace management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import uuid

from backend.app.core.security import hash_password, verify_password
from backend.app.core.auth import create_access_token, get_current_user
from backend.app.core.db import AsyncMongoDB
from backend.app.models.user import User, Workspace
from backend.app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# In-memory user store fallback for development/testing when MongoDB is not connected
_mock_users_db: Dict[str, Dict[str, Any]] = {
    "local@instagram-autopilot.internal": {
        "id": "usr_default_01",
        "email": "local@instagram-autopilot.internal",
        "hashed_password": hash_password("autopilot123"),
        "workspace_id": "default_workspace",
        "full_name": "Autopilot Creator",
        "role": "owner"
    },
    "kbtteja456@gmail.com": {
        "id": "usr_kbtteja",
        "email": "kbtteja456@gmail.com",
        "hashed_password": hash_password("@bhanuteja89"),
        "workspace_id": "default_workspace",
        "full_name": "Bhanu Teja",
        "role": "owner"
    }
}


@router.post("/register", response_model=AuthResponse)
async def register(req: AuthRequest):
    """Register a new user and create their tenant workspace."""
    db = AsyncMongoDB.get_db()
    
    # Check if user exists
    if db is not None:
        existing = await db.users.find_one({"email": req.email})
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
    elif req.email in _mock_users_db:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    workspace_id = f"ws_{uuid.uuid4().hex[:8]}"
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    hashed_pw = hash_password(req.password)

    user_data = {
        "_id": user_id,
        "email": req.email,
        "hashed_password": hashed_pw,
        "workspace_id": workspace_id,
        "full_name": req.full_name or req.email.split("@")[0],
        "role": "owner"
    }

    if db is not None:
        await db.users.insert_one(user_data)
        await db.workspaces.insert_one({
            "_id": workspace_id,
            "name": f"{user_data['full_name']}'s Workspace",
            "owner_id": user_id
        })
    else:
        _mock_users_db[req.email] = user_data

    token = create_access_token({
        "sub": user_id,
        "user_id": user_id,
        "workspace_id": workspace_id,
        "email": req.email,
        "role": "owner"
    })

    return AuthResponse(
        access_token=token,
        user={
            "id": user_id,
            "email": req.email,
            "workspace_id": workspace_id,
            "full_name": user_data["full_name"],
            "role": "owner"
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: AuthRequest):
    """Authenticate existing user and issue JWT."""
    db = AsyncMongoDB.get_db()
    user_data = None

    if db is not None:
        user_data = await db.users.find_one({"email": req.email})
    else:
        user_data = _mock_users_db.get(req.email)

    if not user_data or not verify_password(req.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    user_id = str(user_data.get("_id") or user_data.get("id"))
    workspace_id = user_data.get("workspace_id", "default_workspace")

    token = create_access_token({
        "sub": user_id,
        "user_id": user_id,
        "workspace_id": workspace_id,
        "email": user_data["email"],
        "role": user_data.get("role", "owner")
    })

    return AuthResponse(
        access_token=token,
        user={
            "id": user_id,
            "email": user_data["email"],
            "workspace_id": workspace_id,
            "full_name": user_data.get("full_name"),
            "role": user_data.get("role", "owner")
        }
    )


@router.get("/me")
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Return profile details of the authenticated user."""
    return user
