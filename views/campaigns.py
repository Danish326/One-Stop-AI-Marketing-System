"""
NEXUS — Campaigns Page
Create, view, edit, and delete campaigns.
Features: F-01 (Campaign form), F-14 (Campaign list), F-18 (Tone/channel config)
"""

import streamlit as st
from services import api_client
from config.settings import (
    CHANNELS, TONE_OPTIONS, OBJECTIVE_SUGGESTIONS, DURATION_OPTIONS
)


def render():
    st.header("🎯 Campaigns")

    # ── Check for edit mode ──
    if st.session_state.get("editing_campaign"):
        _render_edit_form()
        return

    # ── Normal view: List + Create ──
    _render_campaign_list()
    st.divider()
    _render_create_form()


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN LIST (F-14)
# ═══════════════════════════════════════════════════════════════════════════════

def _render_campaign_list():
    """Show all campaigns as selectable cards with edit/delete actions."""

    user_id = st.session_state.get("user_id")
    campaigns = api_client.list_campaigns(user_id)

    if not campaigns:
        st.info("No campaigns yet. Create your first one below! 👇")
        return

    st.subheader("Your Campaigns")

    active_id = None
    if st.session_state.get("active_campaign"):
        active_id = st.session_state["active_campaign"].get("id")

    # Channel lookup
    channel_map = {ch["id"]: ch for ch in CHANNELS}

    for camp in campaigns:
        is_active = camp.get("id") == active_id
        border_color = "#6c63ff" if is_active else "rgba(255,255,255,0.08)"
        bg = "rgba(108, 99, 255, 0.06)" if is_active else "rgba(26, 26, 46, 0.3)"

        with st.container(border=True):
            # ── Top row: name + status + actions ──
            top_left, top_right = st.columns([3, 1])

            with top_left:
                label = f"**{camp.get('name', 'Untitled')}**"
                if is_active:
                    label += "  ✅ *Active*"
                st.markdown(label)
                st.caption(f"{camp.get('objective', '')[:120]}{'...' if len(camp.get('objective', '')) > 120 else ''}")

            with top_right:
                status = camp.get("status", "draft").upper()
                color = "#4ade80" if status == "ACTIVE" else "#f59e0b"
                st.markdown(
                    f'<span style="font-size: 0.7rem; font-weight: 700; color: {color}; '
                    f'background: {color}22; padding: 3px 10px; border-radius: 6px; '
                    f'letter-spacing: 0.05em;">{status}</span>',
                    unsafe_allow_html=True,
                )

            # ── Middle row: details ──
            d1, d2, d3 = st.columns(3)
            with d1:
                st.caption(f"🎯 **Audience:** {camp.get('audience', '—')}")
            with d2:
                st.caption(f"🎨 **Tone:** {camp.get('tone', '—')}")
            with d3:
                st.caption(f"📆 **Duration:** {camp.get('duration_weeks', '—')} weeks")

            # Channel pills
            channels = camp.get("channels", [])
            pills_html = ""
            for ch_id in channels:
                ch = channel_map.get(ch_id, {})
                pills_html += (
                    f'<span style="display:inline-block; background: rgba(108,99,255,0.12); '
                    f'padding: 2px 8px; border-radius: 6px; margin: 2px 3px 2px 0; '
                    f'font-size: 0.72rem; color: #b0b0ff;">{ch.get("icon", "")} {ch.get("name", ch_id)}</span>'
                )
            if pills_html:
                st.markdown(pills_html, unsafe_allow_html=True)

            # ── Bottom row: action buttons ──
            b1, b2, b3, b4 = st.columns(4)

            with b1:
                if not is_active:
                    if st.button("✅ Set Active", key=f"select_{camp['id']}", use_container_width=True):
                        st.session_state["active_campaign"] = camp
                        st.rerun()
                else:
                    st.button("✅ Active", key=f"active_{camp['id']}", use_container_width=True, disabled=True)

            with b2:
                if st.button("✏️ Edit", key=f"edit_{camp['id']}", use_container_width=True):
                    st.session_state["editing_campaign"] = camp
                    st.rerun()

            with b3:
                if st.button("🗑️ Delete", key=f"del_{camp['id']}", use_container_width=True):
                    st.session_state[f"confirm_delete_{camp['id']}"] = True
                    st.rerun()

            # ── Delete confirmation ──
            if st.session_state.get(f"confirm_delete_{camp['id']}"):
                st.warning(f"⚠️ Are you sure you want to delete **{camp['name']}**? This cannot be undone.")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("🗑️ Yes, Delete", key=f"confirm_yes_{camp['id']}", use_container_width=True, type="primary"):
                        result = api_client.delete_campaign(camp["id"])
                        # Clear active campaign if this was the active one
                        if is_active:
                            st.session_state["active_campaign"] = None
                        del st.session_state[f"confirm_delete_{camp['id']}"]
                        st.success(f"Deleted **{camp['name']}**.")
                        st.rerun()
                with c_no:
                    if st.button("Cancel", key=f"confirm_no_{camp['id']}", use_container_width=True):
                        del st.session_state[f"confirm_delete_{camp['id']}"]
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  EDIT FORM
# ═══════════════════════════════════════════════════════════════════════════════

def _render_edit_form():
    """Inline edit form for an existing campaign."""

    camp = st.session_state["editing_campaign"]
    campaign_id = camp["id"]

    st.subheader(f"✏️ Editing: {camp.get('name', '')}")

    # Back button
    if st.button("← Back to List"):
        st.session_state["editing_campaign"] = None
        st.rerun()

    with st.form("edit_campaign_form"):
        name = st.text_input("Campaign Name", value=camp.get("name", ""))

        objective = st.text_area("Campaign Objective", value=camp.get("objective", ""))

        col1, col2 = st.columns(2)
        with col1:
            audience = st.text_input("Target Audience", value=camp.get("audience", ""))
        with col2:
            current_tone = camp.get("tone", TONE_OPTIONS[0])
            tone_idx = TONE_OPTIONS.index(current_tone) if current_tone in TONE_OPTIONS else 0
            tone = st.selectbox("Brand Tone", options=TONE_OPTIONS, index=tone_idx)

        # Channels
        channel_options = [f'{ch["icon"]} {ch["name"]}' for ch in CHANNELS]
        channel_ids = [ch["id"] for ch in CHANNELS]

        # Pre-select current channels
        current_channels = camp.get("channels", [])
        default_display = [
            f'{channel_map_lookup(ch_id)["icon"]} {channel_map_lookup(ch_id)["name"]}'
            for ch_id in current_channels
            if channel_map_lookup(ch_id)
        ]

        selected_display = st.multiselect(
            "Channels", options=channel_options, default=default_display,
        )
        selected_channels = [
            channel_ids[channel_options.index(d)]
            for d in selected_display if d in channel_options
        ]

        # Duration
        current_duration = camp.get("duration_weeks", 2)
        dur_idx = DURATION_OPTIONS.index(current_duration) if current_duration in DURATION_OPTIONS else 1
        duration = st.selectbox("Duration (weeks)", options=DURATION_OPTIONS, index=dur_idx)

        # Status
        status = st.selectbox("Status", options=["active", "paused", "completed"], index=0)

        # Submit
        col_save, col_cancel = st.columns(2)
        with col_save:
            save = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        with col_cancel:
            cancel = st.form_submit_button("✖ Cancel", use_container_width=True)

        if save:
            if not name:
                st.error("Campaign name is required.")
                return

            updates = {
                "name": name,
                "objective": objective,
                "audience": audience,
                "tone": tone,
                "channels": selected_channels,
                "duration_weeks": duration,
                "status": status,
            }
            result = api_client.update_campaign(campaign_id, updates)

            if result.get("id"):
                # Update active campaign if this was the active one
                active = st.session_state.get("active_campaign")
                if active and active.get("id") == campaign_id:
                    st.session_state["active_campaign"] = result

                st.session_state["editing_campaign"] = None
                st.success(f"✅ **{name}** updated!")
                st.rerun()
            else:
                st.error(f"Update failed: {result.get('message', 'Unknown error')}")

        if cancel:
            st.session_state["editing_campaign"] = None
            st.rerun()


def channel_map_lookup(ch_id: str) -> dict:
    """Helper to look up a channel by its ID."""
    for ch in CHANNELS:
        if ch["id"] == ch_id:
            return ch
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN CREATION FORM (F-01)
# ═══════════════════════════════════════════════════════════════════════════════

def _render_create_form():
    """Campaign creation form with all required fields."""

    st.subheader("➕ Create New Campaign")

    with st.form("create_campaign_form", clear_on_submit=True):
        name = st.text_input(
            "Campaign Name",
            placeholder="e.g. Winter Menu Launch, Black Friday Blitz",
        )

        objective = st.text_area(
            "Campaign Objective",
            placeholder="What do you want this campaign to achieve?",
            help="Be specific. This drives the AI content generation.",
        )
        st.caption("💡 Suggestions: " + " · ".join(OBJECTIVE_SUGGESTIONS[:4]))

        col1, col2 = st.columns(2)
        with col1:
            audience = st.text_input(
                "Target Audience",
                placeholder="e.g. Foodies aged 25–40 in the city",
            )
        with col2:
            tone = st.selectbox("Brand Tone", options=TONE_OPTIONS, index=0)

        channel_options = [f'{ch["icon"]} {ch["name"]}' for ch in CHANNELS]
        channel_ids = [ch["id"] for ch in CHANNELS]

        selected_display = st.multiselect(
            "Channels", options=channel_options, default=channel_options[:3],
            help="Select which platforms to generate content for.",
        )
        selected_channels = [
            channel_ids[channel_options.index(d)]
            for d in selected_display if d in channel_options
        ]

        duration = st.selectbox("Campaign Duration (weeks)", options=DURATION_OPTIONS, index=1)

        submitted = st.form_submit_button(
            "🚀 Create Campaign", use_container_width=True, type="primary",
        )

        if submitted:
            if not name:
                st.error("Campaign name is required.")
                return
            if not objective:
                st.error("Campaign objective is required.")
                return
            if not selected_channels:
                st.error("Select at least one channel.")
                return

            data = {
                "name": name,
                "objective": objective,
                "audience": audience,
                "tone": tone,
                "channels": selected_channels,
                "duration_weeks": duration,
                "user_id": st.session_state.get("user_id", ""),
            }

            result = api_client.create_campaign(data)

            if result.get("id"):
                st.session_state["active_campaign"] = result
                st.success(f"✅ Campaign **{name}** created and set as active!")
                st.balloons()
                st.rerun()
            else:
                st.error(f"Failed to create campaign: {result.get('message', 'Unknown error')}")
