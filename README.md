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

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | Check with `python3 --version` |
| pip | any | Usually bundled with Python |
| watchdog | 3.0+ | **Optional** but strongly recommended |

---

## Install — step by step

### Step 1 — Check Python

```bash
python3 --version
# Need 3.8 or higher. If missing:

# Ubuntu / Debian
sudo apt update && sudo apt install python3 python3-pip -y

# macOS (via Homebrew)
brew install python3

# Windows — download from https://python.org
# (check "Add to PATH" during install)
```

### Step 2 — Clone the repo

```bash
git clone https://github.com/you/devmind-cli
cd devmind-cli
```

Or if you downloaded the zip:

```bash
unzip devmind-cli.zip
cd devmind
```

### Step 3 — Install DevMind

```bash
# Standard install
pip install -e .

# If pip is not found, try:
pip3 install -e .

# On Linux/macOS, if you get a permissions error:
pip install -e . --user

# On newer Linux distros (Ubuntu 23+) that block system pip:
pip install -e . --break-system-packages
```

### Step 4 — Install watchdog (recommended)

watchdog gives you true real-time file watching via OS-level inotify/FSEvents.
Without it, DevMind falls back to polling every 1.5 seconds — still works, just slightly delayed.

```bash
# With watchdog (recommended)
pip install -e ".[fast]"

# Or install watchdog separately
pip install watchdog

# Verify it's installed
python3 -c "import watchdog; print('watchdog OK')"
```

### Step 5 — Verify install

```bash
devmind --help

# If 'devmind' is not found, your pip bin dir may not be in PATH.
# Fix for Linux/macOS:
export PATH="$HOME/.local/bin:$PATH"
# Add that line to your ~/.bashrc or ~/.zshrc to make it permanent.

# Fix for Windows (PowerShell):
$env:PATH += ";$env:APPDATA\Python\Scripts"
```

---

## Platform-specific notes

### Linux
```bash
sudo apt install python3 python3-pip python3-dev -y
pip install -e ".[fast]"
```

### macOS
```bash
brew install python3
pip3 install -e ".[fast]"
```

### Windows (PowerShell)
```powershell
# Install Python from python.org first, then:
pip install -e ".[fast]"
# Run as: python -m devmind.cli start
```

### Using a virtual environment (cleanest approach)
```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

pip install -e ".[fast]"
devmind start
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
