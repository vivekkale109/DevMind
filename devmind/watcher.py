"""
DevMind — filesystem watcher
Uses watchdog if available, falls back to polling.
"""

import os
import sys
import time
import threading
from pathlib import Path

from devmind import store, ui

# Extensions we care about
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".c", ".cpp",
    ".h", ".java", ".rb", ".php", ".sh", ".bash", ".zsh", ".fish",
    ".toml", ".yaml", ".yml", ".json", ".env", ".md", ".sql", ".css",
    ".html", ".vue", ".svelte", ".dart", ".kt", ".swift", ".lua",
}

_stop_event = threading.Event()


def is_code_file(path: str) -> bool:
    return Path(path).suffix.lower() in CODE_EXTENSIONS


def _ignore(path: str) -> bool:
    p = Path(path)
    ignored_dirs = {
        "__pycache__", ".git", "node_modules", ".venv", "venv",
        ".tox", "dist", "build", ".mypy_cache", ".pytest_cache",
        ".devmind",
    }
    return any(part in ignored_dirs for part in p.parts)


# ── Watchdog backend ─────────────────────────────────────────────────────────

def _start_watchdog(watch_path: str):
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory or _ignore(event.src_path):
                return
            if is_code_file(event.src_path):
                store.log_event("modify", event.src_path)
                rel = Path(event.src_path).relative_to(watch_path)
                ui.info(f"{ui.c('~', ui.YELLOW)} {rel}")

        def on_created(self, event):
            if event.is_directory or _ignore(event.src_path):
                return
            if is_code_file(event.src_path):
                store.log_event("create", event.src_path)
                rel = Path(event.src_path).relative_to(watch_path)
                ui.info(f"{ui.c('+', ui.BGREEN)} {rel}")

        def on_deleted(self, event):
            if event.is_directory or _ignore(event.src_path):
                return
            if is_code_file(event.src_path):
                store.log_event("delete", event.src_path)

    observer = Observer()
    observer.schedule(Handler(), watch_path, recursive=True)
    observer.start()
    ui.success(f"Watchdog active → {ui.c(watch_path, ui.BCYAN)}")
    try:
        while not _stop_event.is_set():
            time.sleep(0.5)
    finally:
        observer.stop()
        observer.join()


# ── Polling fallback ──────────────────────────────────────────────────────────

def _poll_snapshot(watch_path: str) -> dict:
    """Return {filepath: mtime} for all code files."""
    snap = {}
    for root, dirs, files in os.walk(watch_path):
        dirs[:] = [d for d in dirs if not _ignore(os.path.join(root, d))]
        for f in files:
            fp = os.path.join(root, f)
            if is_code_file(fp) and not _ignore(fp):
                try:
                    snap[fp] = os.path.getmtime(fp)
                except OSError:
                    pass
    return snap


def _start_polling(watch_path: str, interval: float = 1.5):
    ui.warn("watchdog not installed — using polling (1.5s interval)")
    ui.success(f"Polling active → {ui.c(watch_path, ui.BCYAN)}")
    prev = _poll_snapshot(watch_path)
    while not _stop_event.is_set():
        time.sleep(interval)
        curr = _poll_snapshot(watch_path)
        for fp, mtime in curr.items():
            if fp not in prev:
                store.log_event("create", fp)
                rel = Path(fp).relative_to(watch_path)
                ui.info(f"{ui.c('+', ui.BGREEN)} {rel}")
            elif mtime != prev.get(fp):
                store.log_event("modify", fp)
                rel = Path(fp).relative_to(watch_path)
                ui.info(f"{ui.c('~', ui.YELLOW)} {rel}")
        prev = curr


# ── Public API ────────────────────────────────────────────────────────────────

def start(watch_path: str):
    _stop_event.clear()
    try:
        import watchdog  # noqa: F401
        _start_watchdog(watch_path)
    except ImportError:
        _start_polling(watch_path)


def stop():
    _stop_event.set()
