"""
NEXUS — Seed Analytics Utility
Generates realistic simulated engagement data per channel for a campaign.
"""

import random


def generate_analytics_data(campaign: dict) -> dict:
    """
    Generate realistic simulated analytics for each channel in a campaign.
    Returns a dict with per-channel metrics and totals.
    """
    channels = campaign.get("channels", [])
    if not channels:
        return {}

    channel_data = {}
    total_reach = 0
    total_clicks = 0
    total_conversions = 0
    total_impressions = 0
    total_shares = 0
    total_comments = 0

    # Base ranges per channel (simulating realistic relative performance)
    _CHANNEL_RANGES = {
        "instagram": {"reach": (8000, 25000), "ctr": (3.5, 6.0), "conv_rate": (0.4, 0.8)},
        "facebook":  {"reach": (5000, 18000), "ctr": (2.0, 4.5), "conv_rate": (0.3, 0.6)},
        "tiktok":    {"reach": (10000, 50000), "ctr": (4.0, 8.0), "conv_rate": (0.2, 0.5)},
        "email":     {"reach": (2000, 8000),   "ctr": (2.5, 5.5), "conv_rate": (0.8, 2.0)},
        "sms":       {"reach": (1000, 5000),   "ctr": (3.0, 7.0), "conv_rate": (1.0, 3.0)},
    }

    for ch in channels:
        ranges = _CHANNEL_RANGES.get(ch, _CHANNEL_RANGES["facebook"])

        reach = random.randint(*ranges["reach"])
        impressions = int(reach * random.uniform(1.3, 1.8))
        engagement_rate = round(random.uniform(*ranges["ctr"]), 1)
        clicks = int(impressions * engagement_rate / 100)
        conv_rate = random.uniform(*ranges["conv_rate"])
        conversions = int(clicks * conv_rate / 100) + random.randint(5, 30)
        shares = random.randint(50, 400)
        comments = random.randint(30, 250)
        likes = int(reach * random.uniform(0.03, 0.12))

        channel_data[ch] = {
            "reach": reach,
            "impressions": impressions,
            "clicks": clicks,
            "engagement_rate": engagement_rate,
            "conversions": conversions,
            "shares": shares,
            "comments": comments,
            "likes": likes,
            "best_post_time": _random_time(),
            "top_content_type": _random_content_type(ch),
        }

        total_reach += reach
        total_clicks += clicks
        total_conversions += conversions
        total_impressions += impressions
        total_shares += shares
        total_comments += comments

    avg_engagement = round(sum(
        channel_data[ch]["engagement_rate"] for ch in channels
    ) / len(channels), 1) if channels else 0

    return {
        "campaign_id": campaign.get("_id", ""),
        "channels": channel_data,
        "totals": {
            "reach": total_reach,
            "impressions": total_impressions,
            "clicks": total_clicks,
            "engagement_rate": avg_engagement,
            "conversions": total_conversions,
            "shares": total_shares,
            "comments": total_comments,
        },
    }


def _random_time():
    hours = random.choice([9, 10, 12, 14, 17, 18, 19, 20, 21])
    return f"{hours}:00"


def _random_content_type(channel):
    types = {
        "instagram": ["Carousel", "Reel", "Story", "Static Post"],
        "facebook":  ["Video", "Link Post", "Photo", "Event"],
        "tiktok":    ["Trending Audio", "Duet", "Tutorial", "Behind-the-scenes"],
        "email":     ["Newsletter", "Promo", "Drip Sequence"],
        "sms":       ["Flash Sale", "Appointment Reminder", "Promo Code"],
    }
    return random.choice(types.get(channel, ["Post"]))
