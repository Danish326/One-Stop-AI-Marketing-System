# 🧠 NEXUS — AI Marketing Command Center

**NEXUS** is an AI-powered marketing platform that lets marketers create campaigns, generate content across channels, track analytics, and manage customer correspondence — all from a single command center.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend API | FastAPI + Uvicorn |
| Database | MongoDB Atlas |
| AI Engine | Anthropic Claude |
| Charts | Custom HTML/SVG/CSS/JS |
| Auth | bcrypt |

> 📖 **[API Keys & AI Integration Guide →](API_KEYS.md)** — Which AI provider to use, free-tier options, and image generation setup

## Getting Started

```bash
# 1. Clone and enter the project
cd nexus

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and Anthropic API key

# 5. Run the application
# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run app.py --server.port 8501 --server.headless true
```

Open **http://localhost:8501** in your browser.  
API docs available at **http://localhost:8000/docs**.

## Features

- 🎯 **Campaign Management** — Create, edit, and track marketing campaigns
- ✦ **AI Content Generation** — Generate channel-specific content with Claude AI
- 📊 **Analytics Dashboard** — Interactive charts with bar/pie toggle and channel legends
- 📅 **Content Calendar** — Schedule and visualize upcoming posts
- 💬 **Correspondence** — AI-drafted customer replies and FAQ management

---

## Improvements Log

| Date | Improvement | Details |
|------|------------|---------|
| 2026-02-27 | 📊 Channel Performance Charts | Replaced basic HTML progress bars with interactive Altair bar + pie charts. Added a toggle to switch between bar chart (engagement rate) and donut chart (reach distribution). Proper color-coded legends with channel brand colors and hover tooltips. Added compact channel metric detail cards below the chart. |
| 2026-02-27 | 🎨 Custom Animated Charts | Replaced Altair with custom HTML/SVG/CSS/JS charts. Light mode palette (#f4f3ef bg, #ffffff cards). SVG donut pie with stroke-dasharray animations (r=80, circumference 502.65). CSS view transitions with opacity/translateY. Toggle with 120ms stagger. Bar animations replay on activation. Updated brand colors: Instagram #FF2D78, Facebook #2D7EFF, TikTok #00BFA5. |
| 2026-02-27 | 💎 Premium Chart Card | Complete pixel-perfect rewrite: gradient icon header with LIVE badge, sliding toggle pill with spring easing, 3 stat cards with colored borders and DM Mono numbers, gradient-fill bar chart with y-axis ticks and grid lines, SVG donut pie with right-side legend showing rate + % of total. All animations staggered and replay on view activation. |
| 2026-02-27 | 🔑 API Keys Documentation | Created `API_KEYS.md` with current AI usage, provider comparison (Gemini, Claude, OpenAI, Groq, HuggingFace), free-tier recommendations, and AI image generation integration plan for campaigns. |
