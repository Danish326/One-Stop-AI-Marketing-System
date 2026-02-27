"""
NEXUS — Calendar Page
Content calendar with weekly grid view showing scheduled/published posts.
Features: F-06 (Calendar grid), F-15 (Status lifecycle), F-16 (Mark as Published)
"""

import streamlit as st
from datetime import datetime, timedelta, date
from services import api_client
from config.settings import CHANNELS


# Channel lookup
_CHANNEL_MAP = {ch["id"]: ch for ch in CHANNELS}


def render():
    st.header("📅 Content Calendar")

    campaign = st.session_state.get("active_campaign")
    if not campaign:
        st.info("No active campaign selected. Head to **Campaigns** to create or pick one.")
        return

    campaign_id = campaign["id"]

    # ── Load all content ──
    content_list = api_client.list_content(campaign_id)

    if not content_list:
        st.info("No content yet. Head to **Generate** to create content first! ✦")
        return

    # Separate by status
    scheduled = [c for c in content_list if c.get("scheduled_at")]
    drafts = [c for c in content_list if c.get("status") == "draft"]

    # ── Stats bar ──
    s1, s2, s3, s4 = st.columns(4)
    total_draft = len([c for c in content_list if c.get("status") == "draft"])
    total_sched = len([c for c in content_list if c.get("status") == "scheduled"])
    total_pub = len([c for c in content_list if c.get("status") == "published"])
    s1.metric("Total", len(content_list))
    s2.metric("📝 Drafts", total_draft)
    s3.metric("📅 Scheduled", total_sched)
    s4.metric("✅ Published", total_pub)

    st.divider()

    # ── Week navigation ──
    if "calendar_week_start" not in st.session_state:
        today = date.today()
        st.session_state["calendar_week_start"] = today - timedelta(days=today.weekday())

    week_start = st.session_state["calendar_week_start"]
    week_end = week_start + timedelta(days=6)

    nav_left, nav_center, nav_right = st.columns([1, 3, 1])
    with nav_left:
        if st.button("◀ Prev Week", use_container_width=True):
            st.session_state["calendar_week_start"] = week_start - timedelta(weeks=1)
            st.rerun()
    with nav_center:
        st.markdown(
            f"<h3 style='text-align: center; margin: 0;'>"
            f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}</h3>",
            unsafe_allow_html=True,
        )
    with nav_right:
        if st.button("Next Week ▶", use_container_width=True):
            st.session_state["calendar_week_start"] = week_start + timedelta(weeks=1)
            st.rerun()

    st.markdown("")

    # ── Build day columns ──
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)

    for day_offset in range(7):
        current_day = week_start + timedelta(days=day_offset)
        is_today = current_day == date.today()

        with cols[day_offset]:
            # Day header
            header_style = "color: #6c63ff; font-weight: 800;" if is_today else "font-weight: 600;"
            st.markdown(
                f'<div style="text-align: center; {header_style} margin-bottom: 0.3rem;">'
                f'{day_names[day_offset]}<br/>'
                f'<span style="font-size: 1.3rem;">{current_day.day}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if is_today:
                st.markdown(
                    '<div style="text-align: center; font-size: 0.6rem; color: #6c63ff; '
                    'font-weight: 700; margin-bottom: 0.3rem;">TODAY</div>',
                    unsafe_allow_html=True,
                )

            # Find posts for this day
            day_posts = _get_posts_for_day(scheduled, current_day)

            if day_posts:
                for post in day_posts:
                    _render_calendar_card(post, campaign_id)
            else:
                st.caption("—")

    st.divider()

    # ── Unscheduled drafts section ──
    if drafts:
        st.subheader(f"📝 Unscheduled Drafts ({len(drafts)})")
        st.caption("These content pieces haven't been scheduled yet. Head to **Generate** page to schedule them.")
        for draft in drafts:
            ch = _CHANNEL_MAP.get(draft.get("channel", ""), {"icon": "📌", "name": "?"})
            status = draft.get("status", "draft").upper()
            body_preview = (draft.get("body", "")[:80] + "...") if len(draft.get("body", "")) > 80 else draft.get("body", "")
            st.markdown(f"{ch['icon']} **{ch['name']}** — {body_preview}")


def _get_posts_for_day(posts: list, target_date: date) -> list:
    """Filter posts that are scheduled for a specific date."""
    day_posts = []
    for post in posts:
        sched_str = post.get("scheduled_at", "")
        if not sched_str:
            continue
        try:
            sched_dt = datetime.fromisoformat(sched_str)
            if sched_dt.date() == target_date:
                day_posts.append(post)
        except (ValueError, TypeError):
            continue
    return day_posts


def _render_calendar_card(post: dict, campaign_id: str):
    """Render a single post card within a calendar day column."""
    ch = _CHANNEL_MAP.get(post.get("channel", ""), {"icon": "📌", "name": "?"})
    status = post.get("status", "draft")
    content_id = post.get("id", "")

    # Status color
    if status == "published":
        badge_color = "#4ade80"
        badge_text = "✅"
    elif status == "scheduled":
        badge_color = "#6c63ff"
        badge_text = "📅"
    else:
        badge_color = "#888"
        badge_text = "📝"

    # Parse time
    sched_str = post.get("scheduled_at", "")
    time_str = ""
    try:
        sched_dt = datetime.fromisoformat(sched_str)
        time_str = sched_dt.strftime("%I:%M %p")
    except (ValueError, TypeError):
        pass

    # Compact card
    st.markdown(
        f'<div style="background: rgba(108,99,255,0.08); padding: 6px 8px; '
        f'border-radius: 8px; margin-bottom: 6px; border-left: 3px solid {badge_color};">'
        f'<div style="font-size: 0.75rem; font-weight: 700;">{ch["icon"]} {ch["name"]}</div>'
        f'<div style="font-size: 0.65rem; color: #aaa;">{time_str}</div>'
        f'<div style="font-size: 0.6rem; color: {badge_color}; font-weight: 600;">{badge_text} {status.upper()}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # "Publish Now Instead" button — only for scheduled (not yet published) posts
    if status == "scheduled":
        if st.button("📤 Publish Now", key=f"cal_pub_{content_id}", use_container_width=True):
            result = api_client.update_content(content_id, {
                "status": "published",
                "published_at": datetime.now().isoformat(),
            })
            if result.get("success"):
                st.session_state["generated_content"] = api_client.list_content(campaign_id)
                st.success(f"📤 {ch['name']} published now instead of scheduled time!")
                st.rerun()
