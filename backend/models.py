"""
NEXUS — Pydantic Models (Request / Response schemas)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════════════════════

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGNS
# ═══════════════════════════════════════════════════════════════════════════════

class CampaignCreate(BaseModel):
    name: str
    objective: str
    audience: str
    tone: str
    channels: list[str]
    duration_weeks: int
    user_id: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    objective: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    channels: Optional[list[str]] = None
    duration_weeks: Optional[int] = None
    status: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    name: str
    objective: str
    audience: str
    tone: str
    channels: list[str]
    duration_weeks: int
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

class ContentPiece(BaseModel):
    channel: str
    content_type: str
    body: str
    hashtags: Optional[list[str]] = []
    posting_time_suggestion: Optional[str] = None
    ai_score: Optional[int] = 0
    score_reasoning: Optional[str] = None

class ContentUpdate(BaseModel):
    body: Optional[str] = None
    status: Optional[str] = None
    hashtags: Optional[list[str]] = None
    is_edited: Optional[bool] = None
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None

class GenerateRequest(BaseModel):
    campaign_id: str
    business_name: Optional[str] = "My Business"


# ═══════════════════════════════════════════════════════════════════════════════
#  SCHEDULES
# ═══════════════════════════════════════════════════════════════════════════════

class ScheduleCreate(BaseModel):
    content_id: str
    campaign_id: str
    channel: str
    scheduled_at: str


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

class InsightRequest(BaseModel):
    campaign_id: str
    business_name: Optional[str] = "My Business"
    campaign_objective: Optional[str] = ""


# ═══════════════════════════════════════════════════════════════════════════════
#  CORRESPONDENCE
# ═══════════════════════════════════════════════════════════════════════════════

class ReplyRequest(BaseModel):
    campaign_id: str
    customer_message: str
    business_name: Optional[str] = "My Business"
    brand_tone: Optional[str] = "Professional"
    campaign_objective: Optional[str] = ""

class SaveFaqRequest(BaseModel):
    campaign_id: str
    question: str
    answer: str
