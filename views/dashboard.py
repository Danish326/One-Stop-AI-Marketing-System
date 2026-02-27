"""
NEXUS — Dashboard (Command Center)
Interactive overview with campaign cards, click-to-expand metrics, and quick actions.
Light warm theme — #F5F3EE bg, #FF4D00 accent, Syne + DM Sans fonts.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date
from services import api_client
from config.settings import CHANNELS

_CHANNEL_MAP = {ch["id"]: ch for ch in CHANNELS}

# Colors — light mode palette
_BG = "#f4f3ef"
_CARD = "#ffffff"
_SURFACE2 = "#f8f7f4"
_ACCENT = "#FF4D00"
_TEXT = "#111118"
_MUTED = "#8a8a9a"
_BORDER = "rgba(0,0,0,0.12)"
_SURFACE = "#ffffff"
_GREEN = "#1A7A4A"
_GREEN_BG = "#E6F5ED"
_ACCENT_LIGHT = "#FFF0EB"

# Brand colors for charts
_BRAND_COLORS = {
    "instagram": "#FF2D78",
    "facebook": "#2D7EFF",
    "tiktok": "#00BFA5",
    "email": "#FF4D00",
    "sms": "#1A7A4A",
}


def render():
    # ══════════════════════════════════════════════════════════════════════════
    #  HERO GREETING
    # ══════════════════════════════════════════════════════════════════════════

    user_name = st.session_state.get("user_name", "Marketer")
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    st.markdown(
        f'<div class="fade-up" style="margin-bottom: 1rem;">'
        f'<span style="display: inline-block; background: {_ACCENT}; color: #fff; '
        f'padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; '
        f'font-family: DM Sans, sans-serif; margin-bottom: 8px;">⚡ {greeting}</span>'
        f'<h1 style="margin: 0; font-family: Syne, sans-serif; font-weight: 800; '
        f'font-size: 2.2rem; color: {_TEXT};">Hello, '
        f'<span style="color: {_ACCENT};">{user_name}</span>.</h1>'
        f'<p style="font-family: Syne, sans-serif; font-size: 1.1rem; color: {_TEXT}; '
        f'margin: 2px 0 0;">Let\'s look at your campaigns.</p>'
        f'<p style="color: {_MUTED}; font-size: 0.85rem; margin-top: 2px;">'
        f'Your marketing command center at a glance.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Load all campaigns ──
    user_id = st.session_state.get("user_id")
    all_campaigns = api_client.list_campaigns(user_id)
    if isinstance(all_campaigns, dict):
        all_campaigns = []

    if not all_campaigns:
        st.divider()
        st.info("🚀 No campaigns yet! Create your first campaign to get started.")
        if st.button("➕ Create Campaign", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Campaigns"
            st.rerun()
        return

    # ══════════════════════════════════════════════════════════════════════════
    #  FILTER + CAMPAIGN CARDS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Filter navbar ──
    if "dash_status_filter" not in st.session_state:
        st.session_state["dash_status_filter"] = "All"

    filters = ["All", "Active", "Paused", "Completed"]
    current_filter = st.session_state.get("dash_status_filter", "All")

    # Navbar: 4 equal columns as a connected bar
    nav_cols = st.columns(len(filters))
    for i, f in enumerate(filters):
        with nav_cols[i]:
            is_active = (f == current_filter)
            btn_type = "primary" if is_active else "secondary"
            if st.button(f, key=f"filter_{f}", use_container_width=True, type=btn_type):
                st.session_state["dash_status_filter"] = f
                st.rerun()

    status_filter = current_filter

    # Apply filter
    if status_filter == "All":
        filtered = all_campaigns
    else:
        filtered = [c for c in all_campaigns if c.get("status", "draft").lower() == status_filter.lower()]

    # ── "Your Campaigns" (left) + "Show All →" (right) ──
    title_col, show_all_col = st.columns([4, 1])
    with title_col:
        st.markdown(
            f'<h3 style="font-family: Syne, sans-serif; font-weight: 700; margin: 0; '
            f'color: {_TEXT};">🎯 Your Campaigns</h3>',
            unsafe_allow_html=True,
        )
    with show_all_col:
        if len(filtered) > 3:
            if st.button("Show All →", key="show_all_btn", use_container_width=True):
                st.session_state["show_all_campaigns"] = not st.session_state.get("show_all_campaigns", False)
                st.rerun()
        else:
            st.markdown("")

    # ── Display up to 3 cards ──
    display_camps = filtered[:3]
    selected_key = "dashboard_selected_campaign"

    if not filtered:
        st.info(f"No {status_filter.lower()} campaigns found.")
    else:
        cols_per_row = min(len(display_camps), 3)
        cols = st.columns(cols_per_row)
        for idx, camp in enumerate(display_camps):
            with cols[idx]:
                _render_campaign_card(camp, selected_key)

        if len(filtered) > 3 and not st.session_state.get("show_all_campaigns", False):
            st.caption(f"Showing 3 of {len(filtered)} campaigns — click **Show All →** to see the rest.")

    # ── Show All panel ──
    if st.session_state.get("show_all_campaigns", False) and len(filtered) > 3:
        _render_show_all_panel(filtered, selected_key)

    # ── Create campaign button ──
    st.markdown(
        f'<div>',
        unsafe_allow_html=True,
    )
    if st.button("➕ Create New Campaign", use_container_width=True):
        st.session_state["current_page"] = "Campaigns"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  SELECTED CAMPAIGN METRICS
    # ══════════════════════════════════════════════════════════════════════════

    selected_id = st.session_state.get(selected_key)
    if selected_id:
        selected_camp = None
        for c in all_campaigns:
            if c.get("id") == selected_id:
                selected_camp = c
                break
        if selected_camp:
            st.markdown(
                f'<hr style="border: none; border-top: 1px solid {_BORDER}; margin: 32px 0;">',
                unsafe_allow_html=True,
            )
            _render_campaign_details(selected_camp)


# ══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN CARD (light theme)
# ══════════════════════════════════════════════════════════════════════════════

def _render_campaign_card(camp: dict, selected_key: str):
    """Light-themed campaign card."""
    campaign_id = camp.get("id", "")
    name = camp.get("name", "Untitled")
    objective = camp.get("objective", "—")
    status = camp.get("status", "draft")
    channels = camp.get("channels", [])

    active = st.session_state.get("active_campaign")
    is_active = active and active.get("id") == campaign_id
    is_selected = st.session_state.get(selected_key) == campaign_id

    # Status badge
    s_upper = status.upper()
    if s_upper == "ACTIVE":
        badge_bg = _GREEN_BG
        badge_color = _GREEN
        badge_dot = "🟢"
    elif s_upper == "PAUSED":
        badge_bg = "#FFF3E0"
        badge_color = "#E65100"
        badge_dot = "🟠"
    elif s_upper == "COMPLETED":
        badge_bg = "#E8E4DC"
        badge_color = _MUTED
        badge_dot = "✅"
    else:
        badge_bg = "#FFF0EB"
        badge_color = _ACCENT
        badge_dot = "📝"

    # Channel icon chips
    chip_html = ""
    for ch_id in channels[:4]:
        ch = _CHANNEL_MAP.get(ch_id, {"icon": "📌"})
        chip_html += (
            f'<span style="background: {_ACCENT_LIGHT}; padding: 2px 6px; border-radius: 6px; '
            f'font-size: 0.7rem; margin-right: 2px;">{ch.get("icon", "📌")}</span>'
        )

    # Card border
    if is_selected:
        card_border = f"border: 2px solid {_ACCENT};"
        card_bg = "#FFFAF8"
        card_shadow = f"box-shadow: 0 0 0 3px {_ACCENT_LIGHT};"
    else:
        card_border = f"border: 1.5px solid {_BORDER};"
        card_bg = _SURFACE
        card_shadow = ""

    st.markdown(
        f'<div class="fade-up-1" style="background: {card_bg}; {card_border} border-radius: 16px; '
        f'padding: 20px; min-height: 140px; {card_shadow}">'
        # Top row: badge + chips
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        f'<span style="font-size: 0.68rem; font-weight: 600; color: {badge_color}; '
        f'background: {badge_bg}; padding: 3px 10px; border-radius: 12px;">{badge_dot} {s_upper}</span>'
        f'<span>{chip_html}</span>'
        f'</div>'
        # Name
        f'<div style="font-family: Syne, sans-serif; font-weight: 700; font-size: 1.05rem; '
        f'color: {_TEXT}; margin-bottom: 4px;">{name}{"  ⭐" if is_active else ""}</div>'
        # Objective
        f'<div style="color: {_MUTED}; font-size: 0.8rem; line-height: 1.4;">'
        f'{objective[:70]}{"..." if len(objective) > 70 else ""}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Action row
    act_col, drop_col = st.columns([2, 1])
    with act_col:
        if is_selected:
            st.button("👁 Viewing", key=f"sel_{campaign_id}", use_container_width=True, disabled=True)
        else:
            if st.button("📊 View Metrics", key=f"sel_{campaign_id}", use_container_width=True):
                st.session_state[selected_key] = campaign_id
                st.session_state["active_campaign"] = camp
                if "generated_content" in st.session_state:
                    del st.session_state["generated_content"]
                st.rerun()

    with drop_col:
        action = st.selectbox(
            "—",
            ["—", "✏️ Edit", "✦ Generate", "📅 Calendar"],
            key=f"action_{campaign_id}",
            label_visibility="collapsed",
        )
        if action == "✏️ Edit":
            st.session_state["editing_campaign"] = camp
            st.session_state["active_campaign"] = camp
            st.session_state["current_page"] = "Campaigns"
            st.rerun()
        elif action == "✦ Generate":
            st.session_state["active_campaign"] = camp
            st.session_state["current_page"] = "Generate"
            st.rerun()
        elif action == "📅 Calendar":
            st.session_state["active_campaign"] = camp
            st.session_state["current_page"] = "Calendar"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  SHOW ALL PANEL
# ══════════════════════════════════════════════════════════════════════════════

def _render_show_all_panel(campaigns: list, selected_key: str):
    """Scrollable inline panel."""
    with st.container(border=True):
        h_l, h_r = st.columns([4, 1])
        with h_l:
            st.markdown(f"**All Campaigns ({len(campaigns)})**")
        with h_r:
            if st.button("✕ Close", key="close_all_btn", use_container_width=True):
                st.session_state["show_all_campaigns"] = False
                st.rerun()

        st.markdown(
            f'<div style="max-height: 400px; overflow-y: auto;">',
            unsafe_allow_html=True,
        )

        for camp in campaigns:
            cid = camp.get("id", "")
            name = camp.get("name", "Untitled")
            objective = camp.get("objective", "—")
            status = camp.get("status", "draft").upper()

            active = st.session_state.get("active_campaign")
            is_active = active and active.get("id") == cid

            if status == "ACTIVE":
                badge_color = _GREEN
            elif status == "DRAFT":
                badge_color = _ACCENT
            else:
                badge_color = _MUTED

            row1, row2 = st.columns([4, 1])
            with row1:
                st.markdown(
                    f'{"⭐ " if is_active else ""}**{name}** '
                    f'<span style="color: {badge_color}; font-size: 0.7rem; font-weight: 600;">{status}</span>'
                    f'<br/><span style="color: {_MUTED}; font-size: 0.78rem;">'
                    f'{objective[:70]}{"..." if len(objective) > 70 else ""}</span>',
                    unsafe_allow_html=True,
                )
            with row2:
                if not is_active:
                    if st.button("📊 View", key=f"all_view_{cid}", use_container_width=True):
                        st.session_state["active_campaign"] = camp
                        st.session_state[selected_key] = cid
                        st.session_state["show_all_campaigns"] = False
                        if "generated_content" in st.session_state:
                            del st.session_state["generated_content"]
                        st.rerun()
                else:
                    st.markdown(
                        f'<span style="color: {_GREEN}; font-size: 0.75rem; font-weight: 600;">✓ Active</span>',
                        unsafe_allow_html=True,
                    )
            st.divider()

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOM ANIMATED CHANNEL CHARTS (HTML/SVG/CSS/JS)
# ══════════════════════════════════════════════════════════════════════════════

def _render_channel_charts(ch_data: dict, campaign_id: str, has_data: bool = True):
    """Render premium animated bar + pie chart card with full spec compliance."""
    import math

    # ── Prepare channel data ──
    channels_info = []
    total_reach = sum(d.get("reach", 0) for d in ch_data.values())
    total_engagement = 0

    for ch_id, data in ch_data.items():
        ch = _CHANNEL_MAP.get(ch_id, {"icon": "\U0001f4cc", "name": ch_id})
        color = _BRAND_COLORS.get(ch_id, _ACCENT)
        rate = data.get("engagement_rate", 0)
        reach = data.get("reach", 0)
        total_engagement += rate
        channels_info.append({
            "id": ch_id,
            "name": ch.get("name", ch_id),
            "icon": ch.get("icon", "\U0001f4cc"),
            "color": color,
            "rate": rate,
            "reach": reach,
            "clicks": data.get("clicks", 0),
            "conversions": data.get("conversions", 0),
            "reach_pct": round(reach / total_reach * 100, 1) if total_reach else 0,
        })

    avg_rate = round(total_engagement / len(channels_info), 1) if channels_info else 0

    # Y-axis: dynamic ticks, at least up to 8
    max_rate_val = max((c["rate"] for c in channels_info), default=8)
    max_y = max(8, math.ceil(max_rate_val / 2) * 2)
    ticks = list(range(0, max_y + 1, 2))

    # SVG donut data
    circumference = 502.65
    slices = []
    offset = 0
    for c in channels_info:
        seg = (c["reach"] / total_reach * circumference) if total_reach else 0
        slices.append({
            "color": c["color"], "name": c["name"], "rate": c["rate"],
            "seg": round(seg, 1), "offset": round(-offset, 1),
            "pct": c["reach_pct"],
        })
        offset += seg

    # Helper: hex to rgb components
    def _rgb(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    # ── Build stat cards HTML ──
    stat_cards = ""
    for c in channels_info:
        r, g, b = _rgb(c["color"])
        stat_cards += (
            f'<div class="stat-card" style="border-color: rgba({r},{g},{b},0.25);">'
            f'<div class="stat-dot-row"><span class="stat-dot" style="background:{c["color"]};"></span>'
            f'<span class="stat-plat">{c["name"].upper()}</span></div>'
            f'<div class="stat-val" style="color:{c["color"]};">{c["rate"]}%</div>'
            f'<div class="stat-sub">engagement rate</div>'
            f'</div>'
        )

    # ── Build y-axis ticks + grid lines ──
    y_ticks = ""
    grid_lines = ""
    for v in reversed(ticks):
        pct = (v / max_y) * 100
        y_ticks += f'<span class="y-tick">{v}</span>'
        if v > 0:
            grid_lines += f'<div class="grid-line" style="bottom:{pct}%;"></div>'

    # ── Build bar columns (with hover tooltip) ──
    bars_html = ""
    for i, c in enumerate(channels_info):
        r, g, b = _rgb(c["color"])
        h_pct = round((c["rate"] / max_y) * 100, 1)
        bars_html += (
            f'<div class="bar-col" '
            f'onmouseenter="showTip(this,\'{c["name"]}\',\'{c["rate"]}\',\'{c["reach"]:,}\',\'{c["clicks"]:,}\',\'{c["color"]}\')" '
            f'onmouseleave="hideTip()">'
            f'<span class="bar-val" style="color:{c["color"]};">{c["rate"]}%</span>'
            f'<div class="bar-el" data-h="{h_pct}" '
            f'style="background:linear-gradient(to top,rgba({r},{g},{b},0.3),{c["color"]});'
            f'--delay:{i*120}ms;"></div>'
            f'<span class="bar-plat" style="color:{c["color"]};"></span>'
            f'</div>'
        )

    # ── Build bar legend ──
    bar_legend = ""
    for c in channels_info:
        bar_legend += (
            f'<span class="bl-item"><span class="bl-dash" style="background:{c["color"]};"></span>'
            f'{c["name"]}</span>'
        )

    # ── Build pie circles ──
    pie_circles = ""
    for i, s in enumerate(slices):
        pie_circles += (
            f'<circle class="pie-slice" r="80" cx="110" cy="110" '
            f'fill="none" stroke="{s["color"]}" stroke-width="28" '
            f'stroke-dasharray="0 {circumference}" '
            f'data-seg="{s["seg"]}" data-circ="{circumference}" '
            f'stroke-dashoffset="{s["offset"]}" '
            f'style="--delay:{i*120}ms;" />'
        )

    # ── Build pie legend (right side) ──
    pie_legend = ""
    for s in slices:
        pie_legend += (
            f'<div class="pl-item">'
            f'<span class="pl-sq" style="background:{s["color"]};"></span>'
            f'<div><span class="pl-name">{s["name"]}</span>'
            f'<span class="pl-detail">{s["rate"]}% &middot; {s["pct"]}% of total</span></div>'
            f'</div>'
        )

    html = f'''<!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:transparent;font-family:'DM Sans',sans-serif;color:#111118}}

    .card{{border-radius:20px;padding:24px;box-shadow:0 4px 24px rgba(0.06,0.06,0.06,0.06); margin-top:5px;}}

    /* ── Header ── */
    .hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
    .hdr-l{{display:flex;align-items:center;gap:12px}}
    .hdr-icon{{width:42px;height:42px;border-radius:10px;background:linear-gradient(135deg,#FF2D78,#FF6B00);display:flex;align-items:center;justify-content:center;font-size:20px}}
    .hdr-t{{font-family:'Syne',sans-serif;font-weight:800;font-size:1.15rem}}
    .hdr-s{{font-family:'DM Mono',monospace;font-size:0.6rem;color:#8a8a9a;letter-spacing:.06em;margin-top:2px}}
    .live{{display:flex;align-items:center;gap:6px;background:rgba(0,191,165,.1);color:#00BFA5;padding:4px 12px;border-radius:20px;font-family:'DM Mono',monospace;font-size:.68rem;font-weight:500}}
    .pulse{{width:6px;height:6px;border-radius:50%;background:#00BFA5;animation:p 2s infinite}}
    @keyframes p{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.4;transform:scale(1.4)}}}}

    /* ── Toggle ── */
    .tog{{position:relative;display:flex;background:#f4f3ef;border-radius:12px;padding:3px;margin-bottom:16px}}
    .tog-pill{{position:absolute;top:3px;left:3px;width:calc(50% - 3px);height:calc(100% - 6px);background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.08);transition:transform .4s cubic-bezier(.34,1.56,.64,1)}}
    .tog-pill.right{{transform:translateX(100%)}}
    .tog-btn{{flex:1;padding:8px 0;border:none;background:transparent;font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;color:#8a8a9a;cursor:pointer;position:relative;z-index:1;transition:color .3s ease}}
    .tog-btn.active{{color:#111118}}

    /* ── Stat cards ── */
    .stats{{display:grid;grid-template-columns:repeat({len(channels_info)},1fr);gap:10px;margin-bottom:16px}}
    .stat-card{{border:1.5px solid;border-radius:12px;padding:14px;background:#fff}}
    .stat-dot-row{{display:flex;align-items:center;gap:5px;margin-bottom:4px}}
    .stat-dot{{width:6px;height:6px;border-radius:50%}}
    .stat-plat{{font-family:'Syne',sans-serif;font-weight:600;font-size:.62rem;letter-spacing:.06em;color:#8a8a9a}}
    .stat-val{{font-family:'DM Mono',monospace;font-weight:500;font-size:1.55rem;line-height:1.1}}
    .stat-sub{{font-size:.62rem;color:#8a8a9a;margin-top:2px}}

    /* ── View container ── */
    .vc{{position:relative;min-height:280px}}
    .cv{{position:absolute;top:0;left:0;width:100%;opacity:0;pointer-events:none;transform:translateY(12px);transition:opacity .3s ease,transform .3s ease}}
    .cv.active{{position:relative;opacity:1;pointer-events:auto;transform:translateY(0)}}

    /* ── Bar chart ── */
    .bar-title{{font-family:'DM Mono',monospace;font-size:.58rem;font-weight:500;color:#8a8a9a;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}}
    .bar-area{{display:flex;gap:0}}
    .y-ax{{display:flex;flex-direction:column;justify-content:space-between;width:26px;padding-right:6px}}
    .y-tick{{font-family:'DM Mono',monospace;font-size:.62rem;color:#8a8a9a;text-align:right;line-height:1}}
    .bars-box{{flex:1;position:relative;height:200px;border-left:1px solid rgba(0,0,0,.06);border-bottom:1px solid rgba(0,0,0,.06)}}
    .grid-line{{position:absolute;left:0;right:0;height:1px;background:rgba(0,0,0,.05)}}
    .bars-row{{position:absolute;inset:0;display:flex;align-items:stretch}}
    .bar-col{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding:0 0px}}
    .bar-val{{font-family:'DM Mono',monospace;font-size:.7rem;font-weight:500;margin-bottom:3px}}
    .bar-el{{width:100%;max-width:48px;border-radius:6px 6px 0 0;height:0;transition:height .7s cubic-bezier(.4,0,.2,1);transition-delay:var(--delay,0ms)}}
    .bar-plat{{font-family:'Syne',sans-serif;font-size:.65rem;font-weight:600;margin-top:6px;white-space:nowrap}}

    /* ── Bar legend ── */
    .bl{{display:flex;justify-content:center;gap:18px;margin-top:14px}}
    .bl-item{{display:flex;align-items:center;gap:6px;font-size:.72rem;color:#8a8a9a}}
    .bl-dash{{width:14px;height:3px;border-radius:2px}}

    /* ── Pie chart ── */
    .pie-lay{{display:flex;align-items:center;gap:28px;justify-content:center;padding:8px 0}}
    .pie-slice{{transition:stroke-dasharray .7s cubic-bezier(.4,0,.2,1);transition-delay:var(--delay,0ms)}}
    .c-label{{font-family:'Syne',sans-serif;font-weight:800;fill:#111118}}
    .c-sub{{font-family:'DM Mono',monospace;font-weight:500;fill:#8a8a9a;font-size:9px;text-transform:uppercase;letter-spacing:.08em}}

    /* ── Pie legend (right) ── */
    .pl{{display:flex;flex-direction:column;gap:12px}}
    .pl-item{{display:flex;align-items:flex-start;gap:8px}}
    .pl-sq{{width:12px;height:12px;border-radius:3px;flex-shrink:0;margin-top:2px}}
    .pl-name{{font-family:'Syne',sans-serif;font-weight:700;font-size:.8rem;display:block}}
    .pl-detail{{font-family:'DM Mono',monospace;font-size:.65rem;color:#8a8a9a;display:block;margin-top:1px}}

    /* ── Hover tooltip ── */
    .tip{{position:fixed;z-index:100;pointer-events:none;opacity:0;transform:translateY(6px);transition:opacity .2s ease,transform .2s ease;background:#fff;border-radius:12px;padding:14px 16px;box-shadow:0 8px 32px rgba(0,0,0,.12);min-width:160px}}
    .tip.show{{opacity:1;transform:translateY(0)}}
    .tip-name{{font-family:'Syne',sans-serif;font-weight:700;font-size:.85rem;margin-bottom:6px;display:flex;align-items:center;gap:6px}}
    .tip-dot{{width:8px;height:8px;border-radius:50%}}
    .tip-row{{display:flex;justify-content:space-between;align-items:center;font-size:.72rem;color:#8a8a9a;padding:3px 0}}
    .tip-row span:last-child{{font-family:'DM Mono',monospace;font-weight:500;color:#111118}}

    /* ── No-data banner ── */
    .no-data{{text-align:center;padding:8px 12px;margin-bottom:12px;background:rgba(0,0,0,.03);border-radius:8px;font-size:.72rem;color:#8a8a9a;font-family:'DM Sans',sans-serif}}
    .no-data b{{color:#FF4D00}}
    </style></head><body>

    <div class="card">
      <!-- Header -->
      <div class="hdr">
        <div class="hdr-l">
          <div class="hdr-icon">\U0001f4ca</div>
          <div><div class="hdr-t">Channel Performance</div>
          <div class="hdr-s">ENGAGEMENT RATE \u00b7 Q1 2025</div></div>
        </div>
        <div class="live"><span class="pulse"></span>LIVE</div>
      </div>

      <!-- Toggle -->
      <div class="tog">
        <div class="tog-pill" id="pill"></div>
        <button class="tog-btn active" id="btn-bar" onclick="setView('bar')">Bar Graph</button>
        <button class="tog-btn" id="btn-pie" onclick="setView('pie')">Pie Chart</button>
      </div>

      <!-- Stat Cards -->
      <div class="stats">{stat_cards}</div>
      {'<div class="no-data">No analytics yet \u2014 <b>seed from Analytics</b> to populate charts</div>' if not has_data else ''}

      <!-- Views -->
      <div class="vc">
        <!-- Bar View -->
        <div class="cv active" id="view-bar">
          <div class="bar-title">ENGAGEMENT RATE (%)</div>
          <div class="bar-area">
            <div class="y-ax">{y_ticks}</div>
            <div class="bars-box">
              {grid_lines}
              <div class="bars-row">{bars_html}</div>
            </div>
          </div>
          <div class="bl">{bar_legend}</div>
        </div>

        <!-- Pie View -->
        <div class="cv" id="view-pie">
          <div class="pie-lay">
            <svg width="220" height="220" viewBox="0 0 220 220">
              <g transform="rotate(-90 110 110)">{pie_circles}</g>
              <circle r="62" cx="110" cy="110" fill="#ffffff"/>
              <text x="110" y="106" text-anchor="middle" class="c-label" font-size="22">{avg_rate}%</text>
              <text x="110" y="122" text-anchor="middle" class="c-sub">AVG TOTAL</text>
            </svg>
            <div class="pl">{pie_legend}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hover tooltip -->
    <div class="tip" id="tip">
      <div class="tip-name" id="tip-name"><span class="tip-dot" id="tip-dot"></span><span id="tip-ch"></span></div>
      <div class="tip-row"><span>Engagement</span><span id="tip-rate"></span></div>
      <div class="tip-row"><span>Reach</span><span id="tip-reach"></span></div>
      <div class="tip-row"><span>Clicks</span><span id="tip-clicks"></span></div>
    </div>

    <script>
    function animateBars(){{
      document.querySelectorAll('.bar-el').forEach(function(el){{
        el.style.height='0';void el.offsetWidth;
        el.style.height=el.dataset.h+'%';
      }});
    }}
    function animatePie(){{
      document.querySelectorAll('.pie-slice').forEach(function(el){{
        var s=parseFloat(el.dataset.seg),c=parseFloat(el.dataset.circ);
        el.setAttribute('stroke-dasharray','0 '+c);void el.offsetWidth;
        el.setAttribute('stroke-dasharray',s+' '+c);
      }});
    }}
    function setView(n){{
      document.querySelectorAll('.cv').forEach(function(v){{v.classList.remove('active')}});
      document.querySelectorAll('.tog-btn').forEach(function(b){{b.classList.remove('active')}});
      var pill=document.getElementById('pill');
      if(n==='pie'){{pill.classList.add('right')}}else{{pill.classList.remove('right')}}
      setTimeout(function(){{
        var t=document.getElementById('view-'+n),b=document.getElementById('btn-'+n);
        if(t)t.classList.add('active');if(b)b.classList.add('active');
        if(n==='bar')animateBars();if(n==='pie')animatePie();
      }},120);
    }}
    setTimeout(animateBars,100);

    var tipEl=document.getElementById('tip');
    function showTip(el,name,rate,reach,clicks,color){{
      document.getElementById('tip-ch').textContent=name;
      document.getElementById('tip-dot').style.background=color;
      document.getElementById('tip-rate').textContent=rate+'%';
      document.getElementById('tip-reach').textContent=reach;
      document.getElementById('tip-clicks').textContent=clicks;
      var r=el.getBoundingClientRect();
      tipEl.style.left=(r.left+r.width/2-80)+'px';
      tipEl.style.top=(r.top-10)+'px';
      tipEl.classList.add('show');
    }}
    function hideTip(){{tipEl.classList.remove('show');}}
    </script></body></html>'''

    components.html(html, height=640, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN DETAILS PANEL
# ══════════════════════════════════════════════════════════════════════════════

def _render_campaign_details(camp: dict):
    """Performance panel for the selected campaign."""
    campaign_id = camp.get("id", "")
    name = camp.get("name", "Untitled")
    channels = camp.get("channels", [])

    st.markdown(
        f'<div class="fade-up-2">'
        f'<h3 style="font-family: Syne, sans-serif; font-weight: 700; color: {_TEXT};">'
        f'📊 <span style="color: {_ACCENT};">{name}</span> — Performance</h3>'
        f'<p style="color: {_MUTED}; font-size: 0.85rem; margin-top: -8px;">'
        f'Live snapshot of your campaign\'s activity</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Content stats as HTML cards ──
    content = api_client.list_content(campaign_id)
    if not content or not isinstance(content, list):
        content = []

    total = len(content)
    pub = len([c for c in content if c.get("status") == "published"])
    sched = len([c for c in content if c.get("status") == "scheduled"])
    drafts = total - pub - sched

    stats = [
        ("📄 CONTENT", total, True),   # True = dark inverted card
        ("✅ PUBLISHED", pub, False),
        ("📅 SCHEDULED", sched, False),
        ("✏️ DRAFTS", drafts, False),
    ]

    cols = st.columns(4)
    for i, (label, value, is_dark) in enumerate(stats):
        with cols[i]:
            if is_dark:
                bg = _TEXT
                text_color = "#fff"
                label_color = "#999"
            else:
                bg = _CARD
                text_color = _TEXT
                label_color = _MUTED

            st.markdown(
                f'<div class="fade-up-3" style="background: {bg}; border: 1px solid {_BORDER}; '
                f'border-radius: 16px; padding: 24px; text-align: left;">'
                f'<div style="font-size: 0.65rem; font-weight: 600; text-transform: uppercase; '
                f'letter-spacing: 0.08em; color: {label_color}; margin-bottom: 4px;">{label}</div>'
                f'<div style="font-family: Syne, sans-serif; font-size: 2.8rem; font-weight: 800; '
                f'color: {text_color}; letter-spacing: -3px; line-height: 1;">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Two columns: Channel Performance + Upcoming Posts ──
    col_perf, col_upcoming = st.columns(2)

    with col_perf:
        # Always render the integrated Channel Performance card
        analytics_result = api_client.get_analytics(campaign_id)
        analytics_data = analytics_result.get("data") if analytics_result else None

        if analytics_data and analytics_data.get("channels"):
            ch_data = analytics_data["channels"]
            _render_channel_charts(ch_data, campaign_id, has_data=True)
        else:
            # Build zero-value defaults from campaign channels
            ch_data = {}
            for ch_id in (channels or ["instagram", "facebook", "tiktok"]):
                ch_data[ch_id] = {
                    "engagement_rate": 0,
                    "reach": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "shares": 0,
                    "likes": 0,
                }
            _render_channel_charts(ch_data, campaign_id, has_data=False)

    with col_upcoming:
        st.markdown(
            f'<h4 style="font-family: Syne, sans-serif; font-weight: 700; color: {_TEXT}; '
            f'margin-top: 16px;">📅 Upcoming Posts</h4>',
            unsafe_allow_html=True,
        )
        _render_upcoming(content)

    # ── Quick action buttons ──
    st.markdown("")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("✦ Generate Content", key="detail_gen", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "Generate"
            st.rerun()
    with q2:
        if st.button("📅 Calendar", key="detail_cal", use_container_width=True):
            st.session_state["current_page"] = "Calendar"
            st.rerun()
    with q3:
        if st.button("◈ Analytics", key="detail_ana", use_container_width=True):
            st.session_state["current_page"] = "Analytics"
            st.rerun()
    with q4:
        if st.button("💬 Correspondence", key="detail_corr", use_container_width=True):
            st.session_state["current_page"] = "Correspondence"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  UPCOMING POSTS
# ══════════════════════════════════════════════════════════════════════════════

def _render_upcoming(content_list: list):
    today = date.today()
    next_week = today + timedelta(days=7)

    upcoming = []
    for c in content_list:
        sched_str = c.get("scheduled_at")
        if not sched_str or c.get("status") == "published":
            continue
        try:
            sched_dt = datetime.fromisoformat(sched_str)
            if today <= sched_dt.date() <= next_week:
                upcoming.append((sched_dt, c))
        except (ValueError, TypeError):
            continue

    if not upcoming:
        st.markdown(
            f'<div style="color: {_MUTED}; font-size: 0.85rem; padding: 16px 0;">'
            f'No upcoming posts in the next 7 days.</div>',
            unsafe_allow_html=True,
        )
        return

    upcoming.sort(key=lambda x: x[0])

    for sched_dt, post in upcoming[:6]:
        ch = _CHANNEL_MAP.get(post.get("channel", ""), {"icon": "📌", "name": "?"})
        day_str = sched_dt.strftime("%b %d").upper()
        time_str = sched_dt.strftime("%I:%M %p")
        status = post.get("status", "draft")

        if status == "scheduled":
            s_bg = "#EEF0FF"
            s_color = "#4158D0"
        else:
            s_bg = _BORDER
            s_color = _MUTED

        st.markdown(
            f'<div style="display: flex; align-items: center; padding: 10px 0; '
            f'border-bottom: 1px solid {_BORDER};">'
            # Date block
            f'<div style="min-width: 50px; font-size: 0.68rem; font-weight: 600; '
            f'color: {_MUTED}; text-transform: uppercase; letter-spacing: 0.03em;">{day_str}</div>'
            # Title + meta
            f'<div style="flex: 1;">'
            f'<div style="font-weight: 500; font-size: 0.82rem; color: {_TEXT};">'
            f'{ch["icon"]} {ch["name"]}</div>'
            f'<div style="font-size: 0.72rem; color: {_MUTED};">{time_str}</div>'
            f'</div>'
            # Status badge
            f'<span style="font-size: 0.65rem; font-weight: 600; color: {s_color}; '
            f'background: {s_bg}; padding: 2px 10px; border-radius: 10px;">{status}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
