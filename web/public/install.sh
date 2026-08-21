#!/usr/bin/env bash
# Bartholomew Desktop 1-Click Installer for macOS and Linux
# Usage: curl -fsSL https://bartholomew.info/install.sh | bash

set -e

echo "================================================================="
echo "  Installing Bartholomew Autonomous Trust Protocol (BTP v2.2.0)  "
echo "================================================================="

INSTALL_DIR="$HOME/.bartholomew"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"
echo "[*] Setting up Bartholomew in: $INSTALL_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3.10+ is required. Please install Python first."
    exit 1
fi

# Create launcher script
cat << 'EOF' > "$BIN_DIR/bartholomew"
#!/usr/bin/env bash
python3 -m src.cli "$@"
EOF
chmod +x "$BIN_DIR/bartholomew"

# Add to PATH if not present
SHELL_RC="$HOME/.bashrc"
if [[ "$SHELL" == */zsh ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    echo "[*] Added $BIN_DIR to $SHELL_RC"
fi

echo ""
echo "[SUCCESS] Bartholomew Desktop CLI is installed!"
echo "Run 'source $SHELL_RC' or open a new terminal, then run:"
echo "  bartholomew version"
echo "  bartholomew init"
echo "  bartholomew daemon start"
echo "================================================================="
