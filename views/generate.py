"""
NEXUS — Generate Page
AI content generation per channel with Content Cards.
Features: F-02 (AI generate), F-03 (Content cards), F-04 (Regenerate), F-05 (Schedule), F-13 (Edit)
"""

import streamlit as st
from datetime import datetime, timedelta, date, time
from services import api_client
from config.settings import CHANNELS, SCORE_HIGH, SCORE_MEDIUM


# Channel lookup
_CHANNEL_MAP = {ch["id"]: ch for ch in CHANNELS}


def render():
    st.header("✦ Generate Content")

    campaign = st.session_state.get("active_campaign")
    if not campaign:
        st.info("No active campaign selected. Head to **Campaigns** to create or pick one.")
        return

    campaign_id = campaign["id"]

    # ── Campaign brief summary ──
    with st.container(border=True):
        st.markdown(f"**Active Campaign:** {campaign.get('name', 'Untitled')}")
        st.caption(f"Objective: {campaign.get('objective', '—')}  ·  Tone: {campaign.get('tone', '—')}  ·  Channels: {', '.join(campaign.get('channels', []))}")

    st.markdown("")

    # ── Generate button ──
    col_gen, col_info = st.columns([1, 2])
    with col_gen:
        if st.button("🚀 Generate All Content", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI is generating content for all channels..."):
                result = api_client.generate_content(campaign_id)
            if result.get("success"):
                st.session_state["generated_content"] = result.get("content", [])
                st.success(f"✅ {result.get('message', 'Content generated!')}")
                st.rerun()
            else:
                st.error(f"Generation failed: {result.get('message', 'Unknown error')}")

    with col_info:
        st.caption("This will generate one content piece per selected channel using AI. Any existing content will be replaced.")

    st.divider()

    # ── Load existing content ──
    content_list = st.session_state.get("generated_content")
    if not content_list:
        # Try loading from backend
        content_list = api_client.list_content(campaign_id)
        if content_list:
            st.session_state["generated_content"] = content_list

    if not content_list:
        st.info("No content generated yet. Click **Generate All Content** to start! 🚀")
        return

    # ── Render content cards ──
    st.subheader(f"📝 Generated Content ({len(content_list)} pieces)")

    for i, piece in enumerate(content_list):
        _render_content_card(piece, i, campaign_id, campaign)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT CARD (F-03)
# ═══════════════════════════════════════════════════════════════════════════════

def _render_content_card(piece: dict, index: int, campaign_id: str, campaign: dict):
    """Render a single content card with score, body, and actions."""

    channel_id = piece.get("channel", "")
    ch = _CHANNEL_MAP.get(channel_id, {"icon": "📌", "name": channel_id})
    score = piece.get("ai_score", 0)
    content_id = piece.get("id", f"piece_{index}")

    # Score color
    if score >= SCORE_HIGH:
        score_color = "#4ade80"  # Green
        score_label = "Excellent"
    elif score >= SCORE_MEDIUM:
        score_color = "#f59e0b"  # Amber
        score_label = "Good"
    else:
        score_color = "#ef4444"  # Red
        score_label = "Needs Work"

    # Status info
    status = piece.get("status", "draft").upper()
    scheduled_at = piece.get("scheduled_at")

    with st.container(border=True):
        # ── Header row: channel + score ──
        h_left, h_right = st.columns([3, 1])
        with h_left:
            st.markdown(f"### {ch['icon']} {ch['name']}")
            type_info = f"Type: **{piece.get('content_type', 'post')}**  ·  Best time: **{piece.get('posting_time_suggestion', '—')}**"
            if scheduled_at:
                type_info += f"  ·  📅 Scheduled: **{scheduled_at[:16]}**"
            st.caption(type_info)
        with h_right:
            st.markdown(
                f'<div style="text-align: center; padding: 0.5rem;">'
                f'<div style="font-size: 2rem; font-weight: 800; color: {score_color};">{score}</div>'
                f'<div style="font-size: 0.7rem; color: {score_color}; font-weight: 600;">{score_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Score reasoning ──
        reasoning = piece.get("score_reasoning", "")
        if reasoning:
            st.caption(f"💡 *{reasoning}*")

        # ── Content body ──
        edit_key = f"editing_{content_id}"
        schedule_key = f"scheduling_{content_id}"
        is_editing = st.session_state.get(edit_key, False)
        is_scheduling = st.session_state.get(schedule_key, False)

        if is_editing:
            # Edit mode
            new_body = st.text_area(
                "Edit Content",
                value=piece.get("body", ""),
                height=200,
                key=f"edit_area_{content_id}",
                label_visibility="collapsed",
            )
            save_col, cancel_col = st.columns(2)
            with save_col:
                if st.button("💾 Save", key=f"save_{content_id}", use_container_width=True, type="primary"):
                    result = api_client.update_content(content_id, {
                        "body": new_body,
                        "is_edited": True,
                    })
                    if result.get("success"):
                        st.session_state["generated_content"] = api_client.list_content(campaign_id)
                        st.session_state[edit_key] = False
                        st.success("Saved!")
                        st.rerun()
                    else:
                        st.error("Save failed.")
            with cancel_col:
                if st.button("✖ Cancel", key=f"cancel_{content_id}", use_container_width=True):
                    st.session_state[edit_key] = False
                    st.rerun()
        elif is_scheduling:
            # Schedule mode
            st.markdown("**📅 Schedule this post:**")
            sc1, sc2 = st.columns(2)
            with sc1:
                sched_date = st.date_input("Date", value=date.today() + timedelta(days=1), key=f"sched_date_{content_id}")
            with sc2:
                sched_time = st.time_input("Time", value=time(18, 0), key=f"sched_time_{content_id}")

            sc_save, sc_cancel = st.columns(2)
            with sc_save:
                if st.button("✅ Confirm Schedule", key=f"sched_confirm_{content_id}", use_container_width=True, type="primary"):
                    sched_dt = datetime.combine(sched_date, sched_time).isoformat()
                    result = api_client.update_content(content_id, {
                        "status": "scheduled",
                        "scheduled_at": sched_dt,
                    })
                    if result.get("success"):
                        st.session_state["generated_content"] = api_client.list_content(campaign_id)
                        st.session_state[schedule_key] = False
                        st.success(f"📅 Scheduled for {sched_date.strftime('%b %d')} at {sched_time.strftime('%I:%M %p')}!")
                        st.rerun()
                    else:
                        st.error("Scheduling failed.")
            with sc_cancel:
                if st.button("✖ Cancel", key=f"sched_cancel_{content_id}", use_container_width=True):
                    st.session_state[schedule_key] = False
                    st.rerun()
        else:
            # Display mode
            body = piece.get("body", "")
            st.markdown(f"```\n{body}\n```")

            # Hashtags
            hashtags = piece.get("hashtags", [])
            if hashtags:
                pills = " ".join(f"`{h}`" for h in hashtags)
                st.markdown(f"**Hashtags:** {pills}")

            # Edited badge
            if piece.get("is_edited"):
                st.caption("✏️ *Manually edited*")

        # ── Action buttons ──
        if not is_editing and not is_scheduling:
            a1, a2, a3, a4, a5 = st.columns(5)
            with a1:
                if st.button("✏️ Edit", key=f"btn_edit_{content_id}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
            with a2:
                if st.button("🔄 Regen", key=f"btn_regen_{content_id}", use_container_width=True):
                    with st.spinner(f"Regenerating {ch['name']}..."):
                        result = api_client.regenerate_content(content_id, campaign_id)
                    if result.get("success"):
                        st.session_state["generated_content"] = api_client.list_content(campaign_id)
                        st.success(f"🔄 {ch['name']} regenerated!")
                        st.rerun()
                    else:
                        st.error("Regeneration failed.")
            with a3:
                # Schedule button: only if NOT published
                if status == "PUBLISHED":
                    st.button("📅 Schedule", key=f"btn_sched_{content_id}", use_container_width=True, disabled=True)
                else:
                    if st.button("📅 Schedule", key=f"btn_sched_{content_id}", use_container_width=True):
                        st.session_state[schedule_key] = True
                        st.rerun()
            with a4:
                # Publish button: only if NOT scheduled
                if status == "PUBLISHED":
                    st.button("✅ Published", key=f"btn_pub_{content_id}", use_container_width=True, disabled=True)
                elif status == "SCHEDULED":
                    st.button("📤 Publish", key=f"btn_pub_{content_id}", use_container_width=True, disabled=True)
                else:
                    if st.button("📤 Publish", key=f"btn_pub_{content_id}", use_container_width=True):
                        result = api_client.update_content(content_id, {
                            "status": "published",
                            "published_at": datetime.now().isoformat(),
                        })
                        if result.get("success"):
                            st.session_state["generated_content"] = api_client.list_content(campaign_id)
                            st.success(f"✅ {ch['name']} published!")
                            st.rerun()
            with a5:
                # Status badge
                status_color = "#4ade80" if status == "PUBLISHED" else "#6c63ff" if status == "SCHEDULED" else "#888"
                st.markdown(
                    f'<div style="text-align:center; padding: 0.45rem; font-size: 0.65rem; '
                    f'color: {status_color}; border: 1px solid {status_color}44; border-radius: 6px; '
                    f'font-weight: 700;">{status}</div>',
                    unsafe_allow_html=True,
                )

