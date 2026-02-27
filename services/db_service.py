"""
NEXUS — Database Service
All MongoDB operations go through this module.
Falls back to in-memory storage if MONGODB_URI is not configured.
"""

import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# ─── Connection ─────────────────────────────────────────────────────────────────

_client = None
_db = None
_use_memory = False

# In-memory store (used when MongoDB is not available)
_memory_store = {
    "users": [],
    "campaigns": [],
    "content": [],
    "analytics": [],
    "schedules": [],
    "correspondence": [],
}


def _init_db():
    """Initialise database connection or fall back to in-memory."""
    global _client, _db, _use_memory

    uri = os.getenv("MONGODB_URI", "")
    if not uri or uri.startswith("mongodb+srv://<"):
        print("⚠️  MONGODB_URI not configured — using in-memory storage.")
        _use_memory = True
        return

    try:
        from pymongo import MongoClient
        from bson import ObjectId  # noqa: F401
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        _client.admin.command("ping")
        _db = _client.get_default_database("nexus")
        _use_memory = False
        print("✅ Connected to MongoDB Atlas.")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed ({e}) — using in-memory storage.")
        _use_memory = True


_init_db()


def get_db():
    """Return the nexus database handle."""
    if _use_memory:
        return None
    return _db


# ─── Helper: timestamps & ids ──────────────────────────────────────────────────

def _now():
    return datetime.now(timezone.utc)


def _generate_id():
    return str(uuid.uuid4())


# ─── In-memory CRUD helpers ────────────────────────────────────────────────────

def _mem_find(collection: str, query: dict) -> list:
    """Simple in-memory find with basic field matching."""
    results = []
    for doc in _memory_store[collection]:
        match = all(doc.get(k) == v for k, v in query.items())
        if match:
            results.append(doc.copy())
    return results


def _mem_find_one(collection: str, query: dict):
    results = _mem_find(collection, query)
    return results[0] if results else None


def _mem_insert(collection: str, doc: dict) -> str:
    doc_id = _generate_id()
    doc["_id"] = doc_id
    _memory_store[collection].append(doc)
    return doc_id


def _mem_update(collection: str, doc_id: str, updates: dict):
    for doc in _memory_store[collection]:
        if doc["_id"] == doc_id:
            doc.update(updates)
            return


def _mem_delete_many(collection: str, query: dict):
    _memory_store[collection] = [
        doc for doc in _memory_store[collection]
        if not all(doc.get(k) == v for k, v in query.items())
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  USERS
# ═══════════════════════════════════════════════════════════════════════════════

def create_user(email: str, hashed_password: str, name: str) -> str:
    """Insert a new user and return its string id."""
    doc = {
        "email": email,
        "password": hashed_password,
        "name": name,
        "auth_provider": "local",
        "created_at": _now(),
    }
    if _use_memory:
        return _mem_insert("users", doc)

    from bson import ObjectId
    result = get_db().users.insert_one(doc)
    return str(result.inserted_id)


def get_user_by_email(email: str):
    """Return user document or None."""
    if _use_memory:
        return _mem_find_one("users", {"email": email})

    return get_db().users.find_one({"email": email})


def get_user_by_id(user_id: str):
    """Return user document by id string."""
    if _use_memory:
        return _mem_find_one("users", {"_id": user_id})

    from bson import ObjectId
    return get_db().users.find_one({"_id": ObjectId(user_id)})


def create_or_get_google_user(email: str, name: str) -> dict:
    """Upsert a Google SSO user. Returns the user document."""
    user = get_user_by_email(email)
    if user:
        return user

    doc = {
        "email": email,
        "password": None,
        "name": name,
        "auth_provider": "google",
        "created_at": _now(),
    }
    if _use_memory:
        _mem_insert("users", doc)
        return doc

    db = get_db()
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGNS
# ═══════════════════════════════════════════════════════════════════════════════

def save_campaign(data: dict) -> str:
    """Insert a new campaign and return its string id."""
    data["created_at"] = _now()
    data["updated_at"] = _now()
    data.setdefault("status", "active")

    if _use_memory:
        return _mem_insert("campaigns", data)

    result = get_db().campaigns.insert_one(data)
    return str(result.inserted_id)


def get_campaigns(user_id: str = None) -> list:
    """Return all campaigns, optionally filtered by user_id, newest first."""
    if _use_memory:
        query = {"user_id": user_id} if user_id else {}
        results = _mem_find("campaigns", query) if user_id else list(_memory_store["campaigns"])
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    query = {}
    if user_id:
        query["user_id"] = user_id
    return list(get_db().campaigns.find(query).sort("created_at", -1))


def get_campaign(campaign_id: str) -> dict:
    """Return a single campaign by id."""
    if _use_memory:
        return _mem_find_one("campaigns", {"_id": campaign_id})

    from bson import ObjectId
    return get_db().campaigns.find_one({"_id": ObjectId(campaign_id)})


def update_campaign(campaign_id: str, updates: dict):
    """Partial update a campaign."""
    updates["updated_at"] = _now()

    if _use_memory:
        _mem_update("campaigns", campaign_id, updates)
        return

    from bson import ObjectId
    get_db().campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": updates}
    )


def delete_campaign(campaign_id: str):
    """Delete a campaign by id."""
    if _use_memory:
        _mem_delete_many("campaigns", {"_id": campaign_id})
        return

    from bson import ObjectId
    get_db().campaigns.delete_one({"_id": ObjectId(campaign_id)})


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

def save_content(campaign_id: str, content_list: list) -> list:
    """Bulk-insert content pieces for a campaign. Returns inserted id strings."""
    now = _now()
    ids = []
    for item in content_list:
        item["campaign_id"] = campaign_id
        item["created_at"] = now
        item["updated_at"] = now
        item.setdefault("status", "draft")
        item.setdefault("is_edited", False)

    if _use_memory:
        for item in content_list:
            ids.append(_mem_insert("content", item))
        return ids

    result = get_db().content.insert_many(content_list)
    return [str(i) for i in result.inserted_ids]


def get_content(campaign_id: str, channel: str = None) -> list:
    """Return content pieces for a campaign, optionally filtered by channel."""
    if _use_memory:
        query = {"campaign_id": campaign_id}
        if channel:
            query["channel"] = channel
        results = _mem_find("content", query)
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    query = {"campaign_id": campaign_id}
    if channel:
        query["channel"] = channel
    return list(get_db().content.find(query).sort("created_at", -1))


def update_content(content_id: str, updates: dict):
    """Partial update a content piece."""
    updates["updated_at"] = _now()

    if _use_memory:
        _mem_update("content", content_id, updates)
        return

    from bson import ObjectId
    get_db().content.update_one(
        {"_id": ObjectId(content_id)},
        {"$set": updates}
    )


def delete_campaign_content(campaign_id: str):
    """Delete all content for a campaign (used before regeneration)."""
    if _use_memory:
        _mem_delete_many("content", {"campaign_id": campaign_id})
        return

    get_db().content.delete_many({"campaign_id": campaign_id})


def auto_publish_overdue():
    """
    Find all content with status 'scheduled' whose scheduled_at is in the past,
    and flip them to 'published'. Called on every page load.
    Returns the count of auto-published items.
    """
    from datetime import datetime
    now = datetime.now()
    count = 0

    if _use_memory:
        # Iterate directly over the original list to modify in-place
        for doc in _memory_store.get("content", []):
            if doc.get("status") != "scheduled":
                continue
            sched_str = doc.get("scheduled_at", "")
            if not sched_str:
                continue
            try:
                sched_dt = datetime.fromisoformat(str(sched_str))
                if sched_dt <= now:
                    doc["status"] = "published"
                    doc["published_at"] = now.isoformat()
                    doc["updated_at"] = _now()
                    count += 1
                    print(f"✅ Auto-published: {doc.get('channel')} (was scheduled for {sched_str})")
            except (ValueError, TypeError) as e:
                print(f"⚠️ Auto-publish parse error for '{sched_str}': {e}")
                continue
        return count

    # MongoDB path
    result = get_db().content.update_many(
        {"status": "scheduled", "scheduled_at": {"$lte": now.isoformat()}},
        {"$set": {
            "status": "published",
            "published_at": now.isoformat(),
            "updated_at": _now(),
        }},
    )
    count = result.modified_count if result else 0
    return count


# ═══════════════════════════════════════════════════════════════════════════════
#  SCHEDULES
# ═══════════════════════════════════════════════════════════════════════════════

def save_schedule(data: dict) -> str:
    """Insert a schedule entry."""
    data["created_at"] = _now()
    data.setdefault("status", "scheduled")
    data.setdefault("published_at", None)

    if _use_memory:
        return _mem_insert("schedules", data)

    result = get_db().schedules.insert_one(data)
    return str(result.inserted_id)


def get_schedules(campaign_id: str) -> list:
    """Get all schedules for a campaign, ordered by date."""
    if _use_memory:
        results = _mem_find("schedules", {"campaign_id": campaign_id})
        return sorted(results, key=lambda x: x.get("scheduled_at", ""))

    return list(
        get_db().schedules.find({"campaign_id": campaign_id})
        .sort("scheduled_at", 1)
    )


def update_schedule(schedule_id: str, updates: dict):
    """Partial update a schedule."""
    if _use_memory:
        _mem_update("schedules", schedule_id, updates)
        return

    from bson import ObjectId
    get_db().schedules.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": updates}
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def save_analytics(data: dict) -> str:
    """Insert or replace analytics for a campaign."""
    data["created_at"] = _now()

    if _use_memory:
        # Remove existing analytics for the campaign
        _mem_delete_many("analytics", {"campaign_id": data["campaign_id"]})
        _mem_insert("analytics", data)
        return data["campaign_id"]

    get_db().analytics.replace_one(
        {"campaign_id": data["campaign_id"]},
        data,
        upsert=True,
    )
    return data["campaign_id"]


def get_analytics(campaign_id: str):
    """Return analytics document for a campaign or None."""
    if _use_memory:
        return _mem_find_one("analytics", {"campaign_id": campaign_id})

    return get_db().analytics.find_one({"campaign_id": campaign_id})


# ═══════════════════════════════════════════════════════════════════════════════
#  CORRESPONDENCE
# ═══════════════════════════════════════════════════════════════════════════════

def save_correspondence(data: dict) -> str:
    """Save a correspondence entry (reply or FAQ)."""
    data["created_at"] = _now()

    if _use_memory:
        return _mem_insert("correspondence", data)

    result = get_db().correspondence.insert_one(data)
    return str(result.inserted_id)


def get_correspondence(campaign_id: str, type_filter: str = None) -> list:
    """Get correspondence history for a campaign."""
    if _use_memory:
        query = {"campaign_id": campaign_id}
        if type_filter:
            query["type"] = type_filter
        results = _mem_find("correspondence", query)
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    query = {"campaign_id": campaign_id}
    if type_filter:
        query["type"] = type_filter
    return list(get_db().correspondence.find(query).sort("created_at", -1))
