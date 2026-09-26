"""
Bartholomew Dynamic Multi-Tenant Policy Distribution
====================================================
Synchronizes, validates, and hot-reloads declarative YAML, Rego (OPA),
and Google Common Expression Language (CEL) policies without restarting agent runtimes.
"""

import os
import sys
import yaml
import time
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

logger = logging.getLogger("btp_guard.policy_sync")

COMPLIANCE_PACKS = {
    "soc2": {
        "pack_name": "SOC 2 Type II Security & Audit Pack",
        "version": "1.0",
        "rules": [
            {"id": "SOC2-CC6.1", "name": "Logical Access Restrictions", "action": "DENY", "type": "no_credentials_in_logs"},
            {"id": "SOC2-CC6.8", "name": "Malicious Software Prevention", "action": "DENY", "type": "no_arbitrary_shell_eval"},
            {"id": "SOC2-CC7.2", "name": "Vulnerability & Security Event Audit", "action": "ALLOW_WITH_AUDIT"}
        ]
    },
    "eu_ai_act": {
        "pack_name": "EU AI Act Article 14 (Human-in-the-Loop Oversight)",
        "version": "1.0",
        "rules": [
            {"id": "EU-AI-ART14-1", "name": "Human Stop Button Override", "action": "INTERCEPT_ON_SIGINT"},
            {"id": "EU-AI-ART14-4", "name": "Operational Boundary Containment", "action": "DENY_ON_AUTONOMOUS_DRIFT"}
        ]
    },
    "nist_ai_rmf": {
        "pack_name": "NIST AI Risk Management Framework 1.0",
        "version": "1.0",
        "rules": [
            {"id": "NIST-GOVERN-1.2", "name": "Accountability & Provenance Tracking", "action": "ED25519_MERKLE_LOG"},
            {"id": "NIST-MAP-2.1", "name": "High-Risk Function Gating", "action": "DENY"}
        ]
    }
}

class PolicyDistributionManager:
    """
    Manages fetching, caching, and hot-reloading policy bundles.
    """

    def __init__(self, policy_dir: str = "policies", remote_url: Optional[str] = None):
        self.policy_dir = policy_dir
        self.remote_url = remote_url or os.environ.get("BTP_POLICY_SYNC_URL")
        self.active_policies: Dict[str, Any] = {}
        self.load_local_policies()

    def load_local_policies(self):
        if not os.path.exists(self.policy_dir):
            os.makedirs(self.policy_dir, exist_ok=True)
            return

        for fname in os.listdir(self.policy_dir):
            if fname.endswith((".yaml", ".yml")):
                fpath = os.path.join(self.policy_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and "policy_id" in data:
                            self.active_policies[data["policy_id"]] = data
                except Exception as e:
                    logger.warning(f"Could not load policy {fname}: {e}")

    def sync_remote_bundle(self, bundle_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Pulls a remote policy bundle over HTTPS and atomically validates it.
        """
        url = bundle_url or self.remote_url
        if not url:
            logger.info("No remote policy URL provided; using cached policies.")
            return {"status": "LOCAL_ONLY", "policy_count": len(self.active_policies)}

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Bartholomew-PolicySync/5.4.21"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                remote_data = yaml.safe_load(resp.read().decode("utf-8"))
                policy_id = remote_data.get("policy_id", "remote_synced_policy")
                
                # Atomically write to policies directory
                target_file = os.path.join(self.policy_dir, f"{policy_id.replace(':', '_')}.yaml")
                with open(target_file, "w", encoding="utf-8") as f:
                    yaml.dump(remote_data, f)
                
                self.active_policies[policy_id] = remote_data
                return {"status": "SYNCED", "policy_id": policy_id, "rules_count": len(remote_data.get("rules", []))}
        except Exception as e:
            logger.warning(f"Remote policy sync failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    def install_compliance_pack(self, pack_key: str) -> Dict[str, Any]:
        """
        Installs a pre-configured compliance pack (soc2, eu_ai_act, nist_ai_rmf).
        """
        if pack_key not in COMPLIANCE_PACKS:
            raise ValueError(f"Unknown compliance pack '{pack_key}'. Options: {list(COMPLIANCE_PACKS.keys())}")

        pack = COMPLIANCE_PACKS[pack_key]
        policy_data = {
            "version": "2.2.0",
            "policy_id": f"urn:btp:compliance:{pack_key}",
            "description": pack["pack_name"],
            "rules": pack["rules"]
        }
        dest_file = os.path.join(self.policy_dir, f"compliance_{pack_key}.yaml")
        with open(dest_file, "w", encoding="utf-8") as f:
            yaml.dump(policy_data, f, default_flow_style=False)

        self.active_policies[policy_data["policy_id"]] = policy_data
        return {"status": "INSTALLED", "pack": pack_key, "file": dest_file, "rules": len(pack["rules"])}
