# DevMind CLI

> Terminal-first coding behavior analyzer. Understand how you actually code.

```
  ██████╗ ███████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗
  ██╔══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗
  ██║  ██║█████╗  ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║
  ██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║██║██║╚██╗██║██║  ██║
  ██████╔╝███████╗ ╚████╔╝ ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
  ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
```

## Install

```bash
git clone https://github.com/vivekkale109/devmind-cli
cd devmind-cli
pip install -e .

# Optional: faster file watching (recommended)
pip install -e ".[fast]"
```

## Usage

```bash
# Start tracking your current project
devmind start

# Watch a specific directory
devmind start ~/projects/myapp

# Check stats at any time (even mid-session)
devmind stats

# Last 8 hours only
devmind stats -H 8

# Get your coding vibe
devmind vibe

# Check if tracking is active
devmind status

# Stop the session
devmind stop

# Wipe the event log
devmind clear
```

## What it tracks

| Signal | How |
|---|---|
| File edits | inotify / polling via watchdog |
| Save frequency | `modify` events per file |
| Time per file | gap analysis between events |
| Activity bursts | clustering rapid edit sequences |
| File switches | sequential file change detection |
| Hourly heatmap | timestamps bucketed by hour |

## Where data lives

```
~/.devmind/
├── session.json   # current/last session metadata
└── events.json    # raw event log (append-only)
```

All data is local. Nothing leaves your machine.

## Vibe examples

```
"You code in bursts like a sprinter — high intensity, then silence."
"You switch files too much → chaotic workflow."
"Laser focus — one file, all session. Surgical precision mode."
"Steady and consistent. You work like a marathon runner."
```

## Extending

Add your own vibe rules in `devmind/analytics.py` → `VIBES` list.
Each entry is `(condition_fn, message_string)`.

Add new event types in `devmind/watcher.py` → `Handler`.

## Dependencies

- Python 3.8+
- `watchdog` (optional, recommended) — falls back to 1.5s polling

---

MIT License
