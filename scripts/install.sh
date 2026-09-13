#!/usr/bin/env bash
# Bartholomew Desktop 1-Click Installer for macOS & Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.sh | bash

set -e

echo -e "\033[1;36m=================================================================\033[0m"
echo -e "\033[1;32m  Installing Bartholomew Autonomous Trust Protocol (BTP v5.4.4)  \033[0m"
echo -e "\033[1;36m=================================================================\033[0m"

INSTALL_DIR="$HOME/.bartholomew"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[!] Python 3.10+ is required. Please install Python first.\033[0m"
    exit 1
fi

echo -e "\033[1;33m[*] Installing btp-guard v5.4.4 from PyPI...\033[0m"
python3 -m pip install --upgrade btp-guard --quiet || true

# Create executable launcher script
cat << 'EOF' > "$BIN_DIR/bartholomew"
#!/usr/bin/env bash
python3 -m btp_guard.cli "$@" 2>/dev/null || python3 -m src.cli "$@"
EOF

chmod +x "$BIN_DIR/bartholomew"

# Add to PATH in .bashrc or .zshrc if needed
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    echo -e "\033[1;32m[*] Added $BIN_DIR to $SHELL_RC\033[0m"
fi

echo -e "\n\033[1;32m[SUCCESS] Bartholomew Desktop CLI v5.4.4 is installed!\033[0m"
echo -e "\033[1;36mRun the 3-second instant safety sandbox:\033[0m"
echo -e "  \033[1;32mbartholomew try\033[0m"
echo -e "\033[1;36mOther commands:\033[0m"
echo -e "  bartholomew version"
echo -e "  bartholomew init"
echo -e "  bartholomew leads"
echo -e "\033[1;36m=================================================================\033[0m"
