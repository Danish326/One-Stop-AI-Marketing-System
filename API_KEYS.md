# 🔑 API Keys — NEXUS AI Integration Guide

## Table of Contents
- [Current Setup](#current-setup)
- [How AI Is Used Right Now](#how-ai-is-used-right-now)
- [What Happens Without an API Key](#what-happens-without-an-api-key)
- [Setting Up an API Key](#setting-up-an-api-key)
- [What Happens When You Provide a Key](#what-happens-when-you-provide-a-key)
- [Which AI Provider to Choose](#which-ai-provider-to-choose)
- [AI Image Generation for Campaigns](#ai-image-generation-for-campaigns)
- [Quick Comparison Table](#quick-comparison-table)

---

## Current Setup

NEXUS uses **one AI API key** and **one database URI** in its `.env` file:

```env
# Required — your MongoDB database
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/nexus

# Optional — AI features (falls back to demo content if missing)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

The AI service is in `services/ai_service.py`, and it currently uses the **Anthropic Claude** SDK.

---

## How AI Is Used Right Now

NEXUS has **3 AI agents**, each serving a specific role:

| Agent | Function | What It Does |
|-------|----------|-------------|
| 🎨 **Content Generator** | `generate_content()` | Generates platform-specific marketing copy (captions, posts, scripts, emails, SMS) for each campaign channel |
| 🔄 **Content Regenerator** | `regenerate_single()` | Regenerates a single piece of content for one channel with a fresh variation |
| 📊 **Insights Analyst** | `generate_insights()` | Analyzes cross-channel analytics data and produces 4 strategic insights with recommendations |
| 💬 **Reply Composer** | `generate_reply()` | Drafts customer service replies, scores confidence (0–1), and flags messages for human escalation |

### Where each agent is triggered:
- **Content Generator** → Generate page (when you click "✨ Generate Content")
- **Insights Analyst** → Analytics page (auto-generates insights from seeded data)
- **Reply Composer** → Correspondence page (drafts replies to customer messages)

---

## What Happens Without an API Key

**NEXUS works perfectly without any API key.** Every AI function has a built-in **fallback system**:

- `generate_content()` → Returns pre-written marketing templates for each channel
- `generate_insights()` → Returns 4 hardcoded analytical insights based on your data
- `generate_reply()` → Uses keyword matching to draft reasonable replies

On startup, you'll see this in your terminal:
```
⚠️  ANTHROPIC_API_KEY not configured — AI features will use fallback content.
```

This is fine for demos and MVPs. The app is fully functional — it just uses static templates instead of AI-generated content.

---

## Setting Up an API Key

### Step 1: Create a `.env` file
```bash
cp .env.example .env
```

### Step 2: Add your API key
```env
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```

### Step 3: Restart the servers
The AI service reads the key at startup. After adding it, restart both the backend and Streamlit:
```bash
# Terminal 1
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2
streamlit run app.py --server.port 8501 --server.headless true
```

You should now see:
```
✅ Anthropic Claude API client initialized.
```

---

## What Happens When You Provide a Key

Once a valid API key is set, **all 3 agents switch from fallback templates to live AI calls**:

| Feature | Without Key | With Key |
|---------|------------|----------|
| Content Generation | Static templates per channel | Unique, campaign-specific copy tailored to your objective, audience, and tone |
| Insights | Hardcoded patterns from data | Deep analytical insights with actionable recommendations specific to your metrics |
| Customer Replies | Keyword-matching responses | Contextual, brand-tone-aware replies with accurate confidence scoring |
| Quality Scores | Fixed scores (70–80) | Dynamic AI-assessed scores (0–100) with detailed reasoning |

### Model Used
Currently: **`claude-sonnet-4-6`** (configurable via `AI_MODEL` env variable)

---

## Which AI Provider to Choose

### 🏆 Recommendation for Your MVP: **Google Gemini**

Here's why, and how each option compares:

### 1. Google Gemini (✅ BEST FOR FREE MVP)

| Aspect | Details |
|--------|---------|
| **Free Tier** | Gemini 2.0 Flash — **free**, 15 requests/minute, 1M tokens/day |
| **Paid** | Gemini Pro — $0.50/1M input tokens, $1.50/1M output |
| **Image Gen** | ✅ Imagen 3 built-in (free tier available) |
| **SDK** | `pip install google-genai` |
| **Best For** | MVP/hackathon — completely free for your workload |

**Why it's best for you:**
- Truly free tier with generous limits (1M tokens/day is ~500+ content generations)
- Built-in image generation (Imagen 3) — no separate API needed
- Fast response times with Flash model
- Google Cloud integration if you scale later

### 2. Anthropic Claude

| Aspect | Details |
|--------|---------|
| **Free Tier** | ❌ No free tier (API requires prepaid credits) |
| **Paid** | Claude Sonnet — $3/1M input, $15/1M output |
| **Image Gen** | ❌ Text only — needs a separate image API |
| **SDK** | `pip install anthropic` (already in your project) |
| **Best For** | Production apps where quality justifies cost |

**Your project is already wired for Claude**, so if you have credits, it works immediately.

### 3. OpenAI (GPT-4o / GPT-4o-mini)

| Aspect | Details |
|--------|---------|
| **Free Tier** | ❌ No free tier ($5 credit for new accounts, expires after 3 months) |
| **Paid** | GPT-4o-mini — $0.15/1M input, $0.60/1M output |
| **Image Gen** | ✅ DALL·E 3 — $0.04/image (1024×1024) |
| **SDK** | `pip install openai` |
| **Best For** | Apps needing both text + image from one vendor |

### 4. Groq (Llama 3 / Mixtral)

| Aspect | Details |
|--------|---------|
| **Free Tier** | ✅ Free — 30 requests/minute, 14,400 requests/day |
| **Paid** | Extremely cheap after free tier |
| **Image Gen** | ❌ Text only |
| **SDK** | `pip install groq` (OpenAI-compatible) |
| **Best For** | Ultra-fast responses, highest free-tier limits |

### 5. Hugging Face Inference API

| Aspect | Details |
|--------|---------|
| **Free Tier** | ✅ Free for many models (rate limited) |
| **Image Gen** | ✅ Stable Diffusion, FLUX — free |
| **SDK** | `pip install huggingface_hub` |
| **Best For** | Open-source models, maximum flexibility |

---

## AI Image Generation for Campaigns

If you want NEXUS to generate **visual posts** (images) for campaigns, here are your options:

### Option A: Google Gemini + Imagen 3 (🏆 Recommended)
- **Free tier available** — generate images with the same API key you use for text
- One SDK, one API key, both text and images
- High-quality marketing-style images
- Supports text-to-image with prompts like:
  > "Create an Instagram-ready product photo for a summer sale campaign, vibrant colors, professional lighting"

### Option B: OpenAI DALL·E 3
- $0.04/image (1024×1024) — very affordable
- Excellent prompt understanding
- Returns a URL you can download and attach to content
- Separate from text API but same `openai` SDK

### Option C: Stability AI (Stable Diffusion)
- Free API tier (25 credits/day)
- SD3 / SDXL models for high-quality images
- More control over style, aspect ratio, seed

### Option D: Hugging Face (FLUX / SD)
- Completely free (with rate limits)
- Can run models like FLUX.1 or Stable Diffusion
- Ideal for MVP with zero budget

### How Image Generation Would Integrate

When integrated, the content generation flow would become:

```
Generate Content → AI creates text copy + image for each channel
                   ↓
     ┌─────────────┼──────────────┐
     │             │              │
  Instagram     Facebook       TikTok
  1080×1080     1200×630      1080×1920
  + caption     + post text   + cover frame
  + hashtags    + hashtags    + script
```

Each channel would get a **platform-optimized image** (correct dimensions) plus the text content. The generated images would be stored and attached to the content piece for scheduling.

---

## Quick Comparison Table

| Provider | Free Tier | Text Quality | Image Gen | Cost After Free | Setup Difficulty |
|----------|-----------|-------------|-----------|----------------|-----------------|
| **Google Gemini** | ✅ 1M tokens/day | ⭐⭐⭐⭐ | ✅ Imagen 3 | Very Low | Easy |
| **Anthropic Claude** | ❌ | ⭐⭐⭐⭐⭐ | ❌ | High | Already set up |
| **OpenAI GPT-4o** | ❌ ($5 credit) | ⭐⭐⭐⭐⭐ | ✅ DALL·E 3 | Medium | Easy |
| **Groq** | ✅ 14.4K req/day | ⭐⭐⭐⭐ | ❌ | Very Low | Easy |
| **Hugging Face** | ✅ Rate limited | ⭐⭐⭐ | ✅ SD/FLUX | Free | Medium |

### 🎯 Bottom Line

**For your hackathon MVP with zero budget:**
1. **Text AI** → **Google Gemini 2.0 Flash** (free, fast, good quality)
2. **Image AI** → **Imagen 3** via same Gemini key (free tier) OR **Hugging Face FLUX** (free)
3. **If you have budget** → **OpenAI GPT-4o-mini + DALL·E 3** (cheapest paid combo)

To switch from Claude to Gemini, only `services/ai_service.py` needs to be updated — the rest of the app is provider-agnostic. All functions return the same JSON structure regardless of which AI backend is used.
