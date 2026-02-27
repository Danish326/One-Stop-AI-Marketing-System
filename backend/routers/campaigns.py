"""
NEXUS — Campaigns Router
CRUD endpoints for campaigns.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from backend.models import CampaignCreate, CampaignUpdate, CampaignResponse
from services.db_service import (
    save_campaign, get_campaigns, get_campaign, update_campaign, delete_campaign
)

router = APIRouter()


def _doc_to_response(doc: dict) -> dict:
    """Convert a MongoDB document to a JSON-safe dict."""
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "objective": doc.get("objective", ""),
        "audience": doc.get("audience", ""),
        "tone": doc.get("tone", ""),
        "channels": doc.get("channels", []),
        "duration_weeks": doc.get("duration_weeks", 1),
        "status": doc.get("status", "draft"),
        "created_at": str(doc.get("created_at", "")),
        "updated_at": str(doc.get("updated_at", "")),
    }


@router.post("/", response_model=CampaignResponse)
def create_campaign(req: CampaignCreate):
    data = req.model_dump()
    campaign_id = save_campaign(data)
    doc = get_campaign(campaign_id)
    return _doc_to_response(doc)


@router.get("/")
def list_campaigns(user_id: str = None):
    docs = get_campaigns(user_id)
    return [_doc_to_response(d) for d in docs]


@router.get("/{campaign_id}", response_model=CampaignResponse)
def read_campaign(campaign_id: str):
    doc = get_campaign(campaign_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _doc_to_response(doc)


@router.patch("/{campaign_id}")
def patch_campaign(campaign_id: str, req: CampaignUpdate):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_campaign(campaign_id, updates)
    doc = get_campaign(campaign_id)
    return _doc_to_response(doc)


@router.delete("/{campaign_id}")
def remove_campaign(campaign_id: str):
    doc = get_campaign(campaign_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found")
    delete_campaign(campaign_id)
    return {"success": True, "message": f"Campaign '{doc.get('name', '')}' deleted."}
