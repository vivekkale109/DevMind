#!/usr/bin/env bash
# DevMind CLI — auto-installer
# Works on Linux and macOS
# Usage: bash install.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

info()    { echo -e "${CYAN}  ▸ ${RESET}$1"; }
success() { echo -e "${GREEN}  ✓ ${RESET}$1"; }
warn()    { echo -e "${YELLOW}  ⚠ ${RESET}$1"; }
error()   { echo -e "${RED}  ✗ ${RESET}$1"; exit 1; }

echo ""
echo -e "${CYAN}${BOLD}  DevMind CLI — installer${RESET}"
echo -e "${CYAN}  ─────────────────────────────────${RESET}"
echo ""

# ── 1. Python check ──────────────────────────────────────────────────────────
info "Checking Python..."

if command -v python3 &>/dev/null; then
    PY=$(python3 --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo "$PY" | cut -d. -f1)
    MINOR=$(echo "$PY" | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        success "Python $PY found"
    else
        error "Python 3.8+ required, found $PY"
    fi
else
    error "Python 3 not found. Install it from https://python.org or via your package manager."
fi

# ── 2. pip check ─────────────────────────────────────────────────────────────
info "Checking pip..."

if python3 -m pip --version &>/dev/null; then
    success "pip found"
else
    warn "pip not found — attempting to install..."
    python3 -m ensurepip --upgrade || error "Could not install pip. Run: sudo apt install python3-pip"
fi

# ── 3. Install DevMind ────────────────────────────────────────────────────────
info "Installing DevMind..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_FLAGS="-e $SCRIPT_DIR"
WATCHDOG_FLAGS="watchdog"

# Detect externally-managed env (Ubuntu 23+, Debian 12+)
EXTERN_MSG=$(python3 -m pip install --dry-run pip 2>&1 || true)
if echo "$EXTERN_MSG" | grep -q "externally-managed"; then
    warn "System Python detected (externally-managed) — using --break-system-packages"
    INSTALL_FLAGS="$INSTALL_FLAGS --break-system-packages"
    WATCHDOG_FLAGS="$WATCHDOG_FLAGS --break-system-packages"
fi

python3 -m pip install $INSTALL_FLAGS -q && success "DevMind installed"

# ── 4. Install watchdog ───────────────────────────────────────────────────────
info "Installing watchdog (fast file watcher)..."

if python3 -m pip install $WATCHDOG_FLAGS -q 2>/dev/null; then
    success "watchdog installed — real-time watching enabled"
else
    warn "watchdog install failed — falling back to polling mode (still works)"
fi

# ── 5. PATH check ─────────────────────────────────────────────────────────────
echo ""
info "Checking PATH..."

if command -v devmind &>/dev/null; then
    success "devmind command available"
else
    warn "devmind not in PATH"
    echo ""
    echo -e "  Add this to your ${BOLD}~/.bashrc${RESET} or ${BOLD}~/.zshrc${RESET}:"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo ""
    echo -e "  Then run: ${BOLD}source ~/.bashrc${RESET}"
    echo ""
    # Auto-add to shell rc
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.bashrc"
    fi
    if [ -n "$SHELL_RC" ] && ! grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        warn "Added to $SHELL_RC — run: source $SHELL_RC"
    fi
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}  ─────────────────────────────────${RESET}"
echo -e "${GREEN}${BOLD}  DevMind is ready.${RESET}"
echo -e "${GREEN}${BOLD}  ─────────────────────────────────${RESET}"
echo ""
echo -e "  ${BOLD}Quick start:${RESET}"
echo -e "  ${CYAN}devmind start${RESET}     # begin tracking"
echo -e "  ${CYAN}devmind stats${RESET}     # view session stats"
echo -e "  ${CYAN}devmind vibe${RESET}      # get your coding vibe"
echo ""
