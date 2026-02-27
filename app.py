"""
NEXUS — AI Marketing Command Center
Main Streamlit entry point: handles auth gate, sidebar navigation, and page routing.
"""

import sys
import os
import streamlit as st

# ── Ensure project root is on sys.path so imports work ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_TAGLINE, APP_ICON
from services.auth_service import (
    init_session, is_authenticated, login, signup, logout
)

# ── Page imports ──
from views import dashboard, campaigns, generate, calendar, analytics, correspondence

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
    /* ── CSS Variables ── */
    :root {
        --bg: #F5F3EE;
        --surface: #FFFFFF;
        --accent: #FF4D00;
        --accent-light: #FFF0EB;
        --text: #1A1814;
        --muted: #8A8680;
        --border: #E8E4DC;
        --green: #1A7A4A;
        --green-bg: #E6F5ED;
    }

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--text);
    }
    .stApp {
        background-color: var(--bg) !important;
    }

    /* ── Headings — Syne ── */
    h1, h2, h3, h4 {
        font-family: 'Syne', sans-serif !important;
        color: var(--text) !important;
    }

    /* ── Sidebar — Dark for contrast ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1814 0%, #2a2520 100%);
        padding-top: 0.5rem;
    }
    [data-testid="stSidebar"] * { color: #c0b8a8 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: none;
        border-radius: 10px;
        color: #c0b8a8 !important;
        text-align: left;
        padding: 0.55rem 0.9rem;
        font-size: 0.88rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        width: 100%;
        transition: all 0.2s ease;
        margin-bottom: 2px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 77, 0, 0.12);
        color: #ffffff !important;
        transform: translateX(3px);
    }
    [data-testid="stSidebar"] .nav-active > div > button,
    .nav-active > div > button {
        background: linear-gradient(90deg, rgba(255, 77, 0, 0.2), rgba(255, 77, 0, 0.08)) !important;
        color: #ffffff !important;
        font-weight: 600;
        border-left: 3px solid var(--accent);
        padding-left: 0.75rem;
    }

    /* ── Section headers in sidebar ── */
    .nav-section-header {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6a6258 !important;
        padding: 0.8rem 0.9rem 0.3rem 0.9rem;
        margin-top: 0.3rem;
    }

    /* ── User profile card ── */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.75rem 0.85rem;
        margin-top: 0.5rem;
    }
    .user-profile-card .user-name {
        font-weight: 600;
        font-size: 0.85rem;
        color: #e8e0d8 !important;
    }
    .user-profile-card .user-email {
        font-size: 0.72rem;
        color: #7a7268 !important;
        margin-top: -2px;
    }

    /* ── Logout button ── */
    .logout-btn > div > button {
        background: rgba(255, 75, 75, 0.08) !important;
        border: 1px solid rgba(255, 75, 75, 0.15) !important;
        color: #ff6b6b !important;
        font-size: 0.78rem !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 8px !important;
        margin-top: 0.4rem;
    }
    .logout-btn > div > button:hover {
        background: rgba(255, 75, 75, 0.18) !important;
    }

    /* ── Login card ── */
    .login-card {
        max-width: 420px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: var(--surface);
        border-radius: 16px;
        border: 1.5px solid var(--border);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    }
    .login-card h2 { text-align: center; margin-bottom: 0.2rem; }
    .login-card p  { text-align: center; color: var(--muted); margin-bottom: 1.5rem; }

    /* ── Primary buttons — Burnt orange ── */
    div[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border: none;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        border-radius: 10px;
        color: #fff !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(255, 77, 0, 0.2);
    }
    div[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"]:hover {
        background: #e64400 !important;
        box-shadow: 0 6px 20px rgba(255, 77, 0, 0.3);
        transform: translateY(-1px);
    }

    /* ── Secondary buttons ── */
    div[data-testid="stMainBlockContainer"] .stButton > button:not([kind="primary"]) {
        background: var(--surface);
        border: 1.5px solid var(--border);
        border-radius: 10px;
        color: var(--text) !important;
        font-weight: 500;
        width: 95%;
        font-family: 'DM Sans', sans-serif;
        transition: all 0.2s ease;
    }
    div[data-testid="stMainBlockContainer"] .stButton > button:not([kind="primary"]):hover {
        border-color: var(--accent);
        color: var(--accent) !important;
        transform: translateY(-1px);
    }

    /* ── Metric cards (st.metric) — Light style ── */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1.5px solid var(--border);
        border-radius: 16px;
        padding: 1.2rem;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -2px;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--muted) !important;
    }

    /* ── Text inputs — Light ── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-light) !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }

    /* ── Progress bars — Orange ── */
    [data-testid="stProgress"] > div > div > div {
        background: var(--accent) !important;
        border-radius: 8px;
    }
    [data-testid="stProgress"] > div > div {
        background: var(--border) !important;
        border-radius: 8px;
    }

    /* ── Tabs ── */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: var(--muted) !important;
    }
    button[data-baseweb="tab"]:hover { color: var(--accent) !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: var(--text) !important; }
    [data-baseweb="tab-highlight"] {
        background: var(--accent) !important;
        height: 3px !important;
        border-radius: 2px;
    }

    /* ── Containers (border=True) ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border) !important;
    }

    /* ── Expanders ── */
    div[data-testid="stExpander"] {
        background: var(--surface);
        border: 1.5px solid var(--border);
        border-radius: 12px;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* ── Dividers ── */
    [data-testid="stMarkdown"] hr {
        border: none;
        border-top: 1px solid var(--border);
    }

    /* ── Radio — pill style ── */
    [data-testid="stRadio"] > div { gap: 0.3rem !important; }
    [data-testid="stRadio"] label {
        background: var(--surface);
        border: 1.5px solid var(--border);
        border-radius: 20px;
        padding: 4px 16px !important;
        font-size: 0.8rem !important;
        font-weight: 500;
        color: var(--muted) !important;
        transition: all 0.2s ease;
    }
    [data-testid="stRadio"] label:has(input:checked) {
        background: var(--text);
        border-color: var(--text);
        color: #fff !important;
    }

    /* ── Fade-up animation ── */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .fade-up { animation: fadeUp 0.5s ease forwards; }
    .fade-up-1 { animation: fadeUp 0.5s ease 0.05s forwards; opacity: 0; }
    .fade-up-2 { animation: fadeUp 0.5s ease 0.1s forwards; opacity: 0; }
    .fade-up-3 { animation: fadeUp 0.5s ease 0.15s forwards; opacity: 0; }
    .fade-up-4 { animation: fadeUp 0.5s ease 0.2s forwards; opacity: 0; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    /* ── Hide Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header[data-testid="stHeader"] { background: var(--bg); }
</style>
""", unsafe_allow_html=True)

# ─── Initialise Session ────────────────────────────────────────────────────────
init_session()

# Ensure page nav default
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# Ensure active campaign default
if "active_campaign" not in st.session_state:
    st.session_state["active_campaign"] = None


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH GATE — Login / Signup
# ═══════════════════════════════════════════════════════════════════════════════

def render_auth():
    """Render 50/50 split login / signup form."""

    import base64, os

    img_path = os.path.join(os.path.dirname(__file__), "auth_bg.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/jpeg;base64,{encoded}" class="left-bg-img"/>'
    else:
        img_tag = ""  # fallback: CSS gradient shows instead

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

        [data-testid="collapsedControl"],
        [data-testid="stSidebar"] {{ display: none !important; }}

        .stApp {{
            background: #ede9e3 !important;
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 980px !important;
            margin: 50px auto;
            padding: 5vh 1rem !important;
            min-height: 90vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        [data-testid="stHorizontalBlock"] {{
            border-radius: 22px !important;
            overflow: hidden !important;
            box-shadow:
                0 0 0 1px rgba(0,0,0,0.07),
                0 20px 60px rgba(0,0,0,0.12),
                0 4px 14px rgba(0,0,0,0.05) !important;
            animation: authFadeUp 0.6s cubic-bezier(0.16,1,0.3,1) both;
            min-height: 620px;
        }}

        @keyframes authFadeUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        [data-testid="column"] {{ padding: 0 !important; gap: 0 !important; }}

        /* ── Left pane wrapper — the .left-pane div we inject controls everything ── */
        .left-pane {{
            position: relative;
            min-height: 620px;
            width: 100%;
            # background: linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%);
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding: 2.75rem;
            overflow: hidden;
        }}

        /* The actual image — fills the container via absolute positioning */
        .left-bg-img {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            z-index: 0;
        }}



        @keyframes drift {{
            from {{ transform: translate(0, 0) scale(1); }}
            to   {{ transform: translate(12px, 16px) scale(1.08); }}
        }}

        /* ── Right pane ── */
        [data-testid="column"]:nth-of-type(2) > div:first-child {{
            padding: 3rem 3.5rem !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-height: 620px;
            background: #ffffff;
            overflow-y: auto;
        }}

        .auth-title {{
            font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 800;
            color: #0f0f18; letter-spacing: -0.025em; line-height: 1.15; margin-bottom: 0.4rem;
        }}
        .auth-subtitle {{
            font-size: 0.875rem; color: #8a8a9a; line-height: 1.5; margin-bottom: 1.75rem;
        }}

        [data-baseweb="tab-list"] {{
            gap: 1.5rem !important;
            border-bottom: 1.5px solid #E8E4DC !important;
            margin-bottom: 1.6rem !important;
        }}
        button[data-baseweb="tab"] {{
            font-family: 'DM Sans', sans-serif !important; font-size: 0.92rem !important;
            font-weight: 500 !important; padding: 0.4rem 0 0.7rem !important; color: #9a97a0 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #0f0f18 !important; border-bottom-color: #FF4D00 !important;
        }}

        div[data-testid="stForm"] {{
            margin-left: -10px;
            border: none !important;
            width: 95%;
            box-shadow: none !important; background: transparent !important;
        }}

        button[kind="primaryFormSubmit"],
        button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, #FF4D00, #FF7A00) !important;
            border: none !important; border-radius: 10px !important;
            font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
            box-shadow: 0 4px 16px rgba(255,77,0,0.30) !important;
        }}

        .or-divider {{
            display: flex; align-items: center; gap: 0.1rem; margin: 1.3rem 5;
            color: #b5b0a8; font-family: 'DM Sans', sans-serif;
            font-size: 0.75rem; font-weight: 600; letter-spacing: 0.09em;
        }}
        .or-divider hr {{ flex: 1; border: none; border-top: 1px solid #E8E4DC; margin: 0; }}
        </style>
    """, unsafe_allow_html=True)

    col_img, col_form = st.columns([1, 1], gap="small")

    with col_img:
        # KEY CHANGE: we own the entire left pane as a single HTML block.
        # The image is an <img> tag absolutely positioned inside .left-pane,
        # so Streamlit's CSS restrictions on background-image don't matter.
        st.markdown(f"""
            <div class="left-pane">
                {img_tag}
                <div class="left-overlay"></div>
                <div class="left-blobs"></div>
                <div class="left-grid"></div>
            </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""
            <h1 class="auth-title">Welcome to NEXUS</h1>
            <p class="auth-subtitle">The AI command center for modern teams.</p>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Log In", "Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Work Email", placeholder="alex@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                if submitted:
                    ok, msg = login(email, password)
                    if ok:
                        st.success("Welcome back! Loading dashboard...")
                        st.rerun()
                    else:
                        st.error(f"⚠️ {msg}")

            st.markdown('<div class="or-divider"><hr> OR CONTINUE WITH <hr></div>', unsafe_allow_html=True)
            st.button("G  Continue with Google", disabled=True, use_container_width=True)

        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                name    = st.text_input("Full Name", placeholder="Alex Morgan")
                email_s = st.text_input("Work Email", placeholder="alex@company.com", key="signup_email")
                pw      = st.text_input("Password", type="password", placeholder="Min 8 characters", key="signup_pw")
                pw2     = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_pw2")
                submitted_s = st.form_submit_button("Create Workspace ✨", use_container_width=True, type="primary")
                if submitted_s:
                    if len(pw) < 6:
                        st.error("⚠️ Password must be at least 6 characters.")
                    elif pw != pw2:
                        st.error("⚠️ Passwords do not match.")
                    else:
                        ok, msg = signup(name, email_s, pw)
                        if ok:
                            st.success("Account created! Logging you in...")
                            st.rerun()
                        else:
                            st.error(f"⚠️ {msg}")

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION (only when authenticated)
# ═══════════════════════════════════════════════════════════════════════════════

NAV_SECTIONS = {
    "CORE": [
        {"key": "Dashboard",       "icon": "⚡",  "module": dashboard},
        {"key": "Campaigns",       "icon": "🎯",  "module": campaigns},
        {"key": "Generate",        "icon": "✦",   "module": generate},
        {"key": "Calendar",        "icon": "📅",  "module": calendar},
    ],
    "INTELLIGENCE": [
        {"key": "Analytics",       "icon": "◈",   "module": analytics},
    ],
    "SYSTEM": [
        {"key": "Correspondence",  "icon": "💬",  "module": correspondence},
    ],
}

# Flat lookup for routing
PAGE_MAP = {}
for items in NAV_SECTIONS.values():
    for item in items:
        PAGE_MAP[item["key"]] = item["module"]


def render_sidebar():
    """Render the premium sidebar navigation."""

    with st.sidebar:
        # ── Branding ──
        st.markdown(
            f'<div style="padding: 0.5rem 0.2rem 0.2rem; text-align: center;">'
            f'<span style="font-size: 1.8rem;">{APP_ICON}</span><br>'
            f'<span style="font-size: 1.3rem; font-weight: 700; color: #fff !important;">{APP_NAME}</span><br>'
            f'<span style="font-size: 0.7rem; color: #6a6a8a !important; letter-spacing: 0.05em;">{APP_TAGLINE}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin: 0.4rem 0;'></div>", unsafe_allow_html=True)

        # ── Navigation Sections ──
        current = st.session_state.get("current_page", "Dashboard")

        for section_name, items in NAV_SECTIONS.items():
            st.markdown(
                f'<div class="nav-section-header">{section_name}</div>',
                unsafe_allow_html=True,
            )

            for item in items:
                is_active = current == item["key"]
                label = f'{item["icon"]}  {item["key"]}'

                # Wrap active item in a div with special class for CSS targeting
                if is_active:
                    st.markdown('<div class="nav-active">', unsafe_allow_html=True)

                if st.button(label, key=f"nav_{item['key']}", use_container_width=True):
                    st.session_state["current_page"] = item["key"]
                    st.rerun()

                if is_active:
                    st.markdown('</div>', unsafe_allow_html=True)

        # ── Spacer ──
        st.markdown("<div style='flex-grow: 1; min-height: 2rem;'></div>", unsafe_allow_html=True)
        st.divider()

        # ── User Profile Card ──
        user_name = st.session_state.get("user_name", "User")
        user_email = st.session_state.get("user_email", "")
        st.markdown(
            f'<div class="user-profile-card">'
            f'  <div class="user-name">👤 {user_name}</div>'
            f'  <div class="user-email">{user_email}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Logout ──
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if not is_authenticated():
        render_auth()
        return

    render_sidebar()

    # ── Auto-publish: flip overdue scheduled posts to published ──
    from services.db_service import auto_publish_overdue
    published_count = auto_publish_overdue()
    if published_count:
        # Clear cached content so UI refreshes with updated statuses
        if "generated_content" in st.session_state:
            del st.session_state["generated_content"]

    # Route to selected page
    page_key = st.session_state.get("current_page", "Dashboard")
    page_module = PAGE_MAP.get(page_key, dashboard)
    page_module.render()


if __name__ == "__main__":
    main()

