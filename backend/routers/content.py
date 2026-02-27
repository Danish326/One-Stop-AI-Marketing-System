"""
NEXUS — Content Router
CRUD + AI generation endpoints for campaign content.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from backend.models import ContentUpdate, GenerateRequest
from services.db_service import (
    get_content, save_content, update_content, delete_campaign_content, get_campaign
)
from services.ai_service import generate_content as ai_generate, regenerate_single as ai_regen

router = APIRouter()


def _doc_to_dict(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "campaign_id": doc.get("campaign_id", ""),
        "channel": doc.get("channel", ""),
        "content_type": doc.get("content_type", ""),
        "body": doc.get("body", ""),
        "hashtags": doc.get("hashtags", []),
        "posting_time_suggestion": doc.get("posting_time_suggestion", ""),
        "ai_score": doc.get("ai_score", 0),
        "score_reasoning": doc.get("score_reasoning", ""),
        "status": doc.get("status", "draft"),
        "is_edited": doc.get("is_edited", False),
        "scheduled_at": str(doc.get("scheduled_at", "")) if doc.get("scheduled_at") else None,
        "published_at": str(doc.get("published_at", "")) if doc.get("published_at") else None,
        "created_at": str(doc.get("created_at", "")),
    }


@router.get("/{campaign_id}")
def list_content(campaign_id: str, channel: str = None):
    docs = get_content(campaign_id, channel)
    return [_doc_to_dict(d) for d in docs]


@router.patch("/{content_id}/update")
def patch_content(content_id: str, req: ContentUpdate):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_content(content_id, updates)
    return {"success": True}


@router.post("/generate")
def generate_content_endpoint(req: GenerateRequest):
    """
    Generate AI content for a campaign.
    Only generates for channels that don't already have content,
    preserving any scheduled/published pieces.
    """
    campaign = get_campaign(req.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Check which channels already have content
    existing = get_content(req.campaign_id)
    existing_channels = {doc.get("channel") for doc in existing}
    all_channels = campaign.get("channels", [])
    missing_channels = [ch for ch in all_channels if ch not in existing_channels]

    if not missing_channels:
        # All channels already have content — return existing
        docs = get_content(req.campaign_id)
        return {
            "success": True,
            "message": "All channels already have content. Use Regenerate on individual cards to refresh.",
            "content": [_doc_to_dict(d) for d in docs],
        }

    # Generate only for missing channels
    campaign_for_gen = dict(campaign)
    campaign_for_gen["channels"] = missing_channels
    content_pieces = ai_generate(campaign_for_gen, business_name=req.business_name)

    if not content_pieces:
        docs = get_content(req.campaign_id)
        return {
            "success": True,
            "message": "No new content generated.",
            "content": [_doc_to_dict(d) for d in docs],
        }

    # Save new pieces (existing ones are untouched)
    saved_ids = save_content(req.campaign_id, content_pieces)

    # Return ALL content (existing + new)
    docs = get_content(req.campaign_id)
    return {
        "success": True,
        "message": f"Generated {len(saved_ids)} new content piece(s) for: {', '.join(missing_channels)}.",
        "content": [_doc_to_dict(d) for d in docs],
    }


@router.post("/regenerate/{content_id}")
def regenerate_single_endpoint(content_id: str, req: GenerateRequest):
    """
    Regenerate a single content piece by its ID.
    """
    campaign = get_campaign(req.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get the existing content piece to know its channel/type
    existing = get_content(req.campaign_id)
    target = None
    for doc in existing:
        if str(doc["_id"]) == content_id:
            target = doc
            break

    if not target:
        raise HTTPException(status_code=404, detail="Content piece not found")

    # Regenerate using AI
    new_piece = ai_regen(
        campaign,
        channel=target["channel"],
        content_type=target["content_type"],
        business_name=req.business_name,
    )

    # Update the existing document
    update_content(content_id, {
        "body": new_piece.get("body", ""),
        "hashtags": new_piece.get("hashtags", []),
        "posting_time_suggestion": new_piece.get("posting_time_suggestion", ""),
        "ai_score": new_piece.get("ai_score", 0),
        "score_reasoning": new_piece.get("score_reasoning", ""),
        "is_edited": False,
    })

    return {"success": True, "message": "Content regenerated."}


@router.delete("/{campaign_id}")
def delete_content(campaign_id: str):
    delete_campaign_content(campaign_id)
    return {"success": True, "message": "All content deleted for campaign."}
