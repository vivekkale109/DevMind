"""
DevMind — local session storage
All data lives in ~/.devmind/
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".devmind"
SESSION_FILE = DATA_DIR / "session.json"
LOG_FILE = DATA_DIR / "events.json"


def ensure_dir():
    DATA_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now().isoformat()


def now_ts():
    return datetime.now().timestamp()


# ── Session ─────────────────────────────────────────────────────────────────

def session_start(watch_path: str):
    ensure_dir()
    session = {
        "started_at": now_iso(),
        "started_ts": now_ts(),
        "watch_path": watch_path,
        "pid": os.getpid(),
        "active": True,
    }
    SESSION_FILE.write_text(json.dumps(session, indent=2))
    return session


def session_end():
    if not SESSION_FILE.exists():
        return
    s = json.loads(SESSION_FILE.read_text())
    s["active"] = False
    s["ended_at"] = now_iso()
    s["ended_ts"] = now_ts()
    SESSION_FILE.write_text(json.dumps(s, indent=2))


def session_get():
    if not SESSION_FILE.exists():
        return None
    return json.loads(SESSION_FILE.read_text())


# ── Event log ────────────────────────────────────────────────────────────────

def log_event(event_type: str, path: str, extra: dict = None):
    ensure_dir()
    events = []
    if LOG_FILE.exists():
        try:
            events = json.loads(LOG_FILE.read_text())
        except Exception:
            events = []

    entry = {
        "ts": now_ts(),
        "iso": now_iso(),
        "type": event_type,   # "save" | "modify" | "create" | "delete"
        "path": str(path),
    }
    if extra:
        entry.update(extra)

    events.append(entry)
    LOG_FILE.write_text(json.dumps(events, indent=2))


def load_events():
    if not LOG_FILE.exists():
        return []
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []


def clear_events():
    if LOG_FILE.exists():
        LOG_FILE.write_text("[]")
