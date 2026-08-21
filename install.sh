#!/usr/bin/env bash
# Bartholomew Desktop 1-Click Installer for macOS & Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.sh | bash

set -e

echo -e "\033[1;36m=================================================================\033[0m"
echo -e "\033[1;32m  Installing Bartholomew Autonomous Trust Protocol (BTP v2.2.0)  \033[0m"
echo -e "\033[1;36m=================================================================\033[0m"

INSTALL_DIR="$HOME/.bartholomew"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[!] Python 3.10+ is required. Please install Python first.\033[0m"
    exit 1
fi

# Create executable launcher script
cat << 'EOF' > "$BIN_DIR/bartholomew"
#!/usr/bin/env bash
python3 -m src.cli "$@"
EOF

chmod +x "$BIN_DIR/bartholomew"

# Add to PATH in .bashrc or .zshrc if needed
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    echo -e "\033[1;32m[*] Added $BIN_DIR to $SHELL_RC\033[0m"
fi

echo -e "\n\033[1;32m[SUCCESS] Bartholomew Desktop CLI is installed!\033[0m"
echo -e "\033[1;36mYou can now run:\033[0m"
echo -e "  bartholomew version"
echo -e "  bartholomew init"
echo -e "  bartholomew audit ."
echo -e "\033[1;36m=================================================================\033[0m"
