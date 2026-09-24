#!/usr/bin/env bash
# ==============================================================================
# Bartholomew Trust Protocol (BTP v5.4) - Universal POSIX Installer
# https://bartholomew.info
#
# Usage:
#   curl -fsSL https://bartholomew.info/install.sh | bash
# ==============================================================================

set -euo pipefail

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[38;2;16;185;129m"
PURPLE="\033[38;2;168;85;247m"
BLUE="\033[38;2;59;130;246m"
RED="\033[38;2;239;68;68m"
DIM="\033[2m"
RESET="\033[0m"

echo -e "${PURPLE}${BOLD}"
echo "    ____             __  __          __                               "
echo "   / __ )____ ______/ /_/ /_  ____  / /___  ____ ___  ___  __  __     "
echo "  / __  / __ \`/ ___/ __/ __ \/ __ \/ / __ \/ __ \`__ \/ _ \/ / / /     "
echo " / /_/ / /_/ / /  / /_/ / / / /_/ / / /_/ / / / / / /  __/ /_/ /      "
echo "/_____/\__,_/_/   \__/_/ /_/\____/_/\____/_/ /_/ /_/\___/\__,__/       "
echo -e "${RESET}"
echo -e "${BOLD}Bartholomew Agentic Runtime Protection (ARP) -- BTP v5.4.20${RESET}"
echo -e "${DIM}Sub-35us deterministic execution firewall for autonomous AI agents.${RESET}"
echo ""

# 1. Environment & Architecture Detection
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
echo -e "[*] Target Host: ${BOLD}${OS} (${ARCH})${RESET}"

# 2. Check Python 3.10+
PYTHON_BIN=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PY_VER=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)
        MAJOR=$("$candidate" -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo 0)
        MINOR=$("$candidate" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 0)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_BIN="$candidate"
            echo -e "[+] Found Python: ${BOLD}${PYTHON_BIN}${RESET} (v${PY_VER})"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}[ERROR] Python 3.10 or higher is required to run Bartholomew.${RESET}"
    echo "Please install Python 3.10+ (via brew, apt, or uv) and retry."
    exit 1
fi

# 3. Installation Method (uv -> pipx -> pip)
echo -e "[*] Installing/Upgrading ${BOLD}btp-guard${RESET}..."

if command -v uv >/dev/null 2>&1; then
    echo -e "    ${DIM}Using uv fast package installer...${RESET}"
    uv pip install --upgrade btp-guard
elif command -v pipx >/dev/null 2>&1; then
    echo -e "    ${DIM}Using pipx application isolator...${RESET}"
    pipx install btp-guard --force || pipx upgrade btp-guard
else
    echo -e "    ${DIM}Using standard pip installer...${RESET}"
    if "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
        "$PYTHON_BIN" -m pip install --upgrade --user btp-guard 2>/dev/null || \
        "$PYTHON_BIN" -m pip install --upgrade --break-system-packages btp-guard 2>/dev/null || \
        "$PYTHON_BIN" -m pip install --upgrade btp-guard
    else
        echo -e "${RED}[ERROR] pip not found. Please install pip or uv.${RESET}"
        exit 1
    fi
fi

# 4. Verify Installation
echo -e "[*] Verifying Bartholomew Sentinel..."

if command -v btp-guard >/dev/null 2>&1; then
    BTP_BIN="btp-guard"
else
    USER_BASE=$("$PYTHON_BIN" -m site --user-base 2>/dev/null || echo "$HOME/.local")
    if [ -x "$USER_BASE/bin/btp-guard" ]; then
        BTP_BIN="$USER_BASE/bin/btp-guard"
    else
        BTP_BIN="$PYTHON_BIN -m src.cli"
    fi
fi

# 5. Initialize config
CONFIG_DIR="$HOME/.btp"
mkdir -p "$CONFIG_DIR"

echo -e "${GREEN}${BOLD}[SUCCESS] Bartholomew installed successfully!${RESET}"
echo ""
echo -e "${BOLD}Quickstart Commands:${RESET}"
echo -e "  1. Test AST safety gate:      ${PURPLE}btp-guard try${RESET}"
echo -e "  2. Protect any process:       ${PURPLE}btp-guard run -- <your-agent-cmd>${RESET}"
echo -e "  3. Verify an MCP server:      ${PURPLE}btp-guard verify-mcp --url http://localhost:8000/sse${RESET}"
echo -e "  4. Python 1-line wrapper:     ${PURPLE}from btp_guard import protect_agent${RESET}"
echo ""
echo -e "${DIM}Docs & Architecture: https://bartholomew.info${RESET}"
