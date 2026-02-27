"""
NEXUS — AI Service
Handles all Gemini AI interactions: content generation, scoring, insights, replies.
Phase 3 implements the Content Generator agent.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini Client ──────────────────────────────────────────────────────────────

_client = None
_api_available = False


def _init_client():
    """Initialize the Google GenAI client if API key is set."""
    global _client, _api_available

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key.startswith("<"):
        print("⚠️  GEMINI_API_KEY not configured — AI features will use fallback content.")
        _api_available = False
        return

    try:
        import google.genai
        _client = google.genai.Client(api_key=api_key)
        _api_available = True
        print("✅ Google Gemini API client initialized.")
    except Exception as e:
        print(f"⚠️  Gemini API init failed ({e}) — using fallback content.")
        _api_available = False


_init_client()


# ─── Config ─────────────────────────────────────────────────────────────────────

AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT GENERATOR (Agent 1)
# ═══════════════════════════════════════════════════════════════════════════════

CONTENT_PROMPT = """You are an expert marketing strategist and copywriter.

A business called "{business_name}" is running a marketing campaign.

Campaign Details:
- Objective: {objective}
- Target Audience: {audience}
- Brand Tone: {tone}
- Duration: {duration_weeks} weeks
- Channels: {channels}

Generate one piece of platform-specific marketing content for EACH of the following channels: {channels}.

For each channel, return:
- channel: the platform name (lowercase: instagram, facebook, tiktok, email, sms)
- content_type: the format (caption / post / script / email / sms)
- body: the full content copy (make it compelling, on-brand, and optimized for the platform)
- hashtags: list of 3–5 relevant hashtags (for social channels only, empty list for email/sms)
- posting_time_suggestion: best day and time to post
- ai_score: your quality score from 0 to 100
- score_reasoning: one sentence explaining the score

Return ONLY a valid JSON array. No explanation. No markdown. No preamble.

Example structure:
[
  {{
    "channel": "instagram",
    "content_type": "caption",
    "body": "...",
    "hashtags": ["#example"],
    "posting_time_suggestion": "Tuesday 7PM",
    "ai_score": 88,
    "score_reasoning": "Strong hook and clear CTA with relevant hashtags."
  }}
]"""


SINGLE_REGEN_PROMPT = """You are an expert marketing strategist and copywriter.

A business called "{business_name}" is running a marketing campaign.

Campaign Details:
- Objective: {objective}
- Target Audience: {audience}
- Brand Tone: {tone}
- Duration: {duration_weeks} weeks

Generate a NEW, DIFFERENT piece of marketing content for the "{channel}" channel.
Content type: {content_type}

Return ONLY a valid JSON object (not an array). No explanation. No markdown. No preamble.

{{
  "channel": "{channel}",
  "content_type": "{content_type}",
  "body": "...",
  "hashtags": ["#example"],
  "posting_time_suggestion": "Tuesday 7PM",
  "ai_score": 85,
  "score_reasoning": "Strong hook and clear CTA."
}}"""


def generate_content(campaign: dict, business_name: str = "My Business") -> list:
    """
    Generate marketing content for all channels in a campaign.
    Returns a list of content piece dicts.
    """
    channels = campaign.get("channels", [])
    if not channels:
        return []

    prompt = CONTENT_PROMPT.format(
        business_name=business_name,
        objective=campaign.get("objective", ""),
        audience=campaign.get("audience", ""),
        tone=campaign.get("tone", ""),
        duration_weeks=campaign.get("duration_weeks", 1),
        channels=", ".join(channels),
    )

    if not _api_available:
        return _fallback_content(campaign)

    return _call_gemini_json_array(prompt, fallback_fn=lambda: _fallback_content(campaign))


def regenerate_single(campaign: dict, channel: str, content_type: str,
                      business_name: str = "My Business") -> dict:
    """
    Regenerate a single content piece for one channel.
    Returns a single content piece dict.
    """
    prompt = SINGLE_REGEN_PROMPT.format(
        business_name=business_name,
        objective=campaign.get("objective", ""),
        audience=campaign.get("audience", ""),
        tone=campaign.get("tone", ""),
        duration_weeks=campaign.get("duration_weeks", 1),
        channel=channel,
        content_type=content_type,
    )

    if not _api_available:
        return _fallback_single(channel, content_type)

    return _call_gemini_json_object(prompt, fallback_fn=lambda: _fallback_single(channel, content_type))


# ═══════════════════════════════════════════════════════════════════════════════
#  GEMINI API HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _call_gemini_json_array(prompt: str, fallback_fn=None) -> list:
    """Call Gemini and parse JSON array response."""
    import google.genai.types as types
    try:
        response = _client.models.generate_content(
            model=AI_MODEL,
            contents=prompt,
        )
        text = response.text.strip()

        # Strip potential markdown fencing
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3].strip()

        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️  Gemini returned invalid JSON: {e}")
        return fallback_fn() if fallback_fn else []
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
        return fallback_fn() if fallback_fn else []


def _call_gemini_json_object(prompt: str, fallback_fn=None) -> dict:
    """Call Gemini and parse JSON object response."""
    import google.genai.types as types
    try:
        response = _client.models.generate_content(
            model=AI_MODEL,
            contents=prompt,
        )
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3].strip()

        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️  Gemini returned invalid JSON: {e}")
        return fallback_fn() if fallback_fn else {}
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
        return fallback_fn() if fallback_fn else {}


# ═══════════════════════════════════════════════════════════════════════════════
#  FALLBACK CONTENT (demo-safe, no API key required)
# ═══════════════════════════════════════════════════════════════════════════════

_CHANNEL_TEMPLATES = {
    "instagram": {
        "content_type": "caption",
        "body": "✨ Something exciting is coming your way! Our new campaign is live and we can't wait for you to see what's in store. Stay tuned for more! 🔥\n\nTap the link in bio to learn more 👆",
        "hashtags": ["#NewLaunch", "#Marketing", "#StayTuned", "#Excited", "#ComingSoon"],
        "posting_time_suggestion": "Wednesday 6PM",
        "ai_score": 78,
        "score_reasoning": "Solid engagement hook with clear CTA, but could be more specific to the campaign."
    },
    "facebook": {
        "content_type": "post",
        "body": "Big things are happening! 🎉\n\nWe're thrilled to announce our latest campaign. Whether you're a long-time fan or just discovering us, there's something for everyone.\n\n👉 Check it out now and let us know what you think in the comments!",
        "hashtags": ["#Announcement", "#Community"],
        "posting_time_suggestion": "Thursday 1PM",
        "ai_score": 75,
        "score_reasoning": "Good community tone, encourages engagement. Could benefit from more specific details."
    },
    "tiktok": {
        "content_type": "script",
        "body": "[HOOK - 0:00] \"Wait until you see this...\"\n[BODY - 0:03] Show the product/service with trending audio\n[CTA - 0:12] \"Follow for more and comment your thoughts!\"\n\nUse trending sound 🔊 | Keep it under 15 seconds",
        "hashtags": ["#ForYou", "#Trending", "#SmallBusiness", "#Viral"],
        "posting_time_suggestion": "Friday 8PM",
        "ai_score": 72,
        "score_reasoning": "Good TikTok format with hook-body-CTA structure. Needs specific content."
    },
    "email": {
        "content_type": "email",
        "body": "Subject: You're Invited! Something Special Inside 🎁\n\nHi there,\n\nWe've been working on something special and couldn't wait to share it with you.\n\nAs a valued member of our community, you're getting first access to our latest campaign.\n\n[CTA BUTTON: Learn More →]\n\nDon't miss out — this is one you'll want to see.\n\nWarm regards,\nThe Team",
        "hashtags": [],
        "posting_time_suggestion": "Tuesday 10AM",
        "ai_score": 80,
        "score_reasoning": "Professional email structure with clear CTA. Subject line drives opens."
    },
    "sms": {
        "content_type": "sms",
        "body": "Hey! 🎉 Something exciting just dropped. Check it out before everyone else: [LINK]. Reply STOP to opt out.",
        "hashtags": [],
        "posting_time_suggestion": "Monday 11AM",
        "ai_score": 70,
        "score_reasoning": "Concise and action-oriented. Includes required opt-out. Could be more specific."
    },
}


def _fallback_content(campaign: dict) -> list:
    """Generate demo content when Gemini API is unavailable."""
    channels = campaign.get("channels", [])
    results = []
    for ch in channels:
        template = _CHANNEL_TEMPLATES.get(ch, _CHANNEL_TEMPLATES["facebook"]).copy()
        template["channel"] = ch
        results.append(template)
    return results


def _fallback_single(channel: str, content_type: str) -> dict:
    """Generate a single fallback piece."""
    template = _CHANNEL_TEMPLATES.get(channel, _CHANNEL_TEMPLATES["facebook"]).copy()
    template["channel"] = channel
    template["content_type"] = content_type
    template["body"] = template["body"] + "\n\n[Regenerated — fallback content]"
    return template


# ═══════════════════════════════════════════════════════════════════════════════
#  INSIGHTS ANALYST (Agent 2) — Phase 5
# ═══════════════════════════════════════════════════════════════════════════════

INSIGHTS_PROMPT = """You are a senior marketing analytics strategist.

A business called "{business_name}" ran a campaign with objective: "{objective}".

Here is the cross-channel performance data:
{analytics_json}

Analyse this data and produce exactly 4 strategic insights. Each insight should answer one of:
1. Which content type or channel performs best and why?
2. Which channel drives the most engagement relative to reach?
3. What is the optimal posting time window based on the data?
4. What specific action should the business take for the next campaign iteration?

Return ONLY a valid JSON array. No explanation. No markdown. No preamble.

[
  {{
    "title": "Short Insight Title",
    "insight": "A 2-3 sentence analytical observation backed by the data.",
    "recommendation": "A specific, actionable recommendation."
  }}
]"""


def generate_insights(analytics_data: dict, campaign: dict,
                      business_name: str = "My Business") -> list:
    """
    Generate AI-powered strategic insights from analytics data.
    Returns a list of insight dicts with title, insight, recommendation.
    """
    prompt = INSIGHTS_PROMPT.format(
        business_name=business_name,
        objective=campaign.get("objective", ""),
        analytics_json=json.dumps(analytics_data.get("channels", {}), indent=2),
    )

    if not _api_available:
        return _fallback_insights(analytics_data)

    return _call_gemini_json_array(prompt, fallback_fn=lambda: _fallback_insights(analytics_data))


def _fallback_insights(analytics_data: dict) -> list:
    """Generate demo insights when Gemini API is unavailable."""
    channels = analytics_data.get("channels", {})
    totals = analytics_data.get("totals", {})

    # Find best performing channel
    best_ch = max(channels, key=lambda c: channels[c].get("engagement_rate", 0)) if channels else "instagram"
    best_data = channels.get(best_ch, {})

    # Find highest reach channel
    top_reach = max(channels, key=lambda c: channels[c].get("reach", 0)) if channels else "instagram"

    return [
        {
            "title": f"🏆 {best_ch.title()} Leads in Engagement",
            "insight": f"{best_ch.title()} achieves a {best_data.get('engagement_rate', 0)}% engagement rate, "
                       f"outperforming other channels. With {best_data.get('clicks', 0):,} clicks from "
                       f"{best_data.get('reach', 0):,} reach, it demonstrates superior audience resonance.",
            "recommendation": f"Double down on {best_ch.title()} content. Increase posting frequency by 30% "
                             f"and allocate more budget to this channel for the next campaign cycle."
        },
        {
            "title": f"📊 {top_reach.title()} Dominates Reach",
            "insight": f"{top_reach.title()} delivers the highest reach at {channels.get(top_reach, {}).get('reach', 0):,} "
                       f"impressions. This channel excels at top-of-funnel awareness, making it ideal for brand visibility campaigns.",
            "recommendation": "Use this channel for brand awareness content and pair it with retargeting "
                             "on higher-converting channels to maximize the full funnel."
        },
        {
            "title": "⏰ Optimize Posting Schedule",
            "insight": f"Top performing content is concentrated during evening hours. "
                       f"With {totals.get('clicks', 0):,} total clicks across all channels, "
                       f"timing plays a critical role in audience engagement.",
            "recommendation": "Shift 60% of posts to the 5PM-9PM window. Test weekend posts "
                             "to capture untapped leisure-time browsing audiences."
        },
        {
            "title": "🎯 Next Campaign Strategy",
            "insight": f"The campaign generated {totals.get('conversions', 0):,} total conversions "
                       f"across {len(channels)} channels with an average engagement rate of "
                       f"{totals.get('engagement_rate', 0)}%. The conversion funnel shows room for optimization.",
            "recommendation": "For the next iteration: A/B test content variations on your top 2 channels, "
                             "add stronger CTAs, and implement retargeting sequences for engaged non-converters."
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  REPLY COMPOSER (Agent 3) — Phase 6
# ═══════════════════════════════════════════════════════════════════════════════

REPLY_PROMPT = """You are an expert customer service representative for a business called "{business_name}".

Campaign context:
- Objective: {objective}
- Brand Tone: {brand_tone}

A customer sent this message:
---
{customer_message}
---

Draft a professional reply that:
1. Addresses the customer's concern or question directly
2. Matches the brand tone specified above
3. Is helpful, empathetic, and action-oriented
4. Includes a clear next step

Also assess your confidence in the reply (0.0 to 1.0):
- 1.0 = Standard question, very confident the reply is correct
- 0.7-0.9 = Moderate confidence, likely a good reply
- 0.3-0.6 = Low confidence, the message may need human review
- Below 0.3 = Very uncertain, definitely needs escalation

Return ONLY a valid JSON object. No explanation. No markdown. No preamble.

{{
  "reply": "Your drafted reply here.",
  "confidence_score": 0.85,
  "escalate": false,
  "escalation_reason": ""
}}"""


def generate_reply(customer_message: str, campaign: dict,
                   business_name: str = "My Business",
                   brand_tone: str = "Professional") -> dict:
    """
    Generate an AI reply to a customer message.
    Returns dict with reply, confidence_score, escalate, escalation_reason.
    """
    prompt = REPLY_PROMPT.format(
        business_name=business_name,
        objective=campaign.get("objective", ""),
        brand_tone=brand_tone,
        customer_message=customer_message,
    )

    if not _api_available:
        return _fallback_reply(customer_message, brand_tone)

    return _call_gemini_json_object(prompt, fallback_fn=lambda: _fallback_reply(customer_message, brand_tone))


def _fallback_reply(customer_message: str, brand_tone: str = "Professional") -> dict:
    """Generate a demo reply when Gemini API is unavailable."""
    msg_lower = customer_message.lower()

    # Simple keyword-based reply generation
    if any(w in msg_lower for w in ["price", "cost", "pricing", "how much"]):
        reply = (
            f"Thank you for your interest in our pricing! We'd love to help you find the perfect plan.\n\n"
            f"Our pricing varies based on your specific needs. I'd recommend scheduling a quick call "
            f"with our team so we can understand your requirements and provide a tailored quote.\n\n"
            f"Would you like me to set that up for you?"
        )
        confidence = 0.82
    elif any(w in msg_lower for w in ["complaint", "issue", "problem", "broken", "not working", "disappointed"]):
        reply = (
            f"I'm truly sorry to hear about this issue. Your experience matters to us, and I want to make this right.\n\n"
            f"Could you provide me with your order number or account details so I can look into this immediately? "
            f"In the meantime, I've flagged this for priority handling.\n\n"
            f"We'll get this resolved for you as quickly as possible."
        )
        confidence = 0.65
    elif any(w in msg_lower for w in ["refund", "cancel", "money back"]):
        reply = (
            f"I understand your concern and I'm sorry for any inconvenience. "
            f"I'd like to help resolve this for you.\n\n"
            f"To process your request, I'll need to review your account details. "
            f"Could you share your order number? I'll escalate this to ensure a swift resolution.\n\n"
            f"Thank you for your patience."
        )
        confidence = 0.45
        return {
            "reply": reply,
            "confidence_score": confidence,
            "escalate": True,
            "escalation_reason": "Refund/cancellation requests require human approval."
        }
    elif any(w in msg_lower for w in ["thank", "great", "awesome", "love", "amazing"]):
        reply = (
            f"Thank you so much for your kind words! It means the world to us. 😊\n\n"
            f"We're always striving to deliver the best experience. If there's anything else "
            f"we can help with, don't hesitate to reach out!\n\n"
            f"Have a wonderful day!"
        )
        confidence = 0.95
    else:
        reply = (
            f"Thank you for reaching out! I appreciate your message.\n\n"
            f"I'd like to make sure I address your query properly. "
            f"Could you provide a bit more detail about what you're looking for? "
            f"That way, I can connect you with the right resources or provide a detailed answer.\n\n"
            f"Looking forward to helping you!"
        )
        confidence = 0.72

    escalate = confidence < 0.6
    return {
        "reply": reply,
        "confidence_score": confidence,
        "escalate": escalate,
        "escalation_reason": "Low confidence score — recommend human review." if escalate else ""
    }
