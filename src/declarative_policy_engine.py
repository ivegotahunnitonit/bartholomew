"""
Bartholomew Declarative Policy Engine
====================================
Parses and evaluates declarative security rules from YAML and JSON files.
Operates with sub-millisecond execution latency and zero cloud dependencies.
"""

import os
import sys
import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple

class DeclarativePolicyEngine:
    def __init__(self, policy_path: Optional[str] = None):
        self.policy_id = "default-policy"
        self.rules: List[Dict[str, Any]] = []
        if policy_path and os.path.exists(policy_path):
            self.load_policy(policy_path)

    def load_policy(self, filepath: str) -> None:
        """Loads policy from JSON or YAML file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Policy file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if filepath.endswith(".json"):
            data = json.loads(content)
        else:
            # Try PyYAML if installed, otherwise basic YAML parser
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                data = self._parse_basic_yaml(content)

        self.policy_id = data.get("policy_id", "urn:btp:policy:custom")
        self.rules = data.get("rules", [])

    def _parse_basic_yaml(self, content: str) -> Dict[str, Any]:
        """Simple native YAML-to-dict parser fallback for zero-dependency environments."""
        result = {"rules": []}
        lines = content.splitlines()
        current_rule = None
        current_list = None
        current_list_key = None

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("policy_id:"):
                result["policy_id"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("- id:"):
                current_rule = {"id": stripped.split(":", 1)[1].strip().strip('"').strip("'")}
                result["rules"].append(current_rule)
                current_list = None
            elif current_rule is not None:
                if stripped.startswith("- ") and current_list_key:
                    val = stripped[2:].strip().strip('"').strip("'")
                    current_rule[current_list_key].append(val)
                elif ":" in stripped:
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if not val:
                        current_rule[key] = []
                        current_list_key = key
                    else:
                        try:
                            if "." in val:
                                current_rule[key] = float(val)
                            else:
                                current_rule[key] = int(val)
                        except ValueError:
                            current_rule[key] = val
                        current_list_key = None

        return result

    def evaluate_payload(self, payload: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Evaluates a payload dictionary against all loaded declarative rules.
        Returns: (is_allowed, reason, latency_microseconds)
        """
        start_us = time.perf_counter()
        raw_str = json.dumps(payload).lower()

        for rule in self.rules:
            rule_type = rule.get("type")
            action = rule.get("action", "DENY")
            message = rule.get("message", f"Rule violation: {rule.get('id')}")

            # 1. Max Threshold Check
            if rule_type == "max_threshold":
                field = rule.get("field")
                max_val = float(rule.get("value", 0.0))
                if field in payload and isinstance(payload[field], (int, float)):
                    if payload[field] > max_val:
                        latency_us = (time.perf_counter() - start_us) * 1_000_000
                        return (False, message, round(latency_us, 2))

            # 2. Forbidden Substrings / Regex
            elif rule_type == "forbidden_substrings":
                patterns = rule.get("patterns", [])
                for pat in patterns:
                    if str(pat).lower() in raw_str:
                        latency_us = (time.perf_counter() - start_us) * 1_000_000
                        return (False, f"{message} (Pattern: '{pat}')", round(latency_us, 2))

            # 3. Disallowed Values
            elif rule_type == "disallowed_values":
                field = rule.get("field")
                disallowed = [str(d).lower() for d in rule.get("disallowed", [])]
                if field in payload and str(payload[field]).lower() in disallowed:
                    latency_us = (time.perf_counter() - start_us) * 1_000_000
                    return (False, message, round(latency_us, 2))

        latency_us = (time.perf_counter() - start_us) * 1_000_000
        return (True, "All declarative policy rules passed.", round(latency_us, 2))
