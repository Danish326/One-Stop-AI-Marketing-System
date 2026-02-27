# Phase 4: Publishing & Calendar — Pre-Coding Plan

> **Status:** 📋 Planning  
> **Date:** 2026-02-26  
> **Phase:** 4 of 6

---

## Goal

Enable users to schedule generated content for publishing, track post status through a lifecycle (Draft → Scheduled → Published), and view everything on a Calendar grid. The dashboard will show upcoming posts for the next 7 days.

---

## Features in Scope

| Feature ID | Feature | Description |
|---|---|---|
| **F-05** | Schedule Posts | Date/time picker on content cards to schedule publishing |
| **F-15** | Post Status Lifecycle | Content moves through Draft → Scheduled → Published |
| **F-06** | Content Calendar | Visual calendar grid showing scheduled posts by date |
| **F-16** | Mark as Published | Manual toggle to mark posts as published |
| **F-07** | Upcoming Posts on Dashboard | Next 7 days of scheduled posts shown on dashboard |

---

## Architecture

```
Generate Page                  Calendar Page                Dashboard
──────────────                 ──────────────               ─────────
Content Cards                  Weekly grid view             "Upcoming Posts"
[📅 Schedule] button           Scheduled posts by day       Next 7 days
  │                            Mark as Published toggle
  ▼
FastAPI → /api/schedules/*
  │
  ▼
db_service.py (schedules collection)
```

**Flow:**
1. User generates content (Phase 3) → content cards appear on Generate page
2. User clicks "📅 Schedule" on a content card → Date/time picker appears → Saves schedule
3. Content status changes from "Draft" → "Scheduled"
4. Calendar page shows all scheduled posts in a weekly grid
5. User can "Mark as Published" → status becomes "Published"
6. Dashboard "Upcoming Posts" section shows the next 7 days

---

## Files to Create / Modify

### New Files
| File | Purpose |
|---|---|
| `PHASE4_COMPLETED.md` | Post-coding summary |

### Modified Files
| File | Changes |
|---|---|
| `views/generate.py` | Add "📅 Schedule" button + date/time picker to content cards |
| `views/calendar.py` | Full rewrite — weekly grid view with scheduled posts and status toggles |
| `views/dashboard.py` | Replace "Upcoming Posts" placeholder with real data from schedules |
| `backend/routers/content.py` | Add schedule-related status updates |
| `backend/models.py` | Add ScheduleUpdate model if needed |
| `services/api_client.py` | Add schedule API functions (create, list, update) |

### Existing (No Changes Needed)
| File | Status |
|---|---|
| `services/db_service.py` | ✅ Schedule CRUD already implemented |
| `backend/models.py` | ✅ `ScheduleCreate` model exists |

---

## UI Design

### Generate Page — Schedule Button
Each content card gets a "📅 Schedule" button that expands a date/time picker.

### Calendar Page — Weekly Grid
```
┌─────────────────────────────────────────────────────┐
│ 📅 Content Calendar                                 │
│                                                     │
│ ◀ Week of Feb 26 – Mar 4, 2026 ▶                   │
│                                                     │
│ Mon 26  │ Tue 27  │ Wed 28  │ Thu 01  │ Fri 02     │
│─────────│─────────│─────────│─────────│────────     │
│ 📸 IG   │         │ 📘 FB   │         │ 🎵 TT      │
│ 6:00 PM │         │ 1:00 PM │         │ 8:00 PM    │
│ [Draft] │         │ [Sched] │         │ [Pub'd]    │
└─────────────────────────────────────────────────────┘
```

### Dashboard — Upcoming Posts Widget
Shows next 7 days of scheduled posts with channel, date, and status.

---

## Verification Plan

### Browser Tests
1. Sign up → Create campaign → Generate content → Schedule a post → Verify it appears on Calendar
2. Open Calendar → Verify posts appear on correct days
3. Mark a post as Published → Verify status badge changes
4. Check Dashboard → Verify Upcoming Posts widget shows scheduled posts

---

## Dependencies
- Phase 3 must be complete (content must exist to schedule)
- `db_service.py` schedule CRUD is ready
- No new packages needed
