"""
Database layer.
Supports MongoDB (if USE_INMEMORY_DB=false and pymongo can connect)
or an in-memory fallback so the project runs out of the box without MongoDB.
"""
from threading import Lock
from datetime import datetime
import uuid

from config import Config

_state = {
    "mode": "memory",  # or "mongo"
    "mongo": None,
    "db": None,
    "memory": {
        "users": [],
        "vault": [],
        "logs": [],
    },
    "lock": Lock(),
}


def init_db(app=None):
    if Config.USE_INMEMORY_DB:
        _state["mode"] = "memory"
        return
    try:
        from pymongo import MongoClient
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # force connection check
        _state["mongo"] = client
        _state["db"] = client[Config.MONGO_DB]
        _state["mode"] = "mongo"
        print("[db] Connected to MongoDB.")
    except Exception as e:
        print(f"[db] MongoDB unavailable ({e}); falling back to in-memory store.")
        _state["mode"] = "memory"


def _now():
    return datetime.utcnow().isoformat() + "Z"


# ---------- Users ----------
def create_user(doc):
    doc.setdefault("_id", str(uuid.uuid4()))
    doc.setdefault("created_at", _now())
    if _state["mode"] == "mongo":
        _state["db"].users.insert_one(doc)
    else:
        with _state["lock"]:
            _state["memory"]["users"].append(doc)
    return doc


def find_user_by_username(username):
    if _state["mode"] == "mongo":
        return _state["db"].users.find_one({"username": username})
    return next((u for u in _state["memory"]["users"] if u["username"] == username), None)


def find_user_by_id(user_id):
    if _state["mode"] == "mongo":
        return _state["db"].users.find_one({"_id": user_id})
    return next((u for u in _state["memory"]["users"] if u["_id"] == user_id), None)


def list_users():
    if _state["mode"] == "mongo":
        return list(_state["db"].users.find({}, {"password_hash": 0}))
    return [{k: v for k, v in u.items() if k != "password_hash"} for u in _state["memory"]["users"]]


# ---------- Vault ----------
def insert_vault(doc):
    doc.setdefault("_id", str(uuid.uuid4()))
    doc.setdefault("created_at", _now())
    if _state["mode"] == "mongo":
        _state["db"].vault.insert_one(doc)
    else:
        with _state["lock"]:
            _state["memory"]["vault"].append(doc)
    return doc


def list_vault(user_id=None):
    if _state["mode"] == "mongo":
        q = {} if user_id is None else {"user_id": user_id}
        return list(_state["db"].vault.find(q))
    items = _state["memory"]["vault"]
    if user_id is not None:
        items = [v for v in items if v["user_id"] == user_id]
    return list(items)


def get_vault(item_id):
    if _state["mode"] == "mongo":
        return _state["db"].vault.find_one({"_id": item_id})
    return next((v for v in _state["memory"]["vault"] if v["_id"] == item_id), None)


def update_vault(item_id, updates):
    if _state["mode"] == "mongo":
        _state["db"].vault.update_one({"_id": item_id}, {"$set": updates})
        return get_vault(item_id)
    item = get_vault(item_id)
    if item:
        item.update(updates)
    return item


def delete_vault(item_id):
    if _state["mode"] == "mongo":
        _state["db"].vault.delete_one({"_id": item_id})
        return True
    with _state["lock"]:
        _state["memory"]["vault"] = [v for v in _state["memory"]["vault"] if v["_id"] != item_id]
    return True


# ---------- Logs ----------
def add_log(entry):
    entry.setdefault("_id", str(uuid.uuid4()))
    entry.setdefault("timestamp", _now())
    if _state["mode"] == "mongo":
        _state["db"].logs.insert_one(entry)
    else:
        with _state["lock"]:
            _state["memory"]["logs"].append(entry)
    return entry


def list_logs(user_id=None, limit=200):
    if _state["mode"] == "mongo":
        q = {} if user_id is None else {"user_id": user_id}
        return list(_state["db"].logs.find(q).sort("timestamp", -1).limit(limit))
    logs = _state["memory"]["logs"]
    if user_id is not None:
        logs = [l for l in logs if l.get("user_id") == user_id]
    return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
