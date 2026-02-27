"""
NEXUS — Authentication Service
Now calls the FastAPI backend via api_client instead of db_service directly.
Handles session management on the Streamlit side.
"""

import streamlit as st
from services import api_client


# ─── Session Helpers ────────────────────────────────────────────────────────────

def init_session():
    """Ensure auth keys exist in session state."""
    defaults = {
        "authenticated": False,
        "user_id": None,
        "user_name": None,
        "user_email": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_session(data: dict):
    """Populate session state after successful auth."""
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = data.get("user_id", "")
    st.session_state["user_name"] = data.get("user_name", "User")
    st.session_state["user_email"] = data.get("user_email", "")
    # Reset campaign state for the new user
    st.session_state["active_campaign"] = None
    st.session_state["editing_campaign"] = None
    st.session_state["generated_content"] = None
    st.session_state["current_page"] = "Dashboard"


def logout():
    """Clear ALL session state so nothing leaks between users."""
    keys_to_clear = [
        "authenticated", "user_id", "user_name", "user_email",
        "active_campaign", "editing_campaign", "generated_content",
        "last_reply", "current_page",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["authenticated"] = False


def is_authenticated() -> bool:
    """Check if user is currently logged in."""
    return st.session_state.get("authenticated", False)


# ─── Auth via FastAPI ───────────────────────────────────────────────────────────

def signup(name: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user via the backend API."""
    if not name or not email or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        result = api_client.signup(name, email, password)
    except Exception as e:
        return False, f"Cannot reach backend: {e}"

    if result.get("success"):
        set_session(result)
        return True, result.get("message", "Account created!")
    return False, result.get("message", "Signup failed.")


def login(email: str, password: str) -> tuple[bool, str]:
    """Authenticate via the backend API."""
    if not email or not password:
        return False, "Email and password are required."

    try:
        result = api_client.login(email, password)
    except Exception as e:
        return False, f"Cannot reach backend: {e}"

    if result.get("success"):
        set_session(result)
        return True, result.get("message", "Welcome back!")
    return False, result.get("message", "Login failed.")


# ─── Google SSO (Scaffold) ──────────────────────────────────────────────────────

def google_sso_callback(user_info: dict) -> tuple[bool, str]:
    """Placeholder for future Google OAuth flow."""
    return False, "Google SSO not yet implemented."
