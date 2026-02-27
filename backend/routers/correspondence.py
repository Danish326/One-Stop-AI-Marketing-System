"""
NEXUS — Correspondence Router
AI reply drafting and FAQ management.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from backend.models import ReplyRequest, SaveFaqRequest
from services.db_service import save_correspondence, get_correspondence, get_campaign
from services.ai_service import generate_reply as ai_reply

router = APIRouter()


def _doc_to_dict(doc: dict) -> dict:
    result = {k: v for k, v in doc.items() if k != "_id"}
    result["id"] = str(doc["_id"])
    return result


@router.get("/{campaign_id}")
def list_correspondence(campaign_id: str, type: str = None):
    docs = get_correspondence(campaign_id, type)
    return [_doc_to_dict(d) for d in docs]


@router.post("/reply")
def draft_reply(req: ReplyRequest):
    """Generate an AI reply to a customer message."""
    campaign = get_campaign(req.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Call AI reply service
    result = ai_reply(
        customer_message=req.customer_message,
        campaign=campaign,
        business_name=req.business_name,
        brand_tone=req.brand_tone,
    )

    # Save to correspondence history
    doc = {
        "campaign_id": req.campaign_id,
        "type": "reply",
        "customer_message": req.customer_message,
        "ai_reply": result.get("reply", ""),
        "confidence_score": result.get("confidence_score", 0),
        "escalate": result.get("escalate", False),
        "escalation_reason": result.get("escalation_reason", ""),
        "saved_as_faq": False,
    }
    doc_id = save_correspondence(doc)

    return {
        "success": True,
        "id": doc_id,
        "reply": result.get("reply", ""),
        "confidence_score": result.get("confidence_score", 0),
        "escalate": result.get("escalate", False),
        "escalation_reason": result.get("escalation_reason", ""),
    }


@router.post("/faq")
def save_faq(req: SaveFaqRequest):
    doc = {
        "campaign_id": req.campaign_id,
        "type": "faq",
        "customer_message": req.question,
        "ai_reply": req.answer,
        "confidence_score": 1.0,
        "escalate": False,
        "saved_as_faq": True,
    }
    faq_id = save_correspondence(doc)
    return {"success": True, "id": faq_id}
