"""
NEXUS — FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, campaigns, content, analytics, correspondence

app = FastAPI(
    title="NEXUS API",
    description="Backend API for NEXUS — AI Marketing Command Center",
    version="0.1.0",
)

# ── CORS (allow Streamlit frontend to call the API) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(auth.router,           prefix="/api/auth",           tags=["Authentication"])
app.include_router(campaigns.router,      prefix="/api/campaigns",      tags=["Campaigns"])
app.include_router(content.router,        prefix="/api/content",        tags=["Content"])
app.include_router(analytics.router,      prefix="/api/analytics",      tags=["Analytics"])
app.include_router(correspondence.router, prefix="/api/correspondence", tags=["Correspondence"])


@app.get("/")
def root():
    return {"status": "ok", "app": "NEXUS API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
