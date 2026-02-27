# Phase 3: AI Content Generation — Pre-Coding Plan

> **Status:** 📋 Planning  
> **Date:** 2026-02-26  
> **Phase:** 3 of 6

---

## Goal

Build the AI Content Generation engine that takes a campaign brief and produces platform-specific marketing content for each selected channel using Claude AI. Users can view, score, edit, and regenerate content — all from the **Generate** page.

---

## Features in Scope

| Feature ID | Feature | Description |
|---|---|---|
| **F-02** | Multi-channel AI Generation | Generate content for Instagram, Facebook, TikTok, Email, SMS using Claude |
| **F-03** | Content Card Component | Display AI-generated content with score badge, copy, and channel icon |
| **F-04** | Regenerate per Piece | Re-generate a single content piece without regenerating all |
| **F-13** | Inline Edit & Save | Edit content body inline and save changes back to the database |

---

## Architecture

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Streamlit UI    │────▶│  FastAPI Backend     │────▶│  Claude AI       │
│  views/generate  │     │  /api/content/gen.   │     │  (Anthropic API) │
│                  │◀────│                      │◀────│                  │
│  Content Cards   │     │  routers/content.py  │     │  ai_service.py   │
└──────────────────┘     └─────────────────────┘     └──────────────────┘
                               │
                               ▼
                         ┌──────────────┐
                         │  db_service   │
                         │  (in-memory)  │
                         └──────────────┘
```

**Data flow:**
1. User clicks "Generate Content" on the Generate page
2. Streamlit calls `api_client.generate_content(campaign_id)`
3. FastAPI `/api/content/generate` loads the campaign from DB
4. `ai_service.generate_content()` sends prompt to Claude
5. Claude returns JSON array of content pieces (one per channel)
6. Content is saved to DB and returned to the frontend
7. Frontend renders Content Cards with AI scores, copy text, and actions

---

## Files to Create / Modify

### New Files
| File | Purpose |
|---|---|
| `services/ai_service.py` | Claude API client with `generate_content()` and JSON parsing |
| `PHASE3_COMPLETED.md` | Post-coding summary (created after implementation) |

### Modified Files
| File | Changes |
|---|---|
| `views/generate.py` | Full rewrite — generate button, content cards, edit/regen UI |
| `backend/routers/content.py` | Update `/generate` endpoint to actually call `ai_service` |
| `services/api_client.py` | Minor — already has `generate_content()` function |
| `.env.example` | Add `ANTHROPIC_API_KEY` placeholder |

---

## AI Prompt Design

Using the prompt from `AI_DESIGN.md`:

- **Input:** Campaign name, objective, audience, tone, channels, duration
- **Prompt:** Structured template asking Claude to generate one content piece per channel
- **Output:** JSON array with `channel`, `content_type`, `body`, `hashtags`, `posting_time_suggestion`, `ai_score`, `score_reasoning`
- **Error handling:** Try/except with fallback content so the UI never breaks

---

## UI Design (Generate Page)

```
┌─────────────────────────────────────────────┐
│  ✦ Generate Content                         │
│                                             │
│  Active Campaign: "Winter Menu Launch"      │
│  [🚀 Generate All Content]                  │
│                                             │
│  ─────────────────────────────────────────  │
│                                             │
│  📸 Instagram                    Score: 88  │
│  ┌─────────────────────────────────────┐    │
│  │ "Cozy up this winter with our..."   │    │
│  │ #WinterMenu #Foodie #LocalEats      │    │
│  │ Best time: Tuesday 7PM              │    │
│  │ [✏️ Edit] [🔄 Regenerate] [📋 Copy] │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  📘 Facebook                     Score: 82  │
│  ┌─────────────────────────────────────┐    │
│  │ "Exciting news! Our winter menu..." │    │
│  │ [✏️ Edit] [🔄 Regenerate] [📋 Copy] │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  🎵 TikTok                       Score: 75  │
│  ┌─────────────────────────────────────┐    │
│  │ "[Hook] Wait until you see what..." │    │
│  │ [✏️ Edit] [🔄 Regenerate] [📋 Copy] │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Verification Plan

1. **API Test:** Call `POST /api/content/generate` with a campaign ID and verify JSON response
2. **UI Test:** Sign up → Create campaign → Click Generate → Verify content cards appear
3. **Edit Test:** Click Edit on a content card → Modify text → Save → Verify change persists
4. **Regenerate Test:** Click Regenerate on a single piece → Verify new content appears
5. **Error Handling:** Test without `ANTHROPIC_API_KEY` → Verify fallback content appears instead of crash

---

## Dependencies

- `anthropic` Python package (already in requirements.txt)
- `ANTHROPIC_API_KEY` environment variable (user must set this)
- Active campaign must exist before generating content

---

## Estimated Effort

~6-8 files touched, ~400-500 lines of new code.
