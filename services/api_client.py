"""
NEXUS — API Client
Streamlit frontend calls this module to interact with the FastAPI backend.
All HTTP requests to the backend go through here.
"""

import requests

# ── Backend URL ──────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

_session = requests.Session()


def _url(path: str) -> str:
    return f"{API_BASE}{path}"


def _handle(resp: requests.Response) -> dict:
    """Parse JSON response, raise on HTTP errors."""
    try:
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        try:
            return resp.json()
        except Exception:
            return {"success": False, "message": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════════════════════

def signup(name: str, email: str, password: str) -> dict:
    resp = _session.post(_url("/auth/signup"), json={
        "name": name, "email": email, "password": password,
    })
    return _handle(resp)


def login(email: str, password: str) -> dict:
    resp = _session.post(_url("/auth/login"), json={
        "email": email, "password": password,
    })
    return _handle(resp)


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGNS
# ═══════════════════════════════════════════════════════════════════════════════

def create_campaign(data: dict) -> dict:
    resp = _session.post(_url("/campaigns/"), json=data)
    return _handle(resp)


def list_campaigns(user_id: str = None) -> list:
    params = {"user_id": user_id} if user_id else {}
    resp = _session.get(_url("/campaigns/"), params=params)
    return _handle(resp)


def get_campaign(campaign_id: str) -> dict:
    resp = _session.get(_url(f"/campaigns/{campaign_id}"))
    return _handle(resp)


def update_campaign(campaign_id: str, updates: dict) -> dict:
    resp = _session.patch(_url(f"/campaigns/{campaign_id}"), json=updates)
    return _handle(resp)


def delete_campaign(campaign_id: str) -> dict:
    resp = _session.delete(_url(f"/campaigns/{campaign_id}"))
    return _handle(resp)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

def list_content(campaign_id: str, channel: str = None) -> list:
    params = {"channel": channel} if channel else {}
    resp = _session.get(_url(f"/content/{campaign_id}"), params=params)
    return _handle(resp)


def update_content(content_id: str, updates: dict) -> dict:
    resp = _session.patch(_url(f"/content/{content_id}/update"), json=updates)
    return _handle(resp)


def generate_content(campaign_id: str, business_name: str = "My Business") -> dict:
    resp = _session.post(_url("/content/generate"), json={
        "campaign_id": campaign_id, "business_name": business_name,
    })
    return _handle(resp)


def regenerate_content(content_id: str, campaign_id: str, business_name: str = "My Business") -> dict:
    resp = _session.post(_url(f"/content/regenerate/{content_id}"), json={
        "campaign_id": campaign_id, "business_name": business_name,
    })
    return _handle(resp)


def delete_content(campaign_id: str) -> dict:
    resp = _session.delete(_url(f"/content/{campaign_id}"))
    return _handle(resp)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def get_analytics(campaign_id: str) -> dict:
    resp = _session.get(_url(f"/analytics/{campaign_id}"))
    return _handle(resp)


def seed_analytics(campaign_id: str) -> dict:
    resp = _session.post(_url(f"/analytics/{campaign_id}/seed"))
    return _handle(resp)


def get_insights(campaign_id: str, business_name: str = "", objective: str = "") -> dict:
    resp = _session.post(_url("/analytics/insights"), json={
        "campaign_id": campaign_id,
        "business_name": business_name,
        "campaign_objective": objective,
    })
    return _handle(resp)


# ═══════════════════════════════════════════════════════════════════════════════
#  CORRESPONDENCE
# ═══════════════════════════════════════════════════════════════════════════════

def list_correspondence(campaign_id: str, type_filter: str = None) -> list:
    params = {"type": type_filter} if type_filter else {}
    resp = _session.get(_url(f"/correspondence/{campaign_id}"), params=params)
    return _handle(resp)


def draft_reply(campaign_id: str, customer_message: str,
                business_name: str = "", brand_tone: str = "",
                campaign_objective: str = "") -> dict:
    resp = _session.post(_url("/correspondence/reply"), json={
        "campaign_id": campaign_id,
        "customer_message": customer_message,
        "business_name": business_name,
        "brand_tone": brand_tone,
        "campaign_objective": campaign_objective,
    })
    return _handle(resp)


def save_faq(campaign_id: str, question: str, answer: str) -> dict:
    resp = _session.post(_url("/correspondence/faq"), json={
        "campaign_id": campaign_id,
        "question": question,
        "answer": answer,
    })
    return _handle(resp)
