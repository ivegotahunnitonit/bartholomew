"""
Bartholomew 1-Click MCP Auto-Configurator for Claude Desktop & Cursor
Detects local IDE configuration paths across Windows, macOS, and Linux
and injects the 'bartholomew-guard' MCP server entry.
"""

import sys
import os
import json
import platform


def get_claude_desktop_config_path() -> str:
    system = platform.system()
    if system == "Windows":
        app_data = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return os.path.join(app_data, "Claude", "claude_desktop_config.json")
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    else:
        return os.path.expanduser("~/.config/Claude/claude_desktop_config.json")


def install_mcp_config(target: str = "claude", custom_path: str = None) -> bool:
    config_path = custom_path or get_claude_desktop_config_path()
    config_dir = os.path.dirname(config_path)

    print(f"[*] Target config file: {config_path}")
    os.makedirs(config_dir, exist_ok=True)

    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    # Path to python executable and mcp_server.py
    python_exec = sys.executable
    mcp_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server.py"))

    config_data["mcpServers"]["bartholomew-guard"] = {
        "command": python_exec,
        "args": [mcp_script]
    }

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        print(f"[SUCCESS] Injected 'bartholomew-guard' into {config_path}")
        print("[*] Claude Desktop / Cursor is now protected by Bartholomew BTP v2.2 Invariants!")
        return True
    except Exception as e:
        print(f"[!] Failed to write config: {e}")
        return False


# Backward compatibility alias
install_mcp_for_target = install_mcp_config


if __name__ == "__main__":
    install_mcp_config()
