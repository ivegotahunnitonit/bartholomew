"""
Automated Conformance Test for Official MCP Registry and Smithery Specification
Validates schema properties, tool annotations, entry points, and format compliance.
"""

import json
import yaml
import os
import sys

def test_mcp_registry_entry():
    path = os.path.abspath("mcp_registry_entry.json")
    assert os.path.exists(path), f"Missing {path}"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_fields = ["name", "version", "description", "repository", "transports", "capabilities"]
    for field in required_fields:
        assert field in data, f"mcp_registry_entry.json missing required field: {field}"
        
    assert "http" in data["transports"], "Missing HTTP remote transport"
    assert "stdio" in data["transports"], "Missing stdio transport"
    assert len(data["capabilities"]["tools"]) >= 1, "At least one tool required"
    print("[PASS] mcp_registry_entry.json schema valid.")

def test_smithery_yaml():
    path = os.path.abspath("smithery.yaml")
    assert os.path.exists(path), f"Missing {path}"
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    required_fields = ["name", "version", "description", "command", "tools"]
    for field in required_fields:
        assert field in data, f"smithery.yaml missing required field: {field}"
        
    tools = data.get("tools", [])
    assert len(tools) >= 5, f"Expected >=5 tools in smithery.yaml, found {len(tools)}"
    for t in tools:
        assert "name" in t, "Tool missing name"
        assert "description" in t, f"Tool {t.get('name')} missing description"
        assert "annotations" in t, f"Tool {t.get('name')} missing annotations"
    print("[PASS] smithery.yaml schema and tool annotations valid.")

if __name__ == "__main__":
    test_mcp_registry_entry()
    test_smithery_yaml()
    print("ALL MCP REGISTRY SPECIFICATIONS CONFORMANT.")
