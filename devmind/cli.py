#!/usr/bin/env python3
"""
╔═══════════════════════════════════╗
║   DevMind CLI — coding analyzer   ║
╚═══════════════════════════════════╝
Usage:
  devmind start [path]   Start a tracking session
  devmind stop           Stop current session
  devmind stats          Show session statistics
  devmind vibe           Get your coding vibe
  devmind clear          Clear event log
  devmind status         Show if tracking is active
"""

import os
import sys
import signal
import argparse
from datetime import datetime
from pathlib import Path

# Make sure the package is importable when run as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from devmind import store, ui
from devmind.analytics import compute_stats, compute_vibe


# ── devmind start ─────────────────────────────────────────────────────────────

def cmd_start(args):
    watch_path = os.path.abspath(args.path or ".")

    if not os.path.isdir(watch_path):
        ui.error(f"Not a directory: {watch_path}")
        sys.exit(1)

    existing = store.session_get()
    if existing and existing.get("active"):
        ui.warn(f"Session already active (PID {existing.get('pid')})")
        ui.info("Run `devmind stop` first, or `devmind status` for details.")
        sys.exit(1)

    ui.header("DevMind  ▸  session start")
    ui.info(f"Watching  {ui.c(watch_path, ui.BCYAN)}")
    ui.info(f"Data dir  {ui.c(str(store.DATA_DIR), ui.DIM)}")
    ui.info(f"PID       {ui.c(os.getpid(), ui.YELLOW)}")
    print()
    ui.info(ui.c("Ctrl+C to stop session", ui.DIM))
    print()

    store.session_start(watch_path)

    def handle_sigint(sig, frame):
        print()
        ui.warn("Stopping session...")
        store.session_end()
        ui.success("Session saved. Run `devmind stats` to review.")
        print()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)

    # Import watcher here so the tool still works if watchdog is missing
    from devmind import watcher
    watcher.start(watch_path)  # blocks until Ctrl+C


# ── devmind stop ─────────────────────────────────────────────────────────────

def cmd_stop(args):
    session = store.session_get()
    if not session or not session.get("active"):
        ui.warn("No active session found.")
        return
    store.session_end()
    ui.success("Session stopped.")


# ── devmind stats ─────────────────────────────────────────────────────────────

def cmd_stats(args):
    since = int(args.hours or 24)
    stats = compute_stats(since_hours=since)

    ui.header(f"DevMind  ▸  stats  [{since}h window]")

    if stats.get("empty"):
        ui.warn("No events recorded yet.")
        ui.info("Run `devmind start` in your project directory.")
        return

    # ── Session info
    ui.section("Session")
    ui.row("Duration", stats["session_duration_fmt"])
    ui.row("Total file events", stats["total_events"])
    ui.row("Files touched", stats["total_files_touched"])
    ui.row("File switches", stats["file_switches"])
    if stats["events_per_minute"]:
        ui.row("Edits / min", f"{stats['events_per_minute']:.1f}")

    # ── Top files
    ui.section("Most edited files")
    top = stats["top_files"]
    if top:
        max_edits = top[0][2] if top else 1
        for name, path, edits, secs in top:
            dur_str = _fmt_secs(secs)
            label = f"{name}  {ui.c(dur_str, ui.DIM)}"
            ui.bar_chart(label, edits, max_edits, color=ui.BCYAN)
    else:
        ui.info("No file edits recorded.")

    # ── Activity bursts
    ui.section("Activity bursts")
    bursts = stats["bursts"]
    if bursts:
        ui.row("Burst count", len(bursts))
        top_burst = max(bursts, key=lambda b: b["intensity"])
        ui.row("Peak intensity", f"{top_burst['intensity']:.1f} edits/min")
        ui.row("Peak burst size", f"{top_burst['event_count']} events")
        # Sparkline of burst intensities
        intensities = [round(b["intensity"], 1) for b in bursts]
        ui.row("Burst profile", ui.spark(intensities))
    else:
        ui.info("No activity bursts detected (need 3+ rapid edits).")

    # ── Hourly heatmap (sparkline)
    ui.section("Hourly activity (0h → 23h)")
    hourly_vals = stats["hourly_values"]
    spark_str = ui.spark(hourly_vals, width=24)
    print(f"  {spark_str}")
    # Mark current hour
    now_h = datetime.now().hour
    print(f"  {ui.c(f'now → hour {now_h}', ui.DIM)}")

    print()


def _fmt_secs(s: int) -> str:
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m"


# ── devmind vibe ─────────────────────────────────────────────────────────────

def cmd_vibe(args):
    stats = compute_stats(since_hours=24)
    vibe = compute_vibe(stats)
    ui.header("DevMind  ▸  vibe check")
    ui.vibe_line(vibe)

    if not stats.get("empty"):
        # Quick one-liners beneath
        ui.info(f"Events recorded  {ui.c(stats['total_events'], ui.BOLD)}")
        ui.info(f"Session length   {ui.c(stats['session_duration_fmt'], ui.BOLD)}")
        ui.info(f"Files touched    {ui.c(stats['total_files_touched'], ui.BOLD)}")
        print()


# ── devmind status ────────────────────────────────────────────────────────────

def cmd_status(args):
    session = store.session_get()
    if not session:
        ui.warn("No session data found.")
        return

    ui.header("DevMind  ▸  status")
    active = session.get("active", False)
    ui.row("Status", ui.c("● ACTIVE", ui.BGREEN) if active else ui.c("○ STOPPED", ui.DIM))
    ui.row("Watch path", session.get("watch_path", "?"))
    ui.row("Started", session.get("started_at", "?"))
    if not active:
        ui.row("Ended", session.get("ended_at", "?"))
    ui.row("PID", session.get("pid", "?"))
    print()


# ── devmind clear ─────────────────────────────────────────────────────────────

def cmd_clear(args):
    store.clear_events()
    store.session_end()
    ui.success("Event log cleared.")


# ── CLI router ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="devmind",
        description="DevMind — coding behavior analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  start [path]   Start tracking (default: current dir)
  stop           Stop active session
  stats          Show statistics  [-H hours, default 24]
  vibe           Get your coding vibe
  status         Show session status
  clear          Wipe event log
        """,
    )

    sub = parser.add_subparsers(dest="command")

    p_start = sub.add_parser("start")
    p_start.add_argument("path", nargs="?", default=None, help="Directory to watch")

    sub.add_parser("stop")

    p_stats = sub.add_parser("stats")
    p_stats.add_argument("-H", "--hours", default=24, type=int,
                         help="Look-back window in hours (default: 24)")

    sub.add_parser("vibe")
    sub.add_parser("status")
    sub.add_parser("clear")

    args = parser.parse_args()

    dispatch = {
        "start":  cmd_start,
        "stop":   cmd_stop,
        "stats":  cmd_stats,
        "vibe":   cmd_vibe,
        "status": cmd_status,
        "clear":  cmd_clear,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        # No command → print banner + help
        print(ui.c("""
  ██████╗ ███████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗
  ██╔══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗
  ██║  ██║█████╗  ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║
  ██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║██║██║╚██╗██║██║  ██║
  ██████╔╝███████╗ ╚████╔╝ ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
  ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
""", ui.CYAN, ui.BOLD))
        print(ui.c("  coding behavior analyzer\n", ui.DIM))
        parser.print_help()
        print()


if __name__ == "__main__":
    main()
