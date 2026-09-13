"""
Bartholomew 1-Click MCP Auto-Configurator for Claude Desktop, Cursor & GPT-6 Astra
Detects local agent configuration paths across Windows, macOS, and Linux
and injects the 'bartholomew-guard' MCP server entry.
"""

import sys
import os
import json
import platform
from typing import Dict, Any, List, Optional


def get_claude_desktop_config_path() -> str:
    system = platform.system()
    if system == "Windows":
        app_data = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return os.path.join(app_data, "Claude", "claude_desktop_config.json")
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    else:
        return os.path.expanduser("~/.config/Claude/claude_desktop_config.json")


def get_cursor_config_path() -> str:
    system = platform.system()
    if system == "Windows":
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        return os.path.join(user_profile, ".cursor", "mcp.json")
    else:
        return os.path.expanduser("~/.cursor/mcp.json")


def get_astra_config_path() -> str:
    return os.path.abspath(".mcp.json")


def get_target_path(target: str, custom_path: Optional[str] = None) -> str:
    if custom_path:
        return os.path.abspath(custom_path)
    target_lower = (target or "claude").lower()
    if target_lower == "cursor":
        return get_cursor_config_path()
    elif target_lower in ("astra", "openai", "swarm"):
        return get_astra_config_path()
    else:
        return get_claude_desktop_config_path()


def install_mcp_config(
    target: str = "claude",
    custom_path: Optional[str] = None,
    dry_run: bool = False
) -> bool:
    target_lower = (target or "claude").lower()
    
    if target_lower == "all":
        targets = ["claude", "cursor", "astra"]
        success = True
        for t in targets:
            if not install_mcp_config(target=t, dry_run=dry_run):
                success = False
        return success

    config_path = get_target_path(target_lower, custom_path)
    config_dir = os.path.dirname(config_path)

    python_exec = sys.executable
    mcp_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server.py"))

    print(f"[*] Target runtime : {target_lower.upper()}")
    print(f"[*] Config file    : {config_path}")

    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    entry = {
        "command": python_exec,
        "args": [mcp_script],
        "env": {
            "BTP_ENFORCE_RING0": "1",
            "BTP_VERSION": "3.1.0"
        }
    }

    config_data["mcpServers"]["bartholomew-guard"] = entry
    config_data["mcpServers"]["bartholomew"] = entry

    if dry_run:
        print(f"[DRY-RUN] Would write following configuration to {config_path}:")
        print(json.dumps(config_data, indent=2))
        return True

    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        print(f"[SUCCESS] Injected 'bartholomew-guard' & 'bartholomew' into {config_path}")
        print(f"[*] {target_lower.upper()} is now protected by Bartholomew BTP v3.1 Ring-0 Invariant Runtime!")
        return True
    except Exception as e:
        print(f"[!] Failed to write config to {config_path}: {e}")
        return False


# Backward compatibility alias
install_mcp_for_target = install_mcp_config


if __name__ == "__main__":
    install_mcp_config()
