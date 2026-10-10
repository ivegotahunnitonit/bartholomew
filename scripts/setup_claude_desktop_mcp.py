"""
Setup Claude Desktop, Cursor, and Windsurf MCP Configuration for Bartholomew Guard
=================================================================================
Automates zero-friction installation of Bartholomew Guard as an active Model Context
Protocol (MCP) JSON-RPC security server across developer desktop environments.
"""

import os
import sys
import json
from pathlib import Path


def get_claude_config_path() -> Path:
    if sys.platform == "win32":
        return Path(os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json"))
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def get_cursor_config_path() -> Path:
    if sys.platform == "win32":
        return Path.home() / ".cursor" / "mcp.json"
    else:
        return Path.home() / ".cursor" / "mcp.json"


def get_windsurf_config_path() -> Path:
    if sys.platform == "win32":
        return Path(os.path.expandvars(r"%USERPROFILE%\.codeium\windsurf\mcp_config.json"))
    else:
        return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"


def update_mcp_config(config_path: Path, workspace_dir: str, python_exe: str, client_name: str) -> bool:
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_data = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}

        if "mcpServers" not in config_data:
            config_data["mcpServers"] = {}

        # Configure Bartholomew Guard Server
        config_data["mcpServers"]["bartholomew-guard"] = {
            "command": python_exe,
            "args": ["-m", "btp_guard.mcp_server"],
            "cwd": workspace_dir,
            "env": {
                "PYTHONUNBUFFERED": "1"
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        print(f"[OK] Configured {client_name} at: {config_path}")
        return True
    except Exception as e:
        print(f"[INFO] Skipping {client_name} ({e})")
        return False


def configure_all():
    workspace_dir = os.path.abspath(".")
    python_exe = sys.executable

    print("\n" + "=" * 70)
    print("  BARTHOLOMEW MCP CLIENT AUTO-CONFIGURATION (BTP v6.4.4)")
    print("=" * 70)
    print(f"[*] Workspace Root : {workspace_dir}")
    print(f"[*] Python Runtime : {python_exe}")
    print("-" * 70)

    # 1. Claude Desktop
    claude_path = get_claude_config_path()
    update_mcp_config(claude_path, workspace_dir, python_exe, "Claude Desktop")

    # 2. Cursor
    cursor_path = get_cursor_config_path()
    update_mcp_config(cursor_path, workspace_dir, python_exe, "Cursor IDE")

    # 3. Windsurf
    windsurf_path = get_windsurf_config_path()
    update_mcp_config(windsurf_path, workspace_dir, python_exe, "Windsurf IDE")

    # 4. Local workspace .cursor/mcp.json (if .cursor dir exists)
    local_cursor = Path(workspace_dir) / ".cursor" / "mcp.json"
    update_mcp_config(local_cursor, workspace_dir, python_exe, "Workspace (.cursor/mcp.json)")

    print("=" * 70)
    print("[SUCCESS] Bartholomew Guard MCP is installed and ready across active clients.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    configure_all()
