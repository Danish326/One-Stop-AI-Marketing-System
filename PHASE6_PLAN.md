# Phase 6: AI Correspondence & Polish — Pre-Coding Plan

> **Status:** 📋 Planning  
> **Date:** 2026-02-26  
> **Phase:** 6 of 6 (FINAL)

---

## Goal

Build the AI correspondence tool for customer message handling. Users paste incoming customer messages and get AI-drafted replies. Low-confidence replies get escalation flags. Frequently asked questions can be saved as FAQ pairs.

---

## Features

| ID | Feature | Description |
|---|---|---|
| **F-17** | AI Reply Drafting | Paste customer message → get AI reply with confidence score |
| **F-22** | Escalation Flag | Low-confidence replies are flagged for human review |
| **F-21** | FAQ Handler | Save Q&A pairs to reuse for future conversations |

---

## Files to Modify

| File | Changes |
|---|---|
| `services/ai_service.py` | Add `generate_reply()` function (Agent 3 — Reply Composer) |
| `backend/routers/correspondence.py` | Wire up real AI reply endpoint |
| `views/correspondence.py` | Full rewrite — message input, reply cards, FAQ manager |

### Existing (No Changes Needed)
| File | Status |
|---|---|
| `services/db_service.py` | ✅ `save_correspondence`, `get_correspondence` ready |
| `services/api_client.py` | ✅ `draft_reply`, `save_faq`, `list_correspondence` ready |
| `backend/models.py` | ✅ `ReplyRequest`, `SaveFaqRequest` ready |

---

## Verification

### Browser Test
1. Create campaign → Navigate to Correspondence page
2. Paste a customer message → Click "Draft Reply"
3. Verify AI reply appears with confidence score
4. Test low-confidence escalation flag
5. Save a reply as FAQ → Verify it appears in FAQ list
