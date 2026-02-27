"""
NEXUS — Analytics Page
Performance dashboard with engagement metrics, channel breakdown, and AI insights.
Features: F-08 (Dashboard), F-09 (Channel breakdown), F-10 (AI insights), F-19 (Refresh), F-20 (Seed)
"""

import streamlit as st
from services import api_client
from config.settings import CHANNELS

# Channel lookup
_CHANNEL_MAP = {ch["id"]: ch for ch in CHANNELS}


def render():
    st.header("◈ Analytics & Insights")

    campaign = st.session_state.get("active_campaign")
    if not campaign:
        st.info("No active campaign selected. Head to **Campaigns** to create or pick one.")
        return

    campaign_id = campaign["id"]

    # ── Load analytics ──
    result = api_client.get_analytics(campaign_id)
    analytics = result.get("data") if result else None

    # ── Top bar: Seed + Refresh ──
    bar1, bar2, bar3 = st.columns([1, 1, 3])
    with bar1:
        if st.button("📊 Seed Analytics", use_container_width=True, type="primary"):
            with st.spinner("Generating simulated analytics data..."):
                seed_result = api_client.seed_analytics(campaign_id)
            if seed_result.get("success"):
                st.success("✅ Analytics data seeded!")
                st.rerun()
            else:
                st.error("Failed to seed analytics.")
    with bar2:
        if st.button("🧠 Generate Insights", use_container_width=True):
            if not analytics:
                st.warning("Seed analytics data first!")
            else:
                with st.spinner("🤖 AI is analyzing performance data..."):
                    insight_result = api_client.get_insights(
                        campaign_id,
                        business_name="My Business",
                        objective=campaign.get("objective", ""),
                    )
                if insight_result.get("success"):
                    st.success("✅ Insights generated!")
                    st.rerun()
                else:
                    st.error(f"Failed: {insight_result.get('message', 'Unknown error')}")
    with bar3:
        st.caption("Seed analytics to simulate real engagement data, then generate AI insights.")

    if not analytics:
        st.divider()
        st.info("📊 No analytics data yet. Click **Seed Analytics** to generate simulated engagement data.")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    #  KPI METRICS ROW
    # ═══════════════════════════════════════════════════════════════════════════

    st.divider()
    st.subheader("📊 Campaign Performance Overview")

    totals = analytics.get("totals", {})

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("👁️ Total Reach", f"{totals.get('reach', 0):,}")
    m2.metric("📈 Engagement Rate", f"{totals.get('engagement_rate', 0)}%")
    m3.metric("🖱️ Total Clicks", f"{totals.get('clicks', 0):,}")
    m4.metric("💰 Conversions", f"{totals.get('conversions', 0):,}")
    m5.metric("💬 Comments", f"{totals.get('comments', 0):,}")

    # ═══════════════════════════════════════════════════════════════════════════
    #  CHANNEL BREAKDOWN (F-09)
    # ═══════════════════════════════════════════════════════════════════════════

    st.divider()
    st.subheader("📈 Channel Performance Breakdown")

    channels_data = analytics.get("channels", {})

    if channels_data:
        for ch_id, data in channels_data.items():
            ch = _CHANNEL_MAP.get(ch_id, {"icon": "📌", "name": ch_id})

            with st.container(border=True):
                # Channel header
                ch_left, ch_right = st.columns([3, 1])
                with ch_left:
                    st.markdown(f"### {ch['icon']} {ch['name']}")
                with ch_right:
                    eng_rate = data.get("engagement_rate", 0)
                    color = "#4ade80" if eng_rate >= 4 else "#f59e0b" if eng_rate >= 2.5 else "#ef4444"
                    st.markdown(
                        f'<div style="text-align: center; padding: 0.3rem;">'
                        f'<div style="font-size: 1.5rem; font-weight: 800; color: {color};">{eng_rate}%</div>'
                        f'<div style="font-size: 0.65rem; color: #aaa;">Engagement</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Metrics row
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Reach", f"{data.get('reach', 0):,}")
                c2.metric("Clicks", f"{data.get('clicks', 0):,}")
                c3.metric("Conversions", f"{data.get('conversions', 0):,}")
                c4.metric("Shares", f"{data.get('shares', 0):,}")
                c5.metric("Likes", f"{data.get('likes', 0):,}")
                c6.metric("Comments", f"{data.get('comments', 0):,}")

                # Reach bar
                max_reach = max(d.get("reach", 0) for d in channels_data.values()) or 1
                reach_pct = data.get("reach", 0) / max_reach
                st.progress(reach_pct, text=f"Reach: {data.get('reach', 0):,}")

                # Extra info
                st.caption(
                    f"🕐 Best post time: **{data.get('best_post_time', '—')}** · "
                    f"🏆 Top format: **{data.get('top_content_type', '—')}**"
                )

    # ═══════════════════════════════════════════════════════════════════════════
    #  AI INSIGHTS (F-10)
    # ═══════════════════════════════════════════════════════════════════════════

    insights = analytics.get("insights", [])

    if insights:
        st.divider()
        st.subheader("🧠 AI Strategic Insights")
        st.caption("Powered by AI analysis of your cross-channel performance data.")

        for i, insight in enumerate(insights):
            with st.container(border=True):
                st.markdown(f"### {insight.get('title', f'Insight {i+1}')}")
                st.markdown(insight.get("insight", ""))
                st.markdown(
                    f'<div style="background: rgba(108,99,255,0.08); padding: 10px 14px; '
                    f'border-radius: 8px; margin-top: 6px; border-left: 3px solid #6c63ff;">'
                    f'💡 <strong>Recommendation:</strong> {insight.get("recommendation", "")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
