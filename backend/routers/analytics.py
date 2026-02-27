"""
NEXUS — Analytics Router
Get/seed analytics and AI insights for campaigns.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from backend.models import InsightRequest
from services.db_service import get_analytics, save_analytics, get_campaign
from utils.seed_analytics import generate_analytics_data
from services.ai_service import generate_insights as ai_insights

router = APIRouter()


def _doc_to_dict(doc: dict) -> dict:
    if not doc:
        return None
    result = {k: v for k, v in doc.items() if k != "_id"}
    result["id"] = str(doc["_id"])
    return result


@router.get("/{campaign_id}")
def read_analytics(campaign_id: str):
    doc = get_analytics(campaign_id)
    if not doc:
        return {"message": "No analytics found. Seed data first.", "data": None}
    return {"data": _doc_to_dict(doc)}


@router.post("/{campaign_id}/seed")
def seed_analytics(campaign_id: str):
    """Seed simulated analytics for a campaign."""
    campaign = get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Generate realistic simulated data
    analytics_data = generate_analytics_data(campaign)
    analytics_data["campaign_id"] = campaign_id

    # Save to DB (replaces existing)
    save_analytics(analytics_data)

    return {
        "success": True,
        "message": "Analytics data seeded successfully.",
        "data": analytics_data,
    }


@router.post("/insights")
def generate_insights(req: InsightRequest):
    """Generate AI insights from analytics data."""
    # Get analytics data first
    analytics_doc = get_analytics(req.campaign_id)
    if not analytics_doc:
        raise HTTPException(status_code=404, detail="No analytics data found. Seed data first.")

    campaign = get_campaign(req.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    # Call AI insights
    insights = ai_insights(
        analytics_data=analytics_doc,
        campaign=campaign,
        business_name=req.business_name,
    )

    # Save insights alongside analytics
    analytics_doc["insights"] = insights
    save_analytics(analytics_doc)

    return {
        "success": True,
        "insights": insights,
    }
