"""
NEXUS — Correspondence Page
AI auto-reply drafting with confidence scoring, escalation flags, and FAQ handler.
Features: F-17 (AI Reply), F-22 (Escalation), F-21 (FAQ Handler)
"""

import streamlit as st
from services import api_client
from config.settings import CHANNELS


def render():
    st.header("💬 AI Correspondence")

    campaign = st.session_state.get("active_campaign")
    if not campaign:
        st.info("No active campaign selected. Head to **Campaigns** to create or pick one.")
        return

    campaign_id = campaign["id"]

    # ── Two-column layout ──
    tab_reply, tab_history, tab_faq = st.tabs(["✉️ Draft Reply", "📜 History", "📋 FAQ Manager"])

    # ═══════════════════════════════════════════════════════════════════════════
    #  TAB 1: Draft Reply (F-17 + F-22)
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_reply:
        st.subheader("✉️ Draft an AI Reply")
        st.caption("Paste a customer message below and our AI will draft a professional reply.")

        customer_msg = st.text_area(
            "Customer Message",
            placeholder="Paste the customer's message here...\n\nExample: 'Hi, I'm interested in your services but I'd like to know more about pricing.'",
            height=150,
            key="customer_msg_input",
        )

        col_send, col_tone = st.columns([1, 1])
        with col_tone:
            brand_tone = st.selectbox(
                "Reply Tone",
                ["Professional", "Friendly", "Casual", "Formal", "Empathetic"],
                index=0,
                key="reply_tone",
            )
        with col_send:
            st.markdown("")  # Spacer
            send_clicked = st.button(
                "🤖 Draft Reply",
                use_container_width=True,
                type="primary",
                disabled=not customer_msg.strip(),
            )

        if send_clicked and customer_msg.strip():
            with st.spinner("🤖 AI is drafting a reply..."):
                result = api_client.draft_reply(
                    campaign_id=campaign_id,
                    customer_message=customer_msg.strip(),
                    business_name="My Business",
                    brand_tone=brand_tone,
                    campaign_objective=campaign.get("objective", ""),
                )

            if result.get("success"):
                st.session_state["last_reply"] = result
                st.rerun()
            else:
                st.error(f"Failed: {result.get('message', 'Unknown error')}")

        # Show last reply
        last_reply = st.session_state.get("last_reply")
        if last_reply and last_reply.get("reply"):
            st.divider()
            _render_reply_card(last_reply, campaign_id)

    # ═══════════════════════════════════════════════════════════════════════════
    #  TAB 2: History
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_history:
        st.subheader("📜 Conversation History")

        history = api_client.list_correspondence(campaign_id)

        if not history or isinstance(history, dict):
            st.info("No conversation history yet. Draft a reply to get started!")
            return

        replies = [h for h in history if h.get("type") == "reply"]

        if not replies:
            st.info("No replies drafted yet.")
        else:
            for item in replies:
                with st.container(border=True):
                    # Customer message
                    st.markdown(f"**🗣️ Customer:** {item.get('customer_message', '—')}")
                    st.divider()

                    # AI reply
                    st.markdown(f"**🤖 AI Reply:**")
                    st.markdown(item.get("ai_reply", "—"))

                    # Confidence + escalation
                    conf = item.get("confidence_score", 0)
                    conf_color = "#4ade80" if conf >= 0.7 else "#f59e0b" if conf >= 0.5 else "#ef4444"
                    cols = st.columns([1, 1, 2])
                    with cols[0]:
                        st.markdown(
                            f'<div style="font-size: 0.75rem; color: {conf_color}; font-weight: 700;">'
                            f'Confidence: {conf:.0%}</div>',
                            unsafe_allow_html=True,
                        )
                    with cols[1]:
                        if item.get("escalate"):
                            st.markdown(
                                '<span style="color: #ef4444; font-weight: 700; font-size: 0.75rem;">'
                                '⚠️ ESCALATE</span>',
                                unsafe_allow_html=True,
                            )

    # ═══════════════════════════════════════════════════════════════════════════
    #  TAB 3: FAQ Manager (F-21)
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_faq:
        st.subheader("📋 FAQ Manager")
        st.caption("Save common Q&A pairs for quick reuse.")

        # Add new FAQ
        with st.expander("➕ Add New FAQ", expanded=False):
            faq_q = st.text_input("Question", placeholder="What does the customer ask?", key="faq_q")
            faq_a = st.text_area("Answer", placeholder="Your standard reply...", height=100, key="faq_a")
            if st.button("💾 Save FAQ", disabled=not (faq_q and faq_a)):
                result = api_client.save_faq(campaign_id, faq_q, faq_a)
                if result.get("success"):
                    st.success("✅ FAQ saved!")
                    st.rerun()

        # List existing FAQs
        all_corr = api_client.list_correspondence(campaign_id, type_filter="faq")

        if not all_corr or isinstance(all_corr, dict):
            st.info("No FAQs saved yet. Add one above!")
        else:
            for faq in all_corr:
                with st.container(border=True):
                    st.markdown(f"**Q:** {faq.get('customer_message', '—')}")
                    st.markdown(f"**A:** {faq.get('ai_reply', '—')}")


def _render_reply_card(reply_data: dict, campaign_id: str):
    """Render the AI reply result with confidence score and escalation flag."""

    # Confidence badge
    conf = reply_data.get("confidence_score", 0)
    if conf >= 0.7:
        conf_color = "#4ade80"
        conf_label = "High Confidence"
    elif conf >= 0.5:
        conf_color = "#f59e0b"
        conf_label = "Moderate Confidence"
    else:
        conf_color = "#ef4444"
        conf_label = "Low Confidence"

    with st.container(border=True):
        # Header
        h1, h2 = st.columns([3, 1])
        with h1:
            st.markdown("### 🤖 AI-Drafted Reply")
        with h2:
            st.markdown(
                f'<div style="text-align: center; padding: 0.3rem;">'
                f'<div style="font-size: 1.3rem; font-weight: 800; color: {conf_color};">{conf:.0%}</div>'
                f'<div style="font-size: 0.65rem; color: {conf_color}; font-weight: 600;">{conf_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Escalation warning
        if reply_data.get("escalate"):
            st.markdown(
                f'<div style="background: rgba(239,68,68,0.1); padding: 10px 14px; '
                f'border-radius: 8px; border-left: 3px solid #ef4444; margin-bottom: 10px;">'
                f'⚠️ <strong>Escalation Recommended</strong> — {reply_data.get("escalation_reason", "This reply needs human review.")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Reply body
        st.markdown(reply_data.get("reply", ""))

        # Action buttons
        a1, a2, a3 = st.columns(3)
        with a1:
            if st.button("📋 Copy Reply", key="copy_reply", use_container_width=True):
                st.code(reply_data.get("reply", ""), language=None)
        with a2:
            if st.button("💾 Save as FAQ", key="save_as_faq", use_container_width=True):
                # Save the last customer message + this reply as FAQ
                customer_msg = st.session_state.get("customer_msg_input", "")
                if customer_msg:
                    result = api_client.save_faq(campaign_id, customer_msg, reply_data.get("reply", ""))
                    if result.get("success"):
                        st.success("✅ Saved as FAQ!")
        with a3:
            if st.button("🔄 Regenerate", key="regen_reply", use_container_width=True):
                st.session_state["last_reply"] = None
                st.rerun()
