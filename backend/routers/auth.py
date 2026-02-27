"""
NEXUS — Auth Router
POST /api/auth/signup
POST /api/auth/login
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from backend.models import SignupRequest, LoginRequest, AuthResponse
from services.db_service import get_user_by_email, create_user, get_user_by_id
import bcrypt

router = APIRouter()


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _check_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest):
    if len(req.password) < 6:
        return AuthResponse(success=False, message="Password must be at least 6 characters.")

    existing = get_user_by_email(req.email)
    if existing:
        return AuthResponse(success=False, message="An account with this email already exists.")

    hashed = _hash_pw(req.password)
    user_id = create_user(req.email, hashed, req.name)
    user = get_user_by_id(user_id)

    return AuthResponse(
        success=True,
        message="Account created successfully!",
        user_id=str(user["_id"]),
        user_name=user.get("name", ""),
        user_email=user.get("email", ""),
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user:
        return AuthResponse(success=False, message="No account found with this email.")

    if user.get("auth_provider") == "google":
        return AuthResponse(success=False, message="This account uses Google Sign-In.")

    if not _check_pw(req.password, user["password"]):
        return AuthResponse(success=False, message="Incorrect password.")

    return AuthResponse(
        success=True,
        message="Welcome back!",
        user_id=str(user["_id"]),
        user_name=user.get("name", ""),
        user_email=user.get("email", ""),
    )
