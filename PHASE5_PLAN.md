# Phase 5: Analytics & Insights — Pre-Coding Plan

> **Status:** 📋 Planning  
> **Date:** 2026-02-26  
> **Phase:** 5 of 6

---

## Goal

Build a full analytics dashboard with simulated engagement data per channel and AI-generated strategic insights. This is the "marketing intelligence engine" layer.

---

## Features

| ID | Feature | Description |
|---|---|---|
| **F-20** | Seed Analytics | Script to generate realistic simulated engagement data per channel |
| **F-08** | Analytics Dashboard | UI with reach, engagement, clicks, conversions metrics |
| **F-09** | Channel Breakdown | Per-channel performance bars/charts |
| **F-10** | AI Insights | Claude generates strategic recommendations from analytics data |
| **F-19** | Refresh Insights | Button to re-generate AI insights |

---

## Architecture

```
Analytics Page (views/analytics.py)
  │
  ├─ "Seed Analytics" button → api_client → analytics router → seed_analytics()
  │    └─ Generates random but realistic engagement data per channel
  │
  ├─ Metrics cards: Reach, Engagement Rate, Clicks, Conversions
  │
  ├─ Channel performance bars (per-channel breakdown)
  │
  └─ "🧠 Generate Insights" button → api_client → analytics router → ai_service
       └─ Claude Insights Analyst prompt → 4 strategic insights
```

---

## Files to Modify

| File | Changes |
|---|---|
| `utils/seed_analytics.py` | **[NEW]** — Generate simulated data per channel |
| `services/ai_service.py` | Add `generate_insights()` function (Agent 2 prompt) |
| `backend/routers/analytics.py` | Implement seed + insights endpoints |
| `views/analytics.py` | Full rewrite — charts, metrics, insights cards |
| `services/api_client.py` | Already has analytics functions |
| `views/dashboard.py` | Update Channel Performance with real data |

---

## Simulated Data Shape

```json
{
  "campaign_id": "...",
  "channels": {
    "instagram": { "reach": 12500, "impressions": 18200, "clicks": 840, "engagement_rate": 4.7, "conversions": 62, "shares": 210, "comments": 156 },
    "facebook":  { "reach": 8900,  "impressions": 13400, "clicks": 520, "engagement_rate": 3.2, "conversions": 38, "shares": 95,  "comments": 78 }
  },
  "totals": { "reach": 21400, "engagement_rate": 3.95, "clicks": 1360, "conversions": 100 }
}
```

---

## Verification

### Browser Test
1. Create campaign → Generate content → Navigate to Analytics
2. Click "Seed Analytics" → Verify metrics appear
3. Verify per-channel breakdown bars
4. Click "Generate Insights" → Verify 4 insight cards appear
5. Dashboard Channel Performance updates with real data
