"""
DevMind — analytics engine
Crunches raw events into insights.
"""

import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from devmind.store import load_events, session_get


# ── Helpers ───────────────────────────────────────────────────────────────────

def _basename(path: str) -> str:
    return os.path.basename(path)


def _to_dt(ts: float) -> datetime:
    return datetime.fromtimestamp(ts)


def _fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    else:
        h, rem = divmod(seconds, 3600)
        m = rem // 60
        return f"{h}h {m}m"


# ── Core stats ────────────────────────────────────────────────────────────────

def compute_stats(since_hours: int = 24) -> dict:
    events = load_events()
    session = session_get()

    cutoff = (datetime.now() - timedelta(hours=since_hours)).timestamp()
    events = [e for e in events if e["ts"] >= cutoff]

    if not events:
        return {"empty": True}

    # Session duration
    session_start_ts = None
    session_end_ts = None
    if session:
        session_start_ts = session.get("started_ts")
        session_end_ts = session.get("ended_ts") or datetime.now().timestamp()

    # File edit counts
    file_edits = defaultdict(int)
    file_times = defaultdict(list)

    for e in events:
        if e["type"] in ("modify", "create"):
            file_edits[e["path"]] += 1
            file_times[e["path"]].append(e["ts"])

    # Time per file (estimate: spread events across time windows)
    file_duration = {}
    for path, times in file_times.items():
        times_sorted = sorted(times)
        if len(times_sorted) == 1:
            file_duration[path] = 30  # assume 30s minimum touch
        else:
            # Sum gaps ≤ 5 minutes between events on the same file
            total = 0
            for i in range(1, len(times_sorted)):
                gap = times_sorted[i] - times_sorted[i - 1]
                if gap <= 300:
                    total += gap
            file_duration[path] = max(total, 30)

    # Activity bursts (group events within 60s windows)
    bursts = _detect_bursts(events)

    # Save frequency (events per file per minute)
    total_events = len(events)
    session_secs = 0
    if session_start_ts and session_end_ts:
        session_secs = session_end_ts - session_start_ts

    # Per-hour activity heatmap (last 24h)
    hourly = defaultdict(int)
    for e in events:
        hour = _to_dt(e["ts"]).hour
        hourly[hour] += 1

    # Most edited files
    top_files = sorted(file_edits.items(), key=lambda x: x[1], reverse=True)[:8]

    # File switches (unique file changes in sequence)
    file_switches = _count_switches(events)

    return {
        "empty": False,
        "total_events": total_events,
        "total_files_touched": len(file_edits),
        "session_duration": session_secs,
        "session_duration_fmt": _fmt_duration(session_secs) if session_secs else "unknown",
        "top_files": [(Path(p).name, p, c, int(file_duration.get(p, 0))) for p, c in top_files],
        "bursts": bursts,
        "file_switches": file_switches,
        "hourly": dict(hourly),
        "hourly_values": [hourly.get(h, 0) for h in range(24)],
        "events_per_minute": round(total_events / (session_secs / 60), 2) if session_secs > 60 else None,
    }


def _detect_bursts(events: list) -> list:
    """Group events into bursts: sequences with ≤ 60s gaps."""
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: e["ts"])
    bursts = []
    burst_start = sorted_events[0]["ts"]
    burst_events = [sorted_events[0]]

    for e in sorted_events[1:]:
        if e["ts"] - burst_events[-1]["ts"] <= 60:
            burst_events.append(e)
        else:
            if len(burst_events) >= 3:
                duration = burst_events[-1]["ts"] - burst_start
                bursts.append({
                    "start": burst_start,
                    "duration": duration,
                    "event_count": len(burst_events),
                    "intensity": len(burst_events) / max(duration / 60, 0.1),
                })
            burst_start = e["ts"]
            burst_events = [e]

    if len(burst_events) >= 3:
        duration = burst_events[-1]["ts"] - burst_start
        bursts.append({
            "start": burst_start,
            "duration": duration,
            "event_count": len(burst_events),
            "intensity": len(burst_events) / max(duration / 60, 0.1),
        })

    return bursts


def _count_switches(events: list) -> int:
    """Count how many times the active file changed."""
    sorted_events = sorted(events, key=lambda e: e["ts"])
    switches = 0
    last_path = None
    for e in sorted_events:
        if e["path"] != last_path and last_path is not None:
            switches += 1
        last_path = e["path"]
    return switches


# ── Vibe engine ───────────────────────────────────────────────────────────────

VIBES = [
    # (condition_fn, message)
    (
        lambda s: len(s["bursts"]) >= 3 and s["bursts"] and
                  max(b["intensity"] for b in s["bursts"]) > 15,
        "You code in bursts like a sprinter — high intensity, then silence. Peak flow state detected."
    ),
    (
        lambda s: s["file_switches"] > 30,
        "You switch files too much → chaotic workflow. Pick one thing, finish it, then move."
    ),
    (
        lambda s: s["file_switches"] > 15,
        "Lots of context switching today. Try batching related changes in one file before jumping."
    ),
    (
        lambda s: s["total_events"] > 200 and s["session_duration"] > 3600,
        "Deep work session detected. You've been locked in for a while — take a break soon."
    ),
    (
        lambda s: s["total_events"] < 10 and s["session_duration"] > 1800,
        "Long session, low output. Stuck? Try rubber duck debugging or a short walk."
    ),
    (
        lambda s: len(s["top_files"]) == 1,
        "Laser focus — one file, all session. Surgical precision mode."
    ),
    (
        lambda s: len(s["bursts"]) == 0 and s["total_events"] > 5,
        "Steady and consistent. No frantic bursts — you work like a marathon runner."
    ),
    (
        lambda s: len(s["bursts"]) >= 2 and
                  max(b["intensity"] for b in s["bursts"]) < 5,
        "Low-intensity session. Warming up or winding down. Either way, you're still shipping."
    ),
    (
        lambda s: s.get("events_per_minute") and s["events_per_minute"] > 10,
        "High-frequency edits. You iterate fast — careful you're not rewriting the same thing twice."
    ),
    (
        lambda s: s["total_files_touched"] >= 5 and s["file_switches"] < 10,
        "Multi-file but disciplined. You're refactoring across the codebase without losing your thread."
    ),
]

DEFAULT_VIBE = "Session recorded. No strong patterns yet — keep coding."


def compute_vibe(stats: dict) -> str:
    if stats.get("empty"):
        return "No activity recorded yet. Run `devmind start` and write some code."

    for condition, message in VIBES:
        try:
            if condition(stats):
                return message
        except Exception:
            continue

    return DEFAULT_VIBE
